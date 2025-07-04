import open3d as o3d
import laspy
import numpy as np
from os import listdir
from os import path
import pyrr

folders = listdir("../Datasets")

def read_data(folder):
    print(folder)

    paths = [f for f in listdir(f'../Datasets/{folder}') if f.endswith(".laz")]
    laslist = [laspy.read(f'../Datasets/{folder}/{path}') for path in paths]

    
    print(list(laslist[0].point_format.dimension_names))
    print()
    """
    x = laslist[0].X
    y = laslist[0].Y
    z = laslist[0].Z

    intensities = []
    red = []
    green = []
    blue = []

    if "intensity" in laslist[0].point_format.dimension_names:
        intensities = np.asarray(laslist[0].intensity,dtype="float64")
    if "red" in laslist[0].point_format.dimension_names:
        red = np.asarray(laslist[0].red,dtype="float64")
        green = np.asarray(laslist[0].green,dtype="float64")
        blue = np.asarray(laslist[0].blue,dtype="float64")

    for las in laslist[1:]:
        x = np.append(x,las.X + (1_000 * (las.header.x_offset - laslist[0].header.x_offset)))
        y = np.append(y,las.Y + (1_000 * (las.header.y_offset - laslist[0].header.y_offset)))
        z = np.append(z,las.Z + (1_000 * (las.header.z_offset - laslist[0].header.z_offset)))

        if "intensity" in las.point_format.dimension_names:
            intensities = np.append(intensities,np.asarray(las.intensity,dtype="float64"))
        if "red" in las.point_format.dimension_names:
            red = np.append(red,np.asarray(las.red,dtype="float64"))
            green = np.append(green,np.asarray(las.green,dtype="float64"))
            blue = np.append(blue,np.asarray(las.blue,dtype="float64"))


    print("intensities:",np.sum(intensities))
    print("red:",np.sum(red))
    print("green:",np.sum(green))
    print("blue:",np.sum(blue))

    print()"""

for i in folders:
    read_data(i)