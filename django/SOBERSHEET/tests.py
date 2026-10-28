from datetime import date

from django.urls import reverse

from AUTHENTICATE.models import Role
from CORE.testing import SPDTestCase
from .models import Sober_Duty, Sober_Exemption
from .views_functions import build_sobersheet_queue, pick_next_sobers, semester_index, semester_label


class SobersheetTestCase(SPDTestCase):

    def setUp(self):
        self.risk = self.make_member('risk', 'ACTIVE', 'RISK_MGR', first='Riley', last='Risk')
        self.adams = self.make_member('adams', 'ACTIVE', last='Adams')
        self.baker = self.make_member('baker', 'ACTIVE', last='Baker')
        self.clark = self.make_member('clark', 'ACTIVE', last='Clark')
        self.alumnus = self.make_member('alumnus', 'ALUMNI')

    def duty(self, user, when, title='Mixer', duty_type='MONITOR'):
        return Sober_Duty.objects.create(user=user, event_title=title, event_date=when, duty_type=duty_type)

    def queue_usernames(self):
        return [(g['label'], [m['profile'].user.username for m in g['brothers']]) for g in build_sobersheet_queue()]


class AccessTests(SobersheetTestCase):

    def test_logged_out_users_are_sent_to_login(self):
        for name in ['sobersheet_dashboard', 'sobersheet_history', 'sobersheet_log', 'sobersheet_picker']:
            with self.subTest(page=name):
                self.assertRedirectsToLogin(self.client.get(reverse(name)))

    def test_active_members_can_view(self):
        self.login(self.adams)
        for url in [reverse('sobersheet_dashboard'), reverse('sobersheet_history'),
                    reverse('brother_sobersheet_history', args=[self.baker.id])]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_alumni_cannot_view(self):
        self.login(self.alumnus)
        self.assertDenied(self.client.get(reverse('sobersheet_dashboard')))

    def test_only_risk_manager_can_manage(self):
        duty = self.duty(self.adams, date(2025, 9, 1))
        self.login(self.adams)
        for url in [reverse('sobersheet_log'), reverse('sobersheet_picker'), reverse('sobersheet_edit', args=[duty.id])]:
            with self.subTest(url=url):
                self.assertDenied(self.client.get(url))
        self.assertDenied(self.client.post(reverse('sobersheet_delete', args=[duty.id])))
        self.assertTrue(Sober_Duty.objects.filter(id=duty.id).exists())

        self.login(self.risk)
        for url in [reverse('sobersheet_log'), reverse('sobersheet_picker'), reverse('sobersheet_edit', args=[duty.id])]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_risk_manager_flag(self):
        self.login(self.adams)
        self.assertFalse(self.client.get(reverse('sobersheet_dashboard')).context['is_risk_manager'])
        self.login(self.risk)
        self.assertTrue(self.client.get(reverse('sobersheet_dashboard')).context['is_risk_manager'])


