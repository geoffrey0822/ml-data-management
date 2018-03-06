import cv2
import os,sys
import numpy as np
import ntpath

if len(sys.argv)<2:
    exit

conf_file=sys.argv[1]
filename=ntpath.basename(conf_file)
fname,fext=os.path.splitext(filename)

file_dir=os.path.dirname(conf_file)
root_name=fname
if len(sys.argv)>2:
    root_name=sys.argv[2]
    
print file_dir

if not os.path.isdir(root_name):
    os.mkdir(root_name)
    
cclass={}
with open(conf_file) as f:
    for line in f:
        data_vec=line.rstrip().split(',')
        class_name=data_vec[5]
        class_path=os.path.join(root_name,class_name)
        dim=([int(data_vec[1]),int(data_vec[2]),int(data_vec[3]),int(data_vec[4])])
        img_file=os.path.join(file_dir,data_vec[0])
        img=cv2.imread(img_file)
        roi=img[dim[1]:dim[3],dim[0]:dim[2],:]
        resized=cv2.resize(roi,(256,256))
        if cclass=={} or (class_name not in cclass.keys()):
            cclass[class_name]=0
            if not os.path.isdir(class_path):
                os.mkdir(class_path)
        else:
            cclass[class_name]+=1
        exp_fpath=os.path.join(class_path,'%d.jpg'%cclass[class_name])
        cv2.imwrite(exp_fpath,resized)
        print '%s processed'%img_file
        
print cclass
print 'finish'