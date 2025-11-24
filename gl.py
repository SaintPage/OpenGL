import glm  # pip install PyGLM
import numbers
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from camera import Camera
from skybox import Skybox

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()


        glClearColor(0.5, 0.7, 0.9, 1.0)  # Fondo azul cielo

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0,0, self.width, self.height)
        glDisable(GL_CULL_FACE)  # Asegurar que no se eliminen caras

        self.camera = Camera(self.width, self.height)
        self.scene = []
        self.activeShader = None
        self.defaultVertexShaderSource = None
        self.defaultFragmentShaderSource = None
        self.shaderCache = {}
        
        # Shader uniforms
        self.elapsedTime = 0.0
        self.value = 0.5
        
        # Lighting
        self.pointLight = glm.vec3(0, 0, 0)
        self.ambientLight = 0.2
        
        # Skybox
        self.skybox = None
        
        # Filled mode - Iniciar con modelo sólido
        self.filledMode = False
        self.ToggleFilledMode()
        
    
    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera
        
        
    def ToggleFilledMode(self):
        self.filledMode = not self.filledMode
        if self.filledMode:
            glDisable(GL_CULL_FACE)  # Desactivar culling para ver todas las caras
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
    
    def get_program(self, vertexSource, fragmentSource):
        if vertexSource is None or fragmentSource is None:
            return None

        key = (vertexSource, fragmentSource)
        program = self.shaderCache.get(key)
        if program is None:
            program = compileProgram(
                compileShader(vertexSource, GL_VERTEX_SHADER),
                compileShader(fragmentSource, GL_FRAGMENT_SHADER)
            )
            self.shaderCache[key] = program
        return program


    def SetShaders(self, vertexShader, fragmentShader):
        self.defaultVertexShaderSource = vertexShader
        self.defaultFragmentShaderSource = fragmentShader
        self.activeShader = self.get_program(vertexShader, fragmentShader)
    

        

    def Render(self):
        # Limpiar UNA SOLA VEZ al inicio
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Render skybox primero con depth en modo fondo
        if self.skybox is not None:
            glDepthFunc(GL_LEQUAL)
            glDepthMask(GL_FALSE)
            self.skybox.Render()
            glDepthMask(GL_TRUE)
            glDepthFunc(GL_LESS)
        
        # NO llamar camera.Update() - la viewMatrix ya está configurada en el loop principal

        for obj in self.scene:
            if not getattr(obj, "visible", True):
                continue

            vertexSource = getattr(obj, "vertexShaderSource", None) or self.defaultVertexShaderSource
            fragmentSource = getattr(obj, "fragmentShaderSource", None) or self.defaultFragmentShaderSource

            program = self.get_program(vertexSource, fragmentSource)
            if program is None:
                continue

            glUseProgram(program)

            timeScale = getattr(obj, "timeScale", 1.0)
            shaderValue = getattr(obj, "shaderValue", None)
            timeValue = self.elapsedTime * timeScale
            valueToUse = shaderValue if shaderValue is not None else self.value

            timeLocation = glGetUniformLocation(program, "time")
            if timeLocation != -1:
                glUniform1f(timeLocation, timeValue)

            valueLocation = glGetUniformLocation(program, "value")
            if valueLocation != -1:
                glUniform1f(valueLocation, valueToUse)

            viewLocation = glGetUniformLocation(program, "viewMatrix")
            if viewLocation != -1:
                glUniformMatrix4fv(viewLocation, 1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix))

            projLocation = glGetUniformLocation(program, "projectionMatrix")
            if projLocation != -1:
                glUniformMatrix4fv(projLocation, 1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix))

            pointLightValue = getattr(obj, "pointLightOverride", None)
            lightLocation = glGetUniformLocation(program, "pointLight")
            if lightLocation != -1:
                lightVec = pointLightValue if pointLightValue is not None else self.pointLight
                glUniform3fv(lightLocation, 1, glm.value_ptr(lightVec))

            ambientOverride = getattr(obj, "ambientOverride", None)
            ambientLocation = glGetUniformLocation(program, "ambientLight")
            if ambientLocation != -1:
                ambientValue = ambientOverride if ambientOverride is not None else self.ambientLight
                glUniform1f(ambientLocation, ambientValue)

            texLocation = glGetUniformLocation(program, "tex0")
            if texLocation != -1:
                glUniform1i(texLocation, 0)

            for uniformName, uniformValue in getattr(obj, "uniformOverrides", {}).items():
                location = glGetUniformLocation(program, uniformName)
                if location == -1:
                    continue

                if isinstance(uniformValue, numbers.Number):
                    glUniform1f(location, float(uniformValue))
                elif isinstance(uniformValue, (tuple, list)):
                    length = len(uniformValue)
                    if length == 2:
                        glUniform2f(location, *uniformValue)
                    elif length == 3:
                        glUniform3f(location, *uniformValue)
                    elif length == 4:
                        glUniform4f(location, *uniformValue)

            modelMatrix = obj.GetModelMatrix()
            modelLocation = glGetUniformLocation(program, "modelMatrix")
            if modelLocation != -1:
                glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm.value_ptr(modelMatrix))

            obj.Render()
