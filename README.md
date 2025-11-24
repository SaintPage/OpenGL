# OpenGL Diorama - Proyecto Final

Un visualizador 3D interactivo de modelos OBJ con múltiples shaders, sistema de cámara dual (órbita/libre) y skybox, desarrollado con PyOpenGL y pygame.

## 📋 Características

### Modelos 3D (7 modelos)
- **Base Floor** - Plano de suelo del diorama
- **Porsche 911 GT2** - Auto deportivo con shader rimlight
- **Penguin** - Pingüino con shader toon/cel-shading
- **Blood Dragon** - Dragón con efectos de plasma espiral
- **Iron Man** - Traje completo con shader glitch/matrix
- **Moon** - Luna con efectos de brillo nocturno

### Shaders Personalizados
Cada modelo utiliza una combinación única de vertex y fragment shaders:

**Vertex Shaders:**
- `vertex_shader` - Shader estándar
- `spiral_shader` - Efecto de espiral/torsión
- `pulse_shader` - Efecto de pulsación/latido
- `glitch_shader` - Efecto de glitch/desplazamiento

**Fragment Shaders:**
- `fragment_shader` - Iluminación Phong estándar
- `rimlight_shader` - Iluminación de bordes con color personalizable
- `hologram_shader` - Efecto holográfico con scanlines
- `toon_shader` - Cel-shading con niveles de iluminación discretos
- `plasma_shader` - Efecto de plasma/fuego animado
- `matrix_shader` - Efecto "Matrix" lluvia digital
- `night_glow_shader` - Brillo nocturno con efectos de fresnel

### Sistema de Cámara Dual

#### Modo Órbita (por defecto)
- La cámara orbita alrededor del modelo activo
- Zoom, elevación y rotación con límites por modelo
- Auto-rotación opcional

#### Modo Libre (FPS)
- Movimiento libre estilo first-person
- Control total de posición y orientación
- Ideal para explorar el diorama completo

### Skybox/Cubemap
- Entorno 360° renderizado como fondo
- Configurable con texturas personalizadas

## 🎮 Controles

### Navegación de Modelos
- `TAB` - Siguiente modelo
- `Shift + TAB` - Modelo anterior
- `F1` - Enfocar Porsche 911 GT2
- `F2` - Enfocar Iron Man Helmet
- `F3` - Enfocar Penguin
- `F4` - Enfocar Blood Dragon
- `F5` - Enfocar Iron Man
- `F6` - Enfocar Moon

### Cámara
- `C` - Alternar entre modo Órbita y modo Libre

#### Modo Órbita
- **Mouse Izquierdo (arrastrar)** - Rotar horizontalmente
- **Mouse Derecho (arrastrar)** - Ajustar elevación
- **Rueda del Mouse** - Zoom in/out
- `A` / `D` o `←` / `→` - Rotar horizontalmente (teclado)
- `W` / `S` o `↑` / `↓` - Ajustar elevación (teclado)
- `Q` / `E` - Zoom in/out (teclado)
- `SPACE` - Activar/desactivar auto-rotación

#### Modo Libre (FPS)
- `W` / `A` / `S` / `D` - Mover adelante/izquierda/atrás/derecha
- `SPACE` - Subir
- `Shift` - Bajar
- **Mouse** - Mirar alrededor (el cursor se oculta automáticamente)

### Shaders (aplicar globalmente - para demostración)
**Vertex Shaders:**
- `7` - Default
- `8` - Spiral/Twist
- `9` - Pulse/Heartbeat
- `0` - Glitch/Displacement

**Fragment Shaders:**
- `1` - Default (con iluminación)
- `2` - Hologram
- `3` - Plasma/Fire
- `4` - Matrix Digital Rain

### Otros
- `F` - Alternar modo wireframe/sólido
- `Z` / `X` - Disminuir/aumentar parámetro 'value' de shader
- `ESC` - Salir del programa

## 🚀 Requisitos

```bash
pip install pygame PyOpenGL PyGLM
```

### Dependencias
- Python 3.8+
- pygame 2.0+
- PyOpenGL 3.1+
- PyGLM 2.5+

## 📂 Estructura del Proyecto

```
OpenGL/
├── RendererOpenGL2025.py  # Programa principal
├── gl.py                   # Motor de renderizado
├── model.py                # Cargador y gestor de modelos OBJ
├── obj.py                  # Parser de archivos .obj
├── camera.py               # Sistema de cámara
├── skybox.py               # Gestor de skybox/cubemap
├── buffer.py               # Manejo de VBOs
├── vertexShader.py         # Vertex shaders GLSL
├── fragmentShader.py       # Fragment shaders GLSL
├── models/                 # Modelos 3D y texturas
│   ├── floor.obj
│   ├── Porsche_911_GT2.obj
│   ├── Penguin/
│   ├── Iron man/
│   ├── IRONMAN/
│   ├── Dragon/
│   └── Moon/
└── skybox/                 # Texturas del cubemap
    ├── right.jpg
    ├── left.jpg
    ├── top.jpg
    ├── bottom.jpg
    ├── front.jpg
    └── back.jpg
```

