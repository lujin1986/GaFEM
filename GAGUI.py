from mttkinter.mtTkinter import *
from ttk import *
from menubar import Menubar
from case import Case
from login import Login
from decoder import InputVar
from evaluation import Evaluation
from control import Control
from pickle import dump

import Pmw

seed = [1,0,1]

class GAGUI:
	def __init__(self, parent):
		self.parent = parent
		self.all = {'Case':None, 'Login': None, 'InputVar': None, 'Evaluation': None, 'Control': None, 'Menubar':None }
		self.parameters = {'Case':{}, 'Login':{},'design variables':[], 'constraint':[], 'seed':[], 'GA parameters':{}, 'multithreading':[], 'file':None, 'results':None}
		self.MainFrame = Frame(parent)
		self.MainFrame.pack(fill=BOTH, expand=1)
		self.InitialFrame = Frame(self.MainFrame)
		self.InitialFrame.pack(side='top', fill=X, expand=1)
		self.Case = Case(self.InitialFrame, self.parameters)
		self.Case.pack(side='left', fill=X, padx=10, expand=1)
		self.Login = Login(self.InitialFrame, self.parameters, self.all)
		self.Login.pack(side='left', fill=BOTH, padx=10, expand=1)
		self.InputVar = InputVar(self.MainFrame, self.parameters)
		self.InputVar.pack(side='top', fill=X, padx=10, expand=1)
		self.Evaluation = Evaluation(self.MainFrame, self.all)
		self.Evaluation.pack(side='top', fill=X, padx=10, expand=1)
		self.Control = Control(parent, self.MainFrame, self.parameters, self.all)
		self.Control.pack(side='top', fill=X, padx=10, expand=1)
		self.Menubar = Menubar(parent, self.parameters, self.all)
		for i in ['Case', 'Login', 'InputVar', 'Evaluation', 'Control', 'Menubar']:
			self.all[i]=getattr(self, i)
root = Tk()
def on_closing():
	f = open("switch.txt", "wb")
	dump(0, f)
	f.close()
	if GUI.Login.abqLicense_on:
		GUI.Login.buttonLogout()
	root.destroy()

Pmw.initialise(root)
GUI=GAGUI(root)
root.title('GaFEM')
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

