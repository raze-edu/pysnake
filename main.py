import pygame
from enum import Enum

class ScreenModes(Enum):
    pygame.FULLSCREEN = 1
    pygame.RESIZEABLE = 2
    pygame.NOFRAME = 3

class Game:
    def __init__(self, screenmode: ScreenModes, width=0, height=0):
        pygame.init()
        pygame.display.set_caption("Cyber Snake 3000")
        self.screenmode = screenmode
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), screenmode.value)
        self.clock = pygame.time.Clock()

    