## 🎨 Características Técnicas

### Arquitectura de Shaders por Modelo
- Cada modelo tiene su propia combinación de shaders
- Sistema de caché de programas de shader para eficiencia
- Soporte para uniforms personalizados por modelo
- Control independiente de iluminación y parámetros

### Sistema de Iluminación
- Luz puntual global configurable
- Luz ambiental ajustable
- Overrides de iluminación por modelo
- Soporte para efectos especiales (rim lighting, fresnel, etc.)

### Optimizaciones
- VAOs (Vertex Array Objects) para rendering eficiente
- Cache de programas de shader compilados
- Normalización automática de modelos
- Soporte para índices negativos en archivos OBJ

### Parseo de OBJ Robusto
- Manejo de índices positivos y negativos
- Soporte para caras con datos faltantes (v, v/vt, v//vn, v/vt/vn)
- Conversión automática de quads a triángulos
- Valores por defecto seguros para datos faltantes

## 🎯 Cumplimiento de Requisitos del Proyecto

### Modelos (25 pts)
✅ 7 modelos cargados (35 pts potenciales, máximo 25)
- Cada modelo posicionado estratégicamente en la escena
- Incluye base/suelo del diorama

### Movimiento de Cámara (30 pts)
✅ Tres movimientos del Lab 10 (10 pts)
- Zoom in/out con límites
- Órbita alrededor del modelo
- Desplazamiento vertical con límites

✅ Funciona con mouse y teclado (5 pts)

✅ Cambio de punto de vista entre modelos (15 pts)
- Teclas F1-F6 para acceso directo
- TAB/Shift+TAB para navegación secuencial
- **EXTRA:** Modo cámara libre (FPS) no requerido

### Uso Creativo de Shaders (30 pts)
✅ Combinaciones únicas por modelo:
- Rimlight shader con color personalizado
- Hologram shader con efectos pulsantes
- Toon/cel-shading
- Plasma animado con spiral vertex shader
- Matrix digital rain con glitch shader
- Night glow con efectos fresnel

✅ Input para variar valores de shader (Z/X)
✅ Efectos de deformación (spiral, pulse, glitch)

### Skybox/Cubemap (5 pts)
✅ Implementado y funcional

### Características Extra (25 pts)
✅ Modo de cámara libre (FPS)
✅ Sistema de auto-rotación
✅ Modo wireframe
✅ Sistema de shader por modelo
✅ Overrides de iluminación por modelo
✅ Controles intuitivos y documentados

### Creatividad y Estética (10 pts)
✅ Diorama cohesivo con temática futurista/fantástica
✅ Iluminación y shaders que complementan cada modelo
✅ Distribución espacial equilibrada

## 🐛 Solución de Problemas

### Los modelos no cargan
- Verifica que las rutas de los archivos .obj sean correctas
- Asegúrate de que las texturas existan en las rutas especificadas
- Revisa la consola para mensajes de error específicos

### Rendimiento bajo
- Algunos modelos tienen alta densidad de polígonos
- Considera reducir la resolución de las texturas
- Desactiva el modo wireframe (tecla F)

### El mouse no responde en modo libre
- Asegúrate de estar en modo libre (presiona C)
- Si el cursor está visible, presiona clic derecho para capturarlo
- Presiona C nuevamente para volver a modo órbita

## 👨‍💻 Desarrollo

### Agregar un Nuevo Modelo

1. Coloca el archivo .obj y texturas en `models/`
2. Agrega una nueva configuración en `MODEL_CONFIGS`:

```python
{
    "name": "Mi Modelo",
    "path": resource_path("models", "mi_modelo.obj"),
    "textures": [resource_path("models", "textura.jpg")],
    "position": glm.vec3(x, y, z),
    "rotation": glm.vec3(rx, ry, rz),
    "scale": glm.vec3(sx, sy, sz),
    "vertexShader": vertex_shader,
    "fragmentShader": fragment_shader,
    "focusKey": pygame.K_F7,  # Tecla de acceso directo
}
```

### Cambiar el Skybox

Reemplaza las texturas en `skybox/` o modifica la lista `skyboxTextures`:

```python
skyboxTextures = [
    resource_path("mi_skybox", "right.jpg"),
    resource_path("mi_skybox", "left.jpg"),
    # ...
]
```

## 📝 Notas

- Los shaders personalizados por modelo no se ven afectados por las teclas 0-4, 7-9 (esas son para demostración global)
- El modo libre es útil para screenshots y exploración detallada
- La auto-rotación solo funciona en modo órbita
- Cada modelo tiene sus propios límites de zoom y elevación optimizados

## 🙏 Créditos

**Modelos 3D:**
- Porsche 911 GT2 - (fuente del modelo)
- Iron Man assets - (fuente del modelo)
- Penguin - (fuente del modelo)
- Blood Dragon - (fuente del modelo)
- Moon - (fuente del modelo)

**Desarrollo:**
- Universidad del Valle de Guatemala
- Curso: Gráficas por Computadora
- Proyecto: Diorama OpenGL

## 📄 Licencia

Proyecto académico - Universidad del Valle de Guatemala
