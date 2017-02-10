# -*- coding: utf-8 -*-
from abjad.tools import lilypondnametools
from abjad.tools import schemetools
from abjad.tools import scoretools
from abjad.tools.spannertools.Spanner import Spanner
from abjad.tools.topleveltools import inspect_
from maxtools.tools.miditools import MidiControl

class MidiControlSpanner(Spanner):
    r'''Midi control spanner
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        )

    ### INITIALIZER ###

    def __init__(self, overrides=None):
        Spanner.__init__(self, overrides=overrides)

    ### PRIVATE METHODS ###

    def _get_annotations(self, leaf):
        inspector = inspect_(leaf)
        midi_control = None
        prototype = MidiControl
        if inspector.has_indicator(prototype):
            midi_control = inspector.get_indicator(prototype)
        return midi_control

    def _get_lilypond_format_bundle(self, leaf):
        lilypond_format_bundle = self._get_basic_lilypond_format_bundle(leaf)
        midi_control = self._get_annotations(leaf)
        if midi_control is None:
            return lilypond_format_bundle
        self._make_midi_control_overrides(
            midi_control=midi_control,
            lilypond_format_bundle=lilypond_format_bundle,
            )
        return lilypond_format_bundle

    def _make_midi_control_overrides(
        self,
        midi_control=None,
        lilypond_format_bundle=None,
        ):
        if midi_control is None:
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
            value=midi_control.markup,
            )
        string = override_.override_string
        lilypond_format_bundle.grob_overrides.append(string)
        y_offset = float(((4 * midi_control.value) / 127) - 2)
        override_ = lilypondnametools.LilyPondGrobOverride(
            grob_name='NoteHead',
            is_once=True,
            property_path='Y-offset',
            value=y_offset,
            )
        string = override_.override_string
        lilypond_format_bundle.grob_overrides.append(string)
