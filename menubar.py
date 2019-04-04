from tkinter import *
from tkinter.ttk import *
import Pmw
import pickle
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from set_obj import SetObj
from webbrowser import open_new


class Menubar:
	def __init__(self, parent, parameters, allunits):
		parent.__init__
		self.parent = parent
		self.parameters = parameters
		self.allunits = allunits
		self.tSize = StringVar()
		self.tSize.set('2')
		self.nPop = StringVar()
		self.nPop.set('25')
		self.nGen = StringVar()
		self.nGen.set('40')
		self.cType = StringVar()
		self.cType.set('one point')
		self.cRate = StringVar()
		self.cRate.set('0.6')
		self.mRate1 = StringVar()
		self.mRate1.set('0.2')
		self.mRate2 = StringVar()
		self.mRate2.set('0.05')
		self.sAddress = StringVar()
		self.sAddress.set('')
		self.File = None
		menu_bar = Menu(parent)	
		file_menu = Menu(menu_bar, tearoff=0)
		file_menu.add_command(label='New', command=self.new_file)
		file_menu.add_command(label='Open', command=self.open_file)
		file_menu.add_command(label='Save', command=self.save_file)
		file_menu.add_command(label='Save as', command=self.saveas_file)
		file_menu.add_separator()
		file_menu.add_command(label='Exit')
		menu_bar.add_cascade(label='File', menu=file_menu)		
		set_menu = Menu(menu_bar, tearoff=0)
		set_menu.add_command(label='GA parameters', command=self.setGApara)
		set_menu.add_command(label='Server', command=self.setServer)
		set_menu.add_command(label='Objectives', command=self.setObjectives)
		menu_bar.add_cascade(label='Set', menu=set_menu)	
		about_menu = Menu(menu_bar, tearoff=0)
		about_menu.add_command(label='About', command=self.about)
		about_menu.add_command(label='Help', command=self.help)
		menu_bar.add_cascade(label='About', menu=about_menu)
		parent.config(menu=menu_bar)	
		
	def about(self):
		self.About=Toplevel(self.parent)
		self.About.title("Evaluated individuals")
		AboutFrame = Frame(self.About)
		AboutFrame.pack()
		Author = Label(AboutFrame, text='Made by: Jin Lu')
		Author.pack()
		Email = Label(AboutFrame, text='E-Mail: jin.lu86@yahoo.com')
		Email.pack()
		Dismiss = Button(AboutFrame, text='Dismiss', command=self.dismiss)
		Dismiss.pack()
		
	def dismiss(self):
		self.About.destroy()
		
	def help(self):
		open_new('https://github.com/lujin1986/GaFEM/blob/master/README.md')
	
	def setGApara(self):
		widgets = []
		self.SetGApara = Pmw.Dialog(self.parent, 
				title="Set the GA parameters", 
				buttons=('OK', 'Cancel'),
				command = self.actionSetGApara)
		self.NPop = Pmw.EntryField(self.SetGApara.interior(),
				labelpos='w',
				label_text='population size:',
				entry_width = 14,
				entry_textvariable=self.nPop)
		self.NPop.pack()
		widgets.append(self.NPop)
		self.NGen = Pmw.EntryField(self.SetGApara.interior(),
				labelpos='w',
				label_text='max. number of generations:',
				entry_width = 14,
				entry_textvariable=self.nGen)
		self.NGen.pack()
		widgets.append(self.NGen)
		self.TSize = Pmw.EntryField(self.SetGApara.interior(),
				labelpos='w',
				label_text='tournament size:',
				entry_width = 14,
				entry_textvariable=self.tSize)	
		self.TSize.pack()
		widgets.append(self.TSize)
		self.CType =Pmw.OptionMenu(self.SetGApara.interior(),              
				labelpos='w',  
				label_text='type of crossover:',
				items=['one-point', 'two-point'],
				menubutton_textvariable=self.cType,
				menubutton_width=9)
		self.CType.pack()
		widgets.append(self.CType)
		self.CRate = Pmw.EntryField(self.SetGApara.interior(),
				labelpos='w',
				label_text='crossover rate:',
				entry_width = 14,
				entry_textvariable=self.cRate)
		self.CRate.pack()
		widgets.append(self.CRate)		
		self.MRate1 = Pmw.EntryField(self.SetGApara.interior(),
				labelpos='w',
				label_text='mutation rate (individual):',
				entry_width = 14,
				entry_textvariable=self.mRate1)	
		self.MRate1.pack()
		widgets.append(self.MRate1)
		self.MRate2 = Pmw.EntryField(self.SetGApara.interior(),
				labelpos='w',
				label_text='mutation rate (allele):',
				entry_width = 14,
				entry_textvariable=self.mRate2)	
		self.MRate2.pack()
		widgets.append(self.MRate2)
		Pmw.alignlabels(widgets)

	def setObjectives(self):
		SetObj(self.parent, self.parameters)	

	def actionSetGApara(self, result):
		if result == 'OK':
			for key, Var in zip(['population size', 'max. number of generations', 'tournament size', 'type of crossover', 
					'crossover rate', 'mutation rate (individual)', 'mutation rate (individual)'], [self.nPop, 
					self.nGen, self.tSize, self.cType, self.cRate, self.mRate1, self.mRate2]):
				self.parameters['GA parameters'][key]= Var.get()
		self.SetGApara.destroy()	
		
	def setServer(self):
		self.allunits['Login'].setServer()

	def actionSetServer(self, result):
		if result == 'OK':
			self.parameters['Login']['server']=self.sAddress.get()
		self.SetServer.destroy()

	def open_file(self):
		filename = tkFileDialog.askopenfilename(defaultextension=".opt", filetypes=[("Opt Files", "*.opt"), ("Result Files", "*.res")])
		self.File = filename
		if filename:
			if filename[-4:] == ".res":
				self.allunits['Control'].Results.config(state='normal')
				f = open(filename, 'rb')
				data = pickle.load(f)
				opt = data['Setup']
				self.loadres = data['Results']
			else:
				self.allunits['Control'].Results.config(state='disabled')
				self.loadres = None
				f = open(filename, 'rb')
				opt = pickle.load(f)
			for key in opt.keys():
				if key != 'Login':
					self.parameters[key] = opt[key]
			self.allunits['Case'].name.set(opt['Case']['name'])		
			self.allunits['Case'].WD.set(opt['Case']['WD'])	
			if opt['Case']['type'] == 'single-objective':
				self.allunits['Case'].radios[0].invoke()
			else:
				self.allunits['Case'].radios[1].invoke()
			for key, Var in zip(['population size', 'max. number of generations', 'tournament size', 'type of crossover', 
					'crossover rate', 'mutation rate (individual)', 'mutation rate (individual)'], [self.nPop, 
					self.nGen, self.tSize, self.cType, self.cRate, self.mRate1, self.mRate2]):
				Var.set(opt['GA parameters'][key])			
			self.allunits['InputVar'].variableList = opt['design variables']
			self.allunits['InputVar'].view_records()
			if opt['constraint'][0]:
				self.allunits['InputVar'].checkb.set(1)
				self.allunits['InputVar'].constraint.set(opt['constraint'][1])
				self.allunits['InputVar'].ConstraintE.config(state='normal')
				self.allunits['InputVar'].Constraint2.config(state='normal')
			else:
				self.allunits['InputVar'].checkb.set(0)
				self.allunits['InputVar'].constraint.set('')
				self.allunits['InputVar'].ConstraintE.config(state='disabled')
				self.allunits['InputVar'].Constraint2.config(state='disabled')
			self.allunits['Evaluation'].grow.set(opt['grow'])			
			self.allunits['Evaluation'].template.set(opt['template'])			
			self.allunits['Evaluation'].objective.set(opt['objective'])	
			if opt['seed'][0]:
				self.allunits['Control'].seeding.set(1)
				self.allunits['Control'].seed = opt['seed'][1]	
				self.allunits['Control'].SetSeed.config(state='normal')
			else:
				self.allunits['Control'].seeding.set(0)
				self.allunits['Control'].seed = []
				self.allunits['Control'].SetSeed.config(state='disabled')
			if opt['elitism']:
				self.allunits['Control'].elitism.set(1)
			else:
				self.allunits['Control'].elitism.set(0)			
			if opt['multithreading'][0]:
				self.allunits['Control'].multithreads.set(1)
				self.allunits['Control'].InputThread.configure(entry_state='normal')
				self.allunits['Control'].threads.set(opt['multithreading'][1])				
			else:
				self.allunits['Control'].multithreads.set(0)
				self.allunits['Control'].InputThread.configure(entry_state='disabled')	
		
	def new_file(self):
		message = "Have you already saved all the changes to the optimization case '%s'?" % self.allunits['Case'].name.get()
		ok = tkMessageBox.askokcancel('Creating a new optimization case', message)
		if ok:
			for key in ['Case', 'GA parameters']:
				self.parameters[key]={}
			for key in ['design variables', 'seed', 'multithreading']:
				self.parameters[key]=[]
			self.allunits['Case'].name.set('')	
			self.allunits['Case'].WD.set('')	
			self.allunits['Case'].radios[0].invoke()			
			self.allunits['InputVar'].variableList = []
			self.allunits['InputVar'].view_records()
			self.allunits['InputVar'].checkb.set(0)
			self.allunits['InputVar'].constraint.set('')
			self.allunits['InputVar'].Constraint2.config(state='disabled')
			self.allunits['Evaluation'].grow.set('')		
			self.allunits['Evaluation'].template.set('')		
			self.allunits['Evaluation'].objective.set('')		
			self.allunits['Control'].seeding.set(0)
			self.allunits['Control'].seed = []
			self.allunits['Control'].SetSeed.config(state='disabled')	
			self.allunits['Control'].elitism.set(0)					
			self.allunits['Control'].multithreads.set(0)
			self.allunits['Control'].InputThread.configure(entry_state='disabled')
			self.File = None	

	def save_file(self):
		if self.File:		
			self.parameters['Case']['name'] = self.allunits['Case'].name.get()			
			self.parameters['Case']['WD'] = self.allunits['Case'].WD.get()	
			self.parameters['Case']['type'] = self.allunits['Case'].type.get()	
			for key, Var in zip(['population size', 'max. number of generations', 'tournament size', 'type of crossover', 
					'crossover rate', 'mutation rate (individual)', 'mutation rate (allele)'], [self.nPop, 
					self.nGen, self.tSize, self.cType, self.cRate, self.mRate1, self.mRate2]):
				self.parameters['GA parameters'][key]=Var.get()			
			self.parameters['design variables'] = self.allunits['InputVar'].variableList
			if self.allunits['InputVar'].checkb.get():
				if self.parameters['constraint']:
					self.parameters['constraint'][0] = 1
					self.parameters['constraint'][1] = self.allunits['InputVar'].constraint.get()
				else:									
					self.parameters['constraint'].append(1)
					self.parameters['constraint'].append(self.allunits['InputVar'].constraint.get())
			else:
				if self.parameters['constraint']:
					self.parameters['constraint'][0]=0
					self.parameters['constraint'][1]=''
				else:										
					self.parameters['constraint'].append(0)
					self.parameters['constraint'].append('')
			self.parameters['grow'] = self.allunits['Evaluation'].grow.get()			
			self.parameters['template'] = self.allunits['Evaluation'].template.get()			
			self.parameters['objective'] = self.allunits['Evaluation'].objective.get()	
			if self.allunits['Control'].seeding.get():
				if self.parameters['seed']:
					self.parameters['seed'][0] = 1
					self.parameters['seed'][1] = self.allunits['Control'].seed
				else:
					self.parameters['seed'][0].append(1)
					self.parameters['seed'][1].append(self.allunits['Control'].seed)			
			else:
				if self.parameters['seed']:
					self.parameters['seed'][0] = 0
					self.parameters['seed'][1] = ''
				else:
					self.parameters['seed'][0].append(1)
					self.parameters['seed'][1].append('')
			if self.allunits['Control'].elitism.get():
				self.parameters['elitism']=1	
			else:
				self.parameters['elitism']=0			
			if self.allunits['Control'].multithreads.get():
				if self.parameters['multithreading']:
					self.parameters['multithreading'][0] = 1
					self.parameters['multithreading'][1] = self.allunits['Control'].threads.get()
				else:
					self.parameters['multithreading'][0].append(1)
					self.parameters['multithreading'][1].append(self.allunits['Control'].threads.get())												
			else:
				if self.parameters['multithreading']:
					self.parameters['multithreading'][0] = 0
					self.parameters['multithreading'][1] = ''
				else:
					self.parameters['multithreading'][0].append(0)
					self.parameters['multithreading'][1].append('')	
			f = open(self.File, 'wb')
			pickle.dump(self.parameters, f)
			f.close()
		else:
			fname = tkFileDialog.SaveAs(filetypes=[('Opt Files', '*.opt')],
						 initialfile='%s.opt' % self.allunits['Case'].name.get(),
						title='Save an optimization case').show()
			if fname[-4:] == ".opt":
				fname = fname[:-4]
			fname = "%s.opt" % fname
			if fname:	
				self.parameters['Case']['name'] = self.allunits['Case'].name.get()			
				self.parameters['Case']['WD'] = self.allunits['Case'].WD.get()	
				self.parameters['Case']['type'] = self.allunits['Case'].type.get()
				for key, Var in zip(['population size', 'max. number of generations', 'tournament size', 'type of crossover', 
						'crossover rate', 'mutation rate (individual)', 'mutation rate (allele)'], [self.nPop, 
						self.nGen, self.tSize, self.cType, self.cRate, self.mRate1, self.mRate2]):
					self.parameters['GA parameters'][key]=Var.get()			
				self.parameters['design variables'] = self.allunits['InputVar'].variableList
				if self.allunits['InputVar'].checkb.get():
					if self.parameters['constraint']:
						self.parameters['constraint'][0] = 1
						self.parameters['constraint'][1] = self.allunits['InputVar'].constraint.get()
					else:									
						self.parameters['constraint'].append(1)
						self.parameters['constraint'].append(self.allunits['InputVar'].constraint.get())
				else:
					if self.parameters['constraint']:
						self.parameters['constraint'][0]=0
						self.parameters['constraint'][1]=''
					else:										
						self.parameters['constraint'].append(0)
						self.parameters['constraint'].append('')
					self.parameters['grow'] = self.allunits['Evaluation'].grow.get()			
					self.parameters['template'] = self.allunits['Evaluation'].template.get()			
					self.parameters['objective'] = self.allunits['Evaluation'].objective.get()	
				if self.allunits['Control'].seeding.get():
					if self.parameters['seed']:
						self.parameters['seed'][0] = 1
						self.parameters['seed'][1] = self.allunits['Control'].seed
					else:
						self.parameters['seed'].append(1)
						self.parameters['seed'].append(self.allunits['Control'].seed)			
				else:
					if self.parameters['seed']:
						self.parameters['seed'][0] = 0
						self.parameters['seed'][1] = ''
					else:
						self.parameters['seed'].append(1)
						self.parameters['seed'].append('')
				if self.allunits['Control'].elitism.get():
					self.parameters['elitism']=1	
				else:
					self.parameters['elitism']=0			
				if self.allunits['Control'].multithreads.get():
					if self.parameters['multithreading']:
						self.parameters['multithreading'][0] = 1
						self.parameters['multithreading'][1] = self.allunits['Control'].threads.get()
					else:
						self.parameters['multithreading'].append(1)
						self.parameters['multithreading'].append(self.allunits['Control'].threads.get())											
				else:
					if self.parameters['multithreading']:
						self.parameters['multithreading'][0] = 0
						self.parameters['multithreading'][1] = ''
					else:
						self.parameters['multithreading'].append(0)
						self.parameters['multithreading'].append('')				
				self.File = fname
				f = open(fname, 'wb')
				save = {}
				for key in self.parameters.keys():
					if key != 'Login':
						save[key]=self.parameters[key]
				pickle.dump(save, f)
				f.close()

	def saveas_file(self):
		self.File = None
		self.save_file()
		
			
				
if __name__ == "__main__":
	root = Tk()
	Menubar(root)
	root.mainloop()	
		
