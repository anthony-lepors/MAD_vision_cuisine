import cv2 as cv
import time
from threading import Thread 
import numpy as np
from camera import WebcamStream
from traitement import acqQR, acqAR, traitement, Library
from affichage import alf,represent
import ffmpegcv
import time
import json

#Caractéristiques de la police d'écriture
font = cv.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

#fichier d'écriture en sortie
OutJson = {'Record':[]}

#initialiser la valeur de temps sur celle de l'ordinateur afin d'avoir la valeur zéro de temps du fichier de sortie
init_Time = time.time()

#instance d'écriture de la vidéo écrivant sur outpy.mp4
out = ffmpegcv.VideoWriter('data/outpy.mp4', None, 10)

#créer une instance de la classe traitement appelé T
T = traitement()

#on travaille sur les ARs et non sur les QRs
AR_active=True

#pilote le nombre 2n de cercle affichés du modèle 3D (Débug)
repeat=1
#cacher la poignée ou tout autre partie rectangulaire des fichiers
HideHandle=False
#si vrai, passage sur les modèles 3D en 4 points
simplified=False

#initialiser la position des curseurs à 0(indispensable pour la fonction associé)
poscourante=0

webcam_stream = WebcamStream(stream_id=0) # 0 id for main camera
#si AR_active vraie, lire les ARs avec acqAR déclaré en tant que acq, sinon lire les QRs avec acqQR déclaré en tant que acq
if AR_active:
    acq = acqAR()
else:
    acq = acqQR()
    
#démarrer les instances de webcam_stream et de acq
webcam_stream.start()
acq.start()

