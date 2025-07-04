import numpy as np
import pye57
import laspy
from os import listdir

folder = "../Datasets/Leica/Outdoor"
path = listdir(folder)[0]
e57 = pye57.E57(f"{folder}/{path}")

# read scan at index 0
data = e57.read_scan(index=0, ignore_missing_fields=True, colors=True, intensity=True)

# 'data' is a dictionary with the point types as keys
assert isinstance(data["cartesianX"], np.ndarray)
assert isinstance(data["cartesianY"], np.ndarray)
assert isinstance(data["cartesianZ"], np.ndarray)

# other attributes can be read using:
# data = e57.read_scan(0, intensity=True, colors=True, row_column=True)
assert isinstance(data["cartesianX"], np.ndarray)
assert isinstance(data["cartesianY"], np.ndarray)
assert isinstance(data["cartesianZ"], np.ndarray)
assert isinstance(data["intensity"], np.ndarray)
assert isinstance(data["colorRed"], np.ndarray)
assert isinstance(data["colorGreen"], np.ndarray)
assert isinstance(data["colorBlue"], np.ndarray)

# the ScanHeader object wraps most of the scan information:
header = e57.get_header(0)
print(header.point_count)
print(header.rotation_matrix)
print(header.translation)

# all the header information can be printed using:
for line in header.pretty_print():
    print(line)

# Create a new LAS file
las_out = laspy.create(point_format=3, file_version='1.2')

# Populate the LAS file with point cloud data
print(data["cartesianX"])
las_out.x = data["cartesianX"]
las_out.y = data["cartesianY"]
las_out.z = data["cartesianZ"]
las_out.intensity = data["intensity"]
las_out.red = data["colorRed"]
las_out.green = data["colorGreen"]
las_out.blue = data["colorBlue"]



xmin = np.floor(np.min(data["cartesianX"]))
ymin = np.floor(np.min(data["cartesianY"]))
zmin = np.floor(np.min(data["cartesianZ"]))

las_out.header.offset = [xmin, ymin, zmin]
las_out.header.scale = [0.001, 0.001, 0.001]

# Close the LAS file
las_out.write(f"{folder}/Convert.las")