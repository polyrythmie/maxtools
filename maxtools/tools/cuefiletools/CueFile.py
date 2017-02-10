# -*- coding: utf-8 -*-
from abjad.tools.abctools.AbjadObject import AbjadObject
from operator import attrgetter
from abjad.tools import systemtools

class CueFile(AbjadObject):
    r'''A cue file.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_cues',
        '_file_name',
        '_context',
        '_name',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        file_name,
        context,
        ):
        self._cues = []
        self._file_name = file_name
        self._context = context

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
        from abjad.tools import systemtools
        if format_specification in ('', 'cue_file'):
            return self._cue_file_format
        elif format_specification == 'storage':
            return systemtools.StorageFormatAgent(self).get_storage_format()
        return str(self)

    def __getitem__(self, number):
        for cue in self.cues:
            if getattr(cue, 'number', None) == number:
                return item
        raise KeyError

    ### PRIVATE METHODS ###

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_file_format(self):
        result = []
        for cue in sorted(self.cues, key=attrgetter('number')):
            result.append(cue._cue_file_format)
        result = '\n'.join(result)
        return result

    ### PUBLIC METHODS ###

    def get_cue_file_length_in_milliseconds(self):
        length = 0
        for cue in self.cues:
            length += cue.get_length_in_milliseconds()
        return length

    ### PUBLIC PROPERTIES ###

    @property
    def context(self):
        return self._context

    @property
    def cues(self):
        return self._cues

    @property
    def file_name(self):
        return self._file_name
