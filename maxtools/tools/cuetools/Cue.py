# -*- coding: utf-8 -*-
from abjad.tools.spannertools.Spanner import Spanner
from operator import attrgetter
from abjad.tools import systemtools
from abjad.tools import durationtools
from abjad.tools import markuptools

# Make a fancy notehead for cues!
class CueAsSpanner(Spanner):
    '''A cue as a spanner.
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

    ### PUBLIC METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def number(self):
        return self._number

    @property
    def reminder(self):
        return self._reminder
