from Engine_code.Eng import APP
import laspy
import numpy as np
from os import listdir
import scipy
import open3d as o3d


#user defined stuff

#folder (within Datasets)
folder = "Roman Fort"



#----------------------------------FUNCTION DEFINITION START----------------------------------#

#reads out 3 arrays of x,y,z coordinates
def read_data(folder):
    paths = [f for f in listdir(f'Datasets/{folder}') if f.endswith(".laz")]
    laslist = [laspy.read(f'Datasets/{folder}/{path}') for path in paths]

    x = laslist[0].X
    y = laslist[0].Y
    z = laslist[0].Z

    for las in laslist[1:]:
        x = np.append(x,las.X + (1_000 * (las.header.x_offset - laslist[0].header.x_offset)))
        y = np.append(y,las.Y + (1_000 * (las.header.y_offset - laslist[0].header.y_offset)))
        z = np.append(z,las.Z + (1_000 * (las.header.z_offset - laslist[0].header.z_offset)))
    return x,y,z

def frame_funtion():
    global v
    
    if "q" in app.keys_being_held:
        print("alpha",app.alpha)
        print("beta",app.beta)
        app.acknowledge_key_press("q")
        
    if "-" in app.keys_being_held:
        app.scale -= 1
        app.shader.set_int("scale",app.scale)

    elif "=" in app.keys_being_held:
        app.scale += 1
        app.shader.set_int("scale",app.scale)

    if "[" in app.keys_being_held:
        app.alpha -= 0.1
        app.shader.set_float("alpha",app.alpha)

    elif "]" in app.keys_being_held:
        app.alpha +=0.1
        app.shader.set_float("alpha",app.alpha)

    if ";" in app.keys_being_held:
        app.beta -= 0.1
        app.shader.set_float("beta",app.beta)

    elif "'" in app.keys_being_held:
        app.beta +=0.1
        app.shader.set_float("beta",app.beta)
        
    if "1" in app.keys_being_held:
        app.c_ID = max(0,app.c_ID -1)
        app.shader.set_int("c_ID",app.c_ID)
        app.acknowledge_key_press("1")

    elif "2" in app.keys_being_held:
        app.c_ID =  min(6,app.c_ID +1)
        app.shader.set_int("c_ID",app.c_ID)
        app.acknowledge_key_press("2")


    if any([x in app.keys_being_held for x in ["a","d","w","s"]]):
        v *= 1.1
        v = min(v,5)
    else:
       v /= 2
       v = max(v,0.05) 
   
    app.camera.do_movement(v)
    app.camera.process_mouse_movement(0.25)
    
  
#----------------------------------FUNCTION DEFINITION END------------------------------------#          

x,y,z = read_data(folder)#,red,green,blue = read_data(folder)

xyz = np.dstack([x,y,z])[0]

with open(f'Datasets/{folder}/Inclusion_data.txt',"r") as f:
    indexes = np.array([int(x) for x in f.read().split("|")],dtype="int32")
with open(f'Datasets/{folder}/Point_data.txt',"r") as f:
    data = np.array([[int(y) for y in x.split(",")] for x in f.read().split("|")],dtype="int32")



print(data[200:230])
xyz = xyz[indexes]

#2000 = 0.955
#1500 = 0.925
#3000 = 0.98

v = 0


app = APP(1280,720)
app.camera.free_look = True
app.cursor(False)

app.set_clear_colour([0.12,0.14,0.11,0])
app.start("data",xyz/1000,data = data,frame_function=frame_funtion)