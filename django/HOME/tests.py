from django.urls import reverse

from CORE.testing import SPDTestCase, png_upload
from .models import BannerImage, RushFormLink, RushSlide


class PublicPagesTests(SPDTestCase):

    def test_public_pages_load_without_login(self):
        for name in ['home', 'ourHistory', 'rush', 'codeOfEthics', 'executive_board']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_public_pages_load_when_logged_in(self):
        self.login(self.make_member('brother', 'ACTIVE'))
        for name in ['home', 'ourHistory', 'rush', 'codeOfEthics', 'executive_board']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_home_shows_banner_and_rush_link(self):
        BannerImage.objects.create(image=png_upload('banner.png'))
        RushFormLink.objects.create(link='https://example.com/rush')
        response = self.client.get(reverse('home'))
        self.assertIsNotNone(response.context['banner_image'])
        self.assertEqual(response.context['rush_form_link'].link, 'https://example.com/rush')

    def test_our_history_counts_active_members(self):
        self.make_member('a1', 'ACTIVE')
        self.make_member('a2', 'ACTIVE', 'EXEC')
        self.make_member('alum', 'ALUMNI')
        response = self.client.get(reverse('ourHistory'))
        self.assertEqual(response.context['num_actives'], 2)

    def test_rush_slides_are_ordered(self):
        RushSlide.objects.create(image=png_upload('b.png'), caption='Second', order=2)
        RushSlide.objects.create(image=png_upload('a.png'), caption='First', order=1)
        response = self.client.get(reverse('rush'))
        self.assertEqual([s.caption for s in response.context['rush_slides']], ['First', 'Second'])

    def test_executive_board_lists_officers_in_order(self):
        self.make_member('risk', 'ACTIVE', 'RISK_MGR', first='Riley')
        self.make_member('pres', 'ACTIVE', 'PRESIDENT', first='Pat')
        self.make_member('plain', 'ACTIVE')
        response = self.client.get(reverse('executive_board'))
        board = [(position, b.firstName) for position, b in response.context['exec_board_brothers']]
        self.assertEqual(board, [('President', 'Pat'), ('Director of Risk Management', 'Riley')])


class SingletonModelTests(SPDTestCase):
    """The banner image and rush form link only ever keep the newest entry."""

    def test_only_one_banner_image_is_kept(self):
        BannerImage.objects.create(image=png_upload('one.png'))
        BannerImage.objects.create(image=png_upload('two.png'))
        self.assertEqual(BannerImage.objects.count(), 1)

    def test_only_one_rush_link_is_kept(self):
        RushFormLink.objects.create(link='https://example.com/old')
        RushFormLink.objects.create(link='https://example.com/new')
        self.assertEqual(list(RushFormLink.objects.values_list('link', flat=True)), ['https://example.com/new'])
