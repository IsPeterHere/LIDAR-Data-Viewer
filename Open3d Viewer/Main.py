import open3d as o3d
import laspy
import pye57
import numpy as np
from os import listdir
from os import path
import pyrr


#user defined stuff

#folder path" (within Datasets) e.g. "Edinburgh"
folder = "St Kilda Specific"

#colour_map picks between no colour (defaults to height map), "normal" map, "intensity"(if included in laz file), and "colour"
colour_map = ""
normal_radius = 100_000
mx_normal_bodies = 800

#preferred file format (las,e57)
file_preference = "las"

#dev stuff
display_logs = True

#save as file
save_name = ""

#----------------------------------FUNCTION DEFINITION START----------------------------------#

#returns bounding data within Bounds.txt file in folder, if file exists
def read_bounds(folder):
    if path.exists(f"../../Datasets/{folder}/Bounds.txt"):
        if display_logs:
            print("Bounds.txt Found")

        with open(f"../../Datasets/{folder}/Bounds.txt") as f:
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
        amax = 10_000_000
        amin = -10_000_000
    
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
def read_data_las(folder):
    paths = [f for f in listdir(f'../../Datasets/{folder}') if f.endswith(".laz") or f.endswith(".las") or f.endswith(".LAS")]
    laslist = [laspy.read(f'../../Datasets/{folder}/{path}') for path in paths]
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
    paths = [f for f in listdir(f'../../Datasets/{folder}') if f.endswith(".e57")]
    e57 = [pye57.E57(f'../../Datasets/{folder}/{path}') for path in paths]
    data = e57[0].read_scan(index=0, ignore_missing_fields=True, colors=True, intensity=True)

    print(len(e57[0].data3d))

    header = e57[0].get_header(0)
    print(header.point_fields)

    intensities = None
    red = green = blue = None

    x = data["cartesianX"]
    y = data["cartesianY"]
    z = data["cartesianZ"]

    
    if do_intensity := ((colour_map == "intensity" or colour_map == "mix") and "intensity" in header.point_fields and np.sum(data["intensity"][:1000]) != 0):
        intensities = np.asarray(data["intensity"])

    if do_colour := (colour_map == "colour" and "colorRed" in header.point_fields and np.sum(data["colorRed"][:1000]) != 0):
        red = np.asarray(data["colorRed"])
        green = np.asarray(data["colorGreen"])
        blue = np.asarray(data["colorBlue"])
    

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

#----------------------------------------------------------------------------------------------WIP
def read_data_e57_polar(folder):
    paths = [f for f in listdir(f'../../Datasets/{folder}') if f.endswith(".e57")]
    e57 = [pye57.E57(f'../../Datasets/{folder}/{path}') for path in paths]

    header = e57[0].get_header(0)
    print(len(e57[0].data3d))
    print(header.point_fields)
    print(header.scan_fields)

    x = np.asarray([])
    y = np.asarray([])
    z = np.asarray([])

    red = np.asarray([])
    green = np.asarray([])
    blue = np.asarray([])

    intensities = None

    for i in range(40,len(e57[0].data3d)):
        data = e57[0].read_scan(index=i, ignore_missing_fields=True, colors=True, intensity=True,transform=False)

        header = e57[0].get_header(i)
        print("Translation:",header.translation)
        print("Rotation:",header.rotation)
        print("Deg Rotation:",list(map(lambda x:np.degrees(x),header.rotation)))
        print("Rot Sum:",np.degrees(sum(header.rotation)))
        print(header.rotation_matrix)
        print()

        #'sphericalRange', 'sphericalAzimuth', 'sphericalElevation
        dist = data["sphericalRange"]
        azimuth = data["sphericalAzimuth"]
        elevation = data["sphericalElevation"]

        flat = dist*np.cos(elevation)

        # x = np.append(x, flat*np.cos(azimuth) + header.translation[0])
        # y = np.append(y, flat*np.sin(azimuth) + header.translation[1])
        # z = np.append(z, dist*np.sin(elevation) + header.translation[2])

        xyz = np.asarray([flat*np.cos(azimuth), flat*np.sin(azimuth), dist*np.sin(elevation)])
        xyz = np.matmul(header.rotation_matrix, xyz)
        xarr = xyz[0] + header.translation[0]
        yarr = xyz[1] + header.translation[1]
        zarr = xyz[2] + header.translation[2]

        x = np.append(x,xarr)
        y = np.append(y,yarr)
        z = np.append(z,zarr)

        red = np.append(red, data["colorRed"])
        green = np.append(green, data["colorGreen"])
        blue = np.append(blue, data["colorBlue"])

    """
    if do_intensity := ((colour_map == "intensity" or colour_map == "mix") and "intensity" in header.point_fields and np.sum(data["intensity"][:1000]) != 0):
        intensities = np.asarray(data["intensity"])

    if do_colour := (colour_map == "colour" and "colorRed" in header.point_fields and np.sum(data["colorRed"][:1000]) != 0):
        red = np.asarray(data["colorRed"])
        green = np.asarray(data["colorGreen"])
        blue = np.asarray(data["colorBlue"])
    

    for file in e57[1:]:
        data = file.read_scan(index=0, ignore_missing_fields=True, colors=True, intensity=True)

        dist = data["sphericalRange"]
        azimuth = data["sphericalAzimuth"]
        elevation = data["sphericalElevation"]

        flat = dist*np.cos(elevation)

        x = np.append(x, flat*np.cos(azimuth))
        y = np.append(y, flat*np.sin(azimuth))
        z = np.append(z, dist*np.sin(elevation))
        
        if do_intensity:
            intensities = np.append(intensities, np.asarray(data["intensity"]))

        if do_colour:
            red = np.append(red, np.asarray(data["colorRed"]))
            green = np.append(green, np.asarray(data["colorGreen"]))
            blue = np.append(blue, np.asarray(data["colorBlue"]))"""

    return x,y,z,intensities,red,green,blue
