# -*- coding: utf-8 -*-
"""atoms.py

@author: ashutosh@hq.siftnet.com
@date: August 1, 2014

Atoms are the most basic units that can be recognized and parsed by the date_range_parser.
"""

import re
import datetime
import utils
import operator
from dateutil import rrule
from utils import SequentialMatcher

#
# Modifiers
#

class ModifierAtom(object):

    def to_json(self):
       raise NotImplementedError


class RelativeOneWayMultiDayModifierAtom(ModifierAtom):

    EXTRACTION_EXP = r'''
                    (?P<after>\bafter\b)|
                    (?P<before>\b(before|prior|no\slater)\b)'''
    EXTRACTION_REGEX = re.compile(EXTRACTION_EXP, flags=re.X|re.I)

    TAG = u'MOD'

    def __init__(self, match, src_time, direction=None):
        if match and direction:
            self.match = match
            self.direction = direction
            self.src_time
        elif match:
            self.__from_match(match, src_time)
        else:
            raise ValueError(u'Insufficient Parameters. Must specify `match` or `match` and `direction`')

    def __from_match(self, match, src_time):
        self.match = match
        self.direction = self.__find_direction(match)
        self.src_time = src_time

    def __find_direction(self, match):
        direction = RelativeOneWayMultiDayModifierAtom.__match_function(match).get(u'direction') 
        if direction != 0:
            return direction
        else:
            raise ValueError(u'RelativeOneWayMultiDayModifierAtom requires unambiguous directionality.')

    @staticmethod
    def __match_function(nltext):
        dir_match = RelativeOneWayMultiDayModifierAtom.EXTRACTION_REGEX.search(nltext)
        if dir_match:
            futr = 1 if dir_match.groupdict().get(u'after') else 0
            past = -1 if dir_match.groupdict().get(u'before') else 0
            direction = futr + past
            if direction != 0:
                return {u'direction': direction, u'match':dir_match.group()}
            else:
                return None

    @staticmethod
    def extract_atom(text, src_time, **kwargs_ignore):
        # Wrap function to pass through params.
        def wrapped_match_function(nltext):
            match_res = RelativeOneWayMultiDayModifierAtom.__match_function(nltext)
            return match_res.get(u'match') if match_res else None
        def wrapped_match_transformer(match):
            return RelativeOneWayMultiDayModifierAtom(match, src_time)

        matcher = SequentialMatcher(wrapped_match_function,\
                match_transformer=wrapped_match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, src_time):
        # Wrap function to pass through params.
        def wrapped_match_function(nltext):
            match_res = RelativeOneWayMultiDayModifierAtom.__match_function(nltext)
            return match_res.get(u'match') if match_res else None

        matcher = SequentialMatcher(wrapped_match_function,\
                label=RelativeOneWayMultiDayModifierAtom.TAG)
        return matcher.extract(text)

    def to_json(self):
        return dict(match=self.match, direction=self.direction, src_time=self.src_time, tag=self.tag_name())

    def to_tag(self):
        return (self.match, self.TAG, self)

    def tag_name(self):
        return u'MOD_RELONEWAYMULTIDAY'

    def reconvertible_text(self):
        if self.direction == -1:
            return u'before'
        elif self.direction == 1:
            return u'after'

    def display_text(self):
        return self.reconvertible_text()

    def modify(self, daterange):
        if isinstance(daterange, DaterangeAtom):
            by_days = daterange.split(u'days')
            if self.direction == -1: # before
                return utils.split_by_days(self.src_time, by_days[0][0])
            elif self.direction == 1: # after
                return utils.split_by_days(by_days[-1][-1], by_days[-1][-1] + datetime.timedelta(days=14))
            else:
                return None
        else:
            raise ValueError(u'daterange must be a subclass of DaterangeAtom')


