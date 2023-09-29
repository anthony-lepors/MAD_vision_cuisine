#importer la librairie opencv
import cv2 as cv
from cv2 import aruco
#la mesure du temps est importante dans la reconstitution de la scène et pour les mesures de performances
import time
#important pour créer des thread afin de pararaléliser le programme (optimisation)
from threading import Thread
import numpy as np
#inutile
#import imutils 
#import matplotlib.pyplot as plt

#Le Json est le format retenu pour le l'encodage du fichier de sortie et pour les bibliothéques
import json
#import csv

#Library=[]

#ouvrir toutes les librairies
with open('data/Library.json', 'r') as openfile:
    Library = json.load(openfile)

with open('data/Light.json', 'r') as openfile:
    Light = json.load(openfile)
    
with open('data/Abridged.json', 'r') as openfile:
    Abridged = json.load(openfile)

#with open('Library.csv', newline='') as csvfile:
    #spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    #for row in spamreader:
        #Library.append(row)

#Qr

#dimension QR/AR       
D=30 #milimètres
Hp=D
Lp=D

#active ou désactive le suivi Lucas-Kanade
suivi=True

#solvePnP lk_params
lk_params = dict( winSize  = (50, 50),
                  maxLevel = 3,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 30, 0.01))

#AR
#dimension AR
AR_size = 30  #milimètres

#Déclarer le dictionnaire et les paramètres
ARDict = aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_250)
ARParams = aruco.DetectorParameters()


#sert à lire les ARs sur un thread indépendant de celui qui est principal
class acqQR :
    # initialization method 
    def __init__(self):
        self.timer=0
        self.old_points = np.array([[]])
        self.QR_detect=False
        self.detect=cv.QRCodeDetector()
        # self.stopped is initialized to False 
        self.stopped = True
        # thread instantiation  
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True # daemon threads run in background 
        
    # method to start thread 
    def start(self):
        self.stopped = False
        self.t.start()
    # method passed to thread to read next available frame  
    def update(self):
        while True :
            if self.stopped is True :
                break
            
    def read(self):
        clone=self.frame.copy()
        clone = cv.cvtColor(clone, cv.COLOR_BGR2GRAY )
        QR=self.detect.detectAndDecodeMulti(clone)
        retval,text,points,qr=QR
        
        if retval:
            self.old_points = np.around(np.array(points,dtype=np.float32), 1)
            self.QR_detect=True
            self.timer=0
            return QR
        else:
            if ((self.QR_detect==True)and(suivi)):
                if ((self.old_frame).any==None):
                    oldclone=self.frame.copy()
                else:
                    oldclone=self.old_frame.copy()
                #print(self.old_points)
                oldclone = cv.cvtColor(oldclone, cv.COLOR_BGR2GRAY )
                News=[]
                for prv in self.old_points:
                    nxt, status, error = cv.calcOpticalFlowPyrLK(oldclone, clone, prv, None, **lk_params)
                    News=News+[nxt]
                News=np.around(np.array(News,dtype=np.float32), 1)
                self.Newpoints=News
                #cv.imshow('clone' , clone)
                #cv.imshow('oldclone' , oldclone)
                self.timer+=1
                if ((self.Newpoints.any==None)or(self.timer>=10)):
                    self.QR_detect=False
                    return QR
                else:
                    retval=True
                    text="presumed"
                    points=self.Newpoints
                    self.oldpoints=self.Newpoints
                    QR=None
                    return retval,text,points,QR
                
            return QR
    #fonction qui sert à rajouter des frames dans le traitement
    def input(self,frame,old_frame):
        self.frame=frame
        self.old_frame=old_frame
    # method to stop reading frames 
    def stop(self):
        self.stopped = True
    












#sert à lire les ARs sur un thread indépendant de celui qui est principal
class acqAR :
    # initialization method 
    def __init__(self):
        self.detect=cv.aruco.ArucoDetector(ARDict, ARParams)
        # self.stopped is initialized to False 
        self.stopped = True
        # thread instantiation  
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True # daemon threads run in background 
        
    # method to start thread 
    def start(self):
        self.stopped = False
        self.t.start()
    # method passed to thread to read next available frame  
    def update(self):
        while True :
            if self.stopped is True :
                break
            #self.grabbed , self.frame = self.vcap.read()
            #if self.grabbed is False :
                #print('[Exiting] No more frames to read')
                #self.stopped = True
                #break 
        #self.vcap.release()
    # method to return latest read frame 
    def read(self):
        clone=self.frame.copy()
        clone = cv.cvtColor(clone, cv.COLOR_BGR2GRAY )
        AR = self.detect.detectMarkers(clone)
        return AR

    #fonction qui sert à rajouter des frames dans le traitement
    def input(self,frame,old_frame):
        self.frame=frame
        self.old_frame=old_frame
    # method to stop reading frames 
    def stop(self):
        self.stopped = True














