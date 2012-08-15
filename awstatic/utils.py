import re


_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
_INTERPOLATION = re.compile('\${(\w*)}')


def is_leap_year(year):
    """Return whether the given year is a leap year."""
    if year % 4:
        return False
    if year % 400 == 0:
        return True
    return year % 100 != 0


def get_number_of_days(yyyymm):
    """Return number of days of the given month."""
    month, year = map(int, (yyyymm[-2:], yyyymm[:-2]))
    n = _DAYS_IN_MONTH[month - 1]
    if month == 2 and is_leap_year(year):
        n += 1
    return n


def interpolate(s, **bindings):
    """Substitute ``${var}`` fragments in ``s`` by their value
    provided in ``bindings``.
    """
    if not bindings:
        return s
    def _sub(matchobj):
        var = matchobj.group(1)
        return bindings.get(var, matchobj.group(0))
    return _INTERPOLATION.sub(_sub, s)
