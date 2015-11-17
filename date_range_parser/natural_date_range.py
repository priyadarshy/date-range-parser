# -*- coding: utf-8 -*-
"""natural_date_range.py

@author: ashutosh@hq.siftnet.com
@date: August 1, 2014

Natural date range takes in a plain text string and looks for tokens like
(this|next) (weekend|week|month) and returns corresponding date ranges.
"""
import datetime
import re
from collections import namedtuple

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import MO as MONDAY, SA as SATURDAY
import utils
import pytz

def natural_daterange_parser(nltext, src_time, first=True):
    isolated_datestrings = __isolate_datestrings(nltext)
    results = [(iso, parse_date_range(iso, src_time)) for iso in isolated_datestrings]
    if len(results) > 0 and first:
        return results[0]
    else:
        return results

def __isolate_datestrings(text):
    # Compose strings to put together a more complicated regular expression.
    natural_range = r'''
                    (?P<pos_mod>\b(this|next|\d+)\b)?\s*
                    (?P<range_type>\b(weekend|month|week)s?)\b
                    '''

    natural_range_exp = re.compile(natural_range, flags=re.X|re.I)
    # Match and the return a cleaned up version of each match.
    substr_match = [text[m.start():m.end()] for m in natural_range_exp.finditer(text) if m]
    return substr_match if substr_match else []

__HandleableRange = namedtuple('HandleableRange', ['starts', 'lasts', 'handle_next'])
"""
Representation of a time range.
starts - datetime.datetime: starting moment of the range
lasts - datetime.timedelta: length of the range
handle_next - function, returns datetime.timedelta. Determines how far the
range has to be moved in the future when 'next' modifier is present.
"""


def parse_date_range(nltext, src_time):
    """
    Takes a natural language representation of time range and returns datetime
    representation of time boundaries of this range. Returns None, if valid
    time range cannot be retrieved from the input.
    """
    hrange = __analyze_range(nltext, src_time)
    src_time = utils.start_of_day(src_time)

    if hrange:
        end_date = hrange.starts + hrange.lasts
        if end_date <= src_time:
            start_date = hrange.starts + datetime.timedelta(days=7)
            hrange = __HandleableRange(start_date, hrange.lasts, hrange.handle_next)
            end_date = hrange.starts + hrange.lasts

        # See if a positional modifier is present.
        pos_mod = re.search(r'\b(next|\d+)\b', nltext, flags=re.X|re.I)
        pos_match = re.search(r'\b\d+\b', nltext, flags=re.X|re.I)
        pos_count = int(pos_match.group()) if pos_match else 1
        if not pos_mod:
            start_date = hrange.starts if hrange.starts > src_time else src_time
            return (start_date, end_date)
        else:
            start_date = hrange.starts
            d = hrange.handle_next()
            d = d * pos_count
            start_date += d
            end_date += d
            start_date = start_date if start_date > src_time else src_time
            return (start_date, end_date)
    else:
        return None


def __get_weekday_datetime(weekday, src_time):
    """
    Gets weekday instance of weekday (dateutil.relativedelta.*) and returns
    datetime for 00:00 of the weekday in the current week.
    """
    today = datetime.datetime(year=src_time.year, month=src_time.month, day=src_time.day, tzinfo=src_time.tzinfo)
    if weekday.weekday < src_time.weekday():
        today = today + relativedelta(weekday=weekday(-1))
    else:
        today = today + relativedelta(weekday=weekday)
    return today

def __analyze_range(nltext, src_time):
    """
    Takes a natural language representation of time range and maps it to
    proper Range object. Returns None, if valid time range cannot be retrieved
    from the input.
    """
    # Construct the current reference time from the source time.
    if isinstance(src_time, datetime.datetime):
        src_time = utils.start_of_day(src_time)
    else:
        raise ValueError(u'Invalid `src_time`. Must be of time datetime.datetime')

    # Construct regex to find various range types.
    range_expr = r'''
                (?P<weekend>weekend)|
                (?P<week>week)|
                (?P<month>month)s?'''
    range_regex = re.compile(range_expr, flags=re.I|re.X)
    range_match = range_regex.search(nltext)

    # Return a __HandleableRange based on the match group type.
    if range_match:
        if range_match.group('weekend'):
            return __HandleableRange(
                __get_weekday_datetime(SATURDAY, src_time),
                datetime.timedelta(days=2),
                lambda: datetime.timedelta(days=7)
            )
        elif range_match.group('week'):
            return __HandleableRange(
                __get_weekday_datetime(MONDAY, src_time),
                datetime.timedelta(days=5),
                lambda: datetime.timedelta(days=7)
            )
        elif range_match.group('month'):
            return __HandleableRange(
                src_time.replace(day=1),
                relativedelta(months=1),
                lambda: relativedelta(months=1)
            )
    else:
        return None
