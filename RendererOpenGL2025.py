import pygame
import pygame.display
from pygame.locals import *
from math import sin, cos, radians
from pathlib import Path
from OpenGL.GL import glGetError, glFinish, GL_NO_ERROR

import glm

from gl import Renderer
from model import Model
from vertexShader import *
from fragmentShader import *

width = 960
height = 540

deltaTime = 0.0

BASE_PATH = Path(__file__).resolve().parent


def resource_path(*parts):
    return str(BASE_PATH.joinpath(*parts))


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

pygame.init()



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

orbitDistance = 5.0  # Distancia radial de la cámara respecto al centro
camAngle = 0.0
camElevation = 15.0
autoRotate = False

models = []
focusable_models = []
focusModelIndex = 0
hotkey_to_focus_index = {}

# Free camera mode
freeCameraMode = False
freeCamPosition = glm.vec3(0, 2, 8)
freeCamYaw = -90.0  # Mirando hacia -Z
freeCamPitch = 0.0
freeCamFront = glm.vec3(0, 0, -1)
freeCamUp = glm.vec3(0, 1, 0)
freeCamRight = glm.vec3(1, 0, 0)

MOUSE_ORBIT_SPEED = 90.0
MOUSE_ELEVATION_SPEED = 75.0
KEYBOARD_ORBIT_SPEED = 60.0
KEYBOARD_ELEVATION_SPEED = 45.0
ZOOM_SPEED = 4.0
MOUSE_ZOOM_STEP = 0.5
FREE_CAM_MOVE_SPEED = 5.0
FREE_CAM_MOUSE_SENSITIVITY = 0.1

rend.SetShaders(currVertexShader, currFragmentShader)


def current_model():
    if not focusable_models:
        return None
    return focusable_models[focusModelIndex]


def update_camera_transform():
    global freeCamFront, freeCamRight, freeCamUp
    
    if freeCameraMode:
        # Free camera mode - FPS style
        front = glm.vec3(
            cos(radians(freeCamYaw)) * cos(radians(freeCamPitch)),
            sin(radians(freeCamPitch)),
            sin(radians(freeCamYaw)) * cos(radians(freeCamPitch))
        )
        freeCamFront = glm.normalize(front)
        freeCamRight = glm.normalize(glm.cross(freeCamFront, glm.vec3(0, 1, 0)))
        freeCamUp = glm.normalize(glm.cross(freeCamRight, freeCamFront))
        
        rend.camera.position = freeCamPosition
        rend.camera.viewMatrix = glm.lookAt(
            freeCamPosition,
            freeCamPosition + freeCamFront,
            freeCamUp
        )
    else:
        # Orbit mode - seguir modelo activo
        active = current_model()
        if active is None:
            return

        target = active.position + glm.vec3(0, active.focusOffset, 0)
        azimuth_rad = radians(camAngle)
        elevation_rad = radians(camElevation)
        horizontal_radius = orbitDistance * cos(elevation_rad)

        rend.camera.position = glm.vec3(
            target.x + sin(azimuth_rad) * horizontal_radius,
            target.y + sin(elevation_rad) * orbitDistance,
            target.z + cos(azimuth_rad) * horizontal_radius
        )

        rend.camera.viewMatrix = glm.lookAt(
            rend.camera.position,
            target,
            glm.vec3(0, 1, 0)
        )


def set_focus_model(index, reset_camera=True):
    global focusModelIndex, orbitDistance, camElevation
    if not focusable_models:
        return

    focusModelIndex = index % len(focusable_models)
    active = focusable_models[focusModelIndex]

    if reset_camera:
        min_zoom, max_zoom = active.zoomLimits
        orbitDistance = clamp(active.defaultOrbitDistance, min_zoom, max_zoom)
        min_elev, max_elev = active.elevationLimits
        camElevation = clamp(active.defaultElevation, min_elev, max_elev)

    print(f"Focus en: {active.name}")
    update_camera_transform()


