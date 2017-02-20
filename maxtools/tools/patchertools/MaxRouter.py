# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
from abjad.tools.abctools.AbjadObject import AbjadObject
from maxtools.tools.cuetools import CueCommand
from maxtools.tools.patchertools.MaxEvent import MaxEvent
from maxtools.tools.patchertools.MaxSetting import MaxSetting

class MaxRouter(AbjadObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_accepts_commands',
        '_command_point_map',
        '_context',
        '_cue_command_point_map',
        '_initialization',
        '_last_effective_settings',
        '_route',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        accepts_commands=None,
        initialization=set(),
        ):
        self._route = route
        if not isinstance(accepts_commands, (list, tuple)):
            accepts_commands = (accepts_commands,)
        self._accepts_commands = accepts_commands
        if not isinstance(initialization, set):
            initialization = set(initialization)
        for init_command in initialization:
            assert isinstance(init_command, accepts_commands)
        self._initialization = initialization

    ### SPECIAL METHODS ###

    def __call__(
        self,
        context,
        initialize=False,
        last_effective_settings=set(),
        ):
        self._context = context
        self._last_effective_settings = set([x for x in last_effective_settings if isinstance(x, self.accepts_commands)])
        if initialize:
            self._last_effective_settings |= self.initialization
        self._collect_command_points()
        self._postprocess_command_point_map()
        self._make_cue_command_point_map()
        return self._cue_command_point_map

    ### PRIVATE METHODS ###

    def _collect_command_points(self):
        self._command_point_map = {}
        prototype = self.accepts_commands
        for leaf in iterate(self._context).by_timeline():
            accepted_commands = set([indicator for indicator in inspect_(leaf).get_indicators(prototype=prototype, unwrap=True)])
            if not accepted_commands:
                continue
            start_offset = inspect_(leaf).get_timespan().start_offset
            if start_offset not in self._command_point_map:
                self._command_point_map[start_offset] = set()
            self._command_point_map[start_offset] |= accepted_commands

    def _make_cue_command_point_map(self,
        ):
        self._cue_command_point_map = {}
        for start_offset, commands in self._command_point_map.iteritems():
            self._cue_command_point_map[start_offset] = set([CueCommand(route=self.route, command=_.command, arguments=_.arguments, automatic=_.automatic) for _ in commands])


    def _postprocess_command_point_map(self):
        postprocessed_command_point_map = {}
        for start_offset in sorted(self._command_point_map):
            commands = self._command_point_map[start_offset]
            new_settings = set([x for x in commands if (isinstance(x, MaxSetting) and not any([x.equivalent_to_setting(y) for y in self._last_effective_settings]))])
            all_commands = new_settings | set([x for x in commands if (isinstance(x, MaxEvent))])
            if not all_commands:
                continue
            postprocessed_command_point_map[start_offset] = all_commands
            self._last_effective_settings = set([x for x in self._last_effective_settings if not any([y.overrides_setting(x) for y in new_settings])]) | new_settings
        self._command_point_map = postprocessed_command_point_map

    ### PRIVATE PROPERTIES ###

    @property
    def _initialization_cue_commands(self):
        cue_commands = set([CueCommand(route=self.route, command=_.command, arguments=_.arguments, automatic=_.automatic) for _ in self.initialization])
        return cue_commands

    ### PUBLIC METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def accepts_commands(self):
        return self._accepts_commands

    @property
    def initialization(self):
        return self._initialization

    @property
    def route(self):
        return self._route
