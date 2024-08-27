from re import S
from pyrr import Vector3,Vector4, vector, vector3, matrix44,matrix33, Quaternion
from math import sin, cos, radians
import numpy as np

class Camera:
    def __init__(self,app):
        self.app = app

        self.camera_pos = Vector3([0.0, 4.0, 3.0])
        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.camera_right = Vector3([1.0, 0.0, 0.0])

        self.yaw = -90
        self.pitch = 0

        self.xoffset = 0
        self.yoffset = 0 


        self.left = False
        self.right = False
        self.forward = False
        self.backward = False

        self.free_look = False
        self.looking_at = None

        self.VIEW_MATRIX = matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)


    def get_view_matrix(self):
        return self.VIEW_MATRIX

    def process_mouse_movement(self,mouse_sensitivity):
        self.xoffset *= mouse_sensitivity
        self.yoffset *= mouse_sensitivity

        self.yaw -= self.xoffset
        self.pitch += self.yoffset

        
        if self.pitch > 89:
            self.pitch = 89
        elif self.pitch < -89:
            self.pitch = -89
            
        if self.yaw > 360:
            self.yaw -= 360
        elif self.yaw < -360:
            self.yaw +=360

        self.update_camera_vectors()

    def update_camera_vectors(self):
        
        rot = matrix33.create_from_eulers([radians(self.pitch),radians(self.yaw),0])
        
        up = Vector3([0,0,1])
        self.camera_front = rot @ Vector3([0.0,1.0,0.0])
        self.camera_right = np.cross(self.camera_front,up)

        self.VIEW_MATRIX = matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
        

    def do_movement(self,velocity):
        if "a" in self.app.keys_being_held:
            self.camera_pos -= self.camera_right * velocity
        if "d" in self.app.keys_being_held:
            self.camera_pos += self.camera_right * velocity
        if "w" in self.app.keys_being_held:
            self.camera_pos += self.camera_front * velocity
        if "s" in self.app.keys_being_held:
            self.camera_pos -= self.camera_front * velocity

        self.VIEW_MATRIX = matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front*100, self.camera_up)


    def look_at(self,look_at,look_from,up = None):
        self.camera_pos = Vector3(look_from,dtype=np.float32)
        self.looking_at = Vector3(look_at.copy(),dtype=np.float32)

        if up is None:

            self.camera_front = vector.normalise(self.looking_at-self.camera_pos)
            self.camera_right = vector.normalise(vector3.cross(self.camera_front, Vector3([0, 1.0, 0])))
            self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_front))
        else:
            self.camera_up = Vector3(up,dtype=np.float32)

        self.VIEW_MATRIX = matrix44.create_look_at(self.camera_pos, self.looking_at, self.camera_up)

    def look_towards(self,look_at,look_from,look_at_speed,look_from_speed):

        if self.looking_at is None:
            self.look_at(look_at,look_from)
               
        look_from = Vector3(look_from,dtype=np.float32)
        look_at = Vector3(look_at,dtype=np.float32)

        #look_at
        for x in range(3):
            if look_at_speed > abs(self.looking_at[x]-look_at[x]):
                self.looking_at[x] = look_at[x]
            else:
                if self.looking_at[x] > look_at[x] :
                    self.looking_at[x] -= look_at_speed
                else:
                    self.looking_at[x] += look_at_speed
        
        #look_from
        for x in range(3):
            if look_from_speed > abs(self.camera_pos[x]-look_from[x]):
                self.camera_pos[x] = look_from[x]
            else:
                if self.camera_pos[x] > look_from[x] :
                    self.camera_pos[x] -= look_from_speed
                else:
                    self.camera_pos[x] += look_from_speed

        #up
        self.camera_front = vector.normalise(self.looking_at-self.camera_pos)
        self.camera_right = vector.normalise(vector3.cross(self.camera_front, Vector3([0, 1.0, 0])))
        self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_front))


        
        self.VIEW_MATRIX = matrix44.create_look_at(self.camera_pos, self.looking_at, self.camera_up)