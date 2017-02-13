# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad.tools import lilypondnametools
from abjad.tools import schemetools
from abjad.tools.spannertools.Spanner import Spanner
from maxtools.tools.cuetools.Cue import Cue

class CueVoiceSpanner(Spanner):
    r'''Creates cue markup in score
    '''

    ### CLASS VARIABLES ###

    __slots__ = ()

    ### INITIALIZER ###

    def __init__(self, overrides=None):
        Spanner.__init__(self, overrides=overrides)

    ### PRIVATE METHODS ###

    def _get_lilypond_format_bundle(self, leaf):
        lilypond_format_bundle = self._get_basic_lilypond_format_bundle(leaf)
        inspector = inspect_(leaf)
        cue = None
        if inspector.has_indicator(prototype=(Cue,)):
            cue = inspector.get_indicator(prototype=(Cue,))
        if cue is None:
            return lilypond_format_bundle
        self._make_cue_overrides(cue, lilypond_format_bundle)
        return lilypond_format_bundle

    def _make_cue_overrides(self, cue=None, lilypond_format_bundle=None):
        if cue is None:
            return
        override_ = lilypondnametools.LilyPondGrobOverride(
            grob_name='NoteHead',
            is_once=True,
            property_path='stencil',
            value=schemetools.Scheme('ly:text-interface::print'),
            )
        string = override_.override_string
        lilypond_format_bundle.grob_overrides.append(string)
        override_ = lilypondnametools.LilyPondGrobOverride(
            grob_name='NoteHead',
            is_once=True,
            property_path='text',
            value=cue.markup,
            )
        string = override_.override_string
        lilypond_format_bundle.grob_overrides.append(string)
        return lilypond_format_bundle
