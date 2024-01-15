import open3d as o3d
import laspy
import numpy as np
from os import listdir
from os import path
import pyrr


#user defined stuff
folder = "St Kilda Specific"


if path.exists(f"Datasets/{folder}/Bounds.txt"):
    with open(f"Datasets/{folder}/Bounds.txt") as f:
        data = f.read().splitlines()
        data = [x for x in data if "#" not in x and len(x) > 0]
        print(data)
        data = [x.split(";")[1] for x in data]
    
    a = data[0].split(",")
    bs = [[float(a[0]),float(a[1])],[float(a[2]),float(a[3])]]

    a = data[1].split(",")
    r = [float(a[0]),float(a[1]),float(a[2])]
    amx = int(data[2])
    amin = int(data[3])

    del a

    print(bs,r,amx,amin)

else:
    bs = [[0,0],[1,1]] 
    r = [0,0,0] 
    amx = 400000
    amin = -100000


#tiling stuff
paths = [f for f in listdir(f'Datasets/{folder}') if f.endswith(".laz")]
laslist = [laspy.read(f'Datasets/{folder}/{path}') for path in paths]

x = laslist[0].X
y = laslist[0].Y
z = laslist[0].Z

for las in laslist[1:]:
    print(las.header.x_offset,las.header.min[0])
    print(las.header.y_offset,las.header.min[1])
    print(las.header.z_offset,las.header.min[2])
    print(las.header.min[0],end="\n\n")
    x = np.append(x,las.X + (1_000_000 * (las.header.x_offset - laslist[0].header.x_offset)/1_000))
    y = np.append(y,las.Y + (1_000_000 * (las.header.y_offset - laslist[0].header.y_offset)/1_000))
    z = np.append(z,las.Z + (1_000_000 * (las.header.z_offset - laslist[0].header.z_offset)/1_000))


x = x - min(x)
y = y - min(y)


#bounding stuff

sizex = max(x)-min(x)
sizey = max(y)-min(y)

box_x = bs[1][0]*sizex
box_y = bs[1][1]*sizey
box_a = bs[0][0]*sizex
box_b = bs[0][1]*sizey


centre = [box_a+((box_x-box_a)/2),box_b+((box_y-box_b)/2),0]

q = pyrr.Quaternion.from_eulers(np.radians(r))
rotation = pyrr.matrix33.create_from_quaternion(q)

box_x -= centre[0]
box_y -= centre[1]
box_a -= centre[0]
box_b -= centre[1]


tpl = [box_a,box_y,0]@rotation.T
tpr = [box_x,box_y,0]@rotation.T
btr = [box_x,box_b,0]@rotation.T
btl = [box_a,box_b,0]@rotation.T

with open("bound.json","w") as f:
    f.write("""
{{
  "axis_max": {amx},
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


        """.format(tpl = str(list(tpl)),tpr = str(list(tpr)),btr = str(list(btr)),btl = str(list(btl)),amx = amx,amin = amin ))





#get point cloud
xyz = np.dstack([x,y,z])[0]
xyz = np.matmul((xyz - centre),rotation.T)

pcd = o3d.geometry.PointCloud()

pcd.points = o3d.utility.Vector3dVector(xyz[:,:3])

# Crop the point cloud
vol = o3d.visualization.read_selection_polygon_volume("bound.json")
selected_pcd = vol.crop_point_cloud(pcd)


# Display the selected point cloud
o3d.visualization.draw_geometries([selected_pcd])