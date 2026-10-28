import json
from unittest import expectedFailure

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from PIL import Image

from CORE.testing import SPDTestCase, PASSWORD, png_upload
from MISC.models import AnnouncementAlert
from .models import Brother_Profile, DashboardLink, Major
from .permissions import has_role, requires_role, get_user_roles
from .utils import contains_profanity


class PermissionsTests(SPDTestCase):

    def setUp(self):
        self.active = self.make_member('active', 'ACTIVE')
        self.no_profile = self.make_member('noprofile', profile=False)

    def test_has_role(self):
        self.assertTrue(has_role(self.active, 'ACTIVE'))
        self.assertFalse(has_role(self.active, 'EXEC'))

    def test_user_without_profile_has_no_roles(self):
        self.assertEqual(get_user_roles(self.no_profile), set())
        self.assertFalse(has_role(self.no_profile, 'ACTIVE'))

    def test_anonymous_user_has_no_roles(self):
        self.assertFalse(has_role(AnonymousUser(), 'ACTIVE'))

    def test_misspelled_role_raises(self):
        with self.assertRaises(ValueError):
            has_role(self.active, 'PHILANTHROPY_CHAIR')
        with self.assertRaises(ValueError):
            requires_role('PLEDGE_BOARD')

    def test_requires_role_redirects_logged_out_user_to_login(self):
        response = self.client.get(reverse('poll'))
        self.assertRedirectsToLogin(response)

    def test_requires_role_redirects_user_without_profile(self):
        self.login(self.no_profile)
        response = self.client.get(reverse('poll'))
        self.assertDenied(response)
        self.assertIn('User profile not found.', self.messages_for(response))

    def test_requires_role_names_missing_roles(self):
        self.login(self.active)
        response = self.client.get(reverse('start_vote'))
        self.assertDenied(response)
        self.assertTrue(any("'EXEC'" in m for m in self.messages_for(response)))

    def test_requires_role_sends_user_back_to_previous_page(self):
        self.login(self.active)
        response = self.client.get(reverse('start_vote'), HTTP_REFERER='/auth/dashboard/')
        self.assertEqual(response['Location'], '/auth/dashboard/')


class LoginLogoutTests(SPDTestCase):

    def setUp(self):
        self.user = self.make_member('brother', 'ACTIVE')

    def test_login_page_loads(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    def test_valid_login_redirects_home(self):
        response = self.client.post(reverse('login'), {'username': 'brother', 'password': PASSWORD})
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_follows_next_parameter(self):
        response = self.client.post(reverse('login') + '?next=/poll/', {'username': 'brother', 'password': PASSWORD})
        self.assertEqual(response['Location'], '/poll/')

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {'username': 'brother', 'password': 'wrong'})
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)
        self.assertIn('Invalid username or password.', self.messages_for(response))
        self.assertNotIn('_auth_user_id', self.client.session)

    @expectedFailure
    def test_login_does_not_redirect_to_other_sites(self):
        """KNOWN BUG: ?next= is followed blindly, so a link can send users to any site after logging in."""
        response = self.client.post(reverse('login') + '?next=https://evil.example.com/',
                                    {'username': 'brother', 'password': PASSWORD})
        self.assertFalse(response['Location'].startswith('https://evil.example.com'))

    def test_logout(self):
        self.login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)


class DashboardAndRosterTests(SPDTestCase):

    def setUp(self):
        self.active = self.make_member('active', 'ACTIVE', last='Adams')
        self.alumnus = self.make_member('alumnus', 'ALUMNI', last='Baker')
        self.new_member = self.make_member('newbie', 'NEW_MEMBER', last='Clark')

    def test_pages_require_login(self):
        for name in ['dashboard', 'roster', 'alumni_roster', 'profile']:
            with self.subTest(page=name):
                self.assertRedirectsToLogin(self.client.get(reverse(name)))

    def test_dashboard_shows_links_and_only_active_announcements(self):
        DashboardLink.objects.create(text='Minutes', link='https://example.com', order=1)
        AnnouncementAlert.objects.create(title='Shown', content='x', is_active=True)
        AnnouncementAlert.objects.create(title='Hidden', content='x', is_active=False)
        self.login(self.active)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([a.title for a in response.context['announcements']], ['Shown'])
        self.assertEqual([l.text for l in response.context['dashboard_links']], ['Minutes'])

    def test_new_members_are_sent_to_new_member_page(self):
        self.login(self.new_member)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/newmember/', fetch_redirect_response=False)

    def test_roster_excludes_alumni(self):
        self.login(self.active)
        response = self.client.get(reverse('roster'))
        self.assertEqual(response.status_code, 200)
        names = [b.user.username for b in response.context['Brother_Profiles']]
        self.assertEqual(names, ['active', 'newbie'])

    def test_alumni_roster_lists_only_alumni(self):
        self.login(self.active)
        response = self.client.get(reverse('alumni_roster'))
        self.assertEqual([b.user.username for b in response.context['Brother_Profiles']], ['alumnus'])


