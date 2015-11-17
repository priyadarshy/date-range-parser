# -*- coding: utf-8 -*-
"""metadata.py

@author: ashutosh@hq.siftnet.com
@date: August 14, 2014

Goes through a traversed parse tree and constructs a plain text interpretation
from the given metadata about the parse.
"""
import atoms

def display_text(parse):
    grammar_type = parse[u'grammar']

    if grammar_type == u'BW_DR':
        components = parse[u'components']
        mod_dr1 = components[0]
        mod_dr2 = components[1]
        return u'between ' + display_text(mod_dr1) + u' and ' +  display_text(mod_dr2)
    elif grammar_type == u'AND_DR':
        components = parse[u'components']
        mod_dr1 = components[0]
        mod_dr2 = components[1]
        return display_text(mod_dr1) + u' and ' + display_text(mod_dr2)
    elif grammar_type == u'REL_DR':
        components = parse[u'components']
        mod_dr1 = components[0]
        mod_dr2 = components[1]
        return display_text(mod_dr1) + u' from ' + display_text(mod_dr2)
    elif grammar_type == u'MOD_DR':
        modifier = parse[u'modifier']
        daterange = parse[u'daterange']
        if modifier:
            if isinstance(modifier, atoms.AbsoluteInnerDayModifierAtom):
                return daterange.display_text() + u' ' + modifier.display_text()
            elif isinstance(modifier, atoms.AbsoluteOneWayInnerDayModifierAtom):
                return daterange.display_text() + u' ' + modifier.display_text()
            elif isinstance(modifier, atoms.RelativeOneWayMultiDayModifierAtom):
                return modifier.display_text() + u' ' + daterange.display_text()
            elif isinstance(modifier, atoms.NaturalInnerDayModifierAtom):
                return daterange.display_text() + u' ' + modifier.display_text()
            else:
                return None
        else:
            return daterange.display_text()

def reconvertible_text(parse):
    grammar_type = parse[u'grammar']

    if grammar_type == u'BW_DR':
        components = parse[u'components']
        mod_dr1 = components[0]
        mod_dr2 = components[1]
        return u'between ' + reconvertible_text(mod_dr1) + u' and ' +  reconvertible_text(mod_dr2)
    elif grammar_type == u'AND_DR':
        components = parse[u'components']
        mod_dr1 = components[0]
        mod_dr2 = components[1]
        return reconvertible_text(mod_dr1) + u' and ' + reconvertible_text(mod_dr2)
    elif grammar_type == u'REL_DR':
        components = parse[u'components']
        mod_dr1 = components[0]
        mod_dr2 = components[1]
        return reconvertible_text(mod_dr1) + u' from ' + reconvertible_text(mod_dr2)
    elif grammar_type == u'MOD_DR':
        modifier = parse[u'modifier']
        daterange = parse[u'daterange']
        text = daterange.reconvertible_text() if u'today' not in daterange.match else 'today'
        if modifier:
            if isinstance(modifier, atoms.AbsoluteInnerDayModifierAtom):
                return text + u' ' + modifier.reconvertible_text()
            elif isinstance(modifier, atoms.AbsoluteOneWayInnerDayModifierAtom):
                return text + u' ' + modifier.reconvertible_text()
            elif isinstance(modifier, atoms.RelativeOneWayMultiDayModifierAtom):
                return modifier.reconvertible_text() + u' ' + text
            elif isinstance(modifier, atoms.NaturalInnerDayModifierAtom):
                return text + u' ' + modifier.reconvertible_text()
            else:
                return None
        else:
            return text

