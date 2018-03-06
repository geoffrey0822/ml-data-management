import os,sys
import cv2
import caffe
import numpy as np
import selectivesearch

def checkRect(box):
    w=box[2]-box[0]
    h=box[3]-box[1]
    if w<5 or h<5:
        return False
    ratio=float(h)/float(w)
    if ratio<0.5 or ratio>1.4:
        return False
    return True

def compute_overlapped(box,gt):
    wa=box[2]-box[0]
    ha=box[3]-box[1]
    wb=gt[2]-gt[0]
    hb=gt[3]-gt[1]
    centA=((wa)/2,(ha)/2)
    centGt=((wb)/2,(hb)/2)
    dist=np.sqrt(np.dot(centA,centGt))
    diag=np.sqrt(wb*wb+hb*hb)
    w_ratio=float(wa)/wb
    h_ratio=float(ha)/hb
    overlapped=dist/diag
    if overlapped>=0.4 and w_ratio>=0.1 and w_ratio<=2.2 and h_ratio>=0.1 and h_ratio<=2.2:
        return overlapped
    else:
        return 0

bbfilepath=sys.argv[1]
bbfile_dir=os.path.dirname(bbfilepath)
exp_dir='negatives'
if not os.path.isdir(exp_dir):
    os.mkdir(exp_dir)
max_n=-1
if len(sys.argv)>2:
    max_n=int(sys.argv[2])
skip=-1
if len(sys.argv)>3:
    skip=int(sys.argv[3])
main_prefix=0
count=0
total=0
iImg=0
with open(bbfilepath,'r') as bbfs:
    print 'start reading...'
    isend=False
    for line in bbfs:
        iImg+=1
        if skip>0 and iImg>1 and iImg%skip!=0:
            continue
        rline=line.rstrip()
        cols=rline.split(',')
        fname=os.path.join(bbfile_dir,cols[0])
        print fname
        img=cv2.imread(fname)
        gs=cv2.cvtColor(img,cv2.COLOR_RGB2LAB)
        #laplacian=cv2.Laplacian(gs,cv2.CV_8U,ksize=3,scale=1)
        #gs=laplacian
        lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
        lbls,rois=selectivesearch.selective_search(gs,scale=2500,sigma=0,min_size=50)
        nvalid=0
        valid_rois=[]
        gt=(int(cols[1]),int(cols[2]),int(cols[3]),int(cols[4]))
        for roii in rois:
            roi=roii['rect']
            if not checkRect(roi) or roi in valid_rois:
                continue
            valid_rois.append(roi)
            overlapped=compute_overlapped(roi,gt)
            if overlapped==0:
                roi_img=img[roi[1]:roi[3],roi[0]:roi[2],:]
                roi_img=cv2.resize(roi_img,(256,256))
                out_path=os.path.join(exp_dir,'%d_%d.jpg'%(main_prefix,count))
                cv2.imwrite(out_path,roi_img)
                count+=1
                total+=1
                if count%1e6==0:
                    count=0
                    main_prefix+=1
                if max_n!=-1 and total>=max_n:
                    isend=True
                    break
            #tmp=gs.copy()
            #cv2.rectangle(tmp,(roi[0],roi[1]),(roi[2],roi[3]),(255,0,0),5)
            #cv2.rectangle(tmp,(gt[0],gt[1]),(gt[2],gt[3]),(0,255,0),5)
            #cv2.imshow('preview',tmp)
            #print roi
            #overlapped=compute_overlapped(roi,gt)
            #print overlapped
            nvalid+=1
            if isend:
                break
            #cv2.waitKey()
        print '%d out of %d boxes are valid'%(nvalid,len(rois))
        
print 'finish'