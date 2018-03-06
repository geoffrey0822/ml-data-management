import os,sys

if len(sys.argv)<3:
    exit
    
dir_name=sys.argv[1]
prefix=sys.argv[2]
print dir_name
for file in os.listdir(dir_name):
    oldname=os.path.join(dir_name,file)
    print oldname
    newname=os.path.join(dir_name,'%s_%s'%(prefix,file))
    os.rename(oldname, newname)

print 'finish'