class ReferencePointModifierAtom(ModifierAtom):

    EXTRACTION_EXP = r'''
                    ((?P<bound_type>\bat\b)\s*)?
                    (?P<hours>(?<![/])[1-9]\d?(?![./]\d{1,2}))
                    (:(?P<mins>\d{1,2}))?
                    (\s*(?P<meridian>(a|p)\.?m\.?))?
                    '''
    # TODO Made meridien not optional.
    EXTRACTION_REGEX = re.compile(EXTRACTION_EXP, flags=re.X|re.I)
    TAG = u'REF'

    def __init__(self, match, src_time, modification=None):
        if all([match, src_time, modification]):
            self.match = match
            self.src_time = src_time
            self.modification = modification
        elif match and src_time:
            self.__from_match(match, src_time)
        else:
            raise ValueError(u'Insufficient Parameters. You must specify both a `match` and `src_time` or all 4 parameters')

    def __from_match(self, match, src_time):
        """ Initialize the instance given a plaintext match string."""
        # It's possible to match but not be parseable because our regex allows values with no meridian.
        # parsedatetime needs this however so we just append PM unless we know otherwise.
        append_meridien_match = self.EXTRACTION_REGEX.search(match) 
        if append_meridien_match:
            if not append_meridien_match.groupdict().get(u'meridian'):
                match = match + " PM"
            seed_dt = utils.safe_parsedatetime_first_nlp(match, src_time).get(u'datetime')
            if seed_dt:
                self.match = match
                self.modification = seed_dt
        else:
            raise ValueError(u'ReferencePointModifierAtom cannot parse and intialized from given match value = '\
                    + unicode(match))

    @staticmethod
    def __match_function(nltext, src_time):
        match = ReferencePointModifierAtom.EXTRACTION_REGEX.search(nltext)
        return match.group() if match else None

    @staticmethod
    def __match_transformer(match, src_time):
        return ReferencePointModifierAtom(match, src_time)

    @staticmethod
    def extract_atom(text, src_time, **kwargs_ignore):
        # Wrap static methods for match function and match transform to close over src_time.
        def wrapped_match_function(nltext): return ReferencePointModifierAtom.__match_function(nltext, src_time)
        def wrapped_match_transformer(match): return ReferencePointModifierAtom.__match_transformer(match, src_time)
        matcher = SequentialMatcher(wrapped_match_function,\
                match_transformer=wrapped_match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, src_time):
        # Wrap static methods for match function and match transform to close over src_time.
        def wrapped_match_function(nltext): return ReferencePointModifierAtom.__match_function(nltext, src_time)
        def wrapped_match_transformer(match): return ReferencePointModifierAtom.__match_transformer(match, src_time)
        matcher = SequentialMatcher(wrapped_match_function, label=ReferencePointModifierAtom.TAG)
        return matcher.extract(text)

    def to_json(self):
        return dict(match=self.match, src_time=self.src_time, modification=self.modification, tag=self.tag_name())

    def to_tag(self):
        return (self.match, self.TAG, self)

    def tag_name(self):
        return u'MOD_REFPOINT'

    def reconvertible_text(self):
        start_text = (utils.start_of_day(datetime.datetime.utcnow()) + self.modification).strftime(u'%I:%M %p')
        return u'at {start_text}'.format(start_text=start_text)

    def display_text(self):
        return self.reconvertible_text()

    def modify(self, daterange):
        if isinstance(daterange, DaterangeAtom):
            return [(self.modification, self.modification)]
        else:
            raise ValueError(u'daterange must be a subclass of DaterangeAtom')


