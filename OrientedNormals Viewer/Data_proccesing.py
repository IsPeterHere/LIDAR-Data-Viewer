from calendar import c
from functools import reduce
from math import e
import laspy
import numpy as np
from os import listdir
import scipy
import open3d as o3d

"""
folder = "Tap o Noth"  #name of folder (within Datasets)
meters = 10_000        #how many units is a meter



neighbor_radius = 2.75 * meters
pick = 85

normal_radius = 10*meters
mx_normal_bodies = 900

lower = 0.15*meters
upper = 1*meters

"""
folder = "White Meldon"  #name of folder (within Datasets)
meters = 1_000        #how many units is a meter



neighbor_radius = 2.2 * meters
pick = 55

normal_radius = 3*meters
mx_normal_bodies = 650

lower = 0.01*meters
upper = 0.5*meters

#----------------------------------FUNCTION DEFINITION START----------------------------------#

#reads out 3 arrays of x,y,z coordinates
def read_data(folder):
    paths = [f for f in listdir(f'Datasets/{folder}') if f.endswith(".laz")]
    
    header = laspy.read(f'Datasets/{folder}/{paths[0]}') 

    conjunction_xyz = np.array([[0,0,0]],dtype="float32")
    conjunction_order_casual = np.array([],dtype="int32")
    conjunction_order = np.array([],dtype="int32")
    
    order_counter = 0
    for i in range(len(paths)):
        las = laspy.read(f'Datasets/{folder}/{paths[i]}') 

        nwx = las.X
        nwy = las.Y
        nwz = las.Z
        
        
        lower = np.asarray(nwy<normal_radius+neighbor_radius*2).nonzero()[0]
        upper = np.asarray(nwy>max(nwy)-normal_radius - neighbor_radius*2).nonzero()[0]
        left  = np.asarray(nwx<normal_radius+neighbor_radius*2).nonzero()[0]
        right = np.asarray(nwx>max(nwx)-normal_radius-neighbor_radius*2).nonzero()[0]
        
        lower_order = np.asarray(nwy<neighbor_radius*2).nonzero()[0]
        upper_order = np.asarray(nwy>max(nwy)-neighbor_radius*2).nonzero()[0]
        left_order  = np.asarray(nwx<neighbor_radius*2).nonzero()[0]
        right_order = np.asarray(nwx>max(nwx)-neighbor_radius*2).nonzero()[0]
        
        c_order = reduce(np.union1d, (lower_order,upper_order,left_order,right_order))
        c_xyz = reduce(np.union1d, (lower,upper,left,right))
        out_order = np.setdiff1d(np.arange(len(nwx)),c_order)
        
        conjunction_order_casual = np.concatenate([conjunction_order_casual,np.array([np.where(c_xyz == i) for i in c_order]).flatten() + len(conjunction_xyz)-1])
        c_order += order_counter
        conjunction_order = np.concatenate([conjunction_order, c_order])
        

        
        nwx_ac = nwx + (1_000 * (las.header.x_offset - header.header.x_offset))
        nwy_ac = nwy + (1_000 * (las.header.y_offset - header.header.y_offset))
        nwz_ac = nwz + (1_000 * (las.header.z_offset - header.header.z_offset))
       
        xyz = np.dstack([nwx,nwy,nwz])[0]
        xyz = xyz.astype(dtype="float32")
        xyz_ac = np.dstack([nwx_ac,nwy_ac,nwz_ac])[0]
        
        c_xyz = xyz_ac[c_xyz]
        conjunction_xyz = np.vstack([conjunction_xyz, c_xyz])

        if len(xyz) > 0:
            yield (order_counter,out_order,None,xyz,f"{paths[i]}")
        order_counter += len(xyz)
        
    yield (order_counter,conjunction_order_casual,conjunction_order,conjunction_xyz[1:],"conjunction")



def proccess_data(order_counter,order,true_order,xyz,name):
    print(f"Begining Block '{name}': containing {len(xyz)} points, with {len(order)} requested")
    tree = scipy.spatial.cKDTree(xyz[:,:-1])
    results = tree.query_ball_point(xyz[:,:-1], neighbor_radius)
    print("KD Tree Done")

    processed_neighbor_indexes = np.array([[i]+results[i][:pick] for i in range(len(results)) if len(results[i]) >= pick])
    print("pass num",len(processed_neighbor_indexes))
    if len(processed_neighbor_indexes) <= 0:
        raise ValueError("No Suitable points found")
    
    processed_neighbors = xyz[processed_neighbor_indexes]
    diffs = processed_neighbors[:,1:] - processed_neighbors[:,None,0]

    print("differences done")

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz[processed_neighbor_indexes[:,0]])
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=normal_radius, max_nn=mx_normal_bodies))
    normals = np.asarray(pcd.normals,dtype="float32")
    print("Normals Done")

    dot_product = np.sum(diffs * normals[:, np.newaxis],axis = -1)
    print("Dots Done")

    lower_neg_Ticks = np.sum((dot_product < -lower ), axis = 1)
    lower_pos_Ticks = np.sum((dot_product > lower ), axis = 1)
    
    upper_neg_Ticks = np.sum((dot_product >= -upper ), axis = 1)
    upper_pos_Ticks = np.sum((dot_product <= upper ), axis = 1)
    
    rest_Ticks = np.sum((dot_product != None ), axis = 1) 
    
    Ticks = np.dstack([lower_neg_Ticks-(rest_Ticks-upper_neg_Ticks),
                       lower_pos_Ticks-(rest_Ticks-upper_pos_Ticks),
                       (rest_Ticks-lower_neg_Ticks-lower_pos_Ticks)+(rest_Ticks-upper_neg_Ticks)+(rest_Ticks-upper_pos_Ticks)])[0]
    
    if name == "conjunction":
        comp = set(processed_neighbor_indexes[:,0])
        o = set(order)
        t_string = "|".join([",".join([str(y) for y in Ticks[x]]) for x in range(len(Ticks)) if processed_neighbor_indexes[:,0][x] in o])
        i_string = "|".join([str(true_order[x]) for x in range(len(true_order)) if order[x] in comp])
    else:
        order = set(order)
        t_string = "|".join([",".join([str(y) for y in Ticks[x]]) for x in range(len(Ticks)) if processed_neighbor_indexes[:,0][x] in order])
        i_string = "|".join([str(order_counter+processed_neighbor_indexes[:,0][x]) for x in range(len(processed_neighbor_indexes[:,0])) if processed_neighbor_indexes[:,0][x] in order])
    
    print(f"Finished {name}")
    return t_string, i_string


print(f"Press Enter to start proccessing {folder}")
input()

with open(f'Datasets/{folder}/Inclusion_data.txt',"w") as f:
    f.write("")
with open(f'Datasets/{folder}/Point_data.txt',"w") as f:
    f.write("")
    

c = ""
for order_counter,order,true_order,xyz,name in read_data(folder):
    t_string,i_string = proccess_data(order_counter,order,true_order,xyz,name)
    
    print("Saving Data...")
    with open(f'Datasets/{folder}/Inclusion_data.txt',"a") as f:
        f.write(c+i_string)
    with open(f'Datasets/{folder}/Point_data.txt',"a") as f:
        f.write(c+t_string)
    print("Saving Finished")
    
    c = "|"
    

print("<All Blocks Done>")
    