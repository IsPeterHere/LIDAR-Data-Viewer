
from Engine_code.Eng import APP
import laspy
import numpy as np
from os import listdir
from os import path
import pyrr
import pye57


#user defined stuff

#folder (within Datasets)
folder = "Leica/Church"
colour_map = "colour"

#----------------------------------FUNCTION DEFINITION START----------------------------------#

#reads out 3 arrays of x,y,z coordinates
def read_data_las(folder):
    paths = [f for f in listdir(f'../Datasets/{folder}') if f.endswith(".laz") or f.endswith(".las")]
    laslist = [laspy.read(f'../Datasets/{folder}/{path}') for path in paths]

    x = laslist[0].X
    y = laslist[0].Y
    z = laslist[0].Z

    intensities = None
    red = green = blue = None
    
    if do_intensity := ((colour_map == "intensity" or colour_map == "mix") and "intensity" in laslist[0].point_format.dimension_names and np.sum(laslist[0].intensity[:1000]) != 0):
        intensities = np.asarray(laslist[0].intensity)

    print(list(laslist[0].point_format.dimension_names))
    print(laslist[0].header.version)

    if do_colour := (colour_map == "colour" and "red" in laslist[0].point_format.dimension_names):
        red = np.asarray(laslist[0].red)
        green = np.asarray(laslist[0].green)
        blue = np.asarray(laslist[0].blue)

    for las in laslist[1:]:
        x = np.append(x,las.X + (1_000 * (las.header.x_offset - laslist[0].header.x_offset)))
        y = np.append(y,las.Y + (1_000 * (las.header.y_offset - laslist[0].header.y_offset)))
        z = np.append(z,las.Z + (1_000 * (las.header.z_offset - laslist[0].header.z_offset)))
        
        if do_intensity:
            intensities = np.append(intensities,las.intensity)

        if do_colour:
            red = np.append(red,np.asarray(las.red))
            green = np.append(green,np.asarray(las.green))
            blue = np.append(blue,np.asarray(las.blue))

    #print(len(intensities),len(x),len(blue))
    return x,y,z,intensities,red,green,blue


def read_data_e57(folder):
    paths = [f for f in listdir(f'../Datasets/{folder}') if f.endswith(".e57")]
    e57 = [pye57.E57(f'../Datasets/{folder}/{path}') for path in paths]
    data = e57[0].read_scan(index=0, ignore_missing_fields=True, colors=True, intensity=True)

    header = e57[0].get_header(0)
    print(header.point_fields)

    intensities = None
    red = green = blue = None

    x = data["cartesianX"][:-1000000]
    y = data["cartesianY"][:-1000000]
    z = data["cartesianZ"][:-1000000]
    
    if do_intensity := ((colour_map == "intensity" or colour_map == "mix") and "intensity" in header.point_fields and np.sum(data["intensity"][:1000]) != 0):
        intensities = np.asarray(data["intensity"])[:-1000000]

    if do_colour := (colour_map == "colour" and "colorRed" in header.point_fields and np.sum(data["colorRed"][:1000]) != 0):
        red = np.asarray(data["colorRed"])[:-1000000]
        green = np.asarray(data["colorGreen"])[:-1000000]
        blue = np.asarray(data["colorBlue"])[:-1000000]
    

    for file in e57[1:]:
        data = file.read_scan(index=0, ignore_missing_fields=True, colors=True, intensity=True)

        x = np.append(x, data["cartesianX"])
        y = np.append(y, data["cartesianY"])
        z = np.append(z, data["cartesianZ"])
        
        if do_intensity:
            intensities = np.append(intensities, np.asarray(data["intensity"]))

        if do_colour:
            red = np.append(red, np.asarray(data["colorRed"]))
            green = np.append(green, np.asarray(data["colorGreen"]))
            blue = np.append(blue, np.asarray(data["colorBlue"]))

    return x,y,z,intensities,red,green,blue





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
    
            

x,y,z,intensities,red,green,blue = read_data_e57(folder)#,red,green,blue = read_data(folder)

xyz = np.dstack([x,y,z])[0]


#c = intensities/max(intensities)
r = red/max(red)
g = green/max(green)
b = blue/max(blue)

colours = np.dstack([r,g,b])[0]


v = 0


app = APP(1280,720)
app.camera.free_look = True
app.cursor(False)

app.start("Colour",xyz,colours,frame_function=f)
