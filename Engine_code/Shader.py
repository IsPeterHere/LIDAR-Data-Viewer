from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *


class Shader:

    def __init__(self,vertex_file_loc,fragment_file_loc):

        self.shader = self.createShader(vertex_file_loc,fragment_file_loc)
        glUseProgram(self.shader)
        
    def createShader(self, vertexFilePath, fragmentFilePath):

        with open(vertexFilePath,"r") as f:
            vertex_src = f.readlines()

        with open(fragmentFilePath,"r") as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
            )

        return shader

    def set_vec3(self,uniform_name,vec3):
        loc = glGetUniformLocation(self.shader, uniform_name)
        glUniform3fv(loc, 1,vec3)

    def set_mat4(self,uniform_name,mat4):
        loc = glGetUniformLocation(self.shader, uniform_name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, mat4)

    def set_int(self,uniform_name,Int):
        loc = glGetUniformLocation(self.shader, uniform_name)
        glUniform1i(loc, Int)

    def set_float(self,uniform_name,Float):
        loc = glGetUniformLocation(self.shader, uniform_name)
        glUniform1f(loc, Float)


    def quit(self):
        glDeleteProgram(self.shader)