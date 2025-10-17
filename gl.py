import glm  # pip install PyGLM
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()


        glClearColor(0.2, 0.2, 0.2, 1.0)

        glEnable(GL_DEPTH_TEST)
        glViewport(0,0, self.width, self.height)

        self.scene = []
        self.activeShader = None
    
    def SetShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER),
                                               compileShader(fragmentShader, GL_FRAGMENT_SHADER))
        else:
            self.activeShader = None
    

        

    def Render(self):
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        glUseProgram(self.activeShader)

        for obj in self.scene:
            obj.Render()
