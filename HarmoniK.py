#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------------------
#  					HarmoniK
#--------------------------------------------------------------------------
VERSION = "v0.1.2"
#
# Petit soft éducatif pour étudier les harmoniques d'une note de musique
#
#
# Licence WTFPL
# Abunux - abunux chez google mail com - 12/11/2010
#


import pygtk
pygtk.require("2.0")
import gtk

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

import numpy

from pyzik import *

class Main:
	#---------------------------------------------------------------------------
	#		Initialisation
	#---------------------------------------------------------------------------
	def __init__(self):
		self.note = Note(duree = 0.5, harmoniques=[1])

		self.mainWindow()
		self.win.show_all()

		self.update_plot()
	#---------------------------------------------------------------------------
	#		Création de la fenêtre principale
	#---------------------------------------------------------------------------
	def mainWindow(self):
		self.win = gtk.Window()
		self.win.set_default_size(1000,500)
		self.win.set_title("HarmoniK "+VERSION)
		#~ self.win.set_icon_from_file("HarmoniK.png")
		self.win.connect("destroy", lambda x: gtk.main_quit())
		self.win.connect("key-press-event",self.play)

		# Layout de la main window
		self.vboxMain = gtk.VBox()
		self.win.add(self.vboxMain)
		self.menuBar = gtk.MenuBar()
		self.vboxMain.pack_start(self.menuBar, expand=False)

		self.notebookMain = gtk.Notebook()
		self.hpanedMainHarmo = gtk.HPaned()

		# 3 lignes à Commenter/décommenter pour les onglets
		#~ self.notebookMain.append_page(self.hpanedMainHarmo,gtk.Label("Harmoniques"))
		#~ self.vboxMain.pack_start(self.notebookMain)
		self.vboxMain.pack_start(self.hpanedMainHarmo)

		self.vboxGauche = gtk.VBox()
		self.vboxDroite = gtk.VBox()

		self.hpanedMainHarmo.pack1(self.vboxGauche, resize=False, shrink=False)
		self.hpanedMainHarmo.pack2(self.vboxDroite, resize=True, shrink=False)
		self.hpanedMainHarmo.set_position(400)

		#-----------------------------------------------------------------------

		# Menu
		#	Menu Fichier
		self.menuitemFichier = gtk.MenuItem(label="Fichier")
		self.menuBar.append(self.menuitemFichier)
		self.menuFichier = gtk.Menu()
		self.menuitemFichier.set_submenu(self.menuFichier)

		#		Charger
		self.menuitemOpen = gtk.ImageMenuItem(stock_id=gtk.STOCK_OPEN)
		self.menuitemOpen.connect("activate",self.open)
		self.menuFichier.append(self.menuitemOpen)

		#		Sauver
		self.menuitemSave = gtk.ImageMenuItem(stock_id=gtk.STOCK_SAVE)
		self.menuitemSave.connect("activate",self.save)
		self.menuFichier.append(self.menuitemSave)

		#		Séparateur
		self.menuFichier.append(gtk.SeparatorMenuItem())

		#		Exporter
		self.menuitemExport = gtk.MenuItem("Exporter en .wav")
		self.menuitemExport.connect("activate",self.export_wav)
		self.menuFichier.append(self.menuitemExport)

		#		Séparateur
		self.menuFichier.append(gtk.SeparatorMenuItem())

		#		Quitter
		self.menuitemQuit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
		self.menuitemQuit.connect("activate", lambda x: gtk.main_quit())
		self.menuFichier.append(self.menuitemQuit)

		#	Menu Aide
		self.menuitemAide = gtk.MenuItem(label="Aide")
		self.menuBar.append(self.menuitemAide)
		self.menuAide = gtk.Menu()
		self.menuitemAide.set_submenu(self.menuAide)
		#		APropos
		self.menuitemAPropos =gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT)
		self.menuitemAPropos.connect("activate", self.aPropos)
		self.menuAide.append(self.menuitemAPropos)

		# ----------------------------------------------------------------------

		# Layout de la partie droite
		#	Courbe
		self.canvas = FigureCanvas(self.note.figure)
		self.toolbar = NavigationToolbar(self.canvas, self.win)

		#	Curseur nombre de périodes
		self.hboxPeriodes = gtk.HBox()
		self.scaleNbPeriodes = gtk.HScale()
		self.scaleNbPeriodes.set_range(1,10)
		self.scaleNbPeriodes.set_increments(1,1)
		self.scaleNbPeriodes.set_digits(0)
		self.scaleNbPeriodes.set_value(1)
		self.scaleNbPeriodes.connect("button-release-event",self.update_plot)
		self.lbPeriodes = gtk.Label("Nombre de périodes à afficher : ")
		self.lbPeriodes.set_alignment(0,0.8)
		self.hboxPeriodes.pack_start(self.lbPeriodes, expand=False)
		self.hboxPeriodes.pack_start(self.scaleNbPeriodes)

		self.vboxDroite.pack_start(self.toolbar, expand=False)
		self.vboxDroite.pack_start(self.canvas)
		self.vboxDroite.pack_start(self.hboxPeriodes, expand=False)

		#-----------------------------------------------------------------------

		# Layout de la partie gauche
		self.tableParam = gtk.Table(5,2)
		self.vboxHarmo = gtk.VBox()
		self.vboxGauche.pack_start(self.tableParam, expand=False)
		self.vboxGauche.pack_start(self.vboxHarmo)

		# 	Partie haut : Paramètres
		self.lbFrequence = gtk.Label(" Fréquence : ")
		self.lbFrequence.set_alignment(0,1)
		self.spinFrequence = gtk.SpinButton()
		self.spinFrequence.set_range(1,FREQ_ECH)
		self.spinFrequence.set_increments(1,10)
		self.spinFrequence.set_digits(0)
		#~ self.spinFrequence.set_text(str(self.note.frequence))
		self.spinFrequence.set_value(self.note.frequence)
		self.spinFrequence.set_tooltip_text("Fréquence en Hz (entre 0 et " + str(FREQ_ECH)\
			+")\nlune1, lune2,..., lune6 pour jouer 'Au clair de la lune'")
		self.spinFrequence.connect("focus-out-event",self.update_param_base)
		self.spinFrequence.connect("activate",self.update_param_base)
		self.spinFrequence.connect("change-value",self.update_param_base)
		self.spinFrequence.connect("button-release-event",self.update_param_base)

		self.lbAmplitude = gtk.Label(" Amplitude : ")
		self.lbAmplitude.set_alignment(0,1)
		self.scaleAmplitude = gtk.HScale()
		self.scaleAmplitude.set_range(0,100)
		self.scaleAmplitude.set_increments(1,5)
		self.scaleAmplitude.set_value(self.note.amplitude)
		self.scaleAmplitude.set_tooltip_text("Amplitude du signal (100 correspond en fait à" + str(AMP_MAX) + " pour le mixer)")
		self.scaleAmplitude.connect("button-release-event",self.update_param_base)

		self.lbDuree = gtk.Label(" Durée : ")
		self.lbDuree.set_alignment(0,1)
		self.scaleDuree = gtk.HScale()
		self.scaleDuree.set_range(0,5)
		self.scaleDuree.set_increments(0.1,0.5)
		self.scaleDuree.set_digits(1)
		self.scaleDuree.set_value(self.note.duree)
		self.scaleDuree.set_tooltip_text("Durée du signal (en secondes)")
		self.scaleDuree.connect("button-release-event",self.update_param_base)

		self.btPlay = gtk.Button(stock=gtk.STOCK_MEDIA_PLAY)
		self.btPlay.set_tooltip_text("Joue le son (barre d'espace)")
		self.btPlay.connect("clicked",self.play)
		self.chAll = gtk.CheckButton()
		self.chAll.set_active(True)
		self.chAll.set_tooltip_text("Affiche ou non la courbe du son")
		self.chAll.connect("toggled",self.update_affich_all)
		self.hboxPlay= gtk.HBox()
		self.hboxPlay.pack_start(self.btPlay)
		self.hboxPlay.pack_start(self.chAll, expand=False)


		self.tableParam.attach(self.lbFrequence,0,1,0,1,yoptions=gtk.SHRINK)
		self.tableParam.attach(self.spinFrequence,1,2,0,1,yoptions=gtk.SHRINK)

		self.tableParam.attach(self.lbAmplitude,0,1,2,3,yoptions=gtk.SHRINK)
		self.tableParam.attach(self.scaleAmplitude,1,2,2,3,yoptions=gtk.SHRINK)

		self.tableParam.attach(self.lbDuree,0,1,3,4,yoptions=gtk.SHRINK)
		self.tableParam.attach(self.scaleDuree,1,2,3,4,yoptions=gtk.SHRINK)
		self.tableParam.attach(self.hboxPlay,0,2,4,5,yoptions=gtk.SHRINK)


		# 	Partie bas : Harmoniques
		# 		Les 2 boutons du bas :
		self.hbboxAddRemoveHarmo = gtk.HButtonBox()
		self.hbboxAddRemoveHarmo.set_layout(gtk.BUTTONBOX_SPREAD)
		self.vboxHarmo.pack_end(self.hbboxAddRemoveHarmo, expand=False)

		self.btAdd = gtk.Button(stock=gtk.STOCK_ADD)
		self.btAdd.set_tooltip_text("Ajoute une harmonique à la liste")
		self.btAdd.connect("clicked",self.add_harmo)
		self.hbboxAddRemoveHarmo.pack_start(self.btAdd)

		self.btRemove = gtk.Button(stock=gtk.STOCK_REMOVE)
		self.btRemove.set_tooltip_text("Enlève la dernière harmonique de la liste")
		self.btRemove.connect("clicked",self.remove_harmo)
		self.hbboxAddRemoveHarmo.pack_start(self.btRemove)

		self.btDelAll = gtk.Button(stock=gtk.STOCK_DELETE)
		self.btDelAll.set_tooltip_text("Supprime toutes les harmoniques de la liste")
		self.btDelAll.connect("clicked",self.del_harmo_all)
		self.hbboxAddRemoveHarmo.pack_start(self.btDelAll)

		# 		La zone de réglage des harmoniques
		self.scrollHarmo = gtk.ScrolledWindow()
		self.scrollHarmo.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		self.vboxHarmo.pack_end(self.scrollHarmo)
		self.viewHarmo = gtk.Viewport()
		self.scrollHarmo.add(self.viewHarmo)
		self.vboxListHarmo = gtk.VBox()
		self.viewHarmo.add(self.vboxListHarmo)

		self.hboxHarmo = []
		self.lbHarmo = []
		self.scaleHarmo = []
		self.btPlayHarmo = []
		self.chHarmo= []
		self.nb_harmo = 0
		self.affich_harmo = "0"
		self.select_harmo = -1
		self.affich_all=True


		for n in range(len(self.note.harmo)):
			self.add_harmo()


	#---------------------------------------------------------------------------
	#		Fonctions du programme
	#---------------------------------------------------------------------------

	#~ def test(self, widget, *arg ):
		#~ print "Test"

	# ---------Gestion des harmoniques (ajout, suppression) --------------------

	def add_harmo(self, widget=None, *arg):
		if (self.nb_harmo+1)*self.note.frequence >= FREQ_ECH :
			return

		n = self.nb_harmo
		self.nb_harmo += 1

		self.lbHarmo.append(gtk.Label(" Harmonique %2d : %5d Hz " % ((n+1),(n+1)*self.note.frequence)))
		self.lbHarmo[n].set_alignment(0,0.8)
		self.scaleHarmo.append(gtk.HScale())
		self.scaleHarmo[n].set_range(0,100)
		self.scaleHarmo[n].set_digits(1)
		self.scaleHarmo[n].set_increments(1,5)
		self.scaleHarmo[n].set_tooltip_text("Amplitude relative de l'harmonique " + str(n+1))
		self.scaleHarmo[n].connect("button-release-event",self.change_harmo)
		self.scaleHarmo[n].connect("value-changed",self.change_harmo)
		self.scaleHarmo[n].connect("focus-in-event", self.update_select_harmo_in)
		self.scaleHarmo[n].connect("focus-out-event", self.update_select_harmo_out)

		self.btPlayHarmo.append(gtk.Button(stock=gtk.STOCK_MEDIA_PLAY))
		self.btPlayHarmo[n].set_tooltip_text("Joue l'harmonique " + str(n+1))
		self.btPlayHarmo[n].connect("clicked", self.play_harmo)
		self.btPlayHarmo[n].connect("focus-in-event", self.update_select_harmo_in)
		self.btPlayHarmo[n].connect("focus-out-event", self.update_select_harmo_out)

		self.chHarmo.append(gtk.CheckButton())
		self.chHarmo[n].set_active(True)
		self.chHarmo[n].set_tooltip_text("Affiche ou non la courbe de l'harmonique " + str(n+1) +" sur le graphique")
		self.chHarmo[n].connect("toggled",self.update_affich_harmo)

		self.hboxHarmo.append(gtk.HBox())
		self.hboxHarmo[n].pack_start(self.lbHarmo[n], expand=False)
		self.hboxHarmo[n].pack_start(self.scaleHarmo[n])
		self.hboxHarmo[n].pack_start(self.btPlayHarmo[n], expand=False)
		self.hboxHarmo[n].pack_start(self.chHarmo[n], expand=False)

		self.vboxListHarmo.pack_start(self.hboxHarmo[n], expand=False)

		if n<len(self.note.harmo):
			self.scaleHarmo[n].set_value(self.note.harmo[n])
		else:
			self.scaleHarmo[n].set_value(0)
			self.note.add_harmonique(0)
			self.update_affich_harmo()

		self.win.show_all()

	def remove_harmo(self, widget=None, event=None):
		if self.nb_harmo > 1 :
			self.note.del_harmo()
			self.update_plot()
			self.vboxListHarmo.remove(self.hboxHarmo[self.nb_harmo-1])
			self.lbHarmo.pop()
			self.hboxHarmo.pop()
			self.scaleHarmo.pop()
			self.btPlayHarmo.pop()
			self.chHarmo.pop()
			#self.nb_harmo -= 1
			self.nb_harmo = len(self.note.harmo)

	def del_harmo_all(self, widget=None, event=None):
		self.set_harmo(0,50)
		for n in range(len(self.note.harmo)-1):
			self.remove_harmo()


	def change_harmo(self, widget=None, event=None):
		n=self.scaleHarmo.index(widget)
		s=0
		for k in range(self.nb_harmo):
			s += self.scaleHarmo[k].get_value()
		if s == 0:
			self.scaleHarmo[n].set_value(0.1)
			print self.scaleHarmo[n].get_value()
		self.note.change_harmonique(n, self.scaleHarmo[n].get_value())
		self.update_plot()

	def set_harmo(self,n,h):
		self.scaleHarmo[n].set_value(h)
		self.note.change_harmonique(n, h)
		self.update_plot()

	def set_all_harmo(self, harmoniques):
		for n in range(len(self.note.harmo)-1):
			self.remove_harmo()
		self.note.set_harmoniques(harmoniques)
		self.set_harmo(0,harmoniques[0])
		for n in range(len(harmoniques)-1):
			self.add_harmo()

	# -------- Mises à jour des paramètres -------------------------------------

	def update_param_base(self, widget=None, *arg ):
		if self.spinFrequence.get_text().lower()[0:4] == "lune" :
			self.lune() # Petit easter egg
			self.spinFrequence.set_text(str(self.note.frequence))
			return

		try:
			new_freq = self.spinFrequence.get_value()
			new_amp = self.scaleAmplitude.get_value()
			new_duree = self.scaleDuree.get_value()
		except :
			self.enFrequence.set_text(str(self.note.frequence))
			self.enDuree.set_text(str(self.note.duree))
			return

		if self.note.frequence != new_freq:
			if new_freq > 0 and new_freq < FREQ_ECH :
				self.note.set_frequence(new_freq)
				for n in range(self.nb_harmo):
					self.lbHarmo[n].set_text(" Harmonique %d : %d Hz " % ((n+1),(n+1)*self.note.frequence))
				self.update_plot()
			else :
				self.enFrequence.set_text(str(self.note.frequence))

		if self.note.amplitude != new_amp :
			self.note.set_amplitude(new_amp)
			self.update_plot()

		if self.note.duree != new_duree:
			if new_duree > 0 and new_duree <= 5:
				self.note.set_duree(new_duree)
				self.update_plot()
			else :
				self.enDuree.set_text(str(self.note.duree))

	def update_affich_harmo(self, widget=None, event=None):
		self.affich_harmo=""
		for n in range(self.nb_harmo):
			if self.chHarmo[n].get_active():
				self.affich_harmo += "1"
			else:
				self.affich_harmo += "0"
		self.update_plot()


	def update_affich_all(self, widget=None, event=None):
		if self.chAll.get_active():
			self.affich_all = True
		else:
			self.affich_all = False
		self.update_plot()

	def update_select_harmo_in(self, widget, event=None):
		try:
			n = self.scaleHarmo.index(widget)
		except:
			n = self.btPlayHarmo.index(widget)
		self.select_harmo = n
		self.update_plot()

	def update_select_harmo_out(self, widget, event=None):
		self.select_harmo = -1
		self.update_plot()

	def update_plot(self, widget=None, *arg ):
		self.note.update_plot(nb_periodes_affichees=int(self.scaleNbPeriodes.get_value()),
					affich_all=self.affich_all,
					affich_harmo=self.affich_harmo, select_harmo=self.select_harmo)
		self.note.figure.canvas.draw()



	# ------- Gestion des fichiers ---------------------------------------------

	def open(self,  widget=None, *arg):
		self.openWin = gtk.FileChooserDialog("Ouvrir",
				self.win, gtk.FILE_CHOOSER_ACTION_OPEN,
				((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)))
		reponse = self.openWin.run()
		if reponse == gtk.RESPONSE_OK:
			nom_fichier=self.openWin.get_filename()
			fichier = open(nom_fichier, "r")
			harmon=[]
			for ligne in fichier:
				harmon.append(float(ligne[0:-2]))
			fichier.close()
		self.openWin.destroy()
		self.set_all_harmo(harmon)

	def save(self,  widget=None, *arg):
		self.saveWin = gtk.FileChooserDialog("Enregistrer",
				self.win, gtk.FILE_CHOOSER_ACTION_SAVE,
				 ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)))
		self.saveWin.set_do_overwrite_confirmation(True)
		reponse = self.saveWin.run()
		if reponse == gtk.RESPONSE_OK:
			nom_fichier=self.saveWin.get_filename()
			fichier = open(nom_fichier, "w")
			for n in range(len(self.note.harmo)):
				fichier.write(str(self.note.harmo[n])+"\n")
			fichier.close()
		self.saveWin.destroy()

	def export_wav(self,  widget=None, *arg):
		self.saveWin = gtk.FileChooserDialog("Exporter en .wav",
				self.win, gtk.FILE_CHOOSER_ACTION_SAVE,
				 ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)))
		self.saveWin.set_do_overwrite_confirmation(True)
		self.filtre=gtk.FileFilter()
		self.filtre.set_name("*.wav")
		self.filtre.add_pattern("*.wav")
		self.saveWin.set_filter(self.filtre)
		reponse = self.saveWin.run()
		if reponse == gtk.RESPONSE_OK:
			nom_fichier=self.saveWin.get_filename()
			if nom_fichier[-4:] != ".wav":
				nom_fichier += ".wav"
			self.note.export_wav(nom_fichier)
		self.saveWin.destroy()


	def aPropos(self, widget=None, event=None):
		#~ pixbuf = gtk.gdk.pixbuf_new_from_file("HarmoniK.png")
		aPropos = gtk.AboutDialog()
		#~ aPropos.set_icon_from_file("HarmoniK.png")
		aPropos.set_name("HarmoniK")
		aPropos.set_version(VERSION)
		aPropos.set_copyright("Licence Creative Common BY - NC - SA")
		aPropos.set_comments(aPropos.get_name() + " " + aPropos.get_version() +\
			" est un logiciel pour étudier les harmoniques des notes de musique.")
		aPropos.set_license("""
Ce logiciel ainsi que la bibliothèque pyzik qu'il utilise sont des logiciels
libres sous licence Creative Common BY - NC - SA.

Vous pouvez le distribuer librement, le modifier, en faire ce que vous voulez
dans le cadre d'applications non commerciales, à condition de citer l'auteur
et de redistribuer vos modifications sous la même licence.""")
		auteurs = ["F. Muller"]
		aPropos.set_authors(auteurs)
		#~ aPropos.set_logo(pixbuf)
		reponse = aPropos.run()
		aPropos.destroy()

	# -------- Fonctions musicales ---------------------------------------------

	def play(self, widget, event=None):
		if event == None or event.keyval==32:
			if float(self.spinFrequence.get_text()) != self.note.frequence:
				self.update_param_base()
			self.note.play()
			self.note.wait()
			return True

	def play_harmo(self, widget):
		n = self.btPlayHarmo.index(widget)
		self.note.play(n)
		self.note.wait()

	def lune(self):
		harmon = []
		oct= self.spinFrequence.get_text()[4:]
		if oct=="" or oct not in "123456" : oct="3"
		instru=Instru(amplitude=self.note.amplitude, octaves=[int(oct),int(oct)],
						duree = self.note.duree, harmoniques=self.note.harmo)
		lune=["DO"+oct,"DO"+oct,"DO"+oct,"RE"+oct,"MI"+oct,"MI"+oct,
				"RE"+oct,"RE"+oct,"DO"+oct,"MI"+oct,"RE"+oct,"RE"+oct,
				"DO"+oct,"DO"+oct,"DO"+oct,"DO"+oct ]
		for note in lune:
			instru.play(note)
			instru.wait()


if __name__ == "__main__":
	Main()
	gtk.main()

