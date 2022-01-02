import pygame_assets as assets
import pygame as pg


menu_background = assets.load.image("menu.png")
menu_play = pg.Rect(47, 59, 321, 159)
menu_quit = pg.Rect(438, 65, 314, 160)

game_neuron_rect = pg.Surface((10, 10))
game_neuron_rect.fill((255, 255, 255))

game_player_rect = pg.Surface((10, 10))
game_player_rect.fill((255, 0, 0))