class AbsoluteOneWayInnerDayModifierAtom(ModifierAtom):

    EXTRACTION_EXP = r'''
                    (?P<bound_type>before|after)\s*
                    (?P<hours>[1-9]\d?(?![./]\d{1,2}))
                    (:(?P<mins>\d{1,2}))?
                    (\s*(?P<meridian>(a|p)\.?m\.?))?
                    '''
    # TODO Made meridien not optional.
    EXTRACTION_REGEX = re.compile(EXTRACTION_EXP, flags=re.X|re.I)
    TAG = u'MOD'

    def __init__(self, match, src_time, modification=None):
        if all([match, src_time, modification]):
            self.match = match
            self.src_time = src_time
            self.modification = modification
        elif match and src_time:
            self.__from_match(match, src_time)
        else:
            raise ValueError(u'Insufficient Parameters. You must specify both a `match` and `src_time` or all 4 parameters')


    def __find_direction(self, match):
        futr_exp = re.compile(r'''after|later''', flags=re.X|re.I)
        past_exp = re.compile(r'''before|prior''', flags=re.X|re.I)
        futr = 1 if re.search(futr_exp, match) else 0
        past = -1 if re.search(past_exp, match) else 0
        # In case we get both just return 0 i.e. we know nothing.
        direction = futr + past
        if direction != 0:
            return direction
        else:
            raise ValueError(u'AbsoluteOneWayInnerDayModifierAtom range requires unambiguous directionality.')


    def __from_match(self, match, src_time):
        """ Initialize the instance given a plaintext match string."""
        # It's possible to match but not be parseable because our regex allows values with no meridian.
        # parsedatetime needs this however so we just append PM unless we know otherwise.
        append_meridien_match = self.EXTRACTION_REGEX.search(match) 
        if append_meridien_match:
            if not append_meridien_match.groupdict().get(u'meridian'):
                match = match + " PM"
            seed_dt = utils.safe_parsedatetime_first_nlp(match, src_time).get(u'datetime')
            if seed_dt:
                direction = self.__find_direction(match)
                self.match = match
                if direction == 1:
                    self.direction = 1
                    self.modification = seed_dt - utils.start_of_day(seed_dt)
                elif direction == -1:
                    self.direction = -1
                    self.modification = seed_dt - utils.start_of_day(seed_dt)
        else:
            raise ValueError(u'AbsoluteOneWayInnerDayModifierAtom cannot parse and intialized from given match value = '\
                    + unicode(match))

    @staticmethod
    def __match_function(nltext, src_time):
        match = AbsoluteOneWayInnerDayModifierAtom.EXTRACTION_REGEX.search(nltext)
        return match.group() if match else None

    @staticmethod
    def __match_transformer(match, src_time):
        return AbsoluteOneWayInnerDayModifierAtom(match, src_time)

    @staticmethod
    def extract_atom(text, src_time, **kwargs_ignore):
        # Wrap static methods for match function and match transform to close over src_time.
        def wrapped_match_function(nltext): return AbsoluteOneWayInnerDayModifierAtom.__match_function(nltext, src_time)
        def wrapped_match_transformer(match): return AbsoluteOneWayInnerDayModifierAtom.__match_transformer(match, src_time)
        matcher = SequentialMatcher(wrapped_match_function,\
                match_transformer=wrapped_match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, src_time):
        # Wrap static methods for match function and match transform to close over src_time.
        def wrapped_match_function(nltext): return AbsoluteOneWayInnerDayModifierAtom.__match_function(nltext, src_time)
        def wrapped_match_transformer(match): return AbsoluteOneWayInnerDayModifierAtom.__match_transformer(match, src_time)
        matcher = SequentialMatcher(wrapped_match_function, label=AbsoluteOneWayInnerDayModifierAtom.TAG)
        return matcher.extract(text)

    def to_json(self):
        return dict(match=self.match, src_time=self.src_time, modification=self.modification, tag=self.tag_name())

    def to_tag(self):
        return (self.match, self.TAG, self)

    def tag_name(self):
        return u'MOD_ABSONEWAYINNERDAY'

    def reconvertible_text(self):
        if self.direction == -1:
            start_text = (utils.start_of_day(datetime.datetime.utcnow()) + self.modification).strftime(u'%I:%M %p')
            return u'before {start_text}'.format(start_text=start_text)
        elif self.direction == 1:
            end_text = (utils.start_of_day(datetime.datetime.utcnow()) + self.modification).strftime(u'%I:%M %p')
            return u'after {end_text}'.format(end_text=end_text)

    def display_text(self):
        return self.reconvertible_text()

    def modify(self, daterange):
        if isinstance(daterange, DaterangeAtom):
            by_days = daterange.split(u'days')
            if self.direction == 1:
                return [(day[0] + self.modification, utils.end_of_day(day[0])) for day in by_days]
            elif self.direction == -1:
                return [(day[0], day[0]+self.modification) for day in by_days]
        else:
            raise ValueError(u'daterange must be a subclass of DaterangeAtom')




