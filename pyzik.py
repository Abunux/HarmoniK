#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#-----------------------------------------------------
# 				pyzik.py
#-----------------------------------------------------
#
# v0.1.4
#
# Bibliothèque implémentant des classes pour étudier les notes de musique
# Principe : Génération d'une fonction périodique par somme de ses harmoniques
# Permet de :
#	- Jouer les sons
#	- Tracer leurs courbes avec leurs harmoniques
#	- Fabriquer des gammes comme on veut
#	- Créer des instruments (des notes sur une gamme)
#
# Basée sur :
#	- numpy et scipy pour les calculs et l'export en .wav
#	- pygame pour le rendu sonore
#	- matplotlib pour la visualisation
#
# Licence WTFPL
# Abunux - abunux chez google mail com - 12/11/2010
#

from __future__ import division
from math import *
import time

import pygame
from pygame.locals import *
import scipy.io.wavfile as wav
import numpy
import matplotlib.pyplot as pyplot
from matplotlib.figure import Figure

# Constantes
FREQ_ECH = 44100
AMP_MAX=32767

# Initialisations
pygame.mixer.pre_init(frequency=FREQ_ECH, channels=1)
pygame.mixer.init()
pygame.init()

def debug(message):
	print message
	pass

#~ ## Fonctions d'évolution ##
#~ fonc_evo = {}
#~ def rien(val, x) :
	#~ """Fonction sans évolution"""
	#~ return val
#~ fonc_evo["-"] = rien
#~
#~ def diminue(val, x) :
	#~ """val diminue en fonction de l'avancement x ([0;1]) de 100 à 0%"""
	#~ return val*(1-x)
#~ fonc_evo["D"] = diminue
#~
#~
#~ def sinusoide(val, x) :
	#~ """val augmente puis diminue en fonction de l'avancement x ([0;1]) de façon sinusoïdale,
	#~ de 0 à 100% pour x dans [0;1/2] puis de 100 à 0% pour x dans [1/2;1]"""
	#~ return val*numpy.sin(x*pi)
#~ fonc_evo["S"] = sinusoide
#~
#~ def augmente(val, x) :
	#~ """val augmente en fonction de l'avancement x ([0;1]) de 0 à 100%"""
	#~ return val*x
#~ fonc_evo["A"] = augmente
#~
#~ def ADSR(val,x,amp_max=1,amp_sust=100,tps_att=0.001,tps_dec=0.001,tps_rel=0.001):
	#~ # Enveloppe ADSR : https://secure.wikimedia.org/wikipedia/fr/wiki/Fichier:Enveloppe_ADSR.png
	#~ #
	#~ # Marche pas… (pb avec numpy.where() )
	#~ #
	#~ tps_sust= 1-(tps_att+tps_dec+tps_rel)
	#~ env= numpy.zeros(len(x))
	#~ env=env+ numpy.where(x<=tps_att , amp_max/tps_att*x , 0)
	#~ env=env+ numpy.where((x>tps_att) and (x<=tps_att+tps_dec) , (amp_sust-amp_max)/tps_dec*(x-tps_att)+amp_max, 0)
	#~ env=env+ numpy.where((x>tps_att+tps_dec) and (x<=tps_att+tps_dec+tps_sust) , amp_sust, 0)
	#~ env=env+ numpy.where(x>tps_att+tps_dec+tps_sust , amp_sust/tps_rel*(1-x))
	#~ return val*env


