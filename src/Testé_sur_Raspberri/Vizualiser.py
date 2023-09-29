import cv2 as cv
import numpy as np
from traitement import acqQR, acqAR, traitement, Library
from affichage import alf,represent
import ffmpegcv
import json
#visualizer
#sert à visualiser une scène 3D à partir d'un descriptif (JSON) de celle ci

#fonction de projection opencv faisant intervenir un modèle 3D, un modèle de caméra, un vecteur de translation et rotation
def projectCV(camera_matrix,dist_coeffs,Points,rv,tv):
    Liste=[]
    #print(Liste)
    #convertir les points d'un système de coordonnées à 4 dimensions (utile pour les matrices de transformation) à un modèle de coordonnées de 3 dimensions
    for i in range(len(Points)):
        Liste.append([(Points[i][0]),(Points[i][1]),(Points[i][2])])
    #changement de format pour la fonction projection
    Liste=np.float32(Liste).reshape(-1,3)
    #fonction pour la fonction projection
    Points,jaco=cv.projectPoints(Liste,rv,tv,camera_matrix,dist_coeffs)
    #changement de format pour l'affichage
    Points=np.array(Points,int).reshape(-1,2)
    return Points

#fonction essentielle pour que la fenêtre de commande ne bloque pas la fonction
def nothing(X):
    pass

#initialisation de la fenêtre de commande
def init_control(r):
    cv.namedWindow('controls')
    cv.createTrackbar('Temps','controls',0,r,nothing)
    cv.createTrackbar('dx','controls',50,500,nothing)
    cv.createTrackbar('dy','controls',50,500,nothing)
    cv.createTrackbar('dz','controls',50,500,nothing)
    cv.createTrackbar('rx','controls',0,360,nothing)
    cv.createTrackbar('ry','controls',0,360,nothing)
    cv.createTrackbar('rz','controls',0,360,nothing)

def load_coordinate(Points,rx=0,ry=0,rz=0,s=1,tx=0,ty=0,tz=0):
    #créer les matrices de rotation, de translation et d'échelle
    rotationX=np.array([(1,0,0,0),(0,np.cos(rx),np.sin(rx),0),(0,-np.sin(rx),np.cos(rx),0),(0,0,0,1)]).reshape(-1,4)
    rotationY=np.array([(np.cos(ry),0,-np.sin(ry),0),(0,1,0,0),(np.sin(ry),0,np.cos(ry),0),(0,0,0,1)]).reshape(-1,4)
    rotationZ=np.array([(np.cos(rz),-np.sin(rz),0,0),(np.sin(rz),np.cos(rz),0,0),(0,0,1,0),(0,0,0,1)]).reshape(-1,4)
    translation=np.array([(1,0,0,tx),(0,1,0,ty),(0,0,1,tz),(0,0,0,1)]).reshape(-1,4)
    Scale=np.array([(s,0,0,0),(0,s,0,0),(0,0,s,0),(0,0,0,1)]).reshape(-1,4)
    #print(translation)
    #multiplication de toutes les matrices
    transform=np.matmul(translation,rotationX)
    transform=np.matmul(transform,rotationY)
    transform=np.matmul(transform,rotationZ)
    transform=np.matmul(transform,Scale)
    transform=np.matmul(transform,translation)
    Points=np.matmul(Points,transform)
    Points=np.array(Points,int)
    return Points

#fonction de décalage afin de changer l'angle de la caméra virtuelle (rotation-> translation)
def rotranslate(translation,rx,ry,rz):
    if (rx!=0):
        translation[0][1]=np.cos(rx)*translation[0][1]-np.sin(rx)*translation[0][2]
        translation[0][2]=np.sin(rx)*translation[0][1]+np.cos(rx)*translation[0][2]
    if (ry!=0):
        translation[0][0]=np.cos(ry)*translation[0][0]+np.sin(ry)*translation[0][2]
        translation[0][2]=-np.sin(ry)*translation[0][0]+np.cos(ry)*translation[0][2]
    if (rz!=0):
        translation[0][0]=np.cos(ry)*translation[0][0]-np.sin(ry)*translation[0][1]
        translation[0][1]=np.sin(ry)*translation[0][0]+np.cos(ry)*translation[0][1]    
    return translation

#paramètres de la police d'écriture
font = cv.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
#déclarer la classe T pour le traitement
T = traitement()

#with open("Light.json", "r+") as openfile:
    ##print(openfile)
    #Light = json.load(openfile)
#ouverture du fichier JSON de sortie
with open("Output.json", "r+") as openfile:
    Output = json.load(openfile)    

Flags=False

#récupération de la liste des temps et de la longueur de celle ci
Temps=Output["Record"][0]["Temps"]
Timerange=len(Output["Record"])-1

#initialisation de la fenêtre de commande
init_control(Timerange)

#créer une frame vide
frame=np.zeros((480,640,3))
size=frame.shape

#initialisation de la matrice de la caméra
dist_coeffs = np.zeros((4,1))
focal_length = size[1]
center = (size[1]/2, size[0]/2)
camera_matrix = np.array([[focal_length, 0, center[0]],[0, focal_length, center[1]],[0, 0, 1]], dtype = "double")

while True :
    #récupérer les valeurs des curseurs
    bar=int(cv.getTrackbarPos('Temps','controls'))
    dx=int((cv.getTrackbarPos('dx','controls')-50)*10)
    dy=int((cv.getTrackbarPos('dy','controls')-50)*10)
    dz=int((cv.getTrackbarPos('dz','controls')-50)*10)
    rx=float((cv.getTrackbarPos('rx','controls'))*(np.pi/180))
    ry=float((cv.getTrackbarPos('ry','controls'))*(np.pi/180))
    rz=float((cv.getTrackbarPos('rz','controls'))*(np.pi/180))
    #récupérer la valeur du temps actuel (instant)
    Temps=Output["Record"][bar]["Temps"]
    #récupérer la liste des objets à l'instant T
    record = Output["Record"][bar]
    #créer une image vide
    show=np.zeros((480,640,3))
    #parcourir la liste des objets à l'instant T
    for objet in record["Objets"]:
        #récupérer l'identifiant AR associé à l'objet
        i=objet["id"]
        #si l'identifiant existe dans la librairie
        if (i<len(Light["Library"])):
            #récupérer le nom et la nature de l'objet
            nom=Light["Library"][i]['nom']
            nature=Light["Library"][i]['nature']
            #récupérer la liste des points du modèle
            List=[]
            for z in Light["Library"][i]['Dimensions']:
                List.append([float(z['x']),float(z['y']),float(z['z']),1])
            points=List
            #format array pour les traitments numériques et int pour la représentation
            points=np.array(points,float)
            draw=np.array(points,int)
            #translater l'objet
            translation=[[[objet['Tx']+dx]],[[objet['Ty']+dy]],[[objet['Tz']+dz]]]
            translation = np.array(translation,float).reshape(-1,3)
            #coordonnées des objets tournées par rapport à l'origine
            translation=rotranslate(translation,rx,ry,rz)
            translation = np.array(translation,float).reshape(-1,3)
            #rotation des modèles
            rotation=[[[objet['Rx']+rx]],[[objet['Ry']+ry]],[[objet['Rz']+rz]]]
            rotation = np.array(rotation,float).reshape(-1,3)  
            #projection et représentation du modèle
            dessin=projectCV(camera_matrix,dist_coeffs,points,rotation,translation)
            show=represent(show,dessin)
    
    cv.imshow('frame' , show)
    key = cv.waitKey(1)
    if key == ord('q'):
        break