def load_model(config):
    model = Model(config["path"])
    model.name = config.get("name", Path(config["path"]).stem)

    for texture_path in config.get("textures", []):
        try:
            model.AddTexture(texture_path)
        except Exception as texture_error:
            print(f"⚠ No se pudo cargar la textura '{texture_path}': {texture_error}")

    if not model.textures:
        fallback_color = config.get("fallbackColor", (255, 255, 255, 255))
        model.AddSolidColorTexture(fallback_color)
        print("  → Se está usando una textura de color sólido de respaldo.")

    model.position = config.get("position", glm.vec3(0, 0, 0))
    model.rotation = config.get("rotation", glm.vec3(0, 0, 0))
    model.scale = config.get("scale", glm.vec3(1, 1, 1))
    model.focusOffset = config.get("focusOffset", model.focusOffset)
    model.defaultOrbitDistance = config.get("defaultOrbitDistance", model.defaultOrbitDistance)
    model.zoomLimits = config.get("zoomLimits", model.zoomLimits)
    model.defaultElevation = config.get("defaultElevation", model.defaultElevation)
    model.elevationLimits = config.get("elevationLimits", model.elevationLimits)
    model.visible = config.get("visible", True)
    model.vertexShaderSource = config.get("vertexShader", currVertexShader)
    model.fragmentShaderSource = config.get("fragmentShader", currFragmentShader)
    model.shaderValue = config.get("shaderValue", model.shaderValue)
    model.timeScale = config.get("timeScale", model.timeScale)
    model.uniformOverrides = config.get("uniformOverrides", {})
    model.pointLightOverride = config.get("pointLight", model.pointLightOverride)
    model.ambientOverride = config.get("ambientLight", model.ambientOverride)

    return model


skyboxTextures = [
    resource_path("skybox", "right.jpg"),
    resource_path("skybox", "left.jpg"),
    resource_path("skybox", "top.jpg"),
    resource_path("skybox", "bottom.jpg"),
    resource_path("skybox", "front.jpg"),
    resource_path("skybox", "back.jpg"),
]
rend.CreateSkybox(skyboxTextures)
print("✓ Skybox cargado exitosamente!")