class Note:
	def __init__(self, frequence = 440, amplitude = 100,
					duree = 1, harmoniques = [1], evolution = None,  periodique = numpy.sin):

		debug("[Note] Début de l'initialisation…")

		# Caractéristiques
		self.periodique = periodique # Générateur de signal périodique (sinusoïde, triangle, carré,…)
		self.frequence = frequence
		self.amplitude = amplitude
		self.duree = duree # En secondes

		# On ne pouvait pas utiliser "evolution=qqch" dans le prototype
		# car on a besoin de la longueur de harmoniques
		#~ if evolution == None :
			#~ self.evolution = [rien]*(len(harmoniques)) # Rien est une fonction constante, donc sans évolution
		#~ elif type(evolution) == type("") :
			#~ self.evolution = [fonc_evo[f] for f in evolution]
		#~ else :
			#~ self.evolution = evolution
		#~ self.enveloppe=enveloppe

		# A mettre à jour juste au moment de l'appel
		self.figure=Figure()
		self.harmo_base = [h/sum(harmoniques)*100 for h in harmoniques]

		# Initialisation des paramètres à mettre à jour par la suite
		self.init0()

		debug("[Note] Initialisation terminée")

	def init0(self):

		# harmoniques est une liste contenant l'amplitude relative de chaque
		# harmonique. Celles-ci sont ensuite normalisées avec des valeurs entre
		# 0 et 100 de sorte que f(x) ne dépasse pas amplitude
		#self.harmo_base = harmoniques
		self.harmo = [h/sum(self.harmo_base)*100 for h in self.harmo_base]
		#self.harmo_base = self.harmo
		self.nb_harmo=len(self.harmo)

		# Tableaux de données pour la note finale
		# comme ça c'est fait une fois pour toutes
		# (on va en avoir besoin pour jouer la note et afficher sa courbe)
		self.array_n=[]
		self.array = self.cree_array()

		# Et le mixer pour la note finale
		self.mixer = self.cree_mixer()

		# Les composants graphiques (courbe)
		# (pour l'intégrer après dans GTK)
		self.subplot=self.figure.add_subplot(111)
		#~ self.update_plot()

	# Mutateurs
	# ---------
	# (en prévision de l'interface graphique)

	def set_frequence(self, frequence):
		self.frequence = frequence
		debug("[Note] Fréquence : %.f" % self.frequence)
		self.update()

	def set_amplitude(self, amplitude):
		self.amplitude = amplitude
		debug("[Note] Amplitude : %.f" % self.amplitude)
		self.update()

	def set_duree(self, duree):
		self.duree = duree
		debug("[Note] Durée : %.f" % self.duree)
		self.update()

	def set_harmoniques(self, harmoniques):
		self.harmo_base = harmoniques
		debug("[Note] Harmoniques : %s" % str(self.harmo_base))
		self.update()

	def change_harmonique(self, n, h):
		self.harmo_base[n] = h
		debug("[Note] Harmoniques base : %s" % str(self.harmo_base))
		self.update()

	def add_harmonique(self, h):
		self.harmo_base.append(h)
		debug("[Note] Harmoniques : %s" % str(self.harmo_base))
		self.update()

	def del_harmo(self):
		if len(self.harmo_base) > 1 :
			self.harmo_base.pop()
		debug("[Note] Harmoniques : %s" % str(self.harmo_base))
		self.update()


	def update(self):
		self.init0()
		debug("[Note] Harmoniques : %s" % str(self.harmo))
		debug("[Note] Update paramètres OK")

	# Partie numérique :
	# ------------------
	# Dans ce qui suit, n est le rang de l'harmonique,
	# ce qui va être pratique plus tard pour étudier les harmoniques séparément.
	# n=-1 correspond à la somme finale de toutes les hamoniques

	def cree_array(self, n=-1):
		xmax=int(self.duree*self.frequence)/self.frequence
		x = numpy.arange(0,xmax,1/FREQ_ECH).astype(float)
		if n>=0 :
			if self.harmo[n] != 0 :
				array_n = self.harmo[n]/100*self.amplitude/100*AMP_MAX * self.periodique(2*(n+1)*pi*self.frequence*x)
			else:
				array_n = numpy.zeros(len(x))
			#~ array_n = self.evolution[n](array_n, numpy.linspace(0.0, 1.0, len(array_n)))
			self.array_n.append(numpy.array(array_n , numpy.int16))
			return numpy.array(array_n , numpy.int16)
		else:
			array = numpy.zeros(len(x))
			for k in range(len(self.harmo)):
				array = array + self.cree_array(k)
			#~ array = self.enveloppe(array, numpy.linspace(0.0, 1.0, len(array)))
			return numpy.array(array, numpy.int16)



	# Partie son :
	# ------------

	def cree_mixer(self, n=-1):
		return pygame.sndarray.make_sound(self.array)

	def play(self, n=-1):
		if n >= 0:
			# Permet de jouer séparément une harmonique
			pygame.sndarray.make_sound(self.array_n[n]).play()
		else :
			self.mixer.play()

	def stop(self):
		# Pas besoin de controler la note si on joue juste une harmonique
		self.mixer.stop()

	def wait(self):
		# Pause pendant que le mixer est occupé
		while pygame.mixer.get_busy() :
			pass

	def play_harmo(self):
		# Joue à la suite chaque harmonique, puis le son final
		debug("[Note] Harmoniques à la suite :")
		for n in range(len(self.harmo)):
			if self.harmo[n] != 0:
				debug("[Note] Harmonique : %d ..." % (n+1))
				self.play(n)
				self.wait()
		debug("[Note] Son final ...")
		self.play()
		self.wait()
		debug("[Note] Fin")

	def export_wav(self,nom_fichier):
		wav.write(nom_fichier,FREQ_ECH,self.array)


	# Partie visualisation :
	# ----------------------

	def update_plot(self, nb_periodes_affichees=1, affich_all=True,affich_harmo="0",select_harmo=-1):
		debug("[Note] Update_plot…")
		# Préparation du graphe
		self.subplot.clear()
		x_max = nb_periodes_affichees*FREQ_ECH/self.frequence
		x = numpy.arange(0, x_max/FREQ_ECH, 1/FREQ_ECH)
		gris_min, gris_max = 0.6, 0.95 # Niveaux de gris pour le graphe des harmoniques

		# Plot des harmoniques
		nb_harmo = len(self.harmo)
		if nb_harmo > 1:
			for n in range(nb_harmo):
				if self.harmo[n] != 0 and ( affich_harmo == "0" or affich_harmo[n] == "1"):
					y = self.array_n[n][0:len(x)]/AMP_MAX*100
					if n == select_harmo :
						couleur='red'
					else:
						couleur = str(gris_max-(nb_harmo-n)*(gris_max-gris_min)/nb_harmo)
					self.subplot.plot(x, y, color=couleur)

		# Plot de la courbe finale
		if affich_all:
			y = self.array[0:len(x)]/AMP_MAX*100
			self.subplot.plot(x, y, color='black')
		self.subplot.axhline()
		self.subplot.set_xlim(0, x_max/FREQ_ECH)
		self.subplot.set_ylim(-self.amplitude,self.amplitude)
		debug("[Note] Update_plot OK")


	#  ----------  À Supprimer de la version finale  ----------------------------------
	def plot(self, nb_periodes_affichees = 1):

		#pyplot.axes(self.subplot) 	# Marche pas : "ValueError: Unknown element o"
		#pyplot.show()
		self.plot2(nb_periodes_affichees)

	def plot2(self, nb_periodes_affichees = 1):
		# Uniquement pour les tests sans interface graphique
		# redondant avec self.update_plot() mais ça ne marche pas pour
		# "charger" self.subplot dans pyplot (voir self.plot() ci-dessus)

		# Préparation du graphe
		x_max = nb_periodes_affichees*FREQ_ECH/self.frequence
		x = numpy.arange(0, x_max, 1)
		gris_min, gris_max = 0.6, 0.95 # Niveaux de gris pour le graphe des harmoniques
		pyplot.axhline(y=0, xmin=0, xmax=x_max)

		# Plot des harmoniques
		nb_harmo = len(self.harmo)
		if nb_harmo > 1:
			for n in range(nb_harmo):
				if self.harmo[n] != 0:
					y = self.cree_array(n)[0:len(x)]
					niv_gris = gris_min+(nb_harmo-n)*(gris_max-gris_min)/nb_harmo
					pyplot.plot(x, y, color=str(niv_gris))

		# Plot de la courbe finale
		y = self.array[0:len(x)]
		pyplot.plot(x, y, color='black')

		pyplot.show()
	#  --------------------------------------------------------------------------------


