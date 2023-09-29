import json
import numpy as np

#programme qui permet de créer une librairie directement basé sur les points du modèle afin de limiter le temps de calcul au démarrage du main
#possède également des modèles abrégés en 4 points afin de faciliter les calculs

#initialiser les librairies
jsonPo='{"Library":[]}'
Library = json.loads(jsonPo)
Light = json.loads(jsonPo)
Abridged = json.loads(jsonPo)

#librairies des dimensions qui sert à créer rapidement de nouveaux modèles en modifiant et en copiant ses composantes
jsonPo={"nom":"","nature":"set","dimensions":{"Dimensions":65,"Unité":"mm"}}
Library["Library"].append(jsonPo)

jsonPo={"nom":"Plaque","nature":"Plaque","dimensions":{"QR/droite/gauche":80.0,"QR/haut/bas":120.0,"Longeur":200,"Largeur":200,"Hauteur":5,"Unité":"mm"},"cercles":[{"PosX":50,"PosY":90.0,"Rayon":30.0,"Unité":"mm"},{"PosX":-40,"PosY":90,"Rayon":50.0,"Unité":"mm"},{"PosX":0.0,"PosY":-60.0,"Rayon":70.0,"Unité":"mm"}]}
Library["Library"].append(jsonPo)

jsonPo={"nom":"poele 1 personne","nature":"poêle","dimensions":{"QR/Centre":200,"QR/Poignée":75,"LargeurPoignée":45,"rotationPoignée":5,"RayonCentre":79,"RayonBords":100,"Hauteur":30,"Unité":"mm"}}
Library["Library"].append(jsonPo)

jsonPo={"nom":"Wok 1 personne","nature":"poêle","dimensions":{"QR/Centre":150,"QR/Poignée":200,"LargeurPoignée":35,"rotationPoignée":15,"RayonCentre":89,"RayonBords":120,"Hauteur":50,"Unité":"mm"}}
Library["Library"].append(jsonPo)

jsonPo={"nom":"Louche","nature":"Louche","dimensions":{"QR/Centre":55,"QR/Poignée":100,"LargeurPoignée":10,"rotationPoignée":0,"RayonCentre1":20,"RayonBords1":30,"RayonCentre2":35,"RayonBords2":45,"Hauteur":15,"Unité":"mm"}}
Library["Library"].append(jsonPo)

jsonPo={"nom":"Spatule","nature":"Spatule","dimensions":{"QR/Centre":55,"QR/Poignée":100,"LargeurPoignée":10,"rotationPoignée":0,"RayonBords1":30,"RayonBords2":45,"Hauteur":15,"Unité":"mm"}}
Library["Library"].append(jsonPo)

jsonPo={"nom":"Curseur","nature":"Curseur","dimensions":{"QR/droite/gauche":0.0,"QR/haut/bas":0.0,"LongeurPoignée":15,"LargeurPoignée":10,"RayonBords1":15,"RayonBords2":15,"Hauteur":15,"HauteurCurseur":5,"Unité":"mm"}}
Library["Library"].append(jsonPo)

#for i in Library['Library']:
    #print(i)

#créer et dumper la librairie des dimensions
library = json.dumps(Library,indent=4)
#print(Library)
with open("Library.json", "w") as outfile:
    outfile.write(library)
    
