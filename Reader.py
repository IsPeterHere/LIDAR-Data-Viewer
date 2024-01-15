
from turtle import color
import open3d as o3d
import laspy
import numpy as np
import pyrr
from scipy.spatial.transform import Rotation as R





#bs = min corner, max corner

bs = [[0,0],[1,1]] 
r = [0,0,0] 
amx = 400_000
amin = -300_000


"""
# hill fort 1 
bs = [[0.27,0.78],[0.4,0.92]] 
r = [-1.5,-5.7,0] 
amx = -27_000
amin = -300_000
"""

"""
#farm stead 1 
bs = [[0.13,0.64],[0.22,0.72]] 
r = [-9,-0.5,0] 
amx = -51_000 
amin = -65_000 
"""

"""

# cotage
bs = [[0.10,0.0],[0.2,0.07]] 
r = [0,0,0] 
amx = 3_000
amin = -300_000"""


s =1_000_000
x = bs[1][1]*s
y = bs[1][0]*s
a = bs[0][1]*s
b = bs[0][0]*s


centre = [a+((x-a)/2),b+((y-b)/2),0]

q = pyrr.Quaternion.from_eulers(np.radians(r))
rotation = pyrr.matrix33.create_from_quaternion(q)

x += -centre[1]
y += -centre[0]
a += -centre[1]
b += -centre[0]


tpl,tpr,btr,btl = [b,x,0]@rotation.T,[y,x,0]@rotation.T,[y,a,0]@rotation.T,[b,a,0]@rotation.T
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
    








#harehope 'NT2044_4PPM_LAS_PHASE3.laz'

las = laspy.read('Datasets/Shetland/HU32SE_2PPM_LAS_PHASE2.laz')

print(list(las.point_format.dimension_names))
print(las.key_point)
print(las.header.min[2])


x = las.X 
y = las.Y 
z = las.Z 

xyz = np.dstack([x,y,z])[0]

xyz = np.matmul((xyz - centre),rotation.T)

pcd = o3d.geometry.PointCloud()

pcd.points = o3d.utility.Vector3dVector(xyz[:,:3])

vol = o3d.visualization.read_selection_polygon_volume("bound.json")

# Crop the point cloud
selected_pcd = vol.crop_point_cloud(pcd)


# Display the selected point cloud
o3d.visualization.draw_geometries([selected_pcd])