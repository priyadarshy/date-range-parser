# -*- coding: utf-8 -*-
"""date_range_parser.py

@author: ashutosh@hq.siftnet.com
@date: July 22, 2014

This file describes classes that have general purpose regular expressions and string extraction
methods that we can use to parse out the various pieces of our sequential date parsing grammar.

"""

import pytz
import utils
import grammar
import datetime
import extraction
import preprocessing
import metadata


def dt_tup_to_js_json_format(tup):
    js_format = lambda tup: {u'startDate': dt_to_js_json_format(tup[0]), u'endDate': dt_to_js_json_format(tup[1])}
    if isinstance(tup, tuple):
        splits = utils.split_by_days(tup[0], tup[1])
        return [js_format(s) for s in splits]

def dt_to_js_json_format(dt):
    if isinstance(dt, datetime.datetime):
        dt = dt.replace(second=0, microsecond=0)
        return dt.isoformat()
    else:
        return None

def parse(text, src_time=None, tz_name=None, parse_type=u'range', limit=1):
    if not src_time:
        try:
            user_tz = pytz.timezone(tz_name)
            src_time = user_tz.normalize(datetime.datetime.now(pytz.utc).astimezone(user_tz))
        except pytz.exceptions.UnknownTimeZoneError:
            # Should probably return a flag to the user that it was parsed with UTC defaults.
            src_time = datetime.datetime.utcnow()
    # src_time should represent today and nothing else.
    src_time = src_time.replace(hour=0, minute=0, second=0, microsecond=0)
    # Sanitize the string and apply spelling correction.
    text = preprocessing.preprocess_input(text)

    # Search through the text for Atoms.
    tagger = extraction.DateGrammarAtomTagger(src_time, parse_type=parse_type);
    # Convert the atoms to tags.
    extractions = tagger.tag(text)
    #print "------ extractions ------"
    #print [e.to_tag() for e in extractions]
    #print "-------------------------\n"

    # Choose the correct grammar type we want to parse for.
    if parse_type == u'range':
        grammar_parser = grammar.range_grammar_regex_parser
    elif parse_type == u'exact':
        grammar_parser = grammar.exact_grammar_regex_parser
    else:
        return dict(result=[], parse=None)

    # Run it through the NLTK tagger with our specified grammar.
    parse_tree = grammar_parser.parse([e.to_tag() for e in extractions])
    # Traverse the tree and compute the result.
    parse = grammar.traverse(parse_tree)
    # Append the plain text interpretation for each parse.
    for p in parse:
        p[u'display_text'] = metadata.display_text(p)
        p[u'reconvertible_text'] = metadata.reconvertible_text(p)

    if len(parse) > 0:
        first_markup = parse[0].get(u'markup')
        if first_markup:
            # Return it in the format the client expects.
            result = [item for mu in first_markup for item in dt_tup_to_js_json_format(mu)]
            return dict(result=result, parse=parse)
    return dict(result=[], parse=None)


def to_json(results):
    return utils.DateRangeParserEncoder().encode(results)