class AbsoluteInnerDayModifierAtom(ModifierAtom):

    # Be sure to escape '{-type' quantifiers since we're using .format() to construct match groups.
    # Look for a time like 5, 13:00, 5:30 etc.
    _time_subex = '(?P<{hour_grp}>(\s|^)\d{{1,2}})(?!\.|/\s)((:(?P<{min_grp}>\d{{1,2}}))?|\w)'
    # Find the AM/PM designation.
    _mer_subex = '(?P<{mer_grp}>(a|p)\.?m\.?)?'
    # Find separation terms.
    _div_subex = '(to|and|\-|thru|through)'    # Format sub-expressions to contain named matched groups.
    _time_exp_0 = _time_subex.format(**{'hour_grp':'t0hr', 'min_grp':'t0min'})
    _time_exp_f = _time_subex.format(**{'hour_grp':'tfhr', 'min_grp':'tfmin'})
    _mer_exp_0 = _mer_subex.format(**{'mer_grp':'t0mer'})
    _mer_exp_f = _mer_subex.format(**{'mer_grp':'tfmer'})
    # Construct the full expression with sub-expressions as format strings.
    EXTRACTION_EXP = r'''
                        (?=[^./])
                        {time_exp_0}
                        \s*
                        {mer_exp_0}
                        \s*{div_subex}\s*
                        (?=[^./])
                        {time_exp_f}
                        \s*
                        {mer_exp_f}
                        '''.format(time_exp_0=_time_exp_0, time_exp_f=_time_exp_f,
                            mer_exp_0=_mer_exp_0, mer_exp_f=_mer_exp_f, div_subex=_div_subex)
    # Construct the actual extraction regular expression object.
    EXTRACTION_REGEX = re.compile(EXTRACTION_EXP, flags=re.X|re.I|re.M)
    # Define the tag name.
    TAG = u'MOD'

    def __init__(self, match, modification=None):
        if match and modification:
            self.match = match
            self.modification = modification
        elif match:
            self.__from_match(match)
        else:
            raise ValueError(u'Insufficient Parameters. Need to specify `match` or `match` and `modification`')

    def __from_match(self, match):
        tod_match = AbsoluteInnerDayModifierAtom.EXTRACTION_REGEX.search(match)
        if tod_match.groupdict()[u't0hr'] and tod_match.groupdict()[u'tfhr']:
        #if tod_match:
            match_text = tod_match.group()
            tod_match = tod_match.groupdict()
            t0mer = self.__am_pm_normalize(tod_match.get(u't0mer'))
            tfmer = self.__am_pm_normalize(tod_match.get(u'tfmer'))

            # Extract all the various subcomponets as integers.
            t0hr = int(tod_match.get(u't0hr', 0) or 0)
            tfhr = int(tod_match.get(u'tfhr', 0) or 0)
            t0min = int(tod_match.get(u't0min', 0) or 0)
            tfmin = int(tod_match.get(u'tfmin', 0) or 0)

            if not any([t0mer, tfmer]):
                if t0hr < 12:
                    t0mer = u'AM'
                if t0hr < 12 and tfhr < 12:
                    if tfhr <= t0hr:
                        t0mer, tfmer = (u'AM', u'PM')
                    else:
                        t0mer, tfmer = (u'AM', u'AM')
                if t0hr >= 12:
                    t0mer, tfmer = (u'PM', u'PM')


            # Find the default mer values.
            if t0hr < 12 and t0mer != u'AM' and t0hr <= tfhr:
                t0hr = t0hr + 12
            if tfhr < 12 and tfmer != u'AM':
                tfhr = tfhr + 12
            t0_total_mins = 60*t0hr + t0min
            tf_total_mins = 60*tfhr + tfmin
            # Set attributes for instance.
            self.match = match_text
            self.modification = (datetime.timedelta(minutes=t0_total_mins), datetime.timedelta(minutes=tf_total_mins))
        else:
            raise ValueError(u'Cannot parse and be initialized from given match value = ' \
                    + unicode(match))

    def __am_pm_normalize(self, mer_match):
        if mer_match:
            if u'a' in mer_match.lower():
                return u'AM'
            elif u'p' in mer_match.lower():
                return u'PM'
        return None

    @staticmethod
    def __match_function(nltext):
        match = AbsoluteInnerDayModifierAtom.EXTRACTION_REGEX.search(nltext)
        if match:
            valid_match = match.groupdict()[u't0hr'] and match.groupdict()[u'tfhr']
            return match.group() if valid_match else None
        else:
            return None

    @staticmethod
    def __match_transformer(match):
        return AbsoluteInnerDayModifierAtom(match)

    @staticmethod
    def extract_atom(text, *ignore, **kwargs_ignore):
        matcher = SequentialMatcher(AbsoluteInnerDayModifierAtom.__match_function,\
                match_transformer=AbsoluteInnerDayModifierAtom.__match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, *ignore):
        matcher = SequentialMatcher(AbsoluteInnerDayModifierAtom.__match_function, label=u'MOD')
        return matcher.extract(text)

    def to_json(self):
        return dict(match=self.match, modification=self.modification, tag=self.tag_name())

    def to_tag(self):
        return (self.match, self.TAG, self)

    def tag_name(self):
        return u'MOD_ABSINNERDAY'

    def reconvertible_text(self):
        start_time = utils.start_of_day(datetime.datetime.utcnow()) + self.modification[0]
        start_text = start_time.strftime(u'%I:%M %p')
        end_time = utils.start_of_day(datetime.datetime.utcnow()) + self.modification[1]
        end_text = end_time.strftime(u'%I:%M %p')
        return u'from {start_text} to {end_text}'.format(start_text=start_text, end_text=end_text)

    def display_text(self):
        return self.reconvertible_text()

    def modify(self, daterange):
        if isinstance(daterange, DaterangeAtom):
            by_days = daterange.split(u'days')
            return [tuple(map(operator.add, self.modification, (day[0], day[0]))) for day in by_days]
        else:
            raise ValueError(u'daterange must be a subclass of DaterangeAtom')


