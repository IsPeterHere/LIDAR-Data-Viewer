import glfw
from OpenGL.GL import *
import numpy as np
import pyrr
import ctypes
import time

try:
    from Engine_code.camera import Camera
except:
    from camera import Camera

try:
    from Engine_code.Shader import Shader
except:
    from Shader import Shader

####################################################################################################################################
#################################<<<<<<<<APP CLASS NEXT>>>>>>>>>>>>>################################################################
####################################################################################################################################


class Call_backs:

    def __init__(self):
        glfw.set_window_size_callback(self.window, self.window_resize)

        self.lastX, self.lastY =self.WIDTH / 2, self.HEIGHT / 2
        self.first_mouse = True
        glfw.set_cursor_pos_callback(self.window, self.mouse_look_clb)


        self.keys_being_held = []
        glfw.set_key_callback(self.window, self.key_input_clb)
        
    def create_projection(self):
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, self.WIDTH / self.HEIGHT, 0.1, 200)
        self.shader.set_mat4("projection",projection)

    def window_resize(self,window, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        glViewport(0, 0, width, height)
        self.create_projection()
        
    def mouse_look_clb(self,window, xpos, ypos):
        if self.camera.free_look:
            if self.first_mouse:
                self.lastX = xpos
                self.lastY = ypos
                self.first_mouse = False

            self.camera.xoffset = xpos - self.lastX
            self.camera.yoffset = self.lastY - ypos

            self.lastX = xpos
            self.lastY = ypos

    def key_input_clb(self,window, key, scancode, action, mode):

        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if action == glfw.PRESS:
            self.keys_being_held.append(glfw.get_key_name(key,scancode))

        elif action == glfw.RELEASE:
            key_name = glfw.get_key_name(key,scancode)
            if key_name in self.keys_being_held:
                self.keys_being_held.remove(key_name)

    def acknowledge_key_press(self,key):
        self.keys_being_held.remove(key)

class APP(Call_backs):

    def __init__(self,WIDTH,HEIGHT,frame_rate = 25):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.frame_rate = frame_rate

        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        # creating the window
        self.window = glfw.create_window(self.WIDTH, self.HEIGHT, "Lidar Viewer", None, None)

        # check if window was created
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        self.camera = Camera(self)

        # set window's position
        glfw.set_window_pos(self.window, 400, 200)
        #create call backs
        Call_backs.__init__(self)
        # make the context current
        glfw.make_context_current(self.window)

        #indicate cursor is enabled
        self.is_cursor_enabled = True
         
        glClearColor(0.1,0.2,0.2,1)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


        #-------------USER STUFF-------------------------

        #The scale factor for the size of the points
        self.scale = 45
        
        


    def start(self,MAP_TYPE,points,colours = None,frame_function = None, closing_function = None):
        
        #--------start_up of shader------------
        
        if MAP_TYPE == "Colour":
            vertex,fragment = "LIDAR-Data-Viewer\Engine_code\Shaders\Colour Map\Vertex.txt","LIDAR-Data-Viewer\Engine_code\Shaders\Colour Map\Fragment.txt"
            
        elif MAP_TYPE == "Height":
            vertex,fragment = "LIDAR-Data-Viewer\Engine_code\Shaders\Height Map\Vertex.txt","LIDAR-Data-Viewer\Engine_code\Shaders\Height Map\Fragment.txt"
            
        self.shader = Shader(vertex,fragment)
        self.shader.set_int("scale",self.scale)
        
        #set up initial projection matrix
        self.create_projection()

        #--------Get Points------------
        self.points = points.flatten()
        self.points = self.points.astype(np.float32)

        position = glGetAttribLocation(self.shader.shader, "a_position")      

        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL_STATIC_DRAW)
        
        glVertexAttribPointer(position, 3, GL_FLOAT , GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        

        #--------Map Type specifics------------
        if MAP_TYPE == "Colour":
        
            self.colours = colours.flatten()
            self.colours = self.colours.astype(np.float32)
        
            position = glGetAttribLocation(self.shader.shader, "a_Color")  
       
            VBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, VBO)
            glBufferData(GL_ARRAY_BUFFER, self.colours.nbytes, self.colours, GL_STATIC_DRAW)
        
            glVertexAttribPointer(position, 3, GL_FLOAT , GL_FALSE, 3 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(position)
            
        elif MAP_TYPE == "Height":
            self.max_height = max(points[:][2])
            self.shader.set_float("max",self.max_height)
        



        #--------Bind user functions------------
        
        def f():
            self.camera.do_movement(1)
            self.camera.process_mouse_movement(0.25)

        if frame_function == None:

            self.frame_function = f

        else:
            self.frame_function = frame_function

        if closing_function == None:

            self.closing_function = f

        else:
            self.closing_function = closing_function

        self.main_loop()

    def main_loop(self):
        
        previous_time = time.time()
        
        while not glfw.window_should_close(self.window):
            

            current_time = time.time()
            elapsed_time = current_time - previous_time
            previous_time = current_time

            # Check if we need to wait
            if elapsed_time < 1.0 / self.frame_rate:
                time.sleep((1.0 / self.frame_rate) - elapsed_time)
        


            glfw.poll_events()
            

            self.frame_function()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            view = self.camera.get_view_matrix()
            self.shader.set_mat4("view",view)
            
            #-----drawing
            
            glDrawArrays(GL_POINTS, 0, len(self.points)//3)
            

            #-----

            glfw.swap_buffers(self.window)
            glFlush()

        self.quit()
    
    def cursor(self,cursor_enabled):
        self.is_cursor_enabled = cursor_enabled
        if cursor_enabled:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        else:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def quit(self):
        self.closing_function()
        self.shader.quit()

        quit()

