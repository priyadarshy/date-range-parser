# -*- coding: utf-8 -*-
"""utils.py

@author: ashutosh@hq.siftnet.com
@date: August 1, 2014

This files contains utilities that are use for the date range parser.

"""


import datetime
import parsedatetime
from natural_date_range import natural_daterange_parser
from dateutil import rrule
import pytz
from json import JSONEncoder

class DateRangeParserEncoder(JSONEncoder):
    """ Custom encoder to encode results from the DateRangeParser."""
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return {u'timedelta':{u'total_seconds':o.total_seconds()}}
        else:
            try:
                return o.to_json()
            except AttributeError:
                try:
                    return o.__dict__
                except AttributeError:
                    return None

def safe_natural_daterange_parser(text, src_time):
    result = natural_daterange_parser(text, src_time)
    if result:
        return {u'start': result[1][0], u'end': result[1][1], u'match': result[0], u'label':u'success'}
    else:
        return {u'start': None, u'end': None, u'match': None, u'label':u'fail'}

def safe_parsedatetime_first_nlp(text, src_time, ignore=None):
    """ SafeParseDatetime is a simple wrapper on the functionality that we need from
    parsedatetime.Calendar().nlp(). It handles parsing and checking all the flags so we don't
    have to clutter client code with the mechanics of dealing with the parse results."""
    calendar = parsedatetime.Calendar()
    # Constants for unpacking NLP match tuples.
    NLP_MTC_DT =  0
    NLP_MTC_FLG = 1
    NLP_MTC_BEG = 2
    NLP_MTC_END = 3
    NLP_MTC_MTC = 4
    # Parsedatetime flags for parse type.
    PARSE_TYPE_FAIL = 0
    PARSE_TYPE_DATE = 1
    PARSE_TYPE_TIME = 2
    PARSE_TYPE_DTTM = 3
    parse_names = [u'fail', u'date', u'time', u'datetime']
    parse = calendar.nlp(text, sourceTime=src_time)
    unacceptable_parses = [PARSE_TYPE_FAIL] if not ignore else [PARSE_TYPE_FAIL, PARSE_TYPE_TIME]
    if parse:
        try:
            first_match = parse[0]
            # Only support dates for now
            if first_match[NLP_MTC_FLG] not in unacceptable_parses:
                return {u'datetime': localize_to(src_time, first_match[NLP_MTC_DT]),
                        u'match': first_match[NLP_MTC_MTC],
                        u'label': parse_names[first_match[NLP_MTC_FLG]]}
        except IndexError:
            pass
    # Always return this if we don't exit in the optimal condition above.
    return {u'datetime': None, u'match':None, u'label': u'fail'}

def localize_to(src_time, dt):
    user_tz = pytz.timezone(src_time.tzinfo.zone)
    return user_tz.localize(dt)

def simple_datestring(dt=None, tup=None):
    """
    Convert a datetime to a simple date string representation like
    Friday July, 17 2014
    """
    if dt:
        isdatetime = isinstance(dt, datetime.datetime)
        return dt.strftime("%A %B %d, %Y %I:%M %p") if isdatetime else u""
    elif isinstance(tup, tuple):
        return (simple_datestring(tup[0]), simple_datestring(tup[1]))
    else:
        return u""

def start_of_day(dt):
    """ Returns the corresponding start of a given day."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def end_of_day(dt):
    """ Returns the corresponding end of a given day. """
    end_of_day = dt + datetime.timedelta(days=1)
    return end_of_day.replace(hour=0, minute=0, second=0, microsecond=0)

def end_of_month(dt):
    """Returns the corresponding end of month."""
    month_bump = dt.month + 1 if dt.month < 12 else 1
    return dt.replace(month=month_bump, day=1,hour=0, minute=0, microsecond=0)

def split_by_days(start, end):
    """ Takes a start and end datetime and splits it into a list of days in between."""
    if (end-start).total_seconds() >= 60*60*24:
        splits = list(rrule.rrule(rrule.DAILY, count=((end - start_of_day(start)).days),
                                    dtstart=start,
                                    until=end))
        return [(s, end_of_day(s)) for s in splits[0:1]] + [(start_of_day(s), end_of_day(s)) for s in splits[1:]]
    else:
        return [(start, end)]

class SequentialMatcher(object):
    """ SequentialMatcher applies a string matching function on an input string and returns
    an ordered list of matches and non-matches where each match as determined by the match_function
    is transformed using the function match_transformed before being placed in the result list.

    The final result looks something like this:
        >>> input_string = u'Some text some_matcheable_text more text other_matcheable_text'
        >>> chunks
        # If match_transformer is provided.
        ['Some text ', match_transformer('some_matchable_text'), 'more text ', match_transformer('other_matcheable_text')]
        # Otherwise the default behaviour is a tuple (match_text, label).
        ['Some text ', ('some_matchable_text', label), 'more text ', ('other_matcheable_text', label)]

    Attributes:
        match_function (function): A python function that returns unaltered matched text.
        match_transformer (function): A python function that takes a single parameter `match_string` which
        is none other than the result of a match_function. The `match_string` is passed into the transformer
        before being inserted into the resultant list.
        label (function): If no match_transformer function is provided the default transformation will be to
        use a tuple (match, label) as the inserted result.
    """

    def __init__(self, match_function, match_transformer=None, label=None):
        self.match_function = match_function  # Should return (match or None)
        if match_transformer:
            self.match_transformer = match_transformer # f (match_str) --> anyobject you want
        elif label:
            self.match_transformer = lambda match_text: (match_text, label)
        else:
            raise ValueError(u'SequentialMatcher requires either a match_transformer function or a label.')

    def __is_leftovers(self, text):
        return text.isspace() or len(text) <= 0

    def extract(self, text):
        """ Generic function for splitting a text string into an array of
        [(match|non-match) ...(match) ... (match|non-match)] items.
        """
        # Segments of a partitioned tuple.
        NON_MATCH = 0
        MATCHED = 1
        REMAINDER = 2
        # Sequentially search the string for matches.
        remainder = text   # Start with entire input as what's left to be matched.
        another_match = self.match_function(remainder)  # next_match is the next result from search.

        chunks = []
        while another_match:
            # Partition the string on the match.
            parts = remainder.partition(another_match)
            # Chunk and append the part before the first match (def not a match).
            if not parts[NON_MATCH].isspace() and not len(parts[NON_MATCH]) == 0:
                non_match = chunks.append(parts[NON_MATCH])
            # Transform the match into a result using the transform function.
            result = self.match_transformer(another_match)
            matched = chunks.append(result)
            # Search the remainder for further matches.
            remainder = parts[REMAINDER]
            if not remainder.isspace() and not len(remainder) == 0:
                another_match = self.match_function(remainder)
            else:
                another_match = None
        # When no more matches, append the remainder to chunks.
        chunks.append(remainder)
        return chunks