MODEL_CONFIGS = [
    {
        "name": "Base Floor",
        "path": resource_path("models", "floor.obj"),
        "fallbackColor": (96, 93, 90, 255),
        "position": glm.vec3(0.0, -0.75, 0.0),
        "rotation": glm.vec3(0, 0, 0),
        "scale": glm.vec3(9.0, 0.05, 9.0),
        "focusOffset": -0.5,
        "defaultOrbitDistance": 7.0,
        "zoomLimits": (3.0, 12.0),
        "defaultElevation": 20.0,
        "elevationLimits": (-5.0, 50.0),
        "focusTarget": False,
        "vertexShader": vertex_shader,
        "fragmentShader": fragment_shader,
        "ambientLight": 0.6,
    },
    {
        "name": "Porsche 911 GT2",
        "path": resource_path("models", "Porsche_911_GT2.obj"),
        "textures": [resource_path("models", "car", "0000.BMP")],
        "position": glm.vec3(2.6, -0.25, 1.1),
        "rotation": glm.vec3(0, -90, 0),
        "scale": glm.vec3(1.0, 1.0, 1.0),
        "focusOffset": 0.3,
        "defaultOrbitDistance": 6.0,
        "zoomLimits": (2.5, 10.0),
        "defaultElevation": 14.0,
        "elevationLimits": (-5.0, 40.0),
        "vertexShader": vertex_shader,
        "fragmentShader": rimlight_shader,
        "uniformOverrides": {"rimColor": (0.8, 0.55, 0.25)},
        "focusKey": pygame.K_F1,
    },
    {
        "name": "Iron Man Helmet",
        "path": resource_path("models", "Iron man", "ironman helmet", "obj", "helmet.obj"),
        "textures": [
            resource_path(
                "models",
                "Iron man",
                "ironman helmet",
                "Ironman_helmet",
                "sourceimages",
                "IRONMAN_FRONT.jpg",
            )
        ],
        "position": glm.vec3(1.4, 0.1, -1.8),
        "rotation": glm.vec3(0, 140, 0),
        "scale": glm.vec3(0.85, 0.85, 0.85),
        "focusOffset": 0.35,
        "defaultOrbitDistance": 5.5,
        "zoomLimits": (2.5, 9.0),
        "defaultElevation": 12.0,
        "elevationLimits": (-10.0, 45.0),
        "fallbackColor": (210, 40, 30, 255),
        "vertexShader": pulse_shader,
        "fragmentShader": hologram_shader,
        "shaderValue": 0.8,
        "timeScale": 1.0,
        "focusKey": pygame.K_F2,
    },
    {
        "name": "Penguin",
        "path": resource_path("models", "Penguin", "PenguinBaseMesh.obj"),
        "textures": [resource_path("models", "Penguin", "Penguin Diffuse Color.png")],
        "position": glm.vec3(-1.9, -0.42, -1.2),
        "rotation": glm.vec3(0, 150, 0),
        "scale": glm.vec3(1.2, 1.2, 1.2),
        "focusOffset": 0.6,
        "defaultOrbitDistance": 4.5,
        "zoomLimits": (2.0, 9.0),
        "defaultElevation": 18.0,
        "elevationLimits": (-10.0, 55.0),
        "vertexShader": vertex_shader,
        "fragmentShader": toon_shader,
        "focusKey": pygame.K_F3,
    },
    {
        "name": "Blood Dragon",
        "path": resource_path("models", "Dragon", "blooddragon", "blooddragon.obj"),
        "fallbackColor": (150, 38, 30, 255),
        "position": glm.vec3(-3.2, -0.1, 2.0),
        "rotation": glm.vec3(0, 130, 0),
        "scale": glm.vec3(1.4, 1.4, 1.4),
        "focusOffset": 0.8,
        "defaultOrbitDistance": 6.5,
        "zoomLimits": (3.0, 12.0),
        "defaultElevation": 20.0,
        "elevationLimits": (0.0, 55.0),
        "vertexShader": spiral_shader,
        "fragmentShader": plasma_shader,
        "shaderValue": 0.9,
        "timeScale": 0.65,
        "focusKey": pygame.K_F4,
    },
    {
        "name": "Iron Man",
        "path": resource_path("models", "IRONMAN", "IronMan", "IronMan.obj"),
        "fallbackColor": (200, 45, 28, 255),
        "position": glm.vec3(0.1, -0.45, -2.6),
        "rotation": glm.vec3(0, 180, 0),
        "scale": glm.vec3(1.2, 1.2, 1.2),
        "focusOffset": 1.1,
        "defaultOrbitDistance": 7.5,
        "zoomLimits": (3.5, 13.0),
        "defaultElevation": 16.0,
        "elevationLimits": (-5.0, 55.0),
        "vertexShader": glitch_shader,
        "fragmentShader": matrix_shader,
        "shaderValue": 0.6,
        "focusKey": pygame.K_F5,
    },
    {
        "name": "Moon",
        "path": resource_path("models", "Moon", "Moon.obj"),
        "textures": [resource_path("models", "Moon", "Moon.jpg")],
        "position": glm.vec3(0.0, 3.2, 0.0),
        "rotation": glm.vec3(0, 45, 0),
        "scale": glm.vec3(0.9, 0.9, 0.9),
        "focusOffset": 0.0,
        "defaultOrbitDistance": 8.0,
        "zoomLimits": (4.0, 14.0),
        "defaultElevation": 30.0,
        "elevationLimits": (10.0, 70.0),
        "vertexShader": vertex_shader,
        "fragmentShader": night_glow_shader,
        "shaderValue": 1.0,
        "timeScale": 0.8,
        "focusKey": pygame.K_F6,
    },
]