class NaturalInnerDayModifierAtom(ModifierAtom):

    # Use combination of subcomponents to make more complicated EXTRACTION_EXP.
    EXTRACTION_SUBCOMPS = {u'morning_seed':r'morn(ing)?|breakfast',
                            u'brunch_seed':r'brunch',
                            u'lunch_seed':r'lunch',
                            u'afternoon_seed':r'after\s?noon|siesta',
                            u'evening_seed':r'dinner|supper|evening|after\swork',
                            u'night_seed':r'night(\stime)?|late\b',
                            u'workday_seed':r'work\s?day|business(\shours)?',
                            u'early_mod':r'early\s?',
                            u'late_mod':r'late\s?'
                            }
    EXTRACTION_EXP = r'''
                        (?P<MOD_EMRN>{early_mod}({morning_seed}))|
                        (?P<MOD_MRN>{morning_seed})|
                        (?P<MOD_LMRN>{late_mod}({morning_seed}))|
                        (?P<MOD_BRNC>{brunch_seed})|
                        (?P<MOD_ELNC>{early_mod}({lunch_seed}))|
                        (?P<MOD_LNC>{lunch_seed})|
                        (?P<MOD_LLNC>{late_mod}({lunch_seed}))|
                        (?P<MOD_EAFR>{early_mod}({afternoon_seed}))|
                        (?P<MOD_AFR>{afternoon_seed})|
                        (?P<MOD_LAFR>{late_mod}({afternoon_seed}))|
                        (?P<MOD_EEVE>{early_mod}({evening_seed}))|
                        (?P<MOD_EVE>{evening_seed})|
                        (?P<MOD_LEVE>{late_mod}({evening_seed}))|
                        (?P<MOD_ENGT>{early_mod}({night_seed}))|
                        (?P<MOD_LNGT>{late_mod}({night_seed}))|
                        (?P<MOD_NGT>{night_seed})|
                        (?P<MOD_WKD>{workday_seed})
                        '''.format(**EXTRACTION_SUBCOMPS)
    EXTRACTION_REGEX = re.compile(EXTRACTION_EXP, flags=re.X|re.I)

    NAME_TO_HOURS = {
        u'MOD_EMRN': (5, 8),
        u'MOD_MRN': (8,11),
        u'MOD_LMRN': (10, 11.5),
        u'MOD_BRNC': (10,14),
        u'MOD_ELNC': (11,12),
        u'MOD_LNC': (11, 13),
        u'MOD_LLNC': (13,14.5),
        u'MOD_EAFR': (12,15),
        u'MOD_AFR': (12,16),
        u'MOD_LAFR': (14.5, 16.5),
        u'MOD_EEVE': (16,18),
        u'MOD_EVE': (17, 20),
        u'MOD_LEVE': (19,22),
        u'MOD_ENGT': (19, 21),
        u'MOD_NGT': (19,22.5),
        u'MOD_LNGT': (22,23.5),
        u'MOD_WKD': (9,17)
    }

    DESCRIPTION = {
        u'MOD_EMRN': u'in the early morning',
        u'MOD_MRN': u'in the morning',
        u'MOD_LMRN': u'late in the morning',
        u'MOD_BRNC': u'for brunch time',
        u'MOD_ELNC': u'for an early lunch',
        u'MOD_LNC': u'during lunch time',
        u'MOD_LLNC': u'for a late lunch',
        u'MOD_EAFR': u'in the early afternoon',
        u'MOD_AFR': u'in the afternoon',
        u'MOD_LAFR': u'in the late afternoon',
        u'MOD_EEVE': u'in the early evening',
        u'MOD_EVE': u'in the evening',
        u'MOD_LEVE': u'late in the evening',
        u'MOD_ENGT': u'early at night',
        u'MOD_NGT': 'at night',
        u'MOD_LNGT': 'late at night',
        u'MOD_WKD': 'during the workday'
    }

    RECONVERTIBLE = {
        u'MOD_EMRN': u'early morning',
        u'MOD_MRN': u'morning',
        u'MOD_LMRN': u'late morning',
        u'MOD_BRNC': u'brunch',
        u'MOD_ELNC': u'early lunch',
        u'MOD_LNC': u'lunch',
        u'MOD_LLNC': u'late lunch',
        u'MOD_EAFR': u'early afternoon',
        u'MOD_AFR': u'afternoon',
        u'MOD_LAFR': u'late afternoon',
        u'MOD_EEVE': u'early evening',
        u'MOD_EVE': u'evening',
        u'MOD_LEVE': u'late evening',
        u'MOD_ENGT': u'early night',
        u'MOD_NGT': 'night',
        u'MOD_LNGT': 'late night',
        u'MOD_WKD': 'workday'
    }


    def __init__(self, match, name=None, modification=None):
        if all([match, name, modification]):
            self.match = match
            self.name = name
            self.modification = modification
        elif match:
            self.__from_match(match)
        else:
            raise ValueError(u'Insufficient Parameters. Must provide `match` or `match` and `name`')

    def __from_match(self, match):
        mod_match = NaturalInnerDayModifierAtom.EXTRACTION_REGEX.search(match)
        mod_group = [k for k,v in mod_match.groupdict().iteritems() if v][0] if mod_match else None
        if mod_group:
            self.match = match
            self.name = mod_group
            # The instance might override NAME_TO_HOURS if there are custom values set in the future.
            self.modification = tuple(map(lambda hrs: datetime.timedelta(hours=hrs), self.NAME_TO_HOURS.get(self.name)))
        else:
            raise ValueError(u'Cannot parse and be initialized from given match value = ' \
                    + unicode(match))

    @staticmethod
    def __match_function(nltext):
        match = NaturalInnerDayModifierAtom.EXTRACTION_REGEX.search(nltext)
        return match.group() if match else None

    @staticmethod
    def __match_transformer(match):
        return NaturalInnerDayModifierAtom(match)

    @staticmethod
    def extract_atom(text, *ignore, **kwags_ignore):
        matcher = SequentialMatcher(NaturalInnerDayModifierAtom.__match_function,\
                match_transformer=NaturalInnerDayModifierAtom.__match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, *ignore):
        matcher = SequentialMatcher(NaturalInnerDayModifierAtom.__match_function, label=u'MOD')
        return matcher.extract(text)

    def to_json(self):
        return dict(match=self.match, modification=self.modification, tag=self.tag_name())

    def to_tag(self):
        return (self.match, u'MOD', self)

    def modify(self, daterange):
        if isinstance(daterange, DaterangeAtom):
            by_days = daterange.split(u'days')
            return [(day[0]+self.modification[0], day[0]+self.modification[1]) for day in by_days]
        else:
            raise ValueError(u'daterange must be a subclass of DaterangeAtom')

    def reconvertible_text(self):
        return self.RECONVERTIBLE[self.name]

    def display_text(self):
        return self.DESCRIPTION[self.name]

    def tag_name(self):
        return self.name


