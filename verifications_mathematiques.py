import numpy as np
import sys
import cv2
import pygame
from pygame import surfarray
import math
from math import pi , sin , cos , acos, atan2, tan

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

def Compute_screen_coordinates (phiu,tetau,phif,tetaf,w,h,x_dist,y_dist) : #corriger que ça change tetau de calculer P1 gros nigaud
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
ratio = 16/9 #Param utilisateur
fov = 2*pi/6 #Param utilisateur (en radian)
file_name = 'grille.jpg' #Param Utilisateur

#######################################################################################################

teta = angle(pi,pi/2)
phi = angle(2*pi,0.0)

print('teta',teta.mod,' ', teta.rad_angle)
print('phi',phi.mod,' ', phi.rad_angle)

#Lecture de l'image et de ses dimensions (on veut une image de ratio 2/1, puisque teta va de 0 à pi, et phi de 0 à 2pi)
pimg = cv2.imread(file_name, cv2.IMREAD_ANYCOLOR)
pimg_h , pimg_w = pimg.shape[:2]
pimg_center = np.array([round(pimg_w/2),round(pimg_h/2)])

pix_per_rad_x = pimg_w/2*pi
pix_per_rad_y = pimg_h/pi

print('img dim', pimg_w, ' ', pimg_h)

#Calcul de la resolution d'affichage en fonction du fov et la taille de l'image
phif = fov/2
tetaf = phif/ratio
print('phif : ',phif, 'tetaf : ',tetaf)
w = int(phif/pi * pimg_w)
h = int(2*tetaf/pi * pimg_h)

x_dist = tan(phif)
y_dist = tan(tetaf)
print('x_dist :', x_dist, ' y_dist : ',y_dist)

img = np.zeros((w,h,3),dtype=np.uint8) #creation de l'img buffer'


print('phif : ', phif, ' | tetaf : ', tetaf)

speed = 0.1

pix_per_rad_x = pimg_w/(2*pi)
pix_per_rad_y = pimg_h/pi
print('pix_per_rad_x : ',pix_per_rad_x,' pix_per_rad_y',pix_per_rad_y)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
running = True
dt = 0

input_flag = False
screen_matrix = Compute_screen_coordinates(phi.rad_angle, teta.rad_angle, phif,tetaf,w,h,x_dist,y_dist)
while running:
    input_flag = False
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame


    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        teta.add((-speed*dt))
        input_flag = True
    if keys[pygame.K_DOWN]:
        teta.add((speed*dt))
        input_flag = True
    if keys[pygame.K_RIGHT]:
        phi.add((-speed*dt))
        input_flag = True
    if keys[pygame.K_LEFT]:
        phi.add((speed*dt))
        input_flag = True

    if input_flag :
        #print('phi : ', phi.rad_angle)
        #print('teta : ', teta.rad_angle)
        screen_matrix = Compute_screen_coordinates(phi.rad_angle, teta.rad_angle, phif,tetaf,w,h,x_dist,y_dist)


    #Add equirectangular map sampling after polar conversion of screen coordinate
    y = 0
    for L in screen_matrix : #L pour Ligne
        x=0
        for P in L : #P pour pixel
            temp_pol = cartesain_to_polar(P)
            img[x][y] = pimg[int(temp_pol[1]*pix_per_rad_y)%pimg_h][int(temp_pol[2]*pix_per_rad_x)%pimg_w]
            x +=1
        y+=1


    surfarray.blit_array(screen, img)
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