focus_instructions = []

for config in MODEL_CONFIGS:
    try:
        model = load_model(config)
        models.append(model)
        rend.scene.append(model)
        print(f"✓ {model.name} cargado exitosamente!")
        print(f"  Triángulos del modelo: {model.vertexCount // 3}")

        if config.get("focusTarget", True):
            focusable_models.append(model)
            focus_idx = len(focusable_models) - 1
            focus_key = config.get("focusKey")
            if focus_key is not None:
                hotkey_to_focus_index[focus_key] = focus_idx
                focus_instructions.append((focus_key, model.name))
    except Exception as error:
        print(f"⚠ Error al cargar {config.get('name', 'modelo')}: {error}")

if focusable_models:
    set_focus_model(0)
else:
    print("⚠ No hay modelos enfocados. Revisa las configuraciones de focusTarget.")

pygame.mouse.get_rel()  # Reset relative mouse movement accumulator

# Time and value uniforms for shaders
elapsedTime = 0.0
value = 0.5

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
print("\nMODELOS:")
print("  TAB / Shift+TAB - Modelo siguiente / anterior")
if focus_instructions:
    mapped_keys = ", ".join(f"{pygame.key.name(key).upper()} -> {name}" for key, name in focus_instructions)
    print(f"  Acceso directo: {mapped_keys}")
print("\nCÁMARA:")
print("  C - Alternar entre modo Órbita y modo Libre")
print("\n  Modo Órbita:")
print("    Mouse Izq. (arrastrar) - Órbita horizontal alrededor del modelo")
print("    Mouse Der. (arrastrar) - Ajuste vertical con límite")
print("    Rueda del mouse - Zoom in/out con límite")
print("    A/D o ←/→ - Órbita horizontal por teclado")
print("    W/S o ↑/↓ - Ajuste vertical por teclado")
print("    Q/E - Zoom in/out por teclado")
print("    SPACE - Activar/desactivar auto-rotación")
print("\n  Modo Libre (FPS):")
print("    W/A/S/D - Mover adelante/izquierda/atrás/derecha")
print("    SPACE/SHIFT - Subir/bajar")
print("    Mouse - Mirar alrededor (clic derecho para capturar)")
print("\nOTROS:")
print("  F - Alternar wireframe")
print("  ESC - Salir")
print("  Z/X - Ajustar parámetro 'value' del shader")
print("=======================\n")

