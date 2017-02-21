# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
from abjad.tools import lilypondnametools
from abjad.tools import markuptools
from abjad.tools import schemetools
from abjad.tools import scoretools
from abjad.tools.spannertools.Spanner import Spanner
from maxtools.tools.cuetools.CueCommand import CueCommand

# Make a fancy notehead for cues!
class Cue(Spanner):
    '''A cue.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_number',
        '_reminder',
        '_time_offset',
        )

    ### INITIALIZER ###

    def __init__(self, number, reminder=False, time_offset=0, overrides=None):
        assert isinstance(number, int), repr(number)
        self._number = number
        self._reminder = bool(reminder)
        self._time_offset = time_offset
        Spanner.__init__(self, overrides=overrides)

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
        from abjad.tools import systemtools
        return systemtools.StorageFormatAgent(self).get_storage_format()

    ### PRIVATE METHODS ###

    def _get_lilypond_format_bundle(self, leaf):
        lilypond_format_bundle = self._get_basic_lilypond_format_bundle(leaf)
        if self._is_my_first_leaf(leaf):
            self._make_cue_start_notehead_overrides(self.number, lilypond_format_bundle)
        if inspect_(leaf).has_indicator(CueCommand):
            self._make_timing_overrides(lilypond_format_bundle)
        return lilypond_format_bundle

    def _make_cue_start_notehead_overrides(self, number, lilypond_format_bundle):
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
            value=self.cue_markup,
            )
        string = override_.override_string
        lilypond_format_bundle.grob_overrides.append(string)
        override_ = lilypondnametools.LilyPondGrobOverride(
            grob_name='NoteHead',
            is_once=True,
            property_path='Y-offset',
            value=-0.75,
            )
        string = override_.override_string
        lilypond_format_bundle.grob_overrides.append(string)

    @staticmethod
    def _make_timing_overrides(lilypond_format_bundle):
        # TODO
        pass

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_command_time_map(self):
        result = {(int(inspect_(leaf).get_timespan(in_seconds=True).start_offset * 1000) + self.time_offset):inspect_(leaf).get_indicators(prototype=CueCommand) for leaf in iterate(self).by_class(scoretools.Leaf)}
        return result

    @property
    def _cue_file_format(self):
        start_offset_in_ms = int(self._get_timespan(in_seconds=True).start_offset * 1000)
        result = ['---------- {}'.format(self.number)]
        for time, commands in self._cue_command_time_map.iteritems():
            time_offset = time - start_offset_in_ms
            result.extend(['{} {}'.format(time_offset, command._cue_format) for command in commands])
        result = '\n'.join(result)
        return result

    @property
    def _duration_in_ms(self):
        return (int(self._get_duration(in_seconds=True) * 1000) + self.time_offset)

    ### PUBLIC METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def number(self):
        return self._number

    @property
    def reminder(self):
        return self._reminder

    @property
    def time_offset(self):
        return self._time_offset

    @property
    def cue_markup(self):
        markup = markuptools.Markup(self.number)
        markup = markup.huge()
        if self.reminder:
            markup = markup.parenthesize()
        else:
            markup = markup.circle()
            markup = markup.override(('circle-padding', 1))
        markup = markup.whiteout()
        return markup
