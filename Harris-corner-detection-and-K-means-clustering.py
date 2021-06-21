import cv2
import numpy as np
import random
import copy

color = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0), (255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
image_path = "image1.jpg"
k_val = 3

def show_save(title, image):
    #cv2.putText(image, title, (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3)
    cv2.imshow(title, image)
    cv2.imwrite('fig/'+title+'_'+str(k_val)+'.jpg', image)
    
def viewallpoints(): 
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    keypoints = cv2.goodFeaturesToTrack(gray,100,0.05,15) 
    keypoints = np.int0(keypoints)
    for i in keypoints:
        x,y = i.ravel()
        cv2.circle(img, (x,y), 3, (255,0,0), -1)

    show_save('data_points', img) 
    return keypoints

def Average(lst): 
    if len(lst)>0:
        return sum(lst) / len(lst) 
    else:
        print("cluster zero len")
        return 0
    
def centroid_initialize(points, k):
    index_k_new=[]
    index = np.random.choice(points.shape[0], k, replace=False) 
    for j in range(0, k):
        index_k_new.append([points[index[j]][0,0],points[index[j]][0,1]])
    return index_k_new

def centroid_find(cluster, k):
    index_k_new=[]   
    for j in range(0, k):
        ave=Average([t[3] for t in cluster if t[2]==j])    
        for i in range(0, len(cluster)):
            if cluster[i][2]==j:
                cluster[i][3]=abs(cluster[i][3]-ave)
        tmp = sorted([t for t in cluster if t[2]==j],key=lambda x: x[3])
        index_k_new.append([tmp[0][0],tmp[0][1]]) 
    return index_k_new           
    
def cluster_find(points, k, index_k):
    cluster = []
    for i in points:
        x = i[0,0]
        y = i[0,1]
        dist = []
        for j in range(0, k):
                xk = index_k[j][0]
                yk = index_k[j][1]
                dist.append([((((x - xk )**2) + ((y-yk)**2) )**0.5),j])
        dist.sort() 
        cluster.append([x,y,dist[0][1],(x**2) + (y**2)])
        # print(cluster)
    return cluster
        
def cluster_show(cluster_new, k):
    img1 = cv2.imread(image_path)
    # print(cluster_new)
    for j in range(0, k):    
        tmp = [t[0:2] for t in cluster_new if t[2]==j]
        for i in range(0, len(tmp)):
            cv2.circle(img1, (tmp[i][0],tmp[i][1]), 3, color[j], -1)
    show_save('clusters', img1) 

def cluster_boun_box(cluster_new, k):
    img1 = cv2.imread(image_path)
    img2 = cv2.imread(image_path)
    img3 = cv2.imread(image_path)
    for i in range(0, len(cluster_new)):
        cluster_new[i][3]=(cluster_new[i][0]**2) + (cluster_new[i][1]**2)
    for j in range(0, k):
        tmp = sorted([t for t in cluster_new if t[2]==j],key=lambda x: x[3])
        x = tmp[0][0]
        y = tmp[0][1]
        x1 = tmp[len(tmp)-1][0]
        y1 = tmp[len(tmp)-1][1]
        image = cv2.rectangle(img1, (x1,y1), (x,y), color[j], 2)
        cv2.putText(image, 'Object'+str(j), (x+20,y+20),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
        show_save("bound box", image)
        
        
        tmp = sorted([t for t in cluster_new if t[2]==j],key=lambda x: x[0])
        x = tmp[0][0]
        x1 = tmp[len(tmp)-1][0]
        tmp = sorted([t for t in cluster_new if t[2]==j],key=lambda x: x[1])
        y = tmp[0][1]
        y1 = tmp[len(tmp)-1][1]
        image1 = cv2.rectangle(img2, (x1,y1), (x,y), color[j], 2)
        cv2.putText(image1, 'Object'+str(j), (x+20,y+20),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
        show_save("bound box1", image1)        
        
        # for corner in range(0,len(tmp)):
        #     x = tmp[corner][0]
        #     y = tmp[corner][1]
        #     x= int(x)
        #     y= int(y)
        #     image2 = cv2.rectangle(img3, (x-10,y-10),(x+10,y+10),color[j], -1)    
        #     show_save("bound box2", img3)
        
def kmean_cal(points, k):     
    # points = np.append(points,np.zeros([len(points),1]),1)
    cluster_old = []
    cluster_new = []
    index_k_old=[]
    index_k_new=[]
    index_k=[]
    
    index_k_new = centroid_initialize(points, k)
    cluster_new = cluster_find(points, k, index_k_new)        
    index_k.append(copy.deepcopy(index_k_new))
   
    cnt=0
    # while [x[0:3] for x in cluster_old] != [x[0:3] for x in cluster_new]:
    while index_k_old != index_k_new:      
        index_k_old = copy.deepcopy(index_k_new) 
        cluster_old = copy.deepcopy(cluster_new) 
        index_k_new = centroid_find(cluster_new, k)
         
        cluster_new = cluster_find(points, k, index_k_new)
        
        # set stop threshold
        diff1 = []
        for elem in [x[0:3] for x in cluster_new]:
            if elem not in [x[0:3] for x in cluster_old]:
                diff1.append(elem)
  
        cnt=cnt+1
        if ((len(diff1)/len(cluster_new))<=0.1) & cnt>50:
            break
        elif cnt>100:
            break
        
        if index_k_new in index_k:
            break
        index_k.append(copy.deepcopy(index_k_new))
                
    cluster_show(cluster_new, k)
    print(cnt)
    cluster_boun_box(cluster_new, k)


points = viewallpoints();    
kmean_cal(points, k_val)
cv2.waitKey(0)
cv2.destroyAllWindows()