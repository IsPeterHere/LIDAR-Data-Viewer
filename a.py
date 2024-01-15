import numpy as np




#min corner, max corner
bs = [[0.1,0],[0.2,0.1]]


origin = np.array([0, 0, 0]) # The center of the cube
extent = np.array([1, 1, 1]) 

x = np.linspace(origin[0] - extent[0]/2, origin[0] + extent[0]/2, num=10) # 10 points along the x-axis
y = np.linspace(origin[1] - extent[1]/2, origin[1] + extent[1]/2, num=10) # 10 points along the y-axis
z = np.linspace(origin[2] - extent[2]/2, origin[2] + extent[2]/2, num=10)

vertices = np.stack(np.meshgrid(x, y, z), axis=-1)

print(vertices)