from imgaug import augmenters as iaa
import cv2
import numpy as np
import os,sys
from pandas._libs.algos import pad_bool

def preprocess(src):
    gs=gs=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    gs=cv2.GaussianBlur(gs,ksize=(9,9),sigmaX=10)
    swimg=cv2.resize(gs,(256,256))
    pimg=cv2.Laplacian(swimg,cv2.CV_32F,ksize=5)
    return pimg

if len(sys.argv)<3:
    print 'not enough input'
    exit()

seq=iaa.Sequential([
        iaa.Scale((0.5,0.5))
    ])
seq=iaa.Scale((0.1,0.5))
seq2=iaa.CropAndPad((-100,100),
                    pad_mode='linear_ramp',
                    keep_size=False,
               sample_independently=True)
seq2=iaa.Crop((0,50),
                    keep_size=False,
               sample_independently=True)

imgdir=sys.argv[1]
expdir=sys.argv[2]
if not os.path.isdir(expdir):
    os.mkdir(expdir)
    
maxN=2
if len(sys.argv)>3:
    maxN=int(sys.argv[3])
edgeOnly=0
if len(sys.argv)>4:
    edgeOnly=int(sys.argv[4])
    
total=0
print edgeOnly
count=0
for jpg in os.listdir(imgdir):
    imgpath=os.path.join(imgdir,jpg)
    testimg=cv2.imread(imgpath)
    fname,fext=os.path.splitext(jpg)
    n=maxN
    outputs=[]
    outputs.append(testimg)
    total+=1
    if edgeOnly!=1:
        while(n>0):
            break
            img=seq.augment_image(testimg)
            dim=len(img)
            wimg=cv2.resize(img,(256,256))
            outputs.append(wimg)
            #cv2.imshow('preview',wimg)
            #print dim
            #cv2.waitKey(1000)
            n-=1
        n=maxN
        while(n>0):
            img=seq2.augment_image(testimg)
            img=testimg
            dim=len(img)
            wimg=cv2.resize(img,(256,256))
            outputs.append(wimg)
            #cv2.imshow('preview',wimg)
            #print dim
            #cv2.waitKey(1000)
            n-=1
        count=0
        for wimg in outputs:
            count+=1
            name='%s_%d.jpg'%(fname,count)
            eimgpath=os.path.join(expdir,name)
            cwimg=wimg
            if edgeOnly==2:
                cwimg=preprocess(wimg)
            cv2.imwrite(eimgpath,cwimg)
        ltotal=total*count
        if total%100==0:
            print '%d(%d)'%(ltotal,len(outputs))
    else:
        count+=1
        name='%s_%d.jpg'%(fname,count)
        cwimg=preprocess(testimg)
        eimgpath=os.path.join(expdir,name)
        cv2.imwrite(eimgpath,cwimg)
        ltotal=total*count
        if total%100==0:
            print '%d(%d)'%(ltotal,len(outputs))
