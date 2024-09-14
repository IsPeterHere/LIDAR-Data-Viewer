import matplotlib.pyplot as plt
import numpy as np

x_arr = np.asarray([0,1,2,3,4,5,6,7,8,9,10])
y_arr = np.asarray([10,9.5,8.5,6.4,5.5,5,5.3,6,6.2,5.6,5])
c_arr = np.asarray([[0.0,1.0,0.0] for _ in range(11)])

n = 720
step = 12
x_arr = np.asarray([x for x in range(0,n,step)])
y_arr = np.asarray(np.sin(np.radians(x_arr)))
print(np.sin(x_arr))
c_arr = np.asarray([[0.0,0.0,0.0] for _ in range(0,n,step)])


plt.scatter(x_arr,y_arr,c=c_arr)
plt.show()




new_x_arr = x_arr.copy()
new_y_arr = y_arr.copy()

for _ in range(30):
    for point in range(1,len(x_arr)-1):
        avg_h = (new_y_arr[point-1] + new_y_arr[point] + new_y_arr[point+1])/3
        new_y_arr[point] = avg_h


plt.scatter(new_x_arr,new_y_arr,c=c_arr)
plt.show()






for point in range(len(x_arr)):
    r = 0
    g = 0
    b = 0

    const = 10

    if new_y_arr[point] > y_arr[point]:
        b = -1/(np.e**(const*(new_y_arr[point] - y_arr[point]))) + 1
    else:
        r = -1/(np.e**(const*(y_arr[point] - new_y_arr[point]))) + 1
    
    print(r,g,b)

    c_arr[point] = [r,g,b]

print(c_arr)
#c_arr = c_arr/max(abs(c_arr.flatten()))

plt.scatter(x_arr,y_arr,c=c_arr)
plt.scatter(new_x_arr,new_y_arr,c="pink")
plt.show()