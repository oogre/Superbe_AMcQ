Description
==============

Unexpected Beauty :
--------------
A l'aide d'un capteur ultra son un Arduino détecte une présence. Il envoie 2 commandes DMX : allumer une lampe + éteindre une autre lampe.
Lorsque le capteur ne capte plus de présence : revenir à l'état initial. Chaque variation doit être fluide.

The Cabinet of Curiosities :
--------------
Le signal vidéo sortant de ce système est diffusé sur 3 écrans parallèlement :
Un RaspberryPI diffuse une vidéo, lorsque le RPI reçoit un signal électrique par ces pinGPIO, il fadeOut la vidéo courante et fadeIn la vidéo correspondante au signal électrique (2 signaux électrique différents contrôlent la lecture de 2 vidéos différentes). L'arrêt de tout signal électrique provoque le retour à l'état initial.
Les vidéo diffuse du son. Ce son doit être fadeIn/Out en suivant la vidéo ou avec un décalage temporelle.
Chaque variation (audio/video) doit être fluide.
Le signal électrique est un signal IO généré par un Arduino connecté en Analog à deux balances électronique. Cet Arduino contrôle aussi l'éclairage de la pièce en DMX.

Installation
==============
RPI :
--------------
- Install <a href="https://www.raspberrypi.org/downloads/raspbian/">Raspbian</a> Release date: 2015-05-05 
- Install <a href="http://omxplayer.sconde.net/">omxplayer</a> omxplayer_0.3.6~git20150710~4d8ffd1_armhf.deb



Utilisation
==============
- Demarrer une vidéo : omxplayer -b -o local movie.mov
	- -b : background noir
	- -o local : sortie audio sur le jack audio

- fadeIn : python omxcontroler.py -i 3000
- fadeOut : python omxcontroler.py -o 3000