class ProfileTests(SPDTestCase):

    def setUp(self):
        self.user = self.make_member('brother', 'ACTIVE')
        self.login(self.user)

    def post_json(self, name, data):
        return self.client.post(reverse(name), json.dumps(data), content_type='application/json').json()

    def profile_data(self, **overrides):
        data = {'username': 'renamed', 'email': 'new@example.com', 'firstName': 'Sam',
                'lastName': 'Smith', 'hometown': 'Kansas City', 'pclass': ''}
        data.update(overrides)
        return data

    def test_profile_page_loads(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['brother_profile'].user, self.user)

    def test_update_profile(self):
        result = self.client.post(reverse('update_profile'), self.profile_data()).json()
        self.assertTrue(result['success'])
        self.user.refresh_from_db()
        self.assertEqual((self.user.username, self.user.email), ('renamed', 'new@example.com'))
        self.assertEqual(self.user.brother_profile.hometown, 'Kansas City')

    def test_update_profile_rejects_profanity(self):
        result = self.client.post(reverse('update_profile'), self.profile_data(firstName='shithead')).json()
        self.assertFalse(result['success'])
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'brother')

    @expectedFailure
    def test_update_profile_accepts_columbia_hometown(self):
        """KNOWN BUG: the profanity filter matches 'bi' inside 'Columbia', so this hometown can't be saved."""
        result = self.client.post(reverse('update_profile'), self.profile_data(hometown='Columbia')).json()
        self.assertTrue(result['success'])

    def test_update_profile_get_is_rejected(self):
        self.assertFalse(self.client.get(reverse('update_profile')).json()['success'])

    def test_change_password(self):
        result = self.post_json('change-password', {'current_password': PASSWORD,
                                                    'new_password1': 'Brand-New-Pass-9', 'new_password2': 'Brand-New-Pass-9'})
        self.assertTrue(result['success'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Brand-New-Pass-9'))
        # still logged in after the change
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)

    def test_change_password_wrong_current_password(self):
        result = self.post_json('change-password', {'current_password': 'nope',
                                                    'new_password1': 'Brand-New-Pass-9', 'new_password2': 'Brand-New-Pass-9'})
        self.assertEqual(result['error'], 'Current password is incorrect.')

    def test_change_password_mismatch(self):
        result = self.post_json('change-password', {'current_password': PASSWORD,
                                                    'new_password1': 'Brand-New-Pass-9', 'new_password2': 'Different-Pass-9'})
        self.assertEqual(result['error'], 'New passwords do not match.')

    @expectedFailure
    def test_change_password_enforces_password_rules(self):
        """KNOWN BUG: AUTH_PASSWORD_VALIDATORS are never applied, so a one-letter password is accepted."""
        result = self.post_json('change-password', {'current_password': PASSWORD,
                                                    'new_password1': 'a', 'new_password2': 'a'})
        self.assertFalse(result['success'])

    def test_update_photo_resizes_and_saves(self):
        response = self.client.post(reverse('update_photo'), {'profile_photo': png_upload()},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(response.json()['success'])
        image = Brother_Profile.objects.get(user=self.user).profileImage
        self.assertTrue(image)
        with Image.open(image.path) as saved:
            self.assertLessEqual(max(saved.size), 300)

    def test_reset_photo(self):
        self.client.post(reverse('update_photo'), {'profile_photo': png_upload()})
        result = self.client.post(reverse('reset_photo')).json()
        self.assertTrue(result['success'])
        self.assertFalse(Brother_Profile.objects.get(user=self.user).profileImage)

    def test_update_majors_replaces_list(self):
        self.post_json('update_majors', {'majors': ['Computer Science', 'Physics']})
        self.post_json('update_majors', {'majors': ['Mathematics']})
        majors = list(Brother_Profile.objects.get(user=self.user).majors.values_list('name', flat=True))
        self.assertEqual(majors, ['Mathematics'])

    def test_add_custom_major_capitalizes(self):
        result = self.post_json('add_custom_major', {'major_name': '  aerospace   engineering '})
        self.assertEqual(result['major_name'], 'Aerospace Engineering')
        self.assertTrue(Major.objects.filter(name='Aerospace Engineering').exists())

    def test_add_custom_major_rejects_profanity(self):
        result = self.post_json('add_custom_major', {'major_name': 'bullshit studies'})
        self.assertFalse(result['success'])


class ProfanityFilterTests(SPDTestCase):

    def test_flags_inappropriate_words(self):
        for text in ['fuck', 'You Bastard', 'shithead']:
            with self.subTest(text=text):
                self.assertTrue(contains_profanity(text))

    def test_allows_normal_text(self):
        for text in ['Computer Science', 'Mechanical Engineering', 'Kansas City', 'St. Louis']:
            with self.subTest(text=text):
                self.assertFalse(contains_profanity(text))

    def test_whitelist(self):
        for text in ['Biology', 'Biomedical Engineering', 'Biological Engineering']:
            with self.subTest(text=text):
                self.assertFalse(contains_profanity(text))

    @expectedFailure
    def test_does_not_flag_words_that_merely_contain_a_bad_word(self):
        """KNOWN BUG: matching is by substring, so ordinary names and places are rejected."""
        for text in ['Columbia', 'Data Analytics', 'Michelle', 'Hancock', 'Classics', 'Hello']:
            self.assertFalse(contains_profanity(text), text)
