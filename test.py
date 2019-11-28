import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '400,200'

from math import *
from PIL import Image
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import pygame
from pygame.locals import *


vertex_src = """
#version 310 es

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;

uniform mat4 model; //combined translation and rotation
uniform mat4 projection;

out vec3 v_color;
out vec2 v_texture;

void main(){
    gl_Position = projection * model * vec4(a_position, 1.0);
    v_texture = a_texture;
}
"""

fragment_src = """
#version 310 es

precision mediump float;

in vec2 v_texture; 

out vec4 out_color;

uniform sampler2D s_texture;

void main(){
    out_color = texture(s_texture, v_texture);
}
"""

def window_resize(event):
    if event.type == pygame.VIDEORESIZE:
        glViewport(0, 0, event.w, event.h)
        print(event.w, event.h)
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1.0*event.w/event.h, 0.1, 100)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        pygame.display.flip()

def leave(event):
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
        pygame.quit()
        quit()


pygame.init()
pygame.display.set_mode((1080, 720), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)

            #Vertices          #Texture
vertices = [-0.5, -0.5,  0.5,  0.0, 0.0,
             0.5, -0.5,  0.5,  1.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 1.0,

            -0.5, -0.5, -0.5,  0.0, 0.0,
             0.5, -0.5, -0.5,  1.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 1.0,

             0.5, -0.5, -0.5,  0.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 1.0,
             0.5, -0.5,  0.5,  0.0, 1.0,

            -0.5,  0.5, -0.5,  0.0, 0.0,
            -0.5, -0.5, -0.5,  1.0, 0.0,
            -0.5, -0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 1.0,

            -0.5, -0.5, -0.5,  0.0, 0.0,
             0.5, -0.5, -0.5,  1.0, 0.0,
             0.5, -0.5,  0.5,  1.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 1.0,

             0.5,  0.5, -0.5,  0.0, 0.0,
            -0.5,  0.5, -0.5,  1.0, 0.0,
            -0.5,  0.5,  0.5,  1.0, 1.0,
             0.5,  0.5,  0.5,  0.0, 1.0]
            

indices =  [0,  1,  2,  2,  3,  0,
            4,  5,  6,  6,  7,  4,
            8,  9, 10, 10, 11,  8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20]

vertices = np.array(vertices, dtype=np.float32)
indices = np.array(indices, dtype=np.uint32)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# Vertex Buffer Object
VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# Element Buffer Object
EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(12))

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)

# Set texture wrapping parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
# Set texture filtering parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# load image
image = Image.open("./textures/ursa.png")
image = image.transpose(Image.FLIP_TOP_BOTTOM)
image_data = image.convert("RGBA").tobytes()

glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)


glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1080/720, 0.1, 100)
translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, -3]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


# The main aplication loop
while True:
    for event in pygame.event.get():
        window_resize(event)
        leave(event)
    
    # Current time
    ct = pygame.time.get_ticks() / 1000

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rot_x = pyrr.Matrix44.from_x_rotation(0.5 * ct)
    rot_y = pyrr.Matrix44.from_y_rotation(0.5 * ct)

    rotation = pyrr.matrix44.multiply(rot_x, rot_y)
    model = pyrr.matrix44.multiply(rotation, translation)

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    pygame.display.flip()
