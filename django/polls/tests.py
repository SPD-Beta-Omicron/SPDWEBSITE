from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from core.testing import SPDTestCase
from .models import Brother_votes, Vote_Poll


class PollAccessTests(SPDTestCase):

    def setUp(self):
        self.active = self.make_member('active', 'ACTIVE')
        self.exec = self.make_member('exec', 'ACTIVE', 'EXEC')
        self.alumnus = self.make_member('alumnus', 'ALUMNI')

    def test_logged_out_users_are_sent_to_login(self):
        for name in ['poll', 'start_vote', 'past_polls', 'poll_results']:
            with self.subTest(page=name):
                self.assertRedirectsToLogin(self.client.get(reverse(name)))

    def test_active_members_can_see_poll_pages(self):
        self.login(self.active)
        for name in ['poll', 'past_polls']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_alumni_cannot_see_poll(self):
        self.login(self.alumnus)
        self.assertDenied(self.client.get(reverse('poll')))

    def test_only_exec_can_open_start_vote(self):
        self.login(self.active)
        self.assertDenied(self.client.get(reverse('start_vote')))
        self.login(self.exec)
        self.assertEqual(self.client.get(reverse('start_vote')).status_code, 200)


class VotingTests(SPDTestCase):

    def setUp(self):
        self.active = self.make_member('active', 'ACTIVE')
        self.exec = self.make_member('exec', 'ACTIVE', 'EXEC')
        self.poll = Vote_Poll.objects.create(Vote_Poll_Name='Budget', created_by=self.exec)

    def vote(self, user, choice):
        self.login(user)
        return self.client.post(reverse('poll'), {choice: '1'})

    def test_exec_starts_a_poll(self):
        self.login(self.exec)
        response = self.client.post(reverse('start_vote'), {'Vote_Poll_Name': 'Formal date'})
        self.assertRedirects(response, reverse('poll'), fetch_redirect_response=False)
        poll = Vote_Poll.objects.get(Vote_Poll_Name='Formal date')
        self.assertEqual(poll.created_by, self.exec)
        self.assertIsNone(poll.Vote_Poll_End)

    def test_poll_page_shows_current_poll(self):
        self.login(self.active)
        self.assertEqual(self.client.get(reverse('poll')).context['current_poll'], self.poll)

    def test_casting_and_changing_a_vote(self):
        response = self.vote(self.active, 'aye')
        self.assertEqual(response.context['aye_votes'], 1)
        response = self.vote(self.active, 'nay')
        self.assertEqual((response.context['aye_votes'], response.context['nay_votes']), (0, 1))
        self.assertEqual(Brother_votes.objects.filter(user=self.active).count(), 1)

    def test_live_results_endpoint(self):
        self.vote(self.active, 'aye')
        self.vote(self.exec, 'nay')
        self.assertEqual(self.client.get(reverse('poll_results')).json(), {'aye_votes': 1, 'nay_votes': 1})

    def test_exec_ends_vote_and_counts_are_saved(self):
        self.vote(self.active, 'aye')
        self.vote(self.exec, 'aye')
        self.client.post(reverse('poll'), {'end_vote': '1'})
        self.poll.refresh_from_db()
        self.assertIsNotNone(self.poll.Vote_Poll_End)
        self.assertEqual((self.poll.Vote_Poll_Count_Yes, self.poll.Vote_Poll_Count_No), (2, 0))
        # everyone's vote is reset for the next poll
        self.assertFalse(Brother_votes.objects.exclude(user_vote_choice='No Vote').exists())

    def test_non_exec_cannot_end_vote(self):
        self.vote(self.active, 'aye')
        response = self.client.post(reverse('poll'), {'end_vote': '1'})
        self.poll.refresh_from_db()
        self.assertIsNone(self.poll.Vote_Poll_End)
        self.assertIn('You need to be an EXEC member to end votes.', self.messages_for(response))
        self.assertEqual(Brother_votes.objects.get(user=self.active).user_vote_choice, 'Aye')

    def test_past_polls_lists_finished_polls_newest_first(self):
        now = timezone.now()
        Vote_Poll.objects.create(Vote_Poll_Name='Older', created_by=self.exec, Vote_Poll_End=now - timedelta(days=2))
        Vote_Poll.objects.create(Vote_Poll_Name='Newer', created_by=self.exec, Vote_Poll_End=now - timedelta(days=1))
        self.login(self.active)
        names = [p.Vote_Poll_Name for p in self.client.get(reverse('past_polls')).context['past_polls']]
        self.assertEqual(names, ['Newer', 'Older'])
