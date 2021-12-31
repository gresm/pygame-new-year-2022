import pygame as pg

from game import game, scene_manager as scenes
from game.scenes import MainMenuScene


scenes.spawn_scene(MainMenuScene)


@game.frame
def frame(window: pg.Surface, delta_time: float):
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            game.stop()
        else:
            scenes.handle_events(ev)

    scenes.update()

    window.fill((0, 0, 0))

    pg.display.update()


if __name__ == '__main__':
    game.run()