class GammeTemperee:
	# Ici on va juste définir les noms des notes de la gamme et leurs fréquences
	# Ce sera pratique pour adapter facilement à d'autres gammes
	# (gammes orientales, gammes à 24 notes, bref tout et n'importe quoi…)
	NOTES_GAMME = ["DO","DOd","RE","REd","MI", "FA",
					"FAd", "SOL", "SOLd","LA", "LAd", "SI"]
	LA3_FREQ = 440.0
	# On passe de la fréquence d'une note à la fréquence du demi ton suivant
	# en multipliant par racine12ème(2) (une bonne vieille suite géométrique)
	COEFF = pow(2, 1/12)

	def __init__(self, octaves = [3,3]):
		self.frequence = {} # Dictionnaire du type {"Nom_note" : Frequence}
		self.liste_notes=[] # Contient la liste ordonnée des noms de toutes les notes

		# octaves correspond à la plage d'octaves à laquelle on veut avoir accès
		# Par exemple octaves=[3,4] créera les notes de DO3 à SI4
		self.octaves = [max(octaves[0], 1) , min(octaves[1], 6)]

		self.cree_notes()

	def cree_notes(self):
		debug("[Gamme] Création de la gamme…")
		si0_freq = self.LA3_FREQ / pow(self.COEFF, 34)
		for k in range( (self.octaves[0]-1)*12 , self.octaves[1]*12 ):
			nom = self.NOTES_GAMME[k%12] + str( int(k/12) + 1)
			freq = si0_freq * pow(self.COEFF, k+1)
			self.frequence.update({nom : freq})
			self.liste_notes.append(nom)

		# Test : OK
		debug("[Gamme] Notes de la gamme :")
		for nom in self.liste_notes:
			debug( "    %s \t: %.2f" % (nom, self.frequence[nom]))



