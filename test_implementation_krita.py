import numpy as np
from krita import *
import inspect
from math import pi , sin , cos , acos, atan2, tan

############################ Batterie de test ########################
#getInfo(Krita.instance())

#d = Krita.instance().createDocument(2000, 4000, "Equirectangular live drawing", "RGBA", "U8", "", 200.0)
#Krita.instance().activeWindow().addView(d)

#curDoc = Krita.instance().activeDocument()
#curLayer = curDoc.activeNode()

#b = curDoc.pixelData(0,0,width,height)
#np = np.frombuffer(b,np.dtype(np.uint8))


#pdata=node.projectionPixelData(node.bounds().left(), node.bounds().top(), node.bounds().width(), node.bounds().height())



#curLayer.setPixelData(np.tobytes(),0,0,width,height)
#curDoc.refreshProjection()


##################### Initialisation Krita ###########################
width = 1280
height = 720
curDoc = Krita.instance().createDocument(width, height, "Equirectangular live drawing", "RGBA", "U8", "", 200.0)
Krita.instance().activeWindow().addView(d)


################ Class EquirectangularProjectedlayer (créé layer krita au startup, nparray de projection) ##############

class ERPLayer :
    
    
    def __init__(self,w,h,pw,ph,instance) :
        #create Layer
        #keep Layer ref in class variable
        #create ERImage

    
    def sample(self,s_mat,pprad_x,pprad_y) :
        #sample ERImage for every s_mat
        # Put it in np array
        #tobytes
        #to layer
        

########### Fonctions et classe mathématiques d'utilité générale ###########

class angle :
    rad_angle = 0.0
    mod = 2*pi

    def __init__(self,mod,value) :
        self.mod = mod
        self.rad_angle = value % self.mod

    def add (self,value) :
        self.rad_angle = (self.rad_angle + value) % self.mod
        return self.rad_angle

    def set_angle(self,value) :
        self.rad_angle = value % self.mod


def polar_to_cartesian(polar) :
    r = polar[0]
    teta = polar[1]
    phi = polar[2]

    x = r*sin(teta)*cos(phi)
    y = r*sin(teta)*sin(phi)
    z = r*cos(teta)
    return np.array([x,y,z])

def cartesain_to_polar(cartesian) :
    x = cartesian[0]
    y = cartesian[1]
    z = cartesian[2]

    r = math.sqrt(x*x + y*y + z*z)
    teta = acos(z/r)
    phi = atan2(y,x)
    return np.array([r,teta,phi])

def Compute_screen_coordinates (phiu,tetau,phif,tetaf,w,h,x_dist,y_dist) : 
    u_cart = polar_to_cartesian([1,tetau,phiu])
    #print('ucart',u_cart)
    ux = u_cart[0]
    uy = u_cart[1]
    uz = u_cart[2]

    x_dir = np.array([-uy,ux,0])
    #print('norme xdirn', np.linalg.norm(x_dir))
    x_dir = x_dir/np.linalg.norm(x_dir)
    y_dir = np.array([-ux * uz, -uy * uz, ux*ux + uy*uy])
    y_dir = y_dir/np.linalg.norm(y_dir)

    P1 = u_cart -x_dist*x_dir -y_dist*y_dir
    P2 = u_cart +x_dist*x_dir -y_dist*y_dir
    P3 = u_cart -x_dist*x_dir +y_dist*y_dir
    P4 = u_cart +x_dist*x_dir +y_dist*y_dir

    screen_coordinates = []

    P1_P3 = np.linspace(P1,P3,h)
    P2_P4 = np.linspace(P2,P4,h)

    for i in range(h) :
        #print('interpol 2 :', np.linspace(P1_P3[i],P2_P4[i],w))
        screen_coordinates.append(np.linspace(P1_P3[i],P2_P4[i],w))

    screen_coordinates = np.array(screen_coordinates)

    #print('PS :',PS)
    #print('screen coordinate \n',screen_coordinates)
    return screen_coordinates

################################### Parametres utilisateur ############################################
ratio = 16./9. #Param utilisateur
fov = 2.*pi/6. #Param utilisateur (en radian)


################### Initialisation des variables de calcul de la projection#############################################
phif = fov/2.
tetaf = phif/ratio

x_dist = tan(phif)
y_dist = tan(tetaf)

#Taille de l'image equiprojetée
pimg_w = 4000
pimg_h = 2000

pix_per_rad_x = pimg_w/2*pi
pix_per_rad_y = pimg_h/pi

teta = angle(pi,pi/2)
phi = angle(2*pi,0.0)

print('teta',teta.mod,' ', teta.rad_angle)
print('phi',phi.mod,' ', phi.rad_angle)


#Variable globale des coordonnées dans l'espace des pixel de l'ecran de projection
screen_matrix = Compute_screen_coordinates(phi.rad_angle, teta.rad_angle, phif,tetaf,w,h,x_dist,y_dist)


def ERSampling(pimg) :
    
    #donne en argument
    global screen_matrix
    global pix_per_rad_x
    global pix_per_rad_y
    #dans la classe
    global pimg_h
    global pimg_w
    
    img =  np.zeros(),dtype=np.uint8)
    y = 0
    for L in screen_matrix : #L pour Ligne
        x=0
        for P in L : #P pour pixel
            temp_pol = cartesain_to_polar(P)
            img[x][y] = pimg[int(temp_pol[1]*pix_per_rad_y)%pimg_h][int(temp_pol[2]*pix_per_rad_x)%pimg_w]
            x +=1
        y+=1

