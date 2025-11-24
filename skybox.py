from numpy import array, float32
import numpy as np
import glm
from OpenGL.GL import * 
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
from math import pi, atan2, asin


skybox_vertex_shader = '''
#version 450 core

layout (location = 0) in vec3 inPosition;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;


out vec3 texCoords;

void main()
{
    texCoords = inPosition;
    mat4 vm = mat4(mat3(viewMatrix));
    gl_Position = projectionMatrix * vm * vec4(inPosition, 1.0);
}

'''


skybox_fragment_shader = '''
#version 450 core

uniform samplerCube skybox;

in vec3 texCoords;

out vec4 fragColor;

void main()
{
    fragColor = texture(skybox, texCoords);
}

'''


def equirectangular_to_cubemap_face(equirect_surface, face_index, face_size):
	"""Convierte una imagen equirectangular a una cara del cubemap"""
	face = pygame.Surface((face_size, face_size))
	pixels = pygame.surfarray.pixels3d(face)
	
	# Obtener los píxeles de la imagen equirectangular
	eq_pixels = pygame.surfarray.array3d(equirect_surface)
	eq_width, eq_height = equirect_surface.get_size()
	
	# Direcciones para cada cara del cubemap
	# 0:+X, 1:-X, 2:+Y, 3:-Y, 4:+Z, 5:-Z
	for y in range(face_size):
		for x in range(face_size):
			# Normalizar coordenadas a [-1, 1]
			u = (2.0 * x / face_size) - 1.0
			v = (2.0 * y / face_size) - 1.0
			
			# Calcular vector 3D según la cara
			if face_index == 0:  # +X (derecha)
				vec = np.array([1.0, -v, -u])
			elif face_index == 1:  # -X (izquierda)
				vec = np.array([-1.0, -v, u])
			elif face_index == 2:  # +Y (arriba)
				vec = np.array([u, 1.0, v])
			elif face_index == 3:  # -Y (abajo)
				vec = np.array([u, -1.0, -v])
			elif face_index == 4:  # +Z (frente)
				vec = np.array([u, -v, 1.0])
			else:  # -Z (atrás)
				vec = np.array([-u, -v, -1.0])
			
			# Normalizar vector
			vec = vec / np.linalg.norm(vec)
			
			# Convertir a coordenadas esféricas
			theta = atan2(vec[0], vec[2])  # ángulo horizontal
			phi = asin(vec[1])  # ángulo vertical
			
			# Mapear a coordenadas UV de la imagen equirectangular
			eq_u = (theta / (2 * pi)) + 0.5
			eq_v = (phi / pi) + 0.5
			
			# Convertir a coordenadas de píxel
			eq_x = int(eq_u * (eq_width - 1))
			eq_y = int(eq_v * (eq_height - 1))
			
			# Copiar el píxel
			pixels[x, y] = eq_pixels[eq_x, eq_y]
	
	del pixels  # Liberar el array
	return face


