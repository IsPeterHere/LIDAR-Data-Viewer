import open3d as o3d
import laspy
import numpy as np
from os import listdir
import pyrr
from os import path


#user defined stuff
folder = "St Kilda"

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
    print("kill")
    bs = [[0,0],[1,1]] 
    r = [0,0,0] 
    amx = 400000
    amin = -100000







#everything else






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




#bouding stuff

sizex = abs(min(x))+max(x)
sizey = abs(min(y))+max(y)


box_x = bs[1][1]*sizey
box_y = bs[1][0]*sizex
box_a = bs[0][1]*sizey
box_b = bs[0][0]*sizex


centre = [box_a+((box_x-box_a)/2),box_b+((box_y-box_b)/2),0]

q = pyrr.Quaternion.from_eulers(np.radians(r))
rotation = pyrr.matrix33.create_from_quaternion(q)

box_x += -centre[1]
box_y += -centre[0]
box_a += -centre[1]
box_b += -centre[0]


tpl,tpr,btr,btl = [box_b,box_x,0]@rotation.T,[box_y,box_x,0]@rotation.T,[box_y,box_a,0]@rotation.T,[box_b,box_a,0]@rotation.T
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

def custom_draw_geometry_with_key_callback(pcd):

    def change_background_to_black(vis):
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0, 0, 0])
        return False

    key_to_callback = {}
    key_to_callback[ord("K")] = change_background_to_black
    o3d.visualization.draw_geometries_with_key_callbacks([pcd], key_to_callback)
 
selected_pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=4000, max_nn=30))
normals = np.asarray(selected_pcd.normals)
normals = ((normals - normals.min(axis=0)) / (normals.max(axis=0) - normals.min(axis=0)))


c1 = normals@[0,1,0]
c2 = normals@[-1/2,1.73,0]
c3 = normals@[-1/2,-1.73,0]

e = np.zeros(shape = [len(normals)])

cn = np.dstack([c1,c2,c3])[0]


selected_pcd.colors = o3d.utility.Vector3dVector(1-normals)

#custom_draw_geometry_with_key_callback(pcd)
o3d.visualization.draw_geometries([selected_pcd])





