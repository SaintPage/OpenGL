import glm  # pip install PyGLM
from OpenGL.GL import *
from numpy import array, float32
import ctypes


class Buffer(object):
    def __init__(self, data):
        self.data = data

        # Vertex Buffer
        self.vertexBuffer = array(self.data, dtype = float32)

        # Vertex Buffer Object
        self.VBO = glGenBuffers(1)

        # Vertex Array Object
        self.VAO = glGenVertexArrays(1)

    def Render(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindVertexArray(self.VAO)

        # Mandar la informacion de vertices
        glBufferData(GL_ARRAY_BUFFER,               # Buffer ID
                     self.vertexBuffer.nbytes,      # Buffer size in bytes
                     self.vertexBuffer,             # Buffer data
                     GL_STATIC_DRAW)                # Usage

        # Atributos

        # Atributo de posiciones
        glVertexAttribPointer(0,                    # Attribute Number
                              3,                    # Size
                              GL_FLOAT,             # Type
                              GL_FALSE,             # Is it normalized?
                              4 * 3,                # Stride
                              ctypes.c_void_p(0))   # Offset
        
        glEnableVertexAttribArray(0)

        glDrawArrays(GL_TRIANGLES, 0, int(len(self.vertexBuffer)/3))    