while isRunning:

    keys = pygame.key.get_pressed()
    mouseVel = pygame.mouse.get_rel()

    active = current_model()
    if active:
        minZoom, maxZoom = active.zoomLimits
        minElev, maxElev = active.elevationLimits
    else:
        minZoom, maxZoom = (1.5, 25.0)
        minElev, maxElev = (-15.0, 60.0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.MOUSEWHEEL:
            orbitDistance = clamp(orbitDistance - event.y * MOUSE_ZOOM_STEP, minZoom, maxZoom)

        elif event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            if event.key == pygame.K_TAB:
                if focusable_models:
                    step = -1 if mods & pygame.KMOD_SHIFT else 1
                    set_focus_model(focusModelIndex + step)
                    active = current_model()
                    if active:
                        minZoom, maxZoom = active.zoomLimits
                        minElev, maxElev = active.elevationLimits

            elif event.key == pygame.K_ESCAPE:
                isRunning = False

            elif event.key == pygame.K_f:
                rend.ToggleFilledMode()
                print("Wireframe mode:", "ON" if not rend.filledMode else "OFF")

            elif event.key == pygame.K_c:
                freeCameraMode = not freeCameraMode
                if freeCameraMode:
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    print("Modo Cámara: LIBRE (FPS)")
                else:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    print("Modo Cámara: ÓRBITA")
                update_camera_transform()

            elif event.key == pygame.K_SPACE:
                if not freeCameraMode:
                    autoRotate = not autoRotate
                    print("Auto-rotate:", "ON" if autoRotate else "OFF")

            elif event.key in hotkey_to_focus_index:
                target_index = hotkey_to_focus_index[event.key]
                set_focus_model(target_index)
                active = current_model()
                if active:
                    minZoom, maxZoom = active.zoomLimits
                    minElev, maxElev = active.elevationLimits

            # Fragment shader selection
            elif event.key == pygame.K_1:
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

    deltaTime = clock.tick(60) / 1000
    elapsedTime += deltaTime

    # Handle Z/X keys for value control
    if keys[K_z]:
        value = max(0.0, value - 1.0 * deltaTime)
    if keys[K_x]:
        value = min(2.0, value + 1.0 * deltaTime)

    if freeCameraMode:
        # Free camera controls
        velocity = FREE_CAM_MOVE_SPEED * deltaTime
        
        if keys[K_w]:
            freeCamPosition += freeCamFront * velocity
        if keys[K_s]:
            freeCamPosition -= freeCamFront * velocity
        if keys[K_a]:
            freeCamPosition -= freeCamRight * velocity
        if keys[K_d]:
            freeCamPosition += freeCamRight * velocity
        if keys[K_SPACE]:
            freeCamPosition += glm.vec3(0, 1, 0) * velocity
        if keys[K_LSHIFT] or keys[K_RSHIFT]:
            freeCamPosition -= glm.vec3(0, 1, 0) * velocity
        
        # Mouse look (cuando está capturado)
        if pygame.event.get_grab():
            freeCamYaw += mouseVel[0] * FREE_CAM_MOUSE_SENSITIVITY
            freeCamPitch -= mouseVel[1] * FREE_CAM_MOUSE_SENSITIVITY
            freeCamPitch = clamp(freeCamPitch, -89.0, 89.0)
        
        update_camera_transform()
    else:
        # Orbit camera controls - mouse
        if pygame.mouse.get_pressed()[0]:  # Left click for orbit
            camAngle -= mouseVel[0] * MOUSE_ORBIT_SPEED * deltaTime
        if pygame.mouse.get_pressed()[2]:  # Right click for elevation
            camElevation = clamp(camElevation - mouseVel[1] * MOUSE_ELEVATION_SPEED * deltaTime, minElev, maxElev)

        # Orbit camera controls - keyboard
        if keys[K_a] or keys[K_LEFT]:
            camAngle -= KEYBOARD_ORBIT_SPEED * deltaTime
        if keys[K_d] or keys[K_RIGHT]:
            camAngle += KEYBOARD_ORBIT_SPEED * deltaTime

        if keys[K_w] or keys[K_UP]:
            camElevation = clamp(camElevation + KEYBOARD_ELEVATION_SPEED * deltaTime, minElev, maxElev)
        if keys[K_s] or keys[K_DOWN]:
            camElevation = clamp(camElevation - KEYBOARD_ELEVATION_SPEED * deltaTime, minElev, maxElev)

        if keys[K_q]:
            orbitDistance = clamp(orbitDistance - ZOOM_SPEED * deltaTime, minZoom, maxZoom)
        if keys[K_e]:
            orbitDistance = clamp(orbitDistance + ZOOM_SPEED * deltaTime, minZoom, maxZoom)

        # Auto-rotate
        if autoRotate:
            camAngle += deltaTime * 30.0

        camAngle = (camAngle + 360.0) % 360.0

        update_camera_transform()

    # Pass time and value to renderer
    rend.elapsedTime = elapsedTime
    rend.value = value

    rend.Render()

    # Asegurar que todo el rendering se complete
    glFinish()

    err = glGetError()
    if err != GL_NO_ERROR:
        print(f"GL ERROR: {err}")

    pygame.display.flip()

pygame.quit()
