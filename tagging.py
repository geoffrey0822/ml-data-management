import os,sys
import numpy as np
import cv2
import time

s_refPt=[]
s_roi=[]
s_buffer=None
s_frame=None
s_busy=False
s_isSquare=False

def roiDraw(event, x,y,flags,param):
    global s_refPt,s_buffer,s_frame,s_roi,s_busy,s_isSquare
    
    if event==cv2.EVENT_LBUTTONDOWN:
        if s_refPt==[]:
            s_refPt=[x,y]
            s_busy=True        
    elif event==cv2.EVENT_LBUTTONUP:
        s_refPt=[]
        s_busy=False
    elif s_busy==True:
        if not s_isSquare:
            s_roi=[s_refPt[0],s_refPt[1],x,y]
        else:
            s_roi=[s_refPt[0],s_refPt[1],x,s_refPt[1]+x-s_refPt[0]]
        
    if (not s_frame is None) and s_roi!=[]:
        s_frame=s_buffer.copy()
        cv2.rectangle(s_frame,(s_roi[0],s_roi[1]),(s_roi[2],s_roi[3]),
                      (0,255,0),2)
        message='Non-Square Mode'
        if s_isSquare:
            message='Square Mode'
        cv2.putText(s_frame,message,(25,25),cv2.FONT_HERSHEY_PLAIN,2,(255,255,0),2)
        cv2.imshow('Editor',s_frame)

if len(sys.argv)<4:
    print 'Must have 3 arguments at least'
    raise
src=sys.argv[1]
dst=sys.argv[2]
labels=sys.argv[3] # class_idx_1:label_1,class_idx_2:label_2, ...
multilabels=labels.split(',')
ndepth=len(multilabels)
dst_keys=''
dst_db='dataset.csv'
if len(sys.argv)>4:
    dst_keys=sys.argv[4]

if len(sys.argv)>5:
    dst_db=sys.argv[5]

if dst_keys!='':
    for depth in range(ndepth):
        label_file='%s_%d.txt'%(dst_keys,depth+1)
        current_keys={}
        if os.path.isfile(label_file):
            with open(label_file,'r') as f:
                for ln in f:
                    line=ln.rstrip('\n')
                    fields=line.split('\t')
                    current_keys[fields[0]]=int(fields[1])
                f.close()
        fields=multilabels[depth].split(':')
        if fields[1] in current_keys.keys():
            continue
        with open(label_file,'a+') as f:
            f.write('%s\t%d\n'%(fields[1],int(fields[0])))

if not os.path.isdir(dst):
    os.mkdir(dst)
    
millis=int(round(time.time()*1000))    

count=1
applySeq=False
cv2.namedWindow('Editor')
cv2.setMouseCallback('Editor',roiDraw)
with open(dst_db,'a+') as outputf:
    for filen in os.listdir(src):
        file_path=os.path.join(src,filen)
        dst_path=os.path.join(dst,'%ld_%d.jpg'%(millis,count))
        img=cv2.imread(file_path)
        s_buffer=img
        s_frame=s_buffer.copy()
        message='Non-Square Mode'
        if s_isSquare:
            message='Square Mode'
        cv2.putText(s_frame,message,(25,25),cv2.FONT_HERSHEY_PLAIN,2,(255,255,0),2)
        cv2.imshow('Editor',s_frame)
        keyIn=cv2.waitKey(30)
        if not applySeq:
            while True:
                keyIn=cv2.waitKey()
                cv2.waitKey(30)
                if keyIn==27:
                    exit()
                elif keyIn==ord('s'):
                    # do sequentially
                    applySeq=True
                    break
                elif keyIn==ord('i'):
                    # do 1-by-1
                    s_roi=[]
                    break
                elif keyIn==ord('b'):
                    s_isSquare=not s_isSquare
                    s_roi=[]
                    s_frame=s_buffer.copy()
                    message='Non-Square Mode'
                    if s_isSquare:
                        message='Square Mode'
                    cv2.putText(s_frame,message,(25,25),cv2.FONT_HERSHEY_PLAIN,2,(255,255,0),2)
                    cv2.imshow('Editor',s_frame)
        else:
            cv2.rectangle(s_frame,(s_roi[0],s_roi[1]),(s_roi[2],s_roi[3]),
                          (0,255,0),2)
            cv2.imshow('Editor',s_frame)
            cv2.waitKey(2)
        roi_img=img[s_roi[1]:s_roi[1]+s_roi[3],s_roi[0]:s_roi[0]+s_roi[2]]
        cv2.imwrite(dst_path,roi_img)
        cls_lbls=''
        for depth in range(ndepth):
            fields=multilabels[depth].split(':')
            if depth>0:
                cls_lbls='%s;%d'%(cls_lbls,int(fields[0]))
            else:
                cls_lbls='%d'%(int(fields[0]))
        outputf.write('%s,%s\n'%(dst_path,cls_lbls))
        count+=1
        
    outputf.close()
print 'finished'
