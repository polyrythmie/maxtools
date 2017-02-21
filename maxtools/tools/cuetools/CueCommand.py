# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject

class CueCommand(AbjadObject):
    '''A cue command.
    '''

    __slots__ = (
        '_arguments',
        '_automatic',
        '_command',
        '_route',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        command,
        arguments=None,
        automatic=False,
        ):
        self._route = route
        self._command = command
        if arguments is not None:
            if not isinstance(arguments, (list, tuple)):
                arguments = (arguments,)
        self._arguments = arguments
        self._automatic = bool(automatic)

    ### SPECIAL METHODS ###

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_format(self):
        cue_command = [self.route, self.command]
        if self.arguments is not None:
            cue_command.extend(str(x) for x in self.arguments)
        cue_command = ' '.join(cue_command)
        return cue_command

    @property
    def _jamoma_format(self):
        cue_command = ['/{}/{}'.format(self.route, self.command)]
        cue_command.extend(self.arguments)
        cue_command = ' '.join(cue_command)
        return cue_command

    ### PRIVATE METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def arguments(self):
        return self._arguments

    @property
    def automatic(self):
        return self._automatic

    @property
    def command(self):
        return self._command

    @property
    def route(self):
        return self._route
