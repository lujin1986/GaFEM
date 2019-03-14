from pickle import dump

import Pmw


class GAGUI:
	def __init__(self, parent):
		""" construct the GUI with different functional modules."""
		self.parent = parent
		self.all = {'Case':None, 'Login': None, 'InputVar': None, 'Evaluation': None, 'Control': None, 'Menubar':None }
		self.parameters = {'Case':{}, 'Login':{},'design variables':[], 'constraint':[], 'seed':[], 'GA parameters':{}, 'multithreading':[], 'file':None, 'results':None}
		self.MainFrame = Frame(parent)
		self.MainFrame.pack(fill='both', expand=1)
		self.InitialFrame = Frame(self.MainFrame)
		self.InitialFrame.pack(side='top', fill='x', expand=1)
		self.Case = Case(self.InitialFrame, self.parameters)
		self.Case.pack(side='left', fill='x', padx=10, expand=1)
		self.Login = Login(self.InitialFrame, self.parameters, self.all)
		self.Login.pack(side='left', fill='both', padx=10, expand=1)
		self.InputVar = InputVar(self.MainFrame, self.parameters)
		self.InputVar.pack(side='top', fill='x', padx=10, expand=1)
		self.Evaluation = Evaluation(self.MainFrame, self.all)
		self.Evaluation.pack(side='top', fill='x', padx=10, expand=1)
		self.Control = Control(parent, self.MainFrame, self.parameters, self.all)
		self.Control.pack(side='top', fill='x', padx=10, expand=1)
		self.Menubar = Menubar(parent, self.parameters, self.all)
		for i in ['Case', 'Login', 'InputVar', 'Evaluation', 'Control', 'Menubar']:
			self.all[i]=getattr(self, i)

def on_closing():
	f = open("switch.txt", "wb")
	dump(0, f)
	f.close()
	if GUI.Login.abqLicense_on:
		GUI.Login.buttonLogout()
	root.destroy()
	
root = Tk()
Pmw.initialise(root)
GUI=GAGUI(root)
root.resizable(width=False, height=True)
root.title('GaFEM')
img = PhotoImage(file='images/icon.png')
root.tk.call('wm', 'iconphoto', root._w, img)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