#lire la première frame et l'utiliser afin d'initialiser le programme de traitement
old_frame = webcam_stream.read()
size=old_frame.shape
T.init(old_frame)
while True :
    if webcam_stream.stopped is True :
        break
    else :
        frame = webcam_stream.read()
        #copier la frame dans la variable Buffer
        Buffer=frame.copy()
    #envoyer la vieille frame et la frame récente sur la classe acq grâce à la fonction input
    acq.input(frame,old_frame)
    #lire la valeur de temps depuis le début du programme
    TimeMark = np.abs(time.time()-init_Time)
    
    #initialiser la liste des objets détectés par la caméra
    Record={}
    
    if AR_active:
        
        #print(TimeMark)
        points, markerIds, rejectedCandidates=acq.read()
        #Record={}
        #créer la structure de stockage des données dans Insta
        Insta=json.dumps({'Temps':TimeMark,'Objets':[]}, indent=4)
        #Si la liste est non vide
        if (len (points)>0):
            #format array pour les traitments numériques et int pour la représentation
            points=np.array(points,float)
            draw=np.array(points,int)
            i=0
            capt={'Temps':TimeMark,'Objets':[]}
            for txt, dr, Poly in zip(markerIds, draw, points):
                #print(int(txt))
                #faire appel à la librairie
                nom,nature=T.Library(int(txt),simplified)
                #Fonction de localisation
                rotation,translation=T.locate(Poly)
                if (nom!=None):
                    #créer une matrice de transformation dans la classe de traitement
                    T.load_coordinate(rotation[0][0],rotation[1][0],rotation[2][0],1,0,0,0)
                    #agir sur les vecteurs de position et de rotation afin de déplacer le modèle 3D
                    rotation,translation=T.Displace(rotation,translation,0,0,0)
                    #créer une projeté à représenter
                    dessin=T.projectCV(rotation,translation)
                    #print(len(dessin))
                    #représenter visuellement la projeté
                    frame=represent(frame,dessin,repeat,HideHandle,simplified)
                    #minx,miny,maxx,maxy = T.boundingrect(dessin,size,8)
                    #if (minx>=0):
                        #cropped=frame[miny:maxy,minx:maxx]
                        #cv.imshow("cropped"+str(txt),cropped)
                        #cv.destroyWindow("cropped"+str(txt))
                        #cv.circle(frame, (minx,miny), 5, (0, 255, 255), 5)
                        #cv.circle(frame, (maxx,maxy), 5, (255, 0, 255), 5)
                    if nature == "Curseur":
                        #print(rotation[2])
                        poscourante=T.curseur(rotation[2][0],8,(np.pi/180)*5,poscourante)
                        frame = cv.putText(frame,"Position:"+str(poscourante),(80,80), font, fontScale, color, thickness, cv.LINE_AA)
                    points=T.GetPos()
                    #Cp correspond aux coordonnées du centre du cercle de l'objet
                    CP=points[-1]
                    CP=[[-CP[0]+translation[0][0]],[CP[1]+translation[1][0]],[CP[2]+translation[2][0]]]
                    Artranslation = translation
                    translation=CP
                #nombres adaptés pour l'affichage et le stockage
                rotation = np.round(((rotation*180)/np.pi),2)
                translation = np.round((translation),2)
                capt['Objets'].append({"id":int(txt),"nom":nom,'Tx':Artranslation[0][0],'Ty':Artranslation[1][0],'Tz':Artranslation[2][0],'Rx':rotation[0][0],'Ry':rotation[1][0],'Rz':rotation[2][0]})
                #fonction de représentation
                frame = alf(i,txt, dr, Poly,rotation,translation,frame,AR_active)
                i+=1
            #ajjoindre la valeur à l'instant t aux valeurs précédentes
            OutJson['Record'].append(capt)
            Insta=json.dumps(capt, indent=4)
        #ecrire le fichier de suivi instantané des objets
        with open("data/Insta.json", "w") as outfile:
            outfile.write(Insta)
    else:
        retval,text,points,QR=acq.read()
        #si la valeur de succès de lecture est vraie
        if retval:
            #format array pour les traitments numériques et int pour la représentation
            points=np.array(points,float)
            draw=np.array(points,int)
            i=0
            for txt, dr, Poly in zip(int(text, draw, points)):
                #faire appel à la librairie
                nom,nature=T.Library()
                #Fonction de localisation
                rotation,translation=T.locate(Poly)
                #print(nom)
                #print(txt)
                #Read=T.readQR(txt)
                
                #Read=T.readQR('{"nom":"poele 1 personne","nature":"poêle","dimensions":{"QR/Centre":200,"QR/Poignée":75,"LargeurPoignée":45,"RayonCentre":79,"RayonBords":100,"Hauteur de poêle":30,"Unité":"mm"}}')
                if (nom!=None):
                    #créer une matrice de transformation dans la classe de traitement
                    T.load_coordinate(rotation[0][0],rotation[1][0],rotation[2][0],1,0,0,0)
                    #T.load_coordinate()
                    #print("Check")
                    #agir sur les vecteurs de position et de rotation afin de déplacer le modèle 3D
                    rotation,translation=T.Displace(rotation,translation,400,0,0)
                    #créer une projeté à représenter
                    dessin=T.projectCV(rotation,translation)
                    #représenter visuellement la projeté
                    frame=represent(frame,dessin)
                    #obtenir les points du modèle
                    points=T.GetPos()
                    #Cp correspond aux coordonnées du centre du cercle de la poêle
                    CP=points[-1]
                    CP=[[-CP[0]+translation[0][0]],[CP[1]+translation[1][0]],[CP[2]+translation[2][0]]]
                    translation=CP
                #nombres adaptés pour l'affichage et le stockage
                rotation = np.round(((rotation*180)/np.pi),2)
                translation = np.round((translation),2)
                #fonction de représentation pour le QR
                frame = alf(i,txt, dr, Poly,rotation,translation,frame,AR_active)
                i+=1
    
    #La frame actuelle non traité devient l'ancienne frame
    old_frame=Buffer
    cv.imshow('frame' , frame)
    out.write(frame)
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    Output=json.dumps(OutJson, indent=4)
    with open("data/Output.json", "w") as outfile:
        outfile.write(Output)
webcam_stream.stop() # stop the webcam stream
#Ecrire le fichier de sortie
capt={'Temps':TimeMark,'Objets':[]}
Insta=json.dumps(capt, indent=4)
with open("data/Insta.json", "w") as outfile:
    outfile.write(Insta)
