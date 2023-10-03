import cv2 as cv
import cv2 as cv
from cv2 import aruco
import matplotlib.pyplot as plt
import numpy as np

#Police
font = cv.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

#Bibliothèque AR
lk_params = dict( winSize  = (50, 50),
                  maxLevel = 3,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 30, 0.01))
#dimension AR
AR_size = 80  #milimètres

#Déclarer le dictionnaire et les paramètres
ARDict = aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_250)
ARParams = aruco.DetectorParameters()

detect=cv.aruco.ArucoDetector(ARDict, ARParams)

# Capture vidéo
cap = cv.VideoCapture(0)

#lecture de la première frame vidéo pour le modèle
ret,frame = cap.read()
#acquisition de la taille de l'image
size=frame.shape
print(size)
#création du modèle pour la fonction solvePnP
Hp=65
Lp=65
hp=int(Hp/2)
lp=int(Lp/2)
dist_coeffs = np.zeros((4,1))
focal_length = size[1]
center = (size[1]/2, size[0]/2)
camera_matrix = np.array([[focal_length, 0, center[0]],[0, focal_length, center[1]],[0, 0, 1]], dtype = "double")
model_points = np.array([(-hp, -lp,0),(+hp, -lp,0),(+hp, +lp,0),(-hp, +lp,0)], dtype="double")

while(True):
    ret,frame = cap.read()
    
    #Lecture des ARs de l'image
    points, markerIds, rejectedCandidates=detect.detectMarkers(frame)

    #si l'emsemble des images lus est non nulle
    if (len (points)>0):
        #format array pour la fonction solve pnp et format entier pour la fonction de dessin sur l'image
        points=np.array(points,float)
        draw=np.array(points,int)
        for txt, dr, Poly in zip(markerIds, draw, points):
            #dessine le carré bleu de l'AR détecté sur l'image
            frame = cv.polylines(frame,[dr],True, (255, 0, 0), 5)
            #Affiche le premier point en rouge
            cv.circle(frame, dr[0][0], 5, (0, 0, 255), 5)
            #ne détermine la distance que si l'identifiant de l'AR est 0
            if (txt==[1]):
                #fonction solvePnP qui renvoie la position réelle d'un objet en fonction d'un modèle et d'une image
                (retval, rotation, translation) = cv.solvePnP(model_points, Poly, camera_matrix, dist_coeffs, flags=cv.SOLVEPNP_ITERATIVE )
                #conversion des radians en degrées et arrondi à la deuxième décimale pour l'affichage
                rotation = np.round(((rotation*180)/np.pi),2)
                translation = np.round((translation),2)
                #Affichage de la position de l'AR [1]
                frame = cv.putText(frame,str(txt),dr[0][0], font, fontScale, color, thickness, cv.LINE_AA)
                frame = cv.putText(frame,"Rx:"+str(rotation[0][0]),(50,50),font,fontScale, color, thickness, cv.LINE_AA)
                frame = cv.putText(frame,"Ry:"+str(rotation[1][0]),(250,50),font,fontScale, color, thickness, cv.LINE_AA)
                frame = cv.putText(frame,"Rz:"+str(rotation[2][0]),(450,50),font,fontScale, color, thickness, cv.LINE_AA)
                frame = cv.putText(frame,"Tx:"+str(translation[0][0]),(50,100),font,fontScale, color, thickness, cv.LINE_AA)
                frame = cv.putText(frame,"Ty:"+str(translation[1][0]),(250,100),font,fontScale, color, thickness, cv.LINE_AA)
                frame = cv.putText(frame,"Tz:"+str(translation[2][0]),(450,100),font,fontScale, color, thickness, cv.LINE_AA)
                #renvoie le nombre d'AR détectés grâce à la taille de la liste issue de la fonction de détection
                frame = cv.putText(frame,"Nombre de ARs:"+str(len(markerIds)),(10,450),font,fontScale, color, thickness, cv.LINE_AA)
    #afficher l'image s'il y a en une
    if ret:
        cv.imshow('Frame',frame)
    #Sortie de la boucle en appuyant sur Q
    else:
        break
    key=cv.waitKey(1)
    if (key==ord('q')):
        break
    
cap.release() 
