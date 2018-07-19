import numpy as np
import cv2
import re
import os
from PIL import Image
import sys
import glob
MARGIN = 10

class bbox:
    def __init__(self,strInfo):
        info = strInfo.split(' ')
        self.mx = int(info[0])-MARGIN
        self.my = int(info[1])-MARGIN
        self.mw = int(info[2])+MARGIN*2
        self.mh = int(info[3])+MARGIN*2
        self.mx2 = self.mx + self.mw
        self.my2 = self.my + self.mh
        self.area = (self.mx2-self.mx+1) * (self.my2-self.my+1)
    def show(self):
        print(self.mx, self.my, self.mx2, self.my2, self.area)
class frameBBox:
    def __init__(self,metaFrames):
        bboxList  = [metaFrames+'/'+it for it in os.listdir(metaFrames)]
        res = []
        print(bboxList)
        for i in bboxList:
            fi = open(i,'r')
            bboxInFrame = fi.readlines()
            for i in bboxInFrame:
                print(i)
            
        self.bbox = res
    
   

class video:
    def __init__(self,videoPath,metaPath):
        print('Video: ',videoPath)
        self.videoPath = videoPath
        self.metaPath = metaPath
        metaFrame = [metaPath+'/'+it for it in os.listdir(metaPath)]
        imgFrame = [videoPath+'/'+it for it in os.listdir(videoPath)]
       
    def show(self):
        print(self.videoPath, self.metaPath)

def readTestTXT(inpFile):
    fi = open(inpFile,'r')
    data = fi.readlines()

    frames = []
    for line in data:
        frames.append(frameBBox(line))
    
    return frames
def processMetaFile(metaFile):
    fi = open(metaFile,'r')
    allBbox = fi.readlines()
    res = []
    for info in allBbox:
        res.append(bbox(info))
    return res
def pixelate(image):
    pixelSize = 15
    # print(image.shape)
    image = Image.fromarray(image)
    image = image.resize((max(image.size[0]/pixelSize,1), max(image.size[1]/pixelSize,1)), Image.NEAREST)
    pixelSize = int (pixelSize * 2)
    image = image.resize((image.size[0]*(pixelSize), image.size[1]*(pixelSize)), Image.NEAREST)
    # print(np.asarray(image).shape)
    return np.asarray(image)

def getY2(bbox):
    return bbox.area

def non_max_suppression_slow(boxes, overlapThresh):
    boxes.sort(key = getY2)
	# if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []
    suppress = []
    pick = []
    # print('before: ')
    # for i in boxes:
    #     i.show()
    # print('after: ')
    while len(boxes)>0:
        n = len(boxes) - 1 #Get last element in list
        pick.append(boxes[n]) #take this to pick list
        suppress = [n] #remove it from list
        i = boxes[n] #take this to compare overlap
        
        for pos in range(n): #with all bbox exept the last one
            j = boxes[pos]
            xx1 = max(i.mx,j.mx)
            yy1 = max(i.my,j.my)
            xx2 = min(i.mx2,j.mx2)
            yy2 = min(i.my2,j.my2)

            w = max(0,xx2 - xx1 + 1)
            h = max(0,yy2 - yy1 + 1)
            intersection = float(w*h)
            union =  i.area + j.area -float(w*h)
            overlap = intersection/(float(j.area))
            overlap = intersection/union
            if overlap > overlapThresh:
                suppress.append(pos)
        suppress.sort(reverse = True)
        for k in suppress:
            del boxes[k]
    return pick

def loadInput(InputDir): #directory to meta and images folders
    meta_path = InputDir + 'meta'
    img_path  = InputDir + 'images'
    out_path = InputDir + 'output'
    folders = os.listdir(meta_path)
    result = []
    
    imgFiles  = glob.glob(img_path+'/*/*/*.JPG')
    metaFolder = glob.glob(meta_path+'/*/*')
 
    for folder in metaFolder:
        if not os.path.exists(folder.replace('meta','output')):
            os.makedirs(folder.replace('meta','output'))
    
    for i in range(len(imgFiles)):
        print(imgFiles[i])
        img = cv2.imread(imgFiles[i])

        imgFileName = os.path.basename(imgFiles[i])
        
        metaFile = glob.glob(meta_path+'/*/*/'+imgFileName.replace('JPG','txt'))
        
        if (len(metaFile)!=1):
            print('----> Meta file not found!')
            continue

        bboxs = processMetaFile(metaFile[0])
        testbbx = list(bboxs)
        bboxs = non_max_suppression_slow(bboxs,0.3)
        
        # for bbox in testbbx:
        #     cv2.rectangle(img, (bbox.mx,bbox.my), (bbox.mx2,bbox.my2), (0,0,255),2)
        
        for bbox in bboxs:
            face = img[bbox.my:bbox.my2,bbox.mx:bbox.mx2]

            if (face.shape[0]==0 or face.shape[1]==0):
                continue
            
            #draw rectangle for debug
            # cv2.rectangle(img, (bbox.mx,bbox.my), (bbox.mx2,bbox.my2), (0,255,0),2)
            # bbox.show()

            lx = face.shape[0]
            ly = face.shape[1]


            tmp = pixelate(img[bbox.my:bbox.my2,bbox.mx:bbox.mx2])[:lx,:ly]

            img[bbox.my:bbox.my2,bbox.mx:bbox.mx2] = tmp

        cv2.imwrite(imgFiles[i].replace('images','output'),img)
        print('--->DONE')
                
            
    return result


def main():
    videoList = loadInput(sys.argv[1])

if (__name__ == "__main__"):
    main()