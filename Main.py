import open3d as o3d
import laspy
import numpy as np
from os import listdir
from os import path
import pyrr


#user defined stuff

#folder (within Datasets)
folder = "HareHope"

#colour_map picks between no colour, "normal" map, "intensity"(if included in laz file)
colour_map = ""

#dev stuff
display_logs = True


#----------------------------------FUNCTION DEFINITION START----------------------------------#

#returns bounding data within Bounds.txt file in folder, if file exists
def read_bounds(folder):
    if path.exists(f"Datasets/{folder}/Bounds.txt"):
        if display_logs:
            print("Bounds.txt Found")

        with open(f"Datasets/{folder}/Bounds.txt") as f:
            data = f.read().splitlines()
            data = [x for x in data if "#" not in x and len(x) > 0]
            data = [x.split(";")[1] for x in data]
        
        
        a = data[0].split(",")
        bs = [[float(a[0]),float(a[1])],[float(a[2]),float(a[3])]]

        a = data[1].split(",")
        r = [float(a[0]),float(a[1]),float(a[2])]
        amax = int(data[2])
        amin = int(data[3])

        del a

    else:
        if display_logs:
            print("Bounds.txt Not Found")

        bs = [[0,0],[1,1]] 
        r = [0,0,0] 
        amax = 1_000_000
        amin = -1_000_000
    
    bounds = bs,r,amax,amin

    if display_logs:
        width = 12
        disp = lambda x,y:print(x+" "*(width-len(x))+str(y))
        strings = ["Bounds: ","Rotation: ", "Max Height: ", "Min Height: "]

        disp(strings[0],bs)
        disp(strings[1],r)
        disp(strings[2],amax)
        disp(strings[3],amin)

    return bounds


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


def apply_bounds(x,y,z,bounds):
    bs,r,amax,amin = bounds

    x = x - min(x)
    y = y - min(y)

    sizex = max(x)-min(x)
    sizey = max(y)-min(y)

    box_x = bs[0][1]*sizex
    box_a = bs[1][1]*sizex
    
    box_y = bs[1][1]*sizey
    box_b = bs[0][0]*sizey

    centre = [box_a+((box_x-box_a)/2),box_b+((box_y-box_b)/2),0]

    q = pyrr.Quaternion.from_eulers(np.radians(r))
    rotation = pyrr.matrix33.create_from_quaternion(q)

    print(box_x,box_a,box_y,box_b)
    print(centre)

    box_x -= centre[0]
    box_y -= centre[1]
    box_a -= centre[0]
    box_b -= centre[1]
    
    print("Using Bounds:",str((box_x,box_a)),str((box_y,box_b)))

    box_x = np.sign(box_x)*(int(abs(box_x))+[1 if int(abs(box_x)) != abs(box_x) else 0][0])
    box_y = np.sign(box_y)*(int(abs(box_y))+[1 if int(abs(box_y)) != abs(box_y) else 0][0])
    box_a = np.sign(box_a)*(int(abs(box_a))+[1 if int(abs(box_a)) != abs(box_a) else 0][0])
    box_b = np.sign(box_b)*(int(abs(box_b))+[1 if int(abs(box_b)) != abs(box_b) else 0][0])


    tpl = [box_a,box_y,0]@rotation.T
    tpr = [box_x,box_y,0]@rotation.T
    btr = [box_x,box_b,0]@rotation.T
    btl = [box_a,box_b,0]@rotation.T

    with open("bound.json","w") as f:
        f.write("""
    {{
    "axis_max": {amax},
    "axis_min": {amin},
    "bounding_polygon": [
        {tpl},
        {tpr},
        {btr},
        {btl}
    ],
    "class_name": "SelectionPolygonVolume",
    "orthogonal_axis": "Z",
    "version_major": 1,
    "version_minor": 0
    }}


            """.format(tpl = str(list(tpl)),tpr = str(list(tpr)),btr = str(list(btr)),btl = str(list(btl)),amax = amax,amin = amin ))

    xyz = np.dstack([x,y,z])[0]
    xyz = np.matmul((xyz - centre),rotation.T) 

    return xyz


def create_pointcloud(xyz):
    print("Creating Point cloud with ",len(xyz), "points.")
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)

    return pcd


def crop_pointcloud(pcd):
    vol = o3d.visualization.read_selection_polygon_volume("bound.json")
    selected_pcd = vol.crop_point_cloud(pcd)

    print("Bounding Selected: ",selected_pcd)

    return selected_pcd




def add_colours(pcd,red,green,blue):

    cn = np.dstack([red,green,blue])[0]
    pcd.colors = o3d.utility.Vector3dVector(cn.astype(np.float64))

    print("Colours added: ",pcd.has_colors())


def convert_to_normalmap(pcd):
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=1000, max_nn=10))
    normals = np.asarray(pcd.normals)
    normals = ((normals - normals.min(axis=0)) / (normals.max(axis=0) - normals.min(axis=0)))


    c1 = normals@[0,1,0.2]
    c2 = normals@[1,0,0]
    c3 = normals@[-1/2,-1.73,0]

    e = np.zeros(shape = [len(normals)])
    
    add_colours(pcd,c1,c2,c3)

def add_intensity(pcd,intensities):
    e = np.zeros(shape = [len(intensities)])

    print(sum(intensities))
    c1 = intensities/max(intensities)
    c2 = intensities/max(intensities)
    c3 = intensities/max(intensities)

    add_colours(pcd,c1,c2,c3)


#----------------------------------FUNCTION DEFINITION END------------------------------------#


bounds = read_bounds(folder)
x,y,z,intensities = read_data(folder)#,red,green,blue = read_data(folder)

xyz = apply_bounds(x,y,z,bounds)

pcd = create_pointcloud(xyz)

if colour_map == "normal":
    convert_to_normalmap(pcd)

elif colour_map == "intensity":
    add_intensity(pcd,intensities)

pcd = crop_pointcloud(pcd)


# Display the selected point cloud
o3d.visualization.draw_geometries([pcd])