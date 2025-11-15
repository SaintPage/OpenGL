from OpenGL.GL import *
from obj import Obj
from buffer import Buffer

import glm

import pygame

class Model(object):
	def __init__(self, filename):
		self.objFile = Obj(filename)

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)

		self.BuildBuffers()

		self.textures = []

		self.visible = True


	def GetModelMatrix(self):

		identity = glm.mat4(1)

		translateMat = glm.translate(identity, self.position)

		pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
		yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
		rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

		rotationMat = pitchMat * yawMat * rollMat

		scaleMat = glm.scale(identity, self.scale)

		return translateMat * rotationMat * scaleMat


	def BuildBuffers(self):

		# First pass: calculate bounding box
		if len(self.objFile.vertices) > 0:
			min_x = min_y = min_z = float('inf')
			max_x = max_y = max_z = float('-inf')
			
			for v in self.objFile.vertices:
				min_x = min(min_x, v[0])
				max_x = max(max_x, v[0])
				min_y = min(min_y, v[1])
				max_y = max(max_y, v[1])
				min_z = min(min_z, v[2])
				max_z = max(max_z, v[2])
			
			# Calculate center and max dimension
			center_x = (min_x + max_x) / 2.0
			center_y = (min_y + max_y) / 2.0
			center_z = (min_z + max_z) / 2.0
			
			size_x = max_x - min_x
			size_y = max_y - min_y
			size_z = max_z - min_z
			max_size = max(size_x, size_y, size_z)
			
			# Normalize vertices to fit in a 2-unit cube centered at origin
			scale = 2.0 / max_size if max_size > 0 else 1.0
			
			# Normalize all vertices
			print(f"Model bounds: X[{min_x:.3f}, {max_x:.3f}] Y[{min_y:.3f}, {max_y:.3f}] Z[{min_z:.3f}, {max_z:.3f}]")
			print(f"Model size: {size_x:.3f} x {size_y:.3f} x {size_z:.3f}")
			print(f"Normalization scale: {scale:.3f}")
			
			for v in self.objFile.vertices:
				v[0] = (v[0] - center_x) * scale
				v[1] = (v[1] - center_y) * scale
				v[2] = (v[2] - center_z) * scale

		# Create VAO
		self.VAO = glGenVertexArrays(1)
		glBindVertexArray(self.VAO)

		positions = []
		texCoords = []
		normals = []

		self.vertexCount = 0

		for face in self.objFile.faces:

			facePositions = []
			faceTexCoords = []
			faceNormals = []

			for i in range(len(face)):
				facePositions.append( self.objFile.vertices [ face[i][0] - 1 ] )
				faceTexCoords.append( self.objFile.texCoords[ face[i][1] - 1 ] )
				faceNormals.append( self.objFile.normals[ face[i][2] - 1 ] )


			for value in facePositions[0]: positions.append(value)
			for value in facePositions[1]: positions.append(value)
			for value in facePositions[2]: positions.append(value)

			for value in faceTexCoords[0]: texCoords.append(value)
			for value in faceTexCoords[1]: texCoords.append(value)
			for value in faceTexCoords[2]: texCoords.append(value)

			for value in faceNormals[0]: normals.append(value)
			for value in faceNormals[1]: normals.append(value)
			for value in faceNormals[2]: normals.append(value)

			self.vertexCount += 3

			if len(face) == 4:
				for value in facePositions[0]: positions.append(value)
				for value in facePositions[2]: positions.append(value)
				for value in facePositions[3]: positions.append(value)

				for value in faceTexCoords[0]: texCoords.append(value)
				for value in faceTexCoords[2]: texCoords.append(value)
				for value in faceTexCoords[3]: texCoords.append(value)

				for value in faceNormals[0]: normals.append(value)
				for value in faceNormals[2]: normals.append(value)
				for value in faceNormals[3]: normals.append(value)

				self.vertexCount += 3


		self.posBuffer = Buffer(positions)
		self.texCoordsBuffer = Buffer(texCoords)
		self.normalsBuffer = Buffer(normals)
		
		# Setup vertex attributes while VAO is bound
		self.posBuffer.Use(0, 3)
		self.texCoordsBuffer.Use(1, 2)
		self.normalsBuffer.Use(2, 3)
		
		# Unbind VAO
		glBindVertexArray(0)


	def AddTexture(self, filename):
		textureSurface = pygame.image.load(filename)
		textureData = pygame.image.tostring(textureSurface, "RGB", True)

		texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D,
					 0,
					 GL_RGB,
					 textureSurface.get_width(),
					 textureSurface.get_height(),
					 0,
					 GL_RGB,
					 GL_UNSIGNED_BYTE,
					 textureData)

		glGenerateMipmap(GL_TEXTURE_2D)

		self.textures.append(texture)


	def Render(self):

		if not self.visible:
			return

		# Bind textures
		for i in range(len(self.textures)):
			glActiveTexture(GL_TEXTURE0 + i)
			glBindTexture(GL_TEXTURE_2D, self.textures[i])

		# Bind VAO (contiene toda la configuración de atributos)
		glBindVertexArray(self.VAO)

		# Draw the model
		glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

		# Unbind VAO
		glBindVertexArray(0)
		
		# Unbind texture
		glBindTexture(GL_TEXTURE_2D, 0)
