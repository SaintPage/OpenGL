import pygame
import pygame.display
from pygame.locals import *

from gl import Renderer
from buffer import Buffer
from vertexShader import *
from fragmentShader import *

width = 960
height = 540

deltaTime = 0.0

screen = pygame.display.set_mode((width, height), pygame.SCALED | pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()


triangle = [-0.5, -0.5, 0,    1.0, 0.0, 0.0,
            0, 0.5, 0,        0.0,  1.0, 0.0,
            0.5, -0.5, 0,      0.0, 0.0, 1.0]

rend = Renderer(screen)

rend.SetShaders(vertex_shader, fragment_shader)

rend.scene.append(Buffer(triangle))

isRunning = True

while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

    deltaTime = clock.tick(60) / 1000

    rend.Render()
    pygame.display.flip()

pygame.quit()