class Skybox(object):
	def __init__(self, textureList):
		self.cameraRef = None
		self.cubemapTexture = None  # Para environment mapping
		
		skyboxVertices = [-1.0,  1.0, -1.0,
						  -1.0, -1.0, -1.0,
						   1.0, -1.0, -1.0,
						   1.0, -1.0, -1.0,
						   1.0,  1.0, -1.0,
						  -1.0,  1.0, -1.0,
						  
						  -1.0, -1.0,  1.0,
						  -1.0, -1.0, -1.0,
						  -1.0,  1.0, -1.0,
						  -1.0,  1.0, -1.0,
						  -1.0,  1.0,  1.0,
						  -1.0, -1.0,  1.0,
						  
						   1.0, -1.0, -1.0,
						   1.0, -1.0,  1.0,
						   1.0,  1.0,  1.0,
						   1.0,  1.0,  1.0,
						   1.0,  1.0, -1.0,
						   1.0, -1.0, -1.0,
						  
						  -1.0, -1.0,  1.0,
						  -1.0,  1.0,  1.0,
						   1.0,  1.0,  1.0,
						   1.0,  1.0,  1.0,
						   1.0, -1.0,  1.0,
						  -1.0, -1.0,  1.0,
						  
						  -1.0,  1.0, -1.0,
						   1.0,  1.0, -1.0,
						   1.0,  1.0,  1.0,
						   1.0,  1.0,  1.0,
						  -1.0,  1.0,  1.0,
						  -1.0,  1.0, -1.0,
						  
						  -1.0, -1.0, -1.0,
						  -1.0, -1.0,  1.0,
						   1.0, -1.0, -1.0,
						   1.0, -1.0, -1.0,
						  -1.0, -1.0,  1.0,
						   1.0, -1.0,  1.0 ]
		
		self.vertexBuffer = array(skyboxVertices, dtype = float32 )
		self.VBO = glGenBuffers(1)
		
		self.shaders = compileProgram(compileShader(skybox_vertex_shader, GL_VERTEX_SHADER),
									  compileShader(skybox_fragment_shader, GL_FRAGMENT_SHADER) )
		
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
		
		# Si solo hay 1 textura, convertir de equirectangular a cubemap
		if len(textureList) == 1:
			try:
				texture = pygame.image.load(textureList[0])
				texture = texture.convert()  # Convertir a RGB
				
				width = texture.get_width()
				height = texture.get_height()
				print(f"Skybox image size: {width}x{height}")
				
				# Detectar si es equirectangular (ratio ~2:1) o imagen normal
				aspect_ratio = width / height
				is_equirect = abs(aspect_ratio - 2.0) < 0.3
				
				# Tamaño de cada cara del cubemap
				face_size = min(512, width // 4 if is_equirect else min(width, height))
				print(f"Generating cubemap faces at {face_size}x{face_size}")
				
				if is_equirect:
					print("Detected equirectangular format, converting to cubemap...")
					# Convertir cada cara desde formato equirectangular
					for i in range(6):
						face = equirectangular_to_cubemap_face(texture, i, face_size)
						face_data = pygame.image.tostring(face, "RGB", False)
						
						glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
									 0, GL_RGB, face_size, face_size,
									 0, GL_RGB, GL_UNSIGNED_BYTE, face_data)
						print(f"  Face {i} generated")
				else:
					# Usar la misma imagen en todas las caras
					print("Using same image for all faces...")
					if width != face_size or height != face_size:
						texture = pygame.transform.scale(texture, (face_size, face_size))
					
					textureData = pygame.image.tostring(texture, "RGB", False)
					for i in range(6):
						glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
									 0, GL_RGB, face_size, face_size,
									 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)
				
				print(f"✓ Skybox loaded successfully!")
			except Exception as e:
				print(f"Error loading skybox: {e}")
				import traceback
				traceback.print_exc()
		else:
			# Cargar 6 texturas diferentes (modo original)
			for i in range(len(textureList)):
				texture = pygame.image.load(textureList[i])
				textureData = pygame.image.tostring(texture, "RGB", False)
				
				glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
							 0,
							 GL_RGB,
							 texture.get_width(),
							 texture.get_height(),
							 0,
							 GL_RGB,
							 GL_UNSIGNED_BYTE,
							 textureData)
			
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
		
		# Guardar referencia para environment mapping
		self.cubemapTexture = self.texture

	def Render(self):
		if self.shaders == None:
			return
		
		glUseProgram(self.shaders)
		
		if self.cameraRef is not None:
			glUniformMatrix4fv( glGetUniformLocation(self.shaders, "viewMatrix"),
								1, GL_FALSE, glm.value_ptr( self.cameraRef.viewMatrix) )
			
			glUniformMatrix4fv( glGetUniformLocation(self.shaders, "projectionMatrix"),
								1, GL_FALSE, glm.value_ptr( self.cameraRef.projectionMatrix) )
		
		glDepthMask(GL_FALSE)
		
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
		
		glBufferData(GL_ARRAY_BUFFER,
					 self.vertexBuffer.nbytes,
					 self.vertexBuffer,
					 GL_STATIC_DRAW)
		
		glEnableVertexAttribArray(0)
		
		glVertexAttribPointer(0,
							  3,
							  GL_FLOAT,
							  GL_FALSE,
							  4 * 3,
							  ctypes.c_void_p(0) )
		
		
		glDrawArrays(GL_TRIANGLES, 0, 36)
		
		glDisableVertexAttribArray(0)

		glDepthMask(GL_TRUE)