class Instru:
	def __init__(self, amplitude = 32767, duree = 1, harmoniques = [1],
					octaves = [3,3], gamme = "GammeTemperee"):
		self.amplitude = amplitude
		self.duree = duree
		self.harmoniques = harmoniques
		self.gamme = eval(gamme)(octaves) # Pas très élégant mais pratique…
		self.touche = {} 	# simule les touches du clavier de l'instru :
							# C'est un dico du type {"Nom" : Note}
		self.cree_touches()

	def cree_touches(self):
		for nom, freq in  self.gamme.frequence.items():
			debug("[Instru] Création de la touche %s" % nom)
			newtouche = Note(frequence = freq, harmoniques = self.harmoniques,
								amplitude =self.amplitude,  duree = self.duree)
			self.touche.update({nom : newtouche})
			del newtouche

	def play(self,note):
		self.touche[note].play()
		debug("[Instru] Note jouée : %s" % note)

	def stop(self,note):
		self.touche[note].stop()

	def play_harmo(self,note):
		self.touche[note].play_harmo()

	def wait(self):
		while pygame.mixer.get_busy() :
			pass

	def plot(self,note):
		self.touche[note].plot()




if __name__ == "__main__":
	def binaire(x) :
		return numpy.where(numpy.sin(x)>=0, 1, -1)

	def bizarre(x) :
		return numpy.sin(x)/(numpy.cos(x)**2+0.01)

	def pics(x) :
		return numpy.sin(x)/(numpy.cos(x)+2)**12

#~
	#~ n = Note(392, harmoniques = [50, 50], evolution = [rien, rien, sinusoide])
	#~ n.play()
	#~ n.wait()
#~
	#~ n = Note(440, harmoniques = [50, 50], evolution = "--S", periodique=binaire)
	#~ n.play()
	#~ n.wait()
#~
	#~ n = Note(349, harmoniques = [40, 10, 25, 10, 5], evolution = [rien, diminue, augmente, diminue, rien, sinusoide])
	#~ n.play()
	#~ n.wait()
#~
	#~ n = Note(175, harmoniques = [40, 10, 25, 10, 5], evolution = [rien, diminue, augmente, diminue, rien, sinusoide], periodique=pics)
	#~ n.play()
	#~ n.wait()
	#~ #n.plot()

	n = Note(262, harmoniques = [100, 110, 105, 110, 100, 90, 80, 70, 45, 30, 15, 10], \
		evolution = [diminue, diminue, diminue, rien, sinusoide, sinusoide, sinusoide, sinusoide, augmente, augmente, augmente, augmente], enveloppe=rien) # Flûte
	n.play()
	n.wait()

	#~ def binaire(x) :
		#~ return numpy.where(numpy.sin(x)>=0, 1, -1)
#~
	#~ n = Note(440, harmoniques = [50, 50], evolution = [rien, rien, sinusoide])
	#~ n.play()
	#~ n.wait()
#~
	#~ n = Note(440, harmoniques = [50, 50], evolution = "--S", periodique=binaire)
	#~ n.play()
	#~ n.wait()
	#~ n.plot()
#~
	#~ n = Note(262, harmoniques = [40, 10, 25, 10, 5], evolution = [rien, diminue, augmente, diminue, rien, sinusoide])
	#~ n.play()
	#~ n.wait()
#~
	#~ n = Note(262, harmoniques = [100, 110, 105, 110, 100, 90, 80, 70, 45, 30, 15, 10], \
		#~ evolution = [rien, diminue, diminue, diminue, rien, sinusoide, sinusoide, sinusoide, sinusoide, augmente, augmente, augmente, augmente]) # Flûte
	#~ n.play()
	#~ n.wait()

	pass

