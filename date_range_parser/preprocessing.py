# -*- coding: utf-8 -*-
"""preprocessing.py

@author: ashutosh@hq.siftnet.com
@date: August 2, 2014

Basic string preprocessing to improve the accuracy of the date_range_parser.

Applies spelling correction, lowercases the string and maps numeric words into
numbers like one --> '1'.
"""

from textblob import TextBlob
import re

def sanitize_string(nltext):
    if isinstance(nltext, basestring):
        return nltext.lower()
    else:
        return u""

def correct_spelling(nltext):
    return nltext
    #blob = TextBlob(nltext)
    #return blob.correct().string

def remove_stop_words(nltext):
    stop_words_exp = r'(in\sthe|\bat\b)'
    stop_words_regex = re.compile(stop_words_exp, flags=re.X|re.I)
    return stop_words_regex.sub(u'', nltext)

def replace_ordinals(nltext):
    def match_function(matchobj):
        return re.sub(r'th|st|nd|rd', '', matchobj.group(), count=1, flags=re.X|re.I)
    # Replace occurences of ordinals next to numbers.
    return re.sub(r'\b\d{1,2}(?P<ordinal>th|st|nd|rd)\b', match_function, nltext, flags=re.X|re.I)

def replace_words(nltext):
    # Match function sent into re.sub
    def match_function(matchobj):
        """ Match function used to substitute based on group type."""
        replacement_map = { u'one': u'1',
                            u'two': u'2',
                            u'couple': u'2',
                            u'three': u'3',
                            u'four': u'4',
                            u'five': u'5',
                            u'six': u'6',
                            u'seven': u'7',
                            u'eight': u'8',
                            u'nine': u'9',
                            u'ten': u'10',
                            u'noon': u'12 pm'}
        return replacement_map.get(matchobj.lastgroup)

    # Replace numeric words with corresponding number string.
    replacements = r'''
                (?P<one>\bone\b)|
                (?P<two>\btwo\b)|
                (?P<couple>\bcouple\b)|
                (?P<three>\bthree\b)|
                (?P<four>\bfour\b)|
                (?P<five>\bfive\b)|
                (?P<six>\bsix\b)|
                (?P<seven>\\bseven\b)|
                (?P<eight>\beight\b)|
                (?P<nine>\bnine\b)|
                (?P<ten>\bten\b)|
                (?P<noon>\bnoon\b)
                '''
    replacement_regex = re.compile(replacements, flags=re.X|re.I)
    return replacement_regex.sub(match_function, nltext)

def preprocess_input(nltext):
    return remove_stop_words(correct_spelling(replace_ordinals(replace_words(sanitize_string(nltext)))))

