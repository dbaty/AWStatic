from unittest import TestCase


class TestIsLeapYear(TestCase):

    def _call_fut(self, year):
        from awstatic.utils import is_leap_year
        return is_leap_year(year)

    def test_basics(self):
        self.assertTrue(self._call_fut(2012))
        self.assertFalse(self._call_fut(2011))
        self.assertTrue(self._call_fut(1600))
        self.assertFalse(self._call_fut(1700))


class TestNumberOfDays(TestCase):

    def _call_fut(self, yyyymm):
        from awstatic.utils import get_number_of_days
        return get_number_of_days(yyyymm)

    def test_basics(self):
        self.assertEqual(self._call_fut('201101'), 31)
        self.assertEqual(self._call_fut('201102'), 28)
        self.assertEqual(self._call_fut('201202'), 29)
        self.assertEqual(self._call_fut('201204'), 30)
        self.assertEqual(self._call_fut('201212'), 31)


class TestInterpolate(TestCase):

    def _call_fut(self, s, **bindings):
        from awstatic.utils import interpolate
        return interpolate(s, **bindings)

    def test_basics(self):
        self.assertEqual(self._call_fut('foo'), 'foo')
        self.assertEqual(self._call_fut('foo', foo='1'), 'foo')
        self.assertEqual(self._call_fut('${foo}'), '${foo}')
        self.assertEqual(self._call_fut('${foo}', bar='1'), '${foo}')
        self.assertEqual(self._call_fut('Value is: ${foo}', foo='1'),
                         'Value is: 1')
