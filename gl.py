import glm  # pip install PyGLM
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
    
    
    def SetShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER),
                                               compileShader(fragmentShader, GL_FRAGMENT_SHADER))
        else:
            self.activeShader = None
    

        

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

        glUseProgram(self.activeShader)
        
        # Pass uniforms to shaders
        if self.activeShader is not None:
            # Time and value
            timeLocation = glGetUniformLocation(self.activeShader, "time")
            if timeLocation != -1:
                glUniform1f(timeLocation, self.elapsedTime)
            
            valueLocation = glGetUniformLocation(self.activeShader, "value")
            if valueLocation != -1:
                glUniform1f(valueLocation, self.value)
            
            # Camera matrices
            glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "viewMatrix"),
                              1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix))
            
            glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "projectionMatrix"),
                              1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix))
            
            # Lighting
            glUniform3fv(glGetUniformLocation(self.activeShader, "pointLight"),
                        1, glm.value_ptr(self.pointLight))
            
            glUniform1f(glGetUniformLocation(self.activeShader, "ambientLight"), self.ambientLight)
            
            # Texture samplers
            glUniform1i(glGetUniformLocation(self.activeShader, "tex0"), 0)

        for obj in self.scene:
            if self.activeShader is not None:
                modelMatrix = obj.GetModelMatrix()
                glUniformMatrix4fv(
                    glGetUniformLocation(self.activeShader, "modelMatrix"),
                    1,
                    GL_FALSE,
                    glm.value_ptr(modelMatrix)
                )
            obj.Render()