#----------------------------------------------------------------------------------------------WIP

def apply_bounds(x,y,z,bounds):
    bs,r,amax,amin = bounds

    x = x - min(x)
    y = y - min(y)

    sizex = max(x)-min(x)
    sizey = max(y)-min(y)

    box_x = bs[1][0]*sizex
    box_y = bs[1][1]*sizey
    box_a = bs[0][0]*sizex
    box_b = bs[0][1]*sizey

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


    tpl = ([box_a,box_y,0]@rotation.T).tolist()
    tpr = ([box_x,box_y,0]@rotation.T).tolist()
    btr = ([box_x,box_b,0]@rotation.T).tolist()
    btl = ([box_a,box_b,0]@rotation.T).tolist()

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
    xyz = np.matmul(xyz,rotation)

    return xyz


def create_pointcloud(xyz):
    print("Creating Point cloud with ",len(xyz), "points.")
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)

    return pcd


def crop_pointcloud(pcd):
    print(pcd)
    vol = o3d.visualization.read_selection_polygon_volume("bound.json")
    #cl,ind = pcd.remove_statistical_outlier(nb_neighbors=20,std_ratio=2)
    #inlier_cloud = pcd.select_by_index(ind)
    selected_pcd = vol.crop_point_cloud(pcd)


    print("Bounding Selected: ",selected_pcd)

    return selected_pcd


def add_colours(pcd,red,green,blue):

    cn = np.dstack([red,green,blue])[0]
    pcd.colors = o3d.utility.Vector3dVector(cn.astype(np.float64))

    print("Colours added: ",pcd.has_colors())

def add_colour(pcd,r,g,b):
    r = r/max(r)
    g = g/max(g)
    b = b/max(b)

    add_colours(pcd,r,g,b)


def convert_to_normalmap(pcd):
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=normal_radius, max_nn=mx_normal_bodies))
    normals = np.asarray(pcd.normals)
    normals = ((normals - normals.min(axis=0)) / (normals.max(axis=0) - normals.min(axis=0)))


    c1 = normals@[0,1,0.2]
    c2 = normals@[1,0,0]
    c3 = normals@[-1/2,-1.73,0]

    e = np.zeros(shape = [len(normals)])
    
    add_colours(pcd,c1,c2,c3)


def add_intensity(pcd,intensities):
    e = np.zeros(shape = [len(intensities)])

    print(sum(intensities[:1000]))
    intensities -= min(intensities)
    c1 = intensities/max(intensities)
    c2 = intensities/max(intensities)
    c3 = intensities/max(intensities)

    add_colours(pcd,c1,c2,c3)


def mix(pcd,intensities):
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=1500, max_nn=30))
    normals = np.asarray(pcd.normals)
    normals = ((normals - normals.min(axis=0)) / (normals.max(axis=0) - normals.min(axis=0)))

    e = np.zeros(shape = [len(normals)])

    c1 = normals@[0,1,0.2]
    c2 = normals@[1,0,0]
    c3 = normals@[-1/2,-1.73,0]

    c1 = c1/2 + intensities/max(intensities)/2
    c2 = c2/2 + intensities/max(intensities)/2
    c3 = c3/2 + intensities/max(intensities)/2

    add_colours(pcd,c1,c2,c3)


#----------------------------------FUNCTION DEFINITION END------------------------------------#


bounds = read_bounds(folder)

if file_preference == "las":
    x,y,z,intensities,red,green,blue = read_data_las(folder)
elif file_preference == "e57":
    x,y,z,intensities,red,green,blue = read_data_e57(folder)
elif file_preference == "e57 polar":
    x,y,z,intensities,red,green,blue = read_data_e57_polar(folder)

xyz = apply_bounds(x,y,z,bounds)

pcd = create_pointcloud(xyz)



if colour_map == "intensity" and intensities.any() != None:
    add_intensity(pcd,intensities)

elif colour_map == "colour" and red.any() != None:
    add_colour(pcd,red,green,blue)

elif colour_map == "mix" and intensities.any() != None:
    mix(pcd,intensities)

pcd = crop_pointcloud(pcd)

if colour_map == "normal":
    convert_to_normalmap(pcd)
"""
with o3d.utility.VerbosityContextManager(
        o3d.utility.VerbosityLevel.Debug) as cm:
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=14)"""


def custom_draw_geometry_with_key_callback(pcd):

    def switch_background_colour(vis):
        opt = vis.get_render_option()
        if list(opt.background_color) == [1,1,1]:
            col = [0.029, 0.186, 0.169]
        else:
            col = [1,1,1]
        opt.background_color = np.asarray(col)

    key_to_callback = {}
    key_to_callback[ord("K")] = switch_background_colour
    o3d.visualization.draw_geometries_with_key_callbacks([pcd], key_to_callback, width=1920, height=1080)


custom_draw_geometry_with_key_callback(pcd)
#o3d.visualization.draw_geometries([pcd])

if save_name != "":
    data = np.asarray(pcd.points,dtype="float32")
     
    header = laspy.LasHeader(point_format=3, version="1.2")
    header.offsets = np.min(data, axis=0)
    header.scales = np.array([0.1, 0.1, 0.1])

    # 2. Create a Las
    las = laspy.LasData(header)

    las.x = data[:, 0]
    las.y = data[:, 1]
    las.z = data[:, 2]

    las.write(f"../../Datasets/{folder}/{save_name}.laz")