#
# Fillers
#
class FillerAtom(object):

    TAG = u'FILL'

    def __init__(self, match):
        self.match = match

    @staticmethod
    def __match_function(nltext):
        only_garbage = re.compile('^\S+$')
        match = only_garbage.search(nltext)
        return match.group() if match else None

    @staticmethod
    def __match_transformer(match):
        return FillerAtom(match)

    @staticmethod
    def extract_atom(text, *ignore, **kwargs_ignore):
        matcher = SequentialMatcher(FillerAtom.__match_function, match_transformer=FillerAtom.__match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, *ignore):
        matcher = SequentialMatcher(FillerAtom.__match_function, label=FillerAtom.TAG)
        return matcher.extract(text)

    def to_json(self):
        return dict(match=self.match)

    def to_tag(self):
        return (self.match, FillerAtom.TAG, self)

    def tag_name(self):
        return self.TAG


#
# Operands
#

class OperandAtom(object):

    # Class Variables.
    EXTRACTION_EXP = r'''
                        (?P<AND>(^|.)\band\b(.|$))|
                        (?P<OR>(^|.)\bor\b.|\beither\b)|
                        (?P<BW>\bbetween\b|\bduring\b)|
                        (?P<DASH>-|.\bthru\b.|\bthrough\b)|
                        (?P<FROM>(^|.)\bfrom\b(.|$))|
                        (?P<IN>(^|.)\bin\b(.|$))|
                        (?P<FOR>(^|.)\bfor\b(.|$))|
                        (?P<TO>(^|.)\bto\b(.|$))|
                        (?P<AT>(^|.)\bat\b(.|$))
                        '''
    EXTRACTION_REGEX = re.compile(EXTRACTION_EXP, flags=re.X|re.I)

    def __init__(self, match, operand=None):
        if operand and match:
            self.match = match
            self.operand = operand
        elif match:
            self.__from_match(match)
        else:
            raise ValueError(u'Insufficient Parameters. Must specify `match` or `match` and `operand`')

    def __from_match(self, match):
        op_match = OperandAtom.EXTRACTION_REGEX.search(match)
        operand_group = [k for k,v in op_match.groupdict().iteritems() if v][0] if op_match else None
        if operand_group:
            self.match = match
            self.operand = operand_group
        else:
            raise ValueError(u'Cannot parse and be initialized from given match value = ' \
                    + unicode(match))

    @staticmethod
    def __match_function(nltext):
        match = OperandAtom.EXTRACTION_REGEX.search(nltext)
        return match.group() if match else None

    @staticmethod
    def __match_transformer(match):
        return OperandAtom(match)

    @staticmethod
    def extract_atom(text, *args_ignore, **kwargs_ignore):
        matcher = SequentialMatcher(OperandAtom.__match_function, match_transformer=OperandAtom.__match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, *ignore):
        matcher = SequentialMatcher(OperandAtom.__match_function, label=u'OP')
        return matcher.extract(text)

    def modify(self, dr_i, dr_f):
        if isinstance(dr_i, DaterangeAtom) and isinstance(dr_f, DaterangeAtom):
            if self.operand == u'AT':
                res = datetime.datetime(dr_i.year, dr_i.month, dr_i.day, dr_f.hour, dr_f.minute, 0, 0);
                return [(res, res)]
            else:
                return []
        else:
            raise ValueError(u'daterange must be a subclass of DaterangeAtom')

    def to_json(self):
        return dict(match=self.match, operand=self.operand, tag=self.tag_name())

    def to_tag(self):
        return (self.match, self.operand, self)

    def tag_name(self):
        return self.operand

