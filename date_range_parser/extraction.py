# -*- coding: utf-8 -*-
"""extraction.py

@author: ashutosh@hq.siftnet.com
@date: August 2, 2014

Looks for a sequence of tagged atoms in a string of text.
"""

import atoms

class DateGrammarAtomTagger(object):

    def __init__(self, src_time, parse_type=u'range'):
        if src_time:
            self.src_time = src_time
            self.parse_type = parse_type
            if parse_type == u'range':
                self.atom_precedence = [atoms.AbsoluteInnerDayModifierAtom,
                        atoms.AbsoluteOneWayInnerDayModifierAtom, atoms.NaturalInnerDayModifierAtom,
                        atoms.RelativeOneWayMultiDayModifierAtom, atoms.OperandAtom,
                        atoms.NaturalDaterangeAtom, atoms.CalendarDateRangeAtom, atoms.FillerAtom]
            elif parse_type == u'exact':
                self.atom_precedence = [
                        #atoms.ReferencePointModifierAtom,
                        atoms.AbsoluteInnerDayModifierAtom,
                        #atoms.AbsoluteOneWayInnerDayModifierAtom,
                        #atoms.NaturalInnerDayModifierAtom,
                        atoms.OperandAtom, atoms.NaturalDaterangeAtom, atoms.CalendarDateRangeAtom, atoms.FillerAtom]
            else:
                raise ValueError(u'Invalid parse_type. Try "range" or "exact"')
        else:
            raise ValueError(u'Insufficient Parameters. `src_time` required or `src_time` and `atom_precedence`')

    def tag(self, nltext):
        result = [nltext]
        # Utility to functions to unpack nested lists and only run extract on non-strings.
        def extract_or_passback(extract_fn, atom_or_str): return extract_fn(atom_or_str, self.src_time, parse_type=self.parse_type) if isinstance(atom_or_str, basestring) else atom_or_str
        def inner_unpack(maybe_list): return [item for item in maybe_list] if isinstance(maybe_list, list) else [maybe_list]
        def unpack(nested_list): return [item for inner in nested_list for item in inner_unpack(inner)]
        # Run the extract_atom static method for each class in order of precedence.
        for AtomClass in self.atom_precedence:
            result = unpack([(extract_or_passback(AtomClass.extract_atom, atom_or_str)) for atom_or_str in result])
        # When we're done, remove any items that are basestrings.
        return filter(lambda r: not isinstance(r, basestring), result)



