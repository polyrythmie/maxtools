# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadValueObject
from abjad.tools import markuptools

class MidiControl(AbjadValueObject):
    r'''A Midi control knob or fader indicator.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_value',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        value=None,
        ):
        if value is not None:
            assert 0 <= value <= 127
        self._value = value

    ### SPECIAL METHODS ###

    def __lt__(self, expr):
        if isinstance(expr, type(self)):
            return self._value < expr._value
        raise TypeError('unorderable types')

    ### PUBLIC PROPERTIES ###

    @property
    def value(self):
        return self._value

    @property
    def markup(self):
        markup = markuptools.Markup(str(self._value))
        return markup
