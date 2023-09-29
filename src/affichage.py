import numpy as np
import cv2 as cv
#hello 

#caractéristiques de la police d'écriture
font = cv.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

#fonction d'affichage, i étant le numéro du modèle affiché
def alf(i,txt, dr, Poly,rotation,translation,frame,AR_active): 
    if AR_active:
        #afficher les contours du code AR
        frame = cv.polylines(frame,[dr],True, (255, 0, 0), 5)
        cv.circle(frame, dr[0][0], 5, (0, 0, 255), 5)
        #cv.circle(frame, dr[0][3], 5, (0, 255, 0), 5)
        #afficher le nom du code AR
        frame = cv.putText(frame,str(txt),dr[0][0], font, fontScale, color, thickness, cv.LINE_AA)
        #afficher la position du code AR
        frame = cv.putText(frame,"Rx:"+str(rotation[0][0]),(50,50+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Ry:"+str(rotation[1][0]),(250,50+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Rz:"+str(rotation[2][0]),(450,50+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Tx:"+str(translation[0][0]),(50,100+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Ty:"+str(translation[1][0]),(250,100+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Tz:"+str(translation[2][0]),(450,100+i*100),font,fontScale, color, thickness, cv.LINE_AA)
    else:
        #afficher les contours du code QR
        frame = cv.polylines(frame,[dr],True, (255, 0, 0), 5)
        cv.circle(frame, dr[0], 5, (0, 0, 255), 5)
        #afficher le nom du code QR
        frame = cv.putText(frame,txt,dr[0], font, fontScale, color, thickness, cv.LINE_AA)
        #afficher la position du code QR
        frame = cv.putText(frame,"Rx:"+str(rotation[0][0]),(50,50+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Ry:"+str(rotation[1][0]),(250,50+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Rz:"+str(rotation[2][0]),(450,50+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Tx:"+str(translation[0][0]),(50,100+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Ty:"+str(translation[1][0]),(250,100+i*100),font,fontScale, color, thickness, cv.LINE_AA)
        frame = cv.putText(frame,"Tz:"+str(translation[2][0]),(450,100+i*100),font,fontScale, color, thickness, cv.LINE_AA)
    return (frame)

def represent(frame,Liste,repeat=1,HideHandle=False,simplified=False):
    #mode de représentation associé au modèle 3D de base
    #les 8 premiers points correspondent à la poignée
    #le dernier points correspond au centre de l'objet qui nous intéresse (ex:centre de la partie circulaire pour la poêle)
    #les autres points décrivent les cercles
    if (simplified==False):
        #nombre de points utilisé pour représenter un cercle
        n=16
        Lo=len(Liste)
        Lo=int((Lo-9)/31)
        #séparer la partie du modèle en la partie circulaire et le centre
        CircleList=Liste[8:]
        Centre=Liste[-1]
        if (repeat!=0):
            for j in range(Lo):
                Circle=CircleList[2*n*(j):2*n*(1+j)]
                for i in range(n):
                    #représentation de la partie circulaire
                    cv.line(frame, Circle[2*i], Circle[(2*i+1)%(2*n)], (100, 100, 255), 5)
                    cv.line(frame, Circle[2*i], Circle[(2*i+2)%(2*n)], (255, 0, 255), 5)
                    cv.line(frame, Circle[2*i+1], Circle[(2*i+3)%(2*n)], (0, 0, 255), 5)
            
        if (HideHandle==False):
            #si l'on ne cache pas la poignée, récupérer la liste de points la définissant
            Handle=Liste[0:8]
            for i in range(8):
                #représentation de la poignée
                cv.line(frame, Handle[i], Handle[(i+4)%8], (0, 255, 0), 5)
                cv.line(frame, Handle[i], Handle[(i+2)%8], (0, 255, 0), 5)
                cv.line(frame, Handle[i], Handle[(i+1)%8], (0, 255, 0), 5)
        #représentation du centre de la zone de cuisson de la poêle 
        cv.circle(frame, Centre, 5, (255, 0, 0), 5)
    #modèle 3D simplifié en 4 points qui correspondent respectivement, à l'extrémité de l'objet du coté du manche, à la position du code lue, au centre qui nous intéresse pour l'objet ainsi que son autre extrémité.
    else:
        for i in range(len(Liste)-1):
            cv.line(frame, Liste[i], Liste[i+1], (0, 255, 0), 5)
            cv.circle(frame, Liste[i], 5, (0, 0, 255), 5)
    return frame

#fonction déprécié qui aurait été adapté juste pour la poêle
def plaque (frame,Liste):
    Bords=Liste[0:4]
    Circles=Liste[8:-1]
    for i in range(4):
        cv.line(frame, Handle[i], Handle[(i+1)%4], (0, 255, 0), 5)
    for i in Circles:
        cv.circle(frame, i[0], i[1], (0, 0, 255), 5)
    return frame
