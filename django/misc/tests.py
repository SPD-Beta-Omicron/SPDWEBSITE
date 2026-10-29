from datetime import datetime
from unittest.mock import patch

import pytz

from core.testing import SPDTestCase
from .models import DayLightSavingsAlert
from .templatetags.dls_tags import dls_alert
from .utils import get_next_dst_change

CHICAGO = pytz.timezone('America/Chicago')


def frozen_now(year, month, day):
    """A stand-in for datetime whose now() always returns the given day in Chicago."""
    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return CHICAGO.localize(datetime(year, month, day, 12, 0))
    return patch('misc.utils.datetime', FrozenDatetime)


class DaylightSavingTests(SPDTestCase):

    def assertChange(self, today, expected):
        with frozen_now(*today):
            change = get_next_dst_change()
        self.assertEqual((change.year, change.month, change.day), expected)

    def test_winter_points_to_spring_forward(self):
        # 2nd Sunday in March 2027
        self.assertChange((2027, 1, 10), (2027, 3, 14))

    def test_summer_points_to_fall_back(self):
        # 1st Sunday in November 2027
        self.assertChange((2027, 6, 1), (2027, 11, 7))

    def test_december_rolls_over_to_next_year(self):
        self.assertChange((2027, 12, 1), (2028, 3, 12))

    def test_change_happens_at_2am(self):
        with frozen_now(2027, 1, 10):
            self.assertEqual(get_next_dst_change().hour, 2)


class DaylightSavingAlertTagTests(SPDTestCase):

    def test_default_message(self):
        with frozen_now(2027, 1, 10):
            result = dls_alert()
        self.assertTrue(result['show_alert'])
        self.assertIn('March 14, 2027', result['message'])
        self.assertIn('forward', result['message'])

    def test_fall_message_says_back(self):
        with frozen_now(2027, 6, 1):
            self.assertIn('back', dls_alert()['message'])

    def test_admin_can_hide_alert(self):
        DayLightSavingsAlert.objects.create(is_active=False)
        self.assertFalse(dls_alert()['show_alert'])

    def test_admin_can_override_message(self):
        DayLightSavingsAlert.objects.create(is_active=True, name='Line one\nLine two')
        self.assertEqual(dls_alert()['message'], 'Line one<br>Line two')