class QueueTests(SobersheetTestCase):

    def test_never_sobered_first_then_oldest_semester(self):
        self.duty(self.adams, date(2025, 9, 1))     # Fall 2025
        self.duty(self.baker, date(2025, 2, 1))     # Spring 2025
        self.assertEqual(self.queue_usernames(), [
            ('Never sobered', ['clark']),
            ('Spring 2025', ['baker']),
            ('Fall 2025', ['adams']),
        ])

    def test_most_recent_duty_decides_the_group(self):
        self.duty(self.adams, date(2024, 2, 1))
        self.duty(self.adams, date(2025, 9, 1))
        self.duty(self.baker, date(2025, 2, 1))
        self.duty(self.clark, date(2025, 2, 1))
        labels = dict(self.queue_usernames())
        self.assertEqual(labels['Fall 2025'], ['adams'])
        self.assertNotIn('Spring 2024', labels)

    def test_risk_manager_is_exempt_and_listed_separately(self):
        self.login(self.adams)
        context = self.client.get(reverse('sobersheet_dashboard')).context
        queued = [m['profile'].user for g in context['queue_groups'] for m in g['brothers']]
        self.assertNotIn(self.risk, queued)
        self.assertEqual([m['profile'].user for m in context['exempt_brothers']], [self.risk])

    def test_becoming_risk_manager_creates_permanent_exemption(self):
        risk_role = Role.objects.get(name='RISK_MGR')
        self.adams.brother_profile.roles.add(risk_role)
        self.assertTrue(Sober_Exemption.objects.filter(user=self.adams).exists())
        # stepping down keeps the exemption
        self.adams.brother_profile.roles.remove(risk_role)
        self.assertNotIn('adams', [u for _, users in self.queue_usernames() for u in users])

    def test_exemption_when_role_is_assigned_from_the_role_side(self):
        Role.objects.get(name='RISK_MGR').brother_profile_set.add(self.baker.brother_profile)
        self.assertTrue(Sober_Exemption.objects.filter(user=self.baker).exists())

    def test_other_roles_do_not_create_exemptions(self):
        self.clark.brother_profile.roles.add(Role.objects.get_or_create(name='EXEC')[0])
        self.assertFalse(Sober_Exemption.objects.filter(user=self.clark).exists())


class LogEditDeleteTests(SobersheetTestCase):

    def setUp(self):
        super().setUp()
        self.login(self.risk)

    def log(self, brothers, title='Formal', duty_type='DRIVER', when='2025-10-04'):
        return self.client.post(reverse('sobersheet_log'), {
            'event_title': title, 'event_date': when, 'duty_type': duty_type,
            'brothers': [b.id for b in brothers]})

    def test_log_duties(self):
        response = self.log([self.adams, self.baker])
        self.assertRedirects(response, reverse('sobersheet_dashboard'), fetch_redirect_response=False)
        self.assertEqual(Sober_Duty.objects.filter(event_title='Formal', duty_type='DRIVER').count(), 2)
        self.assertEqual(Sober_Duty.objects.first().logged_by, self.risk)

    def test_logging_same_event_twice_does_not_duplicate(self):
        self.log([self.adams])
        response = self.log([self.adams, self.baker])
        self.assertIn('Logged 1 sober duty record(s).', self.messages_for(response))
        self.assertEqual(Sober_Duty.objects.count(), 2)

    def test_log_rejects_bad_input(self):
        cases = {
            'blank title': dict(brothers=[self.adams], title='   '),
            'bad duty type': dict(brothers=[self.adams], duty_type='BOUNCER'),
            'nobody selected': dict(brothers=[]),
            'not active': dict(brothers=[self.alumnus]),
        }
        for label, kwargs in cases.items():
            with self.subTest(label):
                response = self.log(**kwargs)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(any(m.startswith('Error logging') for m in self.messages_for(response)))
        self.assertFalse(Sober_Duty.objects.exists())

    def test_log_form_preselects_brothers_from_query(self):
        response = self.client.get(reverse('sobersheet_log'), {'brothers': [self.adams.id]})
        self.assertEqual(response.context['preselected'], {str(self.adams.id)})

    def test_edit_duty(self):
        duty = self.duty(self.adams, date(2025, 9, 1))
        response = self.client.post(reverse('sobersheet_edit', args=[duty.id]), {
            'event_title': 'Renamed', 'event_date': '2025-09-02', 'duty_type': 'DRIVER'})
        self.assertRedirects(response, reverse('sobersheet_history'), fetch_redirect_response=False)
        duty.refresh_from_db()
        self.assertEqual((duty.event_title, duty.event_date, duty.duty_type), ('Renamed', date(2025, 9, 2), 'DRIVER'))

    def test_delete_requires_post(self):
        duty = self.duty(self.adams, date(2025, 9, 1))
        self.assertEqual(self.client.get(reverse('sobersheet_delete', args=[duty.id])).status_code, 405)
        self.client.post(reverse('sobersheet_delete', args=[duty.id]))
        self.assertFalse(Sober_Duty.objects.exists())


