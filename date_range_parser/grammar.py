# -*- coding: utf-8 -*-
"""grammar.py

@author: ashutosh@hq.siftnet.com
@date: August 3, 2014

grammar.py declares the grammar of atoms that we're looking for
as well as the interpretation.
"""

from nltk.chunk import RegexpParser

def handle_bw_dr(tree):
    """Handles subtree with a node type of BW_DR"""
    dt_tup_key = lambda tup: tup[0]
    mod_drs = [t for t in tree.subtrees(lambda t: t.node == u'MOD_DR')]
    if len(mod_drs) >= 2:
        mod_dr1 = handle_mod_dr(mod_drs[0])
        mod_dr2 = handle_mod_dr(mod_drs[1])
        # Handle each MDR and sort them by date.
        mu1 = sorted(mod_dr1.get(u'markup'), key=dt_tup_key)
        mu2 = sorted(mod_dr2.get(u'markup'), key=dt_tup_key)
        # Return the earliest and late date. Interpolate the dateranges.
        markup = [(mu1[0][0], mu2[-1][-1])]
        return dict(markup=markup, grammar=u'BW_DR', components=tuple([mod_dr1, mod_dr2]))
    else:
        return None

def handle_and_dr(tree):
    """Handles subtree with a node type of AND_DR"""
    mod_drs = [t for t in tree.subtrees(lambda t: t.node == u'MOD_DR')]
    if len(mod_drs) >= 2:
        # Return the union of the two dateranges.
        mod_dr1 = handle_mod_dr(mod_drs[0])
        mod_dr2 = handle_mod_dr(mod_drs[1])
        markup = mod_dr1.get(u'markup') + mod_dr2.get(u'markup')
        return dict(markup=markup, grammar=u'AND_DR', components=tuple([mod_dr1, mod_dr2]))
    else:
        return None

def handle_rel_dr(tree):
    """Handles subtree with a node type of REL_DR"""
    mod_drs = [t for t in tree.subtrees(lambda t: t.node == u'MOD_DR')]
    if len(mod_drs) >= 2:
        # Return the union of the two dateranges.
        mod_dr1_md = handle_mod_dr(mod_drs[0])
        mod_dr2_md = handle_mod_dr(mod_drs[1])
        mod_dr1 = mod_dr1_md.get(u'daterange')
        mod_dr2 = mod_dr2_md.get(u'daterange')
        if mod_dr1.TAG == u'NDR' and mod_dr2.TAG == u'CDR':
            mod_dr1.change_src_time(mod_dr2.start)
            markup = mod_dr1.to_markup()
        else:
            markup = []
        return dict(markup=markup, grammar=u'REL_DR', components=tuple([mod_dr1_md, mod_dr2_md]))
    else:
        return None

def handle_ref_dr(tree):
    """Handles subtree with node type AT_DR"""
    references = [c for c in tree if u'REF' in c[1]]
    dateranges = [c for c in tree if c[1] == u'DR']
    if len(references) > 0 and len(dateranges) > 0:
        at_obj = references[0][-1]
        dr_obj = dateranges[0][-1]
        # Apply the *ModifierAtom to the DaterangeAtom.
        markup = at_obj.modify(dr_obj)
        return dict(markup=markup, grammar=u'REF_DR', daterange=dr_obj, modifier=at_obj)
    else:
        return None

def handle_mod_dr(tree):
    """Handles subtree wth node type MOD_DR"""
    modifier = [c for c in tree if u'MOD' in c[1]]
    daterange = [c for c in tree if c[1] == u'DR']
    if len(modifier) > 0 and len(daterange) > 0:
        mod_obj = modifier[0][-1]
        dr_obj = daterange[0][-1]
        # Apply the *ModifierAtom to the DaterangeAtom.
        markup = mod_obj.modify(dr_obj)
        return dict(markup=markup, grammar=u'MOD_DR', daterange=dr_obj, modifier=mod_obj)
    elif len(daterange) > 0:
        # If there is no modifier, return the daterange in markup format.
        dr_obj = daterange[0][-1]
        markup = dr_obj.to_markup()
        return dict(markup=markup, grammar=u'MOD_DR', daterange=dr_obj, modifier=None)
    else:
        markup = None


def traverse(tree):
    try:
        if tree.node == u'S':
            return [res for res in [traverse(c) for c in tree] if res]
        elif tree.node == u'MOD_DR':
            return handle_mod_dr(tree)
        elif tree.node == u'BW_DR':
            return handle_bw_dr(tree)
        elif tree.node == u'AND_DR':
            return handle_and_dr(tree)
        elif tree.node == u'REL_DR':
            return handle_rel_dr(tree)
        elif tree.node == u'AT_DR':
            return handle_ref_dr(tree)
        else:
            return None
    except AttributeError:
        return None


range_grammar = '''
            MOD_DR: {<DR><RANGE|BW|FROM|FOR><MOD.*>|<DR><FILL>?<MOD.*>?|<MOD.*>?<DR>}
            REL_DR: {<MOD_DR><FROM><MOD_DR>}
            BW_DR:  {<BW><MOD_DR><AND><MOD_DR>|<MOD_DR><DASH><MOD_DR>|<FROM><MOD_DR><TO|DASH><MOD_DR>}
            AND_DR: {<MOD_DR><AND|OR|BW><MOD_DR>}
            '''

exact_grammar = '''
            AT_DR:  {<DR><REF>|<REF><DR>}
            MOD_DR: {<DR><RANGE|BW|FROM|FOR><MOD.*>|<DR><FILL>?<MOD.*>?|<MOD.*>?<DR>}
            BW_DR:  {<BW><MOD_DR><AND><MOD_DR>|<MOD_DR><DASH><MOD_DR>|<FROM><MOD_DR><TO|DASH><MOD_DR>}
            '''

#date_grammar_regex_parser = RegexpParser(date_grammar)
range_grammar_regex_parser = RegexpParser(range_grammar)
exact_grammar_regex_parser = RegexpParser(exact_grammar)


