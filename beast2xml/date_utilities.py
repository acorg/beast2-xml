from datetime import timedelta, datetime
from datetime import datetime as dt
import calendar
import time


def decimal_to_date(decimal):
    ''' Convert year decimal to date.'''
    year = int(decimal)
    d = timedelta(days=(decimal - year)*(365 + calendar.isleap(year)))
    day_one = datetime(year,1,1)
    date = d + day_one
    return date

def date_to_decimal(date):
    """ Convert date to year decimal (year fraction).

    Parameters
    ----------
    date : str
        Date to be converted.

    Returns
    -------
    date_as_year_decimal : float
    """
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction

