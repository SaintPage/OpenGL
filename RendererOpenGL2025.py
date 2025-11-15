import pygame
import pygame.display
from pygame.locals import *
from math import sin, cos, radians
from OpenGL.GL import glFlush, glGetError, GL_NO_ERROR

import glm

from gl import Renderer
from model import Model
from vertexShader import *
from fragmentShader import *

width = 960
height = 540

deltaTime = 0.0

# Inicializar pygame PRIMERO
pygame.init()

# NO configurar OpenGL context attributes - dejar que pygame use defaults
# Esto usa Compatibility Profile que es más compatible

screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("OpenGL Renderer 2025")
clock = pygame.time.Clock()

rend = Renderer(screen)

# Lighting setup - Luz más fuerte y mejor posicionada
rend.pointLight = glm.vec3(5, 5, 10)  # Luz desde arriba y adelante
rend.ambientLight = 0.8  # Más luz ambiental para ver mejor

# Current shader configuration
currVertexShader = vertex_shader
currFragmentShader = fragment_shader

rend.SetShaders(currVertexShader, currFragmentShader)

# Camera setup
rend.camera.position = glm.vec3(0, 0, 3)  # Posición inicial de la cámara

# Create skybox
skyboxTextures = ["skybox/right.jpg", 
                  "skybox/left.jpg", 
                  "skybox/top.jpg", 
                  "skybox/bottom.jpg", 
                  "skybox/front.jpg", 
                  "skybox/back.jpg"]
rend.CreateSkybox(skyboxTextures)
print("✓ Skybox cargado exitosamente!")

# Load Penguin model
try:
    penguin = Model("models/PenguinBaseMesh.obj")
    
    # Cargar textura del pingüino
    penguin.AddTexture("models/Penguin Diffuse Color.png")
    
    # Ajustar posición y escala
    penguin.position = glm.vec3(0, 0, 0)  # Centro
    penguin.rotation.y = 0  # Sin rotación inicial
    penguin.scale = glm.vec3(1.0, 1.0, 1.0)  # Tamaño normalizado
    
    rend.scene.append(penguin)
    print("✓ Pingüino cargado exitosamente!")
    print("  Usa la rueda del mouse para hacer zoom")
    print("  Presiona ESPACIO para auto-rotar")
except Exception as e:
    print(f"⚠ Error al cargar modelo: {e}")
    print("  Verifica que el archivo existe en models/Porsche_911_GT2.obj")

# Time and value uniforms for shaders
elapsedTime = 0.0
value = 0.5

# Camera rotation
camAngle = 0

isRunning = True

print("\n=== SHADER CONTROLS ===")
print("VERTEX SHADERS:")
print("  7 - Default vertex shader")
print("  8 - Spiral/Twist shader")
print("  9 - Pulse/Heartbeat shader")
print("  0 - Glitch/Displacement shader")
print("\nFRAGMENT SHADERS:")
print("  1 - Default fragment shader (with lighting)")
print("  2 - Hologram shader")
print("  3 - Plasma/Fire shader")
print("  4 - Matrix Digital Rain shader")
print("\nCONTROLS:")
print("  Z/X - Decrease/Increase shader value parameter")
print("  Left/Right Click - Rotate camera")
print("  Mouse Wheel - Zoom in/out")
print("  F - Toggle wireframe mode")
print("  SPACE - Auto-rotate camera")
print("  ESC - Quit")
print("=======================\n")

autoRotate = False

while isRunning:
    
    keys = pygame.key.get_pressed()
    mouseVel = pygame.mouse.get_rel()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        
        elif event.type == pygame.MOUSEWHEEL:
            rend.camera.position.z -= event.y * deltaTime * 10
        
        elif event.type == pygame.KEYDOWN:
            # Fragment shader selection
            if event.key == pygame.K_1:
                currFragmentShader = fragment_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Fragment Shader: Default (with lighting)")
            
            elif event.key == pygame.K_2:
                currFragmentShader = hologram_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Fragment Shader: Hologram")
            
            elif event.key == pygame.K_3:
                currFragmentShader = plasma_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Fragment Shader: Plasma/Fire")
            
            elif event.key == pygame.K_4:
                currFragmentShader = matrix_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Fragment Shader: Matrix Digital Rain")
            
            # Vertex shader selection
            elif event.key == pygame.K_7:
                currVertexShader = vertex_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Vertex Shader: Default")
            
            elif event.key == pygame.K_8:
                currVertexShader = spiral_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Vertex Shader: Spiral/Twist")
            
            elif event.key == pygame.K_9:
                currVertexShader = pulse_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Vertex Shader: Pulse/Heartbeat")
            
            elif event.key == pygame.K_0:
                currVertexShader = glitch_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Vertex Shader: Glitch/Displacement")
            
            elif event.key == pygame.K_f:
                rend.ToggleFilledMode()
                print("Wireframe mode:", "ON" if not rend.filledMode else "OFF")
            
            elif event.key == pygame.K_SPACE:
                autoRotate = not autoRotate
                print("Auto-rotate:", "ON" if autoRotate else "OFF")
            
            elif event.key == pygame.K_ESCAPE:
                isRunning = False

    deltaTime = clock.tick(60) / 1000
    elapsedTime += deltaTime
    
    # Handle Z/X keys for value control
    if keys[K_z]:
        value = max(0.0, value - 1.0 * deltaTime)
    if keys[K_x]:
        value = min(2.0, value + 1.0 * deltaTime)
    
    # Camera rotation with mouse
    if pygame.mouse.get_pressed()[0]:  # Left click
        camAngle -= mouseVel[0] * deltaTime * 100
    if pygame.mouse.get_pressed()[2]:  # Right click
        camAngle += mouseVel[0] * deltaTime * 100
    
    # Auto-rotate
    if autoRotate:
        camAngle += deltaTime * 30
    
    # Update camera position (orbit around model)
    if len(rend.scene) > 0:
        # Órbita alrededor del modelo
        distance = 5.0  # Distancia consistente con posición inicial
        rend.camera.position.x = sin(radians(camAngle)) * distance
        rend.camera.position.y = 1.0
        rend.camera.position.z = cos(radians(camAngle)) * distance
        
        # Calcular viewMatrix directamente sin usar LookAt
        rend.camera.viewMatrix = glm.lookAt(
            rend.camera.position, 
            rend.scene[0].position, 
            glm.vec3(0, 1, 0)
        )
        
       
    # Pass time and value to renderer
    rend.elapsedTime = elapsedTime
    rend.value = value

    rend.Render()
    
    # Asegurar que todo el rendering se complete
    from OpenGL.GL import glFinish
    glFinish()
    
    pygame.display.flip()
    clock.tick(60)  # Limitar a 60 FPS

pygame.quit()
