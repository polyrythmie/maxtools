# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
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
        )

    ### INITIALIZER ###

    def __init__(self, number, reminder=False, overrides=None):
        assert isinstance(number, int), repr(number)
        self._number = number
        self._reminder = bool(reminder)
        Spanner.__init__(self, overrides=overrides)

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
        from abjad.tools import systemtools
        return systemtools.StorageFormatAgent(self).get_storage_format()

    ### PRIVATE METHODS ###

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_command_time_map(self):
        result = {int(inspect_(leaf).get_timespan(in_seconds=True).start_offset * 1000):inspect_(leaf).get_indicators(prototype=CueCommand) for leaf in iterate(self).by_class(scoretools.Leaf)}
        return result

    @property
    def _cue_file_format(self):
        start_offset_in_ms = int(self._get_timespan(in_seconds=True).start_offset * 1000)
        result = []
        if self.number != 0:
            result.append('---------- {}'.format(self.number))
        for time, commands in self._cue_command_time_map.iteritems():
            time_offset = time - start_offset_in_ms
            result.extend(['{} {}'.format(time_offset, command._cue_format) for command in commands])
        result = '\n'.join(result)
        return result

    @property
    def _duration_in_ms(self):
        return int(self._get_duration(in_seconds=True) * 1000)

    ### PUBLIC METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def number(self):
        return self._number

    @property
    def reminder(self):
        return self._reminder