#effectue toutes les opérations de traitement de l'image 
class traitement:
    #initialisation du traitement de l'image
    def init(self,frame):
        #valeur interne du nombre de points pour définir un cercle: doit égaler n dans le module affichage
        self.n=10
        size=frame.shape
        #taille du code AR à détecter
        global Hp
        global Lp
        hp=int(Hp/2)
        lp=int(Lp/2)
        #Modèle de la caméra
        self.dist_coeffs = np.zeros((4,1))
        focal_length = size[1]
        self.center = (size[1]/2, size[0]/2)
        self.camera_matrix = np.array([[focal_length, 0, self.center[0]],[0, focal_length, self.center[1]],[0, 0, 1]], dtype = "double")
        self.model_points = np.array([(-hp, -lp,0),(+hp, -lp,0),(+hp, +lp,0),(-hp, +lp,0)], dtype="double")
        #self.model_points = np.array([(-hp, lp,0),(+hp, lp,0),(hp, -lp,0),(-hp, -lp,0)], dtype="double")
       
    #fonction qui sert à localiser le code AR   
    def locate(self,Poly):
        (retval, rotation, translation) = cv.solvePnP(self.model_points, Poly, self.camera_matrix, self.dist_coeffs, flags=cv.SOLVEPNP_P3P)
        return(rotation,translation)    
    
    #fonction Librairie adpaté à la librairie des points simplifié (en 4 points) ou non (actuellement utilisé)
    def Library(self,i,simplified=False):
        #Light correspond à la libraire des points
        if (simplified==False):
            #si l'identifiant i existe dans la librairie, récupérer son nom, sa nature et son modèle
            if (i<len(Light["Library"])):
                nom=Light["Library"][i]['nom']
                nature=Light["Library"][i]['nature']
                List=[]
                for z in Light["Library"][i]['Dimensions']:
                    List.append([float(z['x']),float(z['y']),float(z['z']),1])
                self.Points=List
            #sinon, dire qu'il n'y a rien
            else:
                nom=None
                nature=None
        #si l'identifiant i existe dans la librairie, récupérer son nom, sa nature et son modèle
        if (simplified==True):
            if (i<len(Abridged["Library"])):
                nom=Abridged["Library"][i]['nom']
                nature=Abridged["Library"][i]['nature']
                List=[]
                for z in Abridged["Library"][i]['Dimensions']:
                    List.append([float(z['x']),float(z['y']),float(z['z']),1])
                self.Points=List
            #sinon, dire qu'il n'y a rien
            else:
                nom=None
                nature=None
        return nom,nature
    def GetPos(self):
        return self.Points
    #modifie directement le vecteur de rotation et de translation afin de modifier la position de l'objet de la bibliothéque dans l'image    
    def Displace(self,rv,tv,tx=0,ty=0,tz=0,rx=0,ry=0,rz=0):
        tv[0]+=tx
        tv[1]+=ty
        tv[2]+=tz
        rv[0]+=rx
        rv[1]+=ry
        rv[2]+=rz
        return(rv,tv)
    #crée une projeté à afficher dans l'image en partant d'un modèle d'objet, de caméra, d'un vecteur de rotation et de translation 
    def projectCV(self,rv,tv):
        Liste=[]
        #print(Liste)
        for i in range(len(self.Points)):
            Liste.append([(self.Points[i][0]),(self.Points[i][1]),(self.Points[i][2])])
        Liste=np.float32(Liste).reshape(-1,3)
        #test=np.float32([[0],[0],[0]]).reshape(-1,3)
        Points,jaco=cv.projectPoints(Liste,rv,tv,self.camera_matrix,self.dist_coeffs)
        Points=np.array(Points,int).reshape(-1,2)
        return Points
    
    def tout_en_un(self,i,rv,tv,simplified=False):
        Library(self,i,simplified=False)
        
    
    #renvoie les coordonnées d'un rectangle de découpage à partir des points de la projeté d'un objet
    def boundingrect(self,List,size,limit=0):
        List=List[limit:]
        #print(List)
        X,Y,Z=size
        minx=X
        maxx=0
        miny=Y
        maxy=0
        for i in List:
            x,y=i
            if (minx>x):
                minx=x
            if (miny>y):
                miny=y
            if (maxx<x):
                maxx=x
            if (maxy<y):
                maxy=y
        if (minx<0):
            minx=0
        if (miny<0):
            miny=0
        if (maxx>X):
            maxx=Y-1
        if (maxy>Y):
            maxy=X-1
        #print(size)
        return(minx,miny,maxx,maxy)
    
    #fonction de distance entre 2 points dans un espace 3D
    def euclidian(self,vec1,vec2):
        return np.sqrt(np.power((vec1[0]-vec2[0]),2)+np.power((vec1[1]-vec2[1]),2)+np.power((vec1[2]-vec2[2]),2))
    
    #fonction renvoyant lisant la valeur de cuisson d'un curseur en fonction de sa rotation
    def curseur(self,rotation,nombrePosition,Hysteresis,poscourante=0):
        Total=np.pi
        Angle=Total/nombrePosition
        if ((rotation > ((poscourante+1)*Angle+Hysteresis)%Total)or(rotation < (poscourante-1)*Angle*-Hysteresis)%Total):
            poscourante=int((rotation+np.pi)/Angle)
        return(poscourante)