class HistoryTests(SobersheetTestCase):

    def test_history_grouped_by_event_newest_first(self):
        self.duty(self.adams, date(2025, 9, 1), title='Mixer')
        self.duty(self.baker, date(2025, 9, 1), title='Mixer')
        self.duty(self.clark, date(2025, 10, 1), title='Formal')
        self.login(self.adams)
        groups = self.client.get(reverse('sobersheet_history')).context['history_groups']
        self.assertEqual([(g['title'], len(g['duties'])) for g in groups], [('Formal', 1), ('Mixer', 2)])

    def test_brother_history_grouped_by_semester(self):
        self.duty(self.adams, date(2025, 9, 1))
        self.duty(self.adams, date(2025, 10, 1), title='Formal')
        self.duty(self.adams, date(2025, 3, 1))
        self.login(self.baker)
        context = self.client.get(reverse('brother_sobersheet_history', args=[self.adams.id])).context
        self.assertEqual([(g['label'], len(g['duties'])) for g in context['semester_groups']],
                         [('Fall 2025', 2), ('Spring 2025', 1)])
        self.assertEqual(context['lifetime_total'], 3)

    def test_brother_history_unknown_user(self):
        self.login(self.adams)
        response = self.client.get(reverse('brother_sobersheet_history', args=[99999]))
        self.assertRedirects(response, reverse('sobersheet_dashboard'), fetch_redirect_response=False)


class PickerTests(SobersheetTestCase):

    def setUp(self):
        super().setUp()
        self.duty(self.adams, date(2025, 2, 1))
        self.duty(self.baker, date(2025, 2, 15))
        # clark has never sobered

    def picked(self, count, method):
        return [p['profile'].user.username for p in pick_next_sobers(count, method)]

    def test_never_sobered_are_picked_first(self):
        self.assertEqual(self.picked(1, 'earliest'), ['clark'])

    def test_earliest_fills_from_next_group_by_date(self):
        self.assertEqual(self.picked(2, 'earliest'), ['clark', 'adams'])

    def test_random_still_takes_whole_older_groups_first(self):
        picks = self.picked(2, 'random')
        self.assertEqual(picks[0], 'clark')
        self.assertIn(picks[1], {'adams', 'baker'})

    def test_asking_for_more_than_available(self):
        self.assertEqual(sorted(self.picked(10, 'earliest')), ['adams', 'baker', 'clark'])

    def test_picker_page(self):
        self.login(self.risk)
        response = self.client.post(reverse('sobersheet_picker'), {'count': 5, 'method': 'earliest'})
        self.assertEqual(len(response.context['picks']), 3)
        self.assertTrue(any('Only 3 eligible brothers' in m for m in self.messages_for(response)))

    def test_picker_rejects_bad_input(self):
        self.login(self.risk)
        for data in [{'count': 0, 'method': 'earliest'}, {'count': 2, 'method': 'alphabetical'}, {'count': 'two'}]:
            with self.subTest(data=data):
                response = self.client.post(reverse('sobersheet_picker'), data)
                self.assertNotIn('picks', response.context)
                self.assertTrue(any(m.startswith('Error') for m in self.messages_for(response)))


class SemesterHelperTests(SPDTestCase):

    def test_semester_labels(self):
        self.assertEqual(semester_label(semester_index(date(2025, 1, 15))), 'Spring 2025')
        self.assertEqual(semester_label(semester_index(date(2025, 6, 30))), 'Spring 2025')
        self.assertEqual(semester_label(semester_index(date(2025, 7, 1))), 'Fall 2025')

    def test_fall_sorts_after_spring(self):
        self.assertLess(semester_index(date(2025, 3, 1)), semester_index(date(2025, 9, 1)))
        self.assertLess(semester_index(date(2025, 9, 1)), semester_index(date(2026, 3, 1)))