#
# Dateranges.
#

class DaterangeAtom(object):
    """DaterangeAtom a top level abstract object that can be recognized by the DateRangeParser.

    Attributes:
        start (datetime.datetime): Datetime that represents the start of the range.
        end (datetime.datetime): Datetime that represent the end of the range.
        match (string|unicode): Plain-text input that was used to generate this atom.
        src_time (datetime): The source time to base all calculation on. Preferably localized.

    """
    def __init__(self, start, end, match, src_time):
        """ Initialize a DaterangeAtom with all three parameters. """
        if all([start, end, match, src_time]):
            self.start = start
            self.end = end
            self.match = match
            self.src_time = src_time
        else:
            raise ValueError(u'DaterangeAtom requires `start`, `end`, `match` and `src_time`')

    def split(self, split_on=u'days'):
        """ Convenience function that allows a DateRange to be split into a list of single days."""
        # Map split on string to a recurrence rule.
        split_on_rules = {u'days': rrule.DAILY,
                          u'weeks': rrule.WEEKLY,
                          u'months': rrule.MONTHLY}
        # If there is a valid rule return a split date range.
        rule = split_on_rules.get(split_on)
        if rule:
            splits = list(rrule.rrule(rule, count=((self.end - utils.start_of_day(self.start)).days),
                                    dtstart=self.start,
                                    until=self.end))
            return [(s, utils.end_of_day(s)) for s in splits]
        else:
            raise ValueError(u'split_on value not supported.')

    def to_markup(self):
        return [(self.start, self.end)]

    def to_json(self):
        return dict(start=self.start, end=self.end, match=self.match, src_time=self.src_time, tag=self.tag_name())

    def to_tag(self):
        """ Atoms and TaggedAtoms can also be represented as TaggedObjects for RegexTagging."""
        return (self.match, u'DR', self)

    def tag_name(self):
        return self.TAG

    def is_single_day(self):
        return ((self.end - self.start).total_seconds() <= 60.00*60*24)


