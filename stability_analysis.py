# Python script to collect data from MATLAB/SIMULINK model of Exoskeleton and pharse data to decide the stability of exoskeleton motion
import time
import os
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import csv
import platform
import socket, struct


# Recieve UDP Packets from MATLAB
udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
udp_socket2.bind(("127.0.0.1", 6337))
count2 = 0
ncount2 = 0
data_collect2 = np.array([])
data_predict2 = []
tdelt2 = 0
y_list = []
time_s =[]
print('INIT COMPLETE')
print('WAITING FOR SAFELEGS')
start = time.time()





for count in range(0,101,1):
  # recive data and unpack it and transform it to a array for further processing
  recv_msg2 = recv_data2[0]
  send_addr2 = recv_data2[1] 
  
  recv_msg_decode = struct.unpack("dddddddddddddddddddddddddddd", recv_msg2)
  recv_msg_decode = np.asarray(recv_msg_decode)
  
  # preparing Index
  x_idx = list(range(0,12))
  z_idx = list(range(14,26))
  com_idx = [12,26]
  
  # Transform data
  x = np.asarray(recv_msg_decode[x_idx])
  x = x[~np.isnan(x)]
  z = np.asarray(recv_msg_decode[z_idx])
  z = z[~np.isnan(z)]
  
  # save center of mass of the exoskeleton
  com = list(recv_msg_decode[com_idx])
  time_sim= recv_msg_decode[13]
  
  # save Base of Support points the points represents the feet location points and "X" represents center of mass
  #          ._______________________________.
  #        .|                                  |.
  #          |.                              .| 
  #          |                               |
  #          |            X                  | 
  #          |.                               |.
  #        .|                                  |.
  #          .________________________________.
  # the about figure represents the support polygon and COM
  
  
  bos= np.column_stack((x,z))
  hull=ConvexHull(points=bos)  
  pointstodraw=[]
  for n in hull.vertices:         # Has the index of the choosen vertices from list 'p'
    pointstodraw.append(bos[n])   # We are adding all the vertices corresponding to the index number of p in a new list pointstodraw

  poly_path = mplPath.Path(np.array(pointstodraw)) # The polygon is generated based on the coordinates passed
  
  '''
  plt.plot(bos[hull.vertices,0], bos[hull.vertices,1], 'r--', lw=2)
  plt.plot(bos[hull.vertices[0],0], bos[hull.vertices[0],1], 'ro')
  plt.show()
  '''
  header = ['Labels']
  a = "NO"
  

  if poly_path.contains_point(com):
    # if COM is inside the BOS the model is stable
    a = "YES"
    y_list.append(a)
    time_s.append(time_sim)
    print("Yes: ",time_sim)
  else:
    # if not model is unstable
    a = "NO"
    y_list.append(a)
    time_s.append(time_sim)
    print("No: ",time_sim)

    
# save the stabiliy data into scv for further ML training
header = ["Time","Labels"]    
with open('Labels.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    for i in range(0,len(y_list)):
      data = {'Time': time_s[i], 
              'Labels': y_list[i]}
      writer.writerow(data)

