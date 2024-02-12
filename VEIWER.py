from Engine_code.Eng import APP
import laspy
import numpy as np
from os import listdir
from os import path
import pyrr


#user defined stuff

#folder (within Datasets)
folder = "Edinburgh"


#----------------------------------FUNCTION DEFINITION START----------------------------------#

#reads out 3 arrays of x,y,z coordinates
def read_data(folder):
    paths = [f for f in listdir(f'Datasets/{folder}') if f.endswith(".laz")]
    laslist = [laspy.read(f'Datasets/{folder}/{path}') for path in paths]

    x = laslist[0].X
    y = laslist[0].Y
    z = laslist[0].Z

    intensities = np.asarray(laslist[0].intensity,dtype="float64")
    """
    red = np.asarray(laslist[0].scan_angle_rank,dtype="float64")
    green = np.asarray(laslist[0].green,dtype="float64")
    blue = np.asarray(laslist[0].blue,dtype="float64")"""

    for las in laslist[1:]:
        x = np.append(x,las.X + (1_000 * (las.header.x_offset - laslist[0].header.x_offset)))
        y = np.append(y,las.Y + (1_000 * (las.header.y_offset - laslist[0].header.y_offset)))
        z = np.append(z,las.Z + (1_000 * (las.header.z_offset - laslist[0].header.z_offset)))

        intensities = np.append(intensities,np.asarray(las.intensity,dtype="float64"))
        """red = np.append(red,np.asarray(las.scan_angle_rank,dtype="float64"))
        green = np.append(green,np.asarray(las.green,dtype="float64"))
        blue = np.append(blue,np.asarray(las.blue,dtype="float64"))"""

    #print(len(intensities),len(x),len(blue))
    return x,y,z,intensities#,red,green,blue





#----------------------------------FUNCTION DEFINITION END------------------------------------#
def f():
    global v
    
    if "-" in app.keys_being_held:
        app.scale -= 1
        app.shader.set_int("scale",app.scale)
        #app.acknowledge_key_press("-")
    elif "=" in app.keys_being_held:
        app.scale += 1
        app.shader.set_int("scale",app.scale)
        #app.acknowledge_key_press("=")

    if any([x in app.keys_being_held for x in ["a","d","w","s"]]):
        v *= 1.1
        v = min(v,1)
    else:
       v /= 2
       v = max(v,0.05) 
   
    app.camera.do_movement(v)
    app.camera.process_mouse_movement(0.25)
    
            

x,y,z,intensities = read_data(folder)#,red,green,blue = read_data(folder)

xyz = np.dstack([x,y,z])[0]


c = intensities/max(intensities)

colours = np.dstack([c,c,c])[0]


v = 0


app = APP(1280,720)
app.camera.free_look = True
app.cursor(False)

app.start("Colour",xyz/10000,colours,frame_function=f)