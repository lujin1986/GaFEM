from tkinter import *
from tkinter.ttk import *
from pickle import dump, load
import Pmw
import tkinter.messagebox as tkMessageBox
import subprocess 
import shlex 
import os, shutil
from result_multi import Result
from numpy import savetxt, array 
from threading import Thread
from time import sleep


class Control:
	def __init__(self, root, parent, parameters, allunits):
		parent.__init__
		self.root = root
		self.parent = parent
		self.parameters = parameters
		self.allunits = allunits
		self.seed = []
		self.seedvalue = {}
		self.restart = IntVar()
		self.restart.set(0)
		self.elitism = IntVar()
		self.elitism.set(0)
		self.multithreads = IntVar()
		self.multithreads.set(0)
		self.threads = StringVar()
		self.threads.set('1')
		self.seeding = IntVar()
		self.seeding.set(0)
		self.ControlFrame = LabelFrame(parent, text='Control')
		self.ControlFrame.pack()
		self.Frame= Frame(self.ControlFrame)
		self.Frame.pack(side='top')
		self.CheckRestart = Checkbutton(self.Frame, text = "resume", variable=self.restart)	
		self.CheckRestart.grid(row=0,column=0, ipadx=5, sticky='w')
		self.CheckElitism = Checkbutton(self.Frame, text = "elitism", variable=self.elitism)	
		self.CheckElitism.grid(row=1,column=0, ipadx=5, sticky='w')
		self.CheckThread = Checkbutton(self.Frame, text = "multi-threads:", variable=self.multithreads, command=self.checkThreadStatus)	
		self.CheckThread.grid(row=0,column=1, sticky='w')
		#self.InputThread = Entry(self.Frame, width = 11, textvariable=self.threads, state = 'disabled')
		self.InputThread= Pmw.EntryField(self.Frame, entry_width=11, validate={'validator':'numeric', 'min':1}, entry_textvariable=self.threads, entry_state='disabled')
		self.InputThread.grid(row=0,column=2, sticky='w', padx=2)
		self.CheckSeed = Checkbutton(self.Frame, text = "seeding:", variable=self.seeding, command=self.checkSeedStatus)	
		self.CheckSeed.grid(row=1,column=1, sticky='w')
		self.SetSeed = Button(self.Frame, text = "set seed", command=self.setseed, state = 'disabled')
		self.SetSeed.grid(row=1,column=2, sticky='w')
		self.Optimize = Button(self.Frame, text = "      Start   \nOptimization", command=self.start)
		self.Optimize.grid(row=0,column=3, rowspan=3, padx=15, stick = 'e')
		self.Results = Button(self.Frame, text = "  View   \nResults", command=self.results, state= 'disabled')
		self.Results.grid(row=0,column=4, rowspan=3, stick = 'e')
		self.ResultWidget = None
		self.cwd = os.getcwd()
		self.wd = self.cwd
	
	def pack(self, side='top', fill=None, expand=None, padx=0, pady=0):
		self.ControlFrame.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)		

	def start(self):
		if self.Optimize.cget('text') == "      Start   \nOptimization":
			self.parameters['Case']['name'] = self.allunits['Case'].name.get()			
			self.parameters['Case']['WD'] = self.allunits['Case'].WD.get()	
			self.parameters['Case']['type'] = self.allunits['Case'].type.get()
			if not self.parameters['GA parameters']:				
				for key, Var in zip(['population size', 'max. number of generations', 'tournament size', 'type of crossover', 
						'crossover rate', 'mutation rate (individual)', 'mutation rate (allele)'], [40, 
						25, 2, 'one-point', 0.6, 0.2, 0.05]):
					self.parameters['GA parameters'][key]=Var			
			self.parameters['design variables'] = self.allunits['InputVar'].variableList
			if self.allunits['InputVar'].checkb.get():
				if self.parameters['constraint']:
					self.parameters['constraint'][0] = 1
					self.parameters['constraint'][1] = self.allunits['InputVar'].constraint.get()
				else:										
					self.parameters['constraint'][0].append(1)
					self.parameters['constraint'][1].append(self.allunits['InputVar'].constraint.get())
			else:
				if self.parameters['constraint']:
					self.parameters['constraint'][0]=0
					self.parameters['constraint'][1]=''
				else:								
					self.parameters['constraint'][0].append(0)
			self.parameters['grow'] = self.allunits['Evaluation'].grow.get()			
			self.parameters['template'] = self.allunits['Evaluation'].template.get()			
			self.parameters['objective'] = self.allunits['Evaluation'].objective.get()	
			if self.seeding.get():
				if self.parameters['seed']:
					self.parameters['seed'][0] = 1
					self.parameters['seed'][1] = self.seed
				else:
					self.parameters['seed'][0].append(1)
					self.parameters['seed'][1].append(self.seed)			
			else:
				if self.parameters['seed']:
					self.parameters['seed'][0] = 0
					self.parameters['seed'][1] = ''
				else:
					self.parameters['seed'][0].append(1)
					self.parameters['seed'][1].append('')
			if self.elitism.get():
				self.parameters['elitism']=1	
			else:
				self.parameters['elitism']=0			
			if self.multithreads.get():
				if self.parameters['multithreading']:
					self.parameters['multithreading'][0] = 1
					self.parameters['multithreading'][1] = self.threads.get()
				else:
					self.parameters['multithreading'][0].append(1)
					self.parameters['multithreading'][1].append(self.threads.get())				
						
			else:
				if self.parameters['multithreading']:
					self.parameters['multithreading'][0] = 0
					self.parameters['multithreading'][1] = ''
				else:
					self.parameters['multithreading'][0].append(0)
					self.parameters['multithreading'][1].append('')	
			WD = self.parameters['Case']['WD'].strip()
			if self.parameters['Case']['WD'] == "current":
				WD = self.cwd
			elif not (WD[0]=='/' or WD[1]==':'):
				WD = os.path.join(self.cwd, WD)
				self.wd = WD
								
			if not os.path.exists(WD):	
				os.makedirs(WD)
			if not self.restart.get() or not os.path.exists(WD +'/%s' % self.parameters['Case']['name']):
				if not os.path.exists(WD +'/%s' % self.parameters['Case']['name']):
					os.makedirs(WD +'/%s' % self.parameters['Case']['name'])
					self.restart.set(0)
				else:
		
					message = 'Old optimization files exist. Do you want to continue the last optimization process? (If you press cancel, the old files will be removed.)'
					ok = tkMessageBox.askokcancel('Restart', message)
					if ok:
						self.restart.set(1)
					else:
						os.chdir(self.cwd)
						try:
							shutil.rmtree(WD +'/%s' % self.parameters['Case']['name'])
							os.makedirs(WD +'/%s' % self.parameters['Case']['name'])
						except:
							tkMessageBox.showerror(title='Error', message="The folder %s cannot be deleted due to the occupation of some other processes. Please abort all the relevant processes or delete the folder manually and try again." % self.parameters['Case']['name'])
							savetxt("switch.txt", array([0]))
							self.Optimize.config(text = "      Start   \nOptimization")
							return							
				os.chdir(WD +'/%s' % self.parameters['Case']['name'])
				if not os.path.exists('main3.py'):
					shutil.copy(self.cwd+'/main3.py', 'main3.py')

				if self.parameters['constraint'][0]:
					if not os.access(os.path.split(self.parameters['constraint'][1])[1], os.R_OK):
						file = self.parameters['constraint'][1].strip()
						if not (file[0]=='/' or file[1]==':'):
							file = os.path.join(self.wd, file)
						try:
							shutil.copy(file, os.path.split(file)[1])
						except:
							tkMessageBox.showerror(title='Error', message="The file '%' does not exist." % self.parameters['constraint'][1])
							savetxt("switch.txt", array([0]))
							self.Optimize.config(text = "      Start   \nOptimization")
							return
				for file in self.parameters['grow'].split(','):
					file = file.strip()
					if not (file[0]=='/' or file[1]==':'):
						file = os.path.join(self.wd, file)
					if not os.access(os.path.split(file)[1], os.R_OK):

						#try:
						shutil.copy(file, os.path.split(file)[1])
						"""
						except:
							tkMessageBox.showerror(title='Error', message="The file '%s' does not exist." % file)
							savetxt("switch.txt", array([0]))
							self.Optimize.config(text = "      Start   \nOptimization")
							return
						"""
				for file in self.parameters['template'].split(','):
					file = file.strip()
					if not (file[0]=='/' or file[1]==':'):
						file = os.path.join(self.wd, file)
					if not os.access(os.path.split(file)[1], os.R_OK):
						try:
							shutil.copy(file, os.path.split(file)[1])
						except:
							tkMessageBox.showerror(title='Error', message="The file '%' does not exist." % file)
							savetxt("switch.txt", array([0]))
							self.Optimize.config(text = "      Start   \nOptimization")
							return
				if not os.access(os.path.split(self.parameters['objective'])[1], os.R_OK):
					file = self.parameters['objective'].strip()
					if not (file[0]=='/' or file[1]==':'):
						file = os.path.join(self.wd, file)
					try:
						shutil.copy(file, os.path.split(file)[1])
					except:
						tkMessageBox.showerror(title='Error', message="The file '%s' does not exist." % file)
						savetxt("switch.txt", array([0]))
						self.Optimize.config(text = "      Start   \nOptimization")
						return
						
			else: os.chdir(WD +'/%s' % self.parameters['Case']['name'])
			name = "%s.opt" % self.parameters['Case']['name']
			f = open(name, 'wb')
			dump(self.parameters, f)
			f.close()
			savetxt("switch.txt", array([1]))
			self.Optimize.config(text = "      Stop    \nOptimization")
			sleep(1)
			if self.ResultWidget:
				self.ResultWidget.newwindow.destroy()
				if self.ResultWidget.PrintR:
					self.ResultWidget.PrintR.destroy()
			self.ResultWidget = Result(self.ControlFrame, self.parameters, self.Optimize, self.restart.get(), self.cwd, self.allunits['Login'] )
			self.ResultWidget.newwindow.protocol("WM_DELETE_WINDOW", self.closeRW)
			self.Results.config(state='disabled')
		
		else:
			savetxt("switch.txt", array([0]))
			if self.ResultWidget.cluster:
				self.ResultWidget.sftp.remove("switch.txt")
				self.ResultWidget.sftp.put("switch.txt","switch.txt")

			self.Optimize.config(text = "      Start   \nOptimization")
			self.Results.config(state='normal')
	def closeRW(self):
		if self.ResultWidget.switch:
			message = "Are you going to stop the optimization process"
			ok = tkMessageBox.askokcancel('', message)
			if ok:
				self.ResultWidget.switch=0
				if self.ResultWidget.cluster:
					self.ResultWidget.sftp.remove("switch.txt")
					self.ResultWidget.sftp.put("switch.txt","switch.txt")
				if self.ResultWidget.PrintR:
					self.ResultWidget.PrintR.destroy()
				self.ResultWidget.newwindow.destroy()
				self.ResultWidget = None
				self.Optimize.config(text = "      Start   \nOptimization")
				self.Results.config(state='normal')
				savetxt("switch.txt", array([0]))

		else:
			if self.ResultWidget.PrintR:
				self.ResultWidget.PrintR.destroy()
			self.ResultWidget.newwindow.destroy()
			self.ResultWidget = None
			self.Results.config(state='normal')
			if self.allunits['Menubar'].loadres is not None:
				os.chdir('..')
				WD = self.parameters['Case']['WD'].strip()
				if self.parameters['Case']['WD'] == "current":
					WD = self.cwd
				elif not (WD[0]=='/' or WD[1]==':'):
					WD = os.path.join(self.cwd, WD)
					self.wd = WD
				os.rmtree(WD +'/%s' % self.parameters['Case']['name'])
	
	def results(self):
		if not self.ResultWidget:
			if self.allunits['Menubar'].loadres is not None:
				results = self.allunits['Menubar'].loadres
				WD = self.parameters['Case']['WD'].strip()
				if self.parameters['Case']['WD'] == "current":
					WD = self.cwd
				elif not (WD[0]=='/' or WD[1]==':'):
					WD = os.path.join(self.cwd, WD)
					self.wd = WD
				if os.path.exists(WD+'/%s' % self.parameters['Case']['name']):
					message = 'Old optimization files in the folder %s/%s exist. View the results from result file (.res) needs to recreate this folder. If you press OK, the contents of the folder will be removed.' % (WD, self.parameters['Case']['name'])
					ok = tkMessageBox.askokcancel('View results', message)
					if ok:
						try:
							shutil.rmtree(WD+'/%s' % self.parameters['Case']['name'])
						except:
							tkMessageBox.showerror(title='Error', message="The folder %s cannot be deleted due to the occupation of some other processes. Please abort all the relevant processes or delete the folder manually and try again." % self.parameters['Case']['name'])
							return
					else:
						return
				os.makedirs(WD+'/%s' % self.parameters['Case']['name'])
				os.chdir(WD+'/%s' % self.parameters['Case']['name'])
				if self.parameters['Case']['type'] == 'single-objective':
					with open("result.txt", 'w') as f:
						f.write("name; \t values of variables; \t fitness\n")
						for i, j, k in zip(list(results['name']), list(results['values of variables']), list(results['fitness'])):
							f.write("%s; \t %s; \t %s\n" % (str(i), str(j), str(k)))
				else:
					GEN = len(results)
					objectives = self.parameters['obj_setting']
					for i in range(GEN):
						with open("final_GEN%d.txt" % i, 'w') as f:
							f.write("name; \t values of variables; ")
							for j in objectives[:-1]:
								f.write("\t %s; " % j[0])
							f.write("\t %s\n" % objectives[-1][0])
							for k in range(len(results[i])):
								f.write("%s; \t %s; " % (str(list(results[i]['name'])[k]), str(list(results[i]['values of variables'])[k])))
								for objective in objectives[:-1]:
									f.write("\t %s; " % str(list(results[i][objective[0]])[k]))
								f.write("\t %s\n" % str(list(results[i][objectives[-1][0]])[k]))


			self.ResultWidget = Result(self.ControlFrame, self.parameters, self.Optimize, self.restart.get(), self.cwd, self.allunits['Login'], viewresults=True )
			self.ResultWidget.newwindow.protocol("WM_DELETE_WINDOW", self.closeRW)
				

	def setseed(self):
		self.SeedDialog = Pmw.Dialog(self.parent,
				  title='Set the Seed',
				  buttons=('OK', 'Cancel'),
				  #defaultbutton='Apply',
				  command=self.actionSeed)


		self.SeedFrame = Pmw.ScrolledFrame(self.SeedDialog.interior(), usehullsize=1, hull_height=210, hull_width=160)		
		self.SeedFrame.pack()
		self.variables = []		
		for i in self.parameters['design variables']:
			label = i[0]
			exec('self.var_%s=StringVar()' % label)
			exec("""self.Seed_%s= Pmw.EntryField(self.SeedFrame.interior(),
							labelpos='w', 
							label_text=label+':',
							entry_width=14,
							entry_textvariable=self.var_%s)""" % (label,label))
			exec("self.Seed_%s.pack(side='top')" % label)
			exec('self.variables.append(self.Seed_%s)' % label)
		Pmw.alignlabels(self.variables)
	

		
	def actionSeed(self, value):
		if value == 'OK':
			seed = []
			for widgit, var in zip(self.variables, self.parameters['design variables']):
				if var[1] == "continuous":
					try:
						value = float(widgit.get())
					except:
						tkMessageBox.showerror(title='Error', message='the value for %s must be a number!' )
						return
					else:
						options = [ var[3]+ (var[4]-var[3])*float(i)/(2**var[2]-1) for i in range(2**var[2]) ]
						residual = [abs(value-i) for i in options]
						ind = residual.index(min(residual))
						stack = []
						for i in range(var[2]):
							stack = ind%2
							ind = ind/2
						for i in range(var[2]):
							seed.append(stack[var[2]-i])
				else:	
					value = widgit.get()
					try:
						ind = var[-1].index(value)
					except:
						optiions = ''
						for i in var[-1]:
							options = option+i *'\n'
						tkMessageBox.showerror(title='Error', message='%s is not a valid candidate value for %s! The valid values are: \n %s' % (value, var[0], options))
						return
					else:
						extra = 2**var[2]-len(var[-1])
						if ind < extra:
							ind = ind * 2
						else:
							ind = ind + extra 
						stack = []
						for i in range(var[2]):
							stack = ind%2
							ind = ind/2
						for i in range(var[2]):
							seed.append(stack[var[2]-i])							
			self.seed = seed
		self.SeedDialog.destroy()

	def checkThreadStatus(self):
		if self.multithreads.get():
			self.InputThread.configure(entry_state='normal')
		else: self.InputThread.configure(entry_state='disabled')

	def checkSeedStatus(self):
		if self.seeding.get():
			self.SetSeed.config(state='normal')
		else: self.SetSeed.config(state='disabled')

if __name__== "__main__":		
	variableList = [['var1'], ['var2'], ['var3'],['var4'], ['var5'], ['var6'],['var7'], ['var8'], ['var9']]
	root = Tk()
	Pmw.initialise(root)
	Control(root, variableList, seed)
	root.mainloop()