#nombre de points pour décrire un cercle    
n=16
#initialiser l'identifiant des objets
id=0
#créer les librairies contenant directent les points à partir de celle des dimensions
for z in Library["Library"]:
    #print(z)
    #nom et nature à mettre dans les nouvelles coordonnées
    nom=z["nom"]
    nature=z["nature"]
    
    #initialser la structure de base pour les bibliothéques
    test={"nom":nom,"nature":nature,"Dimensions":[]}
    testA={"nom":nom,"nature":nature,"Dimensions":[]}
    #test=json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=4)
    #print(test)
    #construction du modèle si la nature est "set"
    if (nature=="set"):
        nom=None
        dimensions=int(z["dimensions"]["Dimensions"])
        D=int(dimensions/2)
        test["Dimensions"].append({"x":-D,"y":D,"z":0,"w":1})
        test["Dimensions"].append({"x":D,"y":D,"z":0,"w":1})
        test["Dimensions"].append({"x":D,"y":-D,"z":0,"w":1})
        test["Dimensions"].append({"x":-D,"y":-D,"z":0,"w":1})
        testA["Dimensions"].append({"x":-D,"y":D,"z":0,"w":1})
        testA["Dimensions"].append({"x":D,"y":D,"z":0,"w":1})
        testA["Dimensions"].append({"x":D,"y":-D,"z":0,"w":1})
        testA["Dimensions"].append({"x":-D,"y":-D,"z":0,"w":1})
    
    #construction du modèle si la nature est "poêle"
    if (nature=="poêle"):
        QC=int(z["dimensions"]["QR/Centre"])
        QP=int(z["dimensions"]["QR/Poignée"])
        LP=int(z["dimensions"]["LargeurPoignée"])
        RP=int(z["dimensions"]["rotationPoignée"])
        RP=-RP*np.pi/180
        RC=int(z["dimensions"]["RayonCentre"])
        RB=int(z["dimensions"]["RayonBords"])
        H=int(z["dimensions"]["Hauteur"])
        unit=(z["dimensions"]["Unité"])
        centre_poeleY=-QC*np.cos(RP)
        points=[]
        alpha=(2*np.pi)/n
        j=(-QC+RB)*np.cos(RP)
        for k in [-np.sin(RP)*QC,H-np.sin(RP)*QC]:
            for i in [-LP/2,+LP/2]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        j=QP*np.cos(RP)
        for k in [np.sin(RP)*QP,H+np.sin(RP)*QP]:
            for i in [-LP/2,+LP/2]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        for i in range(n):
            test["Dimensions"].append({"x":int(np.cos(alpha*i)*RB),"y":int(centre_poeleY+np.sin(alpha*i)*RB),"z":-np.sin(RP)*QC,"w":1})
            test["Dimensions"].append({"x":int(np.cos(alpha*i)*RC),"y":int(centre_poeleY+np.sin(alpha*i)*RC),"z":H-np.sin(RP)*QC,"w":1})
        test["Dimensions"].append({"x":0,"y":int(centre_poeleY),"z":H-np.sin(RP)*QC,"w":1})
        
        testA["Dimensions"].append({"x":0,"y":(-QC+RB)*np.cos(RP),"z":(H/2)-np.sin(RP)*QC,"w":1})
        testA["Dimensions"].append({"x":0,"y":QP*np.cos(RP),"z":(H/2)+np.sin(RP)*QP,"w":1})
        testA["Dimensions"].append({"x":0,"y":int(centre_poeleY),"z":(H/2)-np.sin(RP)*QC,"w":1})
        testA["Dimensions"].append({"x":0,"y":int(centre_poeleY+RB),"z":(H/2)-np.sin(RP)*QC,"w":1})
        
    #construction du modèle si la nature est "Louche"
    if (nature=="Louche"):
        QC=int(z["dimensions"]["QR/Centre"])
        QP=int(z["dimensions"]["QR/Poignée"])
        LP=int(z["dimensions"]["LargeurPoignée"])
        RP=int(z["dimensions"]["rotationPoignée"])
        RP=-RP*np.pi/180
        RC1=int(z["dimensions"]["RayonCentre1"])
        RB1=int(z["dimensions"]["RayonBords1"])
        RC2=int(z["dimensions"]["RayonCentre2"])
        RB2=int(z["dimensions"]["RayonBords2"])
        H=int(z["dimensions"]["Hauteur"])
        unit=(z["dimensions"]["Unité"])
        centre_poeleY=-QC*np.cos(RP)
        points=[]
        alpha=(2*np.pi)/n
        j=(-QC+RB2)*np.cos(RP)
        for k in [-np.sin(RP)*QC,H-np.sin(RP)*QC]:
            for i in [-LP/2,+LP/2]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        j=QP*np.cos(RP)
        for k in [np.sin(RP)*QP,H+np.sin(RP)*QP]:
            for i in [-LP/2,+LP/2]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        for i in range(n):
            test["Dimensions"].append({"x":int(np.cos(alpha*i)*RB1),"y":int(centre_poeleY+np.sin(alpha*i)*RB2),"z":-np.sin(RP)*QC,"w":1})
            test["Dimensions"].append({"x":int(np.cos(alpha*i)*RC1),"y":int(centre_poeleY+np.sin(alpha*i)*RC2),"z":H-np.sin(RP)*QC,"w":1})
        test["Dimensions"].append({"x":0,"y":int(centre_poeleY),"z":H-np.sin(RP)*QC,"w":1})   
        
        testA["Dimensions"].append({"x":0,"y":(-QC+RB2)*np.cos(RP),"z":(H/2)-np.sin(RP)*QC,"w":1})
        testA["Dimensions"].append({"x":0,"y":QP*np.cos(RP),"z":(H/2)+np.sin(RP)*QP,"w":1})
        testA["Dimensions"].append({"x":0,"y":int(centre_poeleY),"z":(H/2)-np.sin(RP)*QC,"w":1})
        testA["Dimensions"].append({"x":0,"y":int(centre_poeleY+RB1),"z":(H/2)-np.sin(RP)*QC,"w":1})
     
    #construction du modèle si la nature est "Spatule"
    if (nature=="Spatule"):
        QC=int(z["dimensions"]["QR/Centre"])
        QP=int(z["dimensions"]["QR/Poignée"])
        LP=int(z["dimensions"]["LargeurPoignée"])
        RP=int(z["dimensions"]["rotationPoignée"])
        RP=-RP*np.pi/180
        RB1=int(z["dimensions"]["RayonBords1"])
        RB2=int(z["dimensions"]["RayonBords2"])
        H=int(z["dimensions"]["Hauteur"])
        unit=(z["dimensions"]["Unité"])
        centre_poeleY=-QC*np.cos(RP)
        points=[]
        alpha=(2*np.pi)/n
        j=(-QC+RB2)*np.cos(RP)
        for k in [-np.sin(RP)*QC,H-np.sin(RP)*QC]:
            for i in [-LP/2,+LP/2]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        j=QP*np.cos(RP)
        for k in [np.sin(RP)*QP,H+np.sin(RP)*QP]:
            for i in [-LP/2,+LP/2]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        for i in range(n):
            test["Dimensions"].append({"x":-RB1,"y":int(centre_poeleY+(2*i/(n-1)-1)*RB2),"z":int(H/2-np.sin(RP)*QC),"w":1})
            test["Dimensions"].append({"x":int(RB1),"y":int(centre_poeleY+(2*i/(n-1)-1)*RB2),"z":int(H/2-np.sin(RP)*QC),"w":1})
        test["Dimensions"].append({"x":0,"y":int(centre_poeleY),"z":H/2-np.sin(RP)*QC,"w":1}) 

        testA["Dimensions"].append({"x":0,"y":(-QC+RB2)*np.cos(RP),"z":(H/2)-np.sin(RP)*QC,"w":1})
        testA["Dimensions"].append({"x":0,"y":QP*np.cos(RP),"z":(H/2)+np.sin(RP)*QP,"w":1})
        testA["Dimensions"].append({"x":0,"y":int(centre_poeleY),"z":(H/2)-np.sin(RP)*QC,"w":1})
        testA["Dimensions"].append({"x":0,"y":int(centre_poeleY+RB2),"z":(H/2)-np.sin(RP)*QC,"w":1})

    #construction du modèle si la nature est "Curseur"
    if (nature=="Curseur"):
        Qdg=float(z["dimensions"]["QR/droite/gauche"])
        Qhb=float(z["dimensions"]["QR/haut/bas"])
        LoP=int(z["dimensions"]["LongeurPoignée"])
        LaP=int(z["dimensions"]["LargeurPoignée"])
        RB1=int(z["dimensions"]["RayonBords1"])
        RB2=int(z["dimensions"]["RayonBords2"])
        H=int(z["dimensions"]["Hauteur"])
        Hc=int(z["dimensions"]["HauteurCurseur"])
        unit=(z["dimensions"]["Unité"])
        centreX=RB2*Qdg
        centreY=RB2*Qhb
        points=[]
        alpha=(2*np.pi)/n
        j=-LoP+centreY
        for k in [-H,-H-Hc]:
            for i in [-LaP/2+centreX,+LaP/2+centreX]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        j=+LoP+centreY
        for k in [-H,-H-Hc]:
            for i in [-LaP/2+centreX,+LaP/2+centreX]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        for i in range(n):
            test["Dimensions"].append({"x":int(np.cos(alpha*i)*RB1+centreX),"y":int(np.sin(alpha*i)*RB1+centreY),"z":0,"w":1})
            test["Dimensions"].append({"x":int(np.cos(alpha*i)*RB2+centreX),"y":int(np.sin(alpha*i)*RB2+centreY),"z":-H,"w":1})
        test["Dimensions"].append({"x":0,"y":0,"z":-H,"w":1}) 
       
        testA["Dimensions"].append({"x":0,"y":-LoP+centreY,"z":(-H/2),"w":1})
        testA["Dimensions"].append({"x":0,"y":+LoP+centreY,"z":(-H/2),"w":1})
        testA["Dimensions"].append({"x":centreX,"y":int(centreY),"z":(-H/2),"w":1})
        testA["Dimensions"].append({"x":centreX,"y":int(centreY+RB2),"z":(-H/2),"w":1})
    
    #construction du modèle si la nature est "Plaque"
    if (nature=="Plaque"):
        centreX=float(z["dimensions"]["QR/droite/gauche"])
        centreY=float(z["dimensions"]["QR/haut/bas"])
        LoP=int(z["dimensions"]["Longeur"])
        LaP=int(z["dimensions"]["Largeur"])
        H=int(z["dimensions"]["Hauteur"])
        unit=(z["dimensions"]["Unité"])
        points=[]
        alpha=(2*np.pi)/n
        j=-LoP+centreY
        for k in [-H,0]:
            for i in [-LaP/2+centreX,+LaP/2+centreX]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})
        j=+LoP+centreY
        for k in [-H,0]:
            for i in [-LaP/2+centreX,+LaP/2+centreX]:
                test["Dimensions"].append({"x":int(i),"y":j,"z":k,"w":1})

        j=-LoP+centreY
        for i in [-LaP/2+centreX,+LaP/2+centreX]:
            testA["Dimensions"].append({"x":int(i),"y":j,"z":-(H/2),"w":1})
        j=+LoP+centreY
        for i in [-LaP/2+centreX,+LaP/2+centreX]:
            testA["Dimensions"].append({"x":int(i),"y":j,"z":-(H/2),"w":1})

        for w in z["cercles"]:
                test["Dimensions"].append({"x":int(np.cos(alpha*i)*float(w["Rayon"])+float(w["PosX"])+centreX),"y":int(np.sin(alpha*i)*float(w["Rayon"])+float(w["PosY"])+centreY),"z":0,"w":1})
                test["Dimensions"].append({"x":int(np.cos(alpha*i)*float(w["Rayon"])+float(w["PosX"])+centreX),"y":int(np.sin(alpha*i)*float(w["Rayon"])+float(w["PosY"])+centreY),"z":-H,"w":1})
                testA["Dimensions"].append({"x":float(w["PosX"])+centreX,"y":float(w["PosY"])+centreY,"z":-(H/2),"w":1})
                testA["Dimensions"].append({"x":float(w["PosX"])+centreX+float(w["Rayon"]),"y":float(w["PosY"])+centreY+float(w["Rayon"]),"z":-(H/2),"w":1})
        test["Dimensions"].append({"x":0,"y":0,"z":-H,"w":1})
        
        
    #ajout de la structure actuelle à la librairie de points normale et abrégé    
    Light["Library"].append(test)
    Abridged["Library"].append(testA)
    id+=1
    
#écriture de la librairie des points
Light=json.dumps(Light, indent=4)
with open("Light.json", "w") as outfile:
    outfile.write(Light)

#écriture de la librairie des points abrégés
Abridged=json.dumps(Abridged, indent=4)
with open("Abridged.json", "w") as outfile:
    outfile.write(Abridged)
