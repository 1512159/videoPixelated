import numpy as np
import cv2
import re
import os
from PIL import Image
import sys
import glob
class bbox:
    def __init__(self,strInfo):
        info = strInfo.split(' ')
        self.mx = int(info[0])
        self.my = int(info[1])
        self.mw = int(info[2])
        self.mh = int(info[3])
        self.mx2 = self.mx + self.mw
        self.my2 = self.my + self.mh
    def show(self):
        print(self.mx, self.my, self.mw, self.mh)
   
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
    pixelSize = 30
    # print(image.shape)
    image = Image.fromarray(image)
    image = image.resize((max(image.size[0]/pixelSize,1), max(image.size[1]/pixelSize,1)), Image.NEAREST)
    pixelSize = int (pixelSize * 2)
    image = image.resize((image.size[0]*(pixelSize), image.size[1]*(pixelSize)), Image.NEAREST)
    # print(np.asarray(image).shape)
    return np.asarray(image)

def loadInput(InputDir): #directory to meta and images folders
    meta_path = InputDir + 'meta'
    img_path  = InputDir + 'images'
    out_path = InputDir + 'output'
    folders = os.listdir(meta_path)
    result = []
    # for folder in folders:
    #     if (os.path.exists(img_path+'/'+folder)):
    #         tmp_img = img_path+'/'+folder
    #         imgFolder = [tmp_img+'/'+it for it in os.listdir(tmp_img)]
            
    #         tmp_meta = meta_path+'/'+folder
    #         metaFolder = [tmp_meta+'/'+it for it in os.listdir(tmp_meta)]
    
    imgFiles  = glob.glob(img_path+'/*/*/*.JPG')
    # metaFiles = glob.glob(meta_path+'/*/*/*.txt')
    metaFolder = glob.glob(meta_path+'/*/*')
    # for folder in imgFolder:
    #     imgFiles = imgFiles + [folder+'/'+it for it in os.listdir(folder)   ]
    # for folder in metaFolder:
    #     metaFiles = metaFiles + [folder+'/'+it for it in os.listdir(folder)]
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
        
        for bbox in bboxs:
            face = img[bbox.my:bbox.my2,bbox.mx:bbox.mx2]

            if (face.shape[0]==0 or face.shape[1]==0):
                continue
            
            #draw rectangle for debug
            # cv2.rectangle(img, (bbox.mx,bbox.my), (bbox.mx2,bbox.my2), (0,255,0),2)
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