class NaturalDaterangeAtom(DaterangeAtom):
    """ NaturalDaterangeAtom is used to represent date ranges that correspond to date ranges like
    'this week', 'this weekend', 'this month' or otherwise relative and non calendar centric date
    ranges.

    Attributes:
    """
    TAG = u'NDR'

    def __init__(self, match, src_time, start=None, end=None):
        if all([match, src_time]):
            self.__from_match(match, src_time)
        elif all([start, end, match, src_time]):
            DaterangeAtom.__init__(self, start, end, match, src_time)
        else:
            raise ValueError(u'Insufficient parameters provided to init.')

    def __from_match(self, match, src_time):
        parsed = utils.safe_natural_daterange_parser(match, src_time)
        if parsed.get(u'label') is not u'fail':
            start = parsed.get(u'start')
            end = parsed.get(u'end')
            DaterangeAtom.__init__(self, start, end, match, src_time)
        else:
            raise ValueError(u'NaturalDaterangeAtom cannot parse and be initialized from given match value = ' \
                    + unicode(match))

    def change_src_time(self, src_time):
        self.__from_match(self.match, src_time);

    @staticmethod
    def extract_atom(text, src_time, **kwargs_ignore):
        parser = utils.safe_natural_daterange_parser
        def match_function(nltext): return parser(nltext, src_time).get(u'match')
        def match_transformer(match): return NaturalDaterangeAtom(match, src_time)
        matcher = SequentialMatcher(match_function, match_transformer=match_transformer)
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, src_time):
        parser = utils.safe_natural_daterange_parser
        def match_function(nltext): return parser(nltext, src_time).get(u'match')
        matcher = SequentialMatcher(match_function, label=NaturalDaterangeAtom.TAG)
        return matcher.extract(text)

    def reconvertible_text(self):
        return self.match

    def display_text(self):
        return self.match



class CalendarDateRangeAtom(DaterangeAtom):

    # Class Variables.
    TAG = u'CDR'

    def __init__(self, match, src_time, start=None, end=None, parse_type=u'range'):
        """ Initialize a CalendarDateRangeAtom with plaintext that can successfully translate to
        a CalendarDateRangeAtom or intialize with all known parameters."""
        self.parse_type = parse_type
        if all([match, src_time]):
            self.__from_match(match, src_time, parse_type=parse_type)
        elif all([start, end, match, src_time]):
            DaterangeAtom.__init__(self, start, end, match, src_time)
        else:
            raise ValueError('Insufficient parameters provided to init')

    def __from_match(self, match, src_time, parse_type=u'range'):
        """ Initialize the instance given a plaintext match string."""
        seed_dt = utils.safe_parsedatetime_first_nlp(match, src_time).get(u'datetime')
        if seed_dt:
            if parse_type == u'range':
                start = utils.start_of_day(seed_dt)
                end = utils.end_of_day(seed_dt)
            elif parse_type == u'exact':
                start = seed_dt
                end = seed_dt + datetime.timedelta(seconds=0)
            else:
                raise ValueError(u'Invalid value for parse_type. Try "range" or "exact"')
            # The special case in which an entire month is specified and not a specific date during it.
            if not re.search('[0-9]', match) and start.day == 1 and u'day' not in match:
                end = utils.end_of_month(seed_dt)
            DaterangeAtom.__init__(self, start, end, match, src_time)
        else:
            raise ValueError(u'CalendarDateRangeAtom cannot parse and intialized from given match value = '\
                    + unicode(match))

    @staticmethod
    def extract_atom(text, src_time, parse_type=u'range'):
        def match_function(nltext): return utils.safe_parsedatetime_first_nlp(nltext, src_time, ignore='time').get(u'match')
        def match_transformer(match): return CalendarDateRangeAtom(match, src_time, parse_type=parse_type)
        matcher = SequentialMatcher(match_function, match_transformer=match_transformer);
        return matcher.extract(text)

    @staticmethod
    def extract_tags(text, src_time):
        def match_function(nltext): return utils.safe_parsedatetime_first_nlp(nltext, src_time, ignore='time').get(u'match')
        matcher = SequentialMatcher(match_function, label=CalendarDaterangeAtom.TAG);
        return matcher.extract(text)

    def reconvertible_text(self):
        return self.start.strftime(u'%x')

    def display_text(self):
        if self.is_single_day():
            return self.start.strftime(u'%A %m/%d')
        else:
            return self.start.strftime(u'%A %m/%d') + u' through ' + (self.end - datetime.timedelta(days=1)).strftime(u'%A %m/%d')
