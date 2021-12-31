from __future__ import annotations

from typing import Type

import pygame as pg


class Scene:
    _instances_cnt: int = -1
    instances: dict[int, Scene] = {}

    _scenes_cnt = -1
    scenes: dict[int, Type[Scene]] = {}

    class_id: int = -1

    scene_manager: SceneManager | None

    def __init__(self, scene_manager: SceneManager | None = None):
        self.manager = scene_manager
        Scene._instances_cnt += 1
        Scene.instances[self._instances_cnt] = self
        self.instance_id = self.current_instance_id()
        self._events: list[pg.event.Event] = []
        self.init()

    def __init_subclass__(cls, **kwargs):
        Scene._scenes_cnt += 1
        Scene.scenes[Scene._scenes_cnt] = cls
        cls.class_id = cls.current_class_id()

    @classmethod
    def current_instance_id(cls):
        return Scene._instances_cnt

    @classmethod
    def current_class_id(cls):
        return Scene._scenes_cnt

    def init(self, *args, **kwargs):
        pass

    def add_event_to_pool(self, event: pg.event.Event):
        self._events.append(event)

    def get_events(self):
        for _ in range(len(self._events)):
            yield self._events.pop()

    def draw(self, surface: pg.Surface):
        pass

    def update(self):
        pass


class SceneManager:
    def __init__(self):
        self.current: Scene | None = None

    def draw(self, surface: pg.Surface):
        if self.current is not None:
            self.current.draw(surface)

    def update(self):
        if self.current:
            self.current.update()

    def set_active_scene(self, scene_id: int | Scene):
        if isinstance(scene_id, Scene):
            self.current = scene_id
        elif scene_id in Scene.instances:
            self.current = Scene.instances[scene_id]

    def spawn_scene(self, scene_id: int | Type[Scene]):
        if isinstance(scene_id, type) and issubclass(scene_id, Scene):
            return self.spawn_scene(scene_id.class_id)
        elif scene_id in Scene.scenes:
            Scene.scenes[scene_id](self)
            self.set_active_scene(Scene.current_instance_id())
            return Scene.current_instance_id()
        return -1

    def handle_events(self, event: pg.event.Event):
        self.current.add_event_to_pool(event)

    def init(self, *args, **kwargs):
        if self.current:
            self.current.init(*args, **kwargs)
