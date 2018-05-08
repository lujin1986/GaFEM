from tkinter import *
from tkinter.ttk import *
from numpy import savetxt, array
from subprocess import Popen, PIPE
from threading import Thread, Lock
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import os, sys
import tkinter.messagebox as tkMessageBox
import Pmw
import paramiko
from matplotlib.figure import Figure
from time import sleep
from datetime import datetime
import pandas as pd
from glob import glob
import os
import shutil
from pickle import dump
from PIL import Image, ImageTk

plt.style.use('ggplot')
	
class Result:
	def __init__(self, parent, parameters, control, restart, cwd, wd, Login, viewresults = None):
		self.parent = parent
		self.viewresults = viewresults
		self.parameters = parameters		
		self.control = control
		self.restart = restart
		self.server = Login.server
		self.switch = 1
		self.process=None
		self.stdout=None
		self.stderr=None
		self.sftp=None
		self.generations=None
		self.plot_GEN=-1
		self.GEN=0
		self.GEN_max = float(parameters['GA parameters']['max. number of generations'])
		self.cluster = self.parameters['Login']['cluster']
		self.remoteFolder=None
		self.lock = Lock()
		self.PrintR = None
		self.final = None
		self.result = None
		self.save = {}
		self.descending = StringVar()
		self.descending.set('True')
		self.sortedby = StringVar()
		self.sortedby.set('name')
		self.wd = wd
		self.style = Style()
		self.style.configure('arrow.TButton', borderwidth=0.01)
		self.f = Figure() #figsize=(5,4), dpi=100
		self.a = self.f.add_subplot(111)

		self.newwindow = Toplevel(parent)
		if self.viewresults:
			self.newwindow.title('Optimization results for %s optimization: %s' % (self.parameters['Case']['type'], self.parameters['Case']['name']))	
		else:		
			self.newwindow.title('%s optimization: %s - in progress...' % (self.parameters['Case']['type'].capitalize(), self.parameters['Case']['name']))	

		self.ConsoleFrame = Frame(self.newwindow)
		self.ConsoleFrame.pack(side='top')
		self.TBFrame=Frame(self.ConsoleFrame)
		self.TBFrame.pack(side='top', fill='both', expand=1)
		self.TextBox = Text(self.TBFrame, fg='white', bg='black',  wrap='word', height = 15)
		self.TextBox.pack(side='left',fill='both', expand=1)
		self.TextBox.tag_configure('green', foreground='green')
		self.TextBox.tag_configure('yellow', foreground='yellow')
		self.TextBox.tag_configure('red', foreground='red')
		self.ScrollBar = Scrollbar(self.TBFrame, command=self.TextBox.yview)
		self.ScrollBar.pack(side='right', fill='y')
		self.TextBox['yscrollcommand'] = self.ScrollBar.set
		self.ProgressFrame = Frame(self.ConsoleFrame)
		self.ProgressFrame.pack(side='top', fill='both', expand=1)
		Label(self.ProgressFrame,text='progress:',justify='left').pack(side='left', anchor='w',  padx=8)
		if self.parameters['Case']['type'] == 'single-objective':
			self.ProgressBar= Progressbar(self.ProgressFrame, length=80, mode='determinate')
		else:  self.ProgressBar= Progressbar(self.ProgressFrame, length=100, mode='determinate')
		self.ProgressBar['maximum']=100
		self.ProgressBar['value']=0
		self.progress = 0
		self.ProgressBar.pack(side='left', fill='both',  expand=1)
		if self.parameters['Case']['type'] == 'single-objective':
			self.ButtonResult = Button(self.ProgressFrame, text='print optimization results', command=self.printR)
			self.ButtonResult.pack(side='left',)
		else:
			self.objectives = [i[0] for i in parameters['obj_setting']]
			self.verAxis = self.objectives[0]
			self.horAxis = self.objectives[-1]
			imageL = Image.open(cwd+'/images/ButtonL.jpg')
			imageL = imageL.resize((16,16), Image.ANTIALIAS)
			self.imageL = ImageTk.PhotoImage(imageL)
			imageR = Image.open(cwd+'/images/ButtonR.jpg')
			imageR = imageR.resize((16,16), Image.ANTIALIAS)
			self.imageR = ImageTk.PhotoImage(imageR)
			self.AxisFrame = Frame(self.ConsoleFrame)
			self.AxisFrame.pack(side='top', fill='both', pady=5, expand=1)
			Label(self.AxisFrame, text="vertical axis:").pack(side='left', anchor='e')
			self.CmbVer = Combobox(self.AxisFrame, state='readonly')
			self.CmbVer['values'] = tuple(self.objectives[:-1])
			self.CmbVer.set(self.objectives[0])
			self.CmbVer.bind('<<ComboboxSelected>>', self.set_ver)
			self.CmbVer.pack(side='left', fill='x', expand=1)
			Label(self.AxisFrame, text="horizontal axis:").pack(side='left', anchor='e', padx=5)
			self.CmbHor = Combobox(self.AxisFrame, state='readonly')
			self.CmbHor['values'] = tuple(self.objectives[1:])
			self.CmbHor.set(self.objectives[-1])
			self.CmbHor.bind('<<ComboboxSelected>>', self.set_hor)
			self.CmbHor.pack(side='left', fill='x', expand=1)
			self.ResultFrame = Frame(self.ConsoleFrame)
			self.ResultFrame.pack(side='top', fill='both', expand=1)
			self.ButtonL = Button(self.ResultFrame, image=self.imageL, command=self.buttonl, state='disabled')
			self.ButtonL.pack(side='left')
			self.CmbGen = Combobox(self.ResultFrame,state='disabled')
			self.CmbGen.bind('<<ComboboxSelected>>', self.set_gen)
			self.CmbGen.pack(side='left', fill='x', expand=1)
			self.ButtonR = Button(self.ResultFrame, image=self.imageR, command=self.buttonr, state='disabled')
			self.ButtonR.pack(side='left')
			Separator(self.ResultFrame, orient='vertical').pack(side='left', padx=5)
			self.ButtonResult = Button(self.ResultFrame, text='print optimization results', command=self.printR)
			self.ButtonResult.pack(side='right')
		self.PlotFrame = Frame(self.ConsoleFrame)
		self.PlotFrame.pack(side='top', fill='both', expand=1)
		self.canvas = FigureCanvasTkAgg(self.f, master=self.PlotFrame)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side='top',  expand=1)
		toolbar = NavigationToolbar2TkAgg(self.canvas, self.PlotFrame)
		toolbar.update()
		self.canvas._tkcanvas.pack(side='top',  expand=1)

		t_runscript = Thread(target=self.runscript)
		t_output = Thread(target=self.readoutput)
		t_plot = Thread(target=self.updateplot)
		t_runscript.start()
		t_output.start()
		t_plot.start()


	def runscript(self):
		if not self.viewresults:
			command = ['python', 'main3.py', str(self.restart), "%s" % self.parameters['Case']['name']]
			savetxt("switch.txt", array([1]))
			if self.cluster:
				self.remoteFolder=str(datetime.now()).replace(' ', '-')
				self.sftp = paramiko.SFTPClient.from_transport(self.server)	
				try: self.sftp.stat('optimization')
				except: self.sftp.mkdir('optimization')
				self.sftp.chdir('optimization')
				self.sftp.mkdir(self.remoteFolder)
				self.sftp.chdir(self.remoteFolder)
				if self.restart:
					files = glob("*")
				else:
					files = ['main3.py', 'objective.py', 'switch.txt']
					for file in self.parameters['template'].split(','):
						files.append(os.path.split(file)[1])
						file = file.strip()
					for file in self.parameters['grow'].split(','):
						file = file.strip()
						files.append(os.path.split(file)[1])
					if self.parameters['constraint'][0]:
						files.append(os.path.split(self.parameters['constraint'][1])[1])
					files.append('%s.opt' % self.parameters['Case']['name'])
				for file in files:
					self.sftp.put(file, file)
				channel = self.server.open_session()
				self.TextBox.insert(END, 'Starting optimizatin engine on the remote computer.\n It might take 1-2 minutes.')
				self.TextBox.see(END)	
				channel.exec_command('cd optimization/%s; %s' % (self.remoteFolder, ' '.join(command)))
				self.stdout = channel.makefile('rb', -1)
				self.stderr = channel.makefile_stderr('rb', -1)
				check = channel.exit_status_ready
				status = channel.recv_exit_status
			else:
				self.process = Popen(command, stdout=PIPE, stderr=PIPE)
				self.stdout = self.process.stdout
				self.stderr = self.process.stderr
				check = self.process.poll
				status = check
			
			while check() is False or check() is None:
				sleep(1)

			error = status()
			savetxt("switch.txt", array([0]))

			if self.cluster:
				sleep(1)
				
				channel = self.server.open_session()
				
				channel.exec_command('cd optimization; rm -fr %s' % self.remoteFolder)
				if channel.recv_exit_status()==1:
					tkMessageBox.showerror(title='Error', message="The removal of intermediate files on the cluster that were generated during the optimization is unsuccessful. Please remove those files manually.")	
			sleep(1)
			self.switch=0
			self.control.config(text="      Start   \nOptimization")
			if error:
				#self.TextBox.config(fg='red')
				self.TextBox.insert(END, 'The optimization process was interrupted unexpectedly.\n', 'red')
				self.TextBox.see(END)	
				self.newwindow.title('%s optimization: %s - Error' % (self.parameters['Case']['type'].capitalize(), self.parameters['Case']['name']))
			else:
				#self.TextBox.config(fg='green')
				if self.GEN+1 == self.GEN_max:
					self.progress = float(self.GEN+1)/self.GEN_max*100
					self.ProgressBar['value'] = self.progress
				if self.progress < 100:
					try:
						self.TextBox.insert(END, 'The optimization process has been stopped.\n', 'yellow')
						self.TextBox.see(END)	
						self.newwindow.title('%s optimization: %s - stopped' % (self.parameters['Case']['type'].capitalize(), self.parameters['Case']['name']))		
					except:
						pass
				else:
					self.TextBox.insert(END, 'The optimization process has been completed!\n', 'green')
					self.TextBox.see(END)	
					self.newwindow.title('%s optimization: %s - completed' % (self.parameters['Case']['type'].capitalize(), self.parameters['Case']['name']))
					if self.parameters['Case']['type'] == 'single-objective':
						results = pd.read_csv("result.txt", sep='; \t ', engine='python')
					else:
						results = []
						for g in range(int(self.GEN_max)):
							result = pd.read_csv('final_GEN%d.txt' % g, sep='; \t ', engine='python')
							results.append(result)
					self.save['Setup']=self.parameters
					self.save['Results']=results
					with open(self.wd+'/%s.res' %self.parameters['Case']['name'], 'wb') as f:
						dump(self.save, f)
				
			try:
				lines=self.stderr.readlines()
				for line in lines:
					self.TextBox.insert(END,line)
					self.TextBox.see(END)	
			except: pass
						
		
	def readoutput(self):
		if not self.viewresults:
			while self.switch:		
				try:
					output = self.stdout.readline()	
				except:
					pass
				else:
					if output:
						try:
							self.TextBox.insert(END,output)
							self.TextBox.see(END)
						except:
							break
				sleep(0.001)
		else:
			self.TextBox.insert(END, 'View the optimization results.')

	def updateplot(self):
		mtime = 0
		mtime_cluster = 0
		GEN_old = -1	

		offspring_max = 1
		population_max = 1
		if self.parameters['Case']['type'] == 'single-objective':
			while self.switch:
				result_file = 'result.txt'
				if self.cluster:
					try:
						new_mtime_cluster = self.sftp.stat(result_file).st_mtime
					except:
						if self.viewresults:
							new_mtime_cluster = 0
						else:
							sleep(1)
							continue
					if new_mtime_cluster > mtime_cluster:
						mtime_cluster = new_mtime_cluster
						allfiles=self.sftp.listdir()
						offsprings = []
						populations = []
						for file in allfiles:
							if file[:10]=='population':
								populations.append(file)
							elif file[:9]=='offspring':
								offsprings.append(file)
						offspring_max_new = len(offsprings)
						population_max_new = len(populations)
						files = []
						for i in range(offspring_max-1, offspring_max_new):
							files.append('offspring_Gen_%d.txt' % i)
						for i in range(population_max-1, population_max_new):
							files.append('population_Gen_%d.txt' % i)
						offspring_max = offspring_max_new
						if population_max_new:
							population_max = population_max_new
						files.append(result_file)
						files.append('valid_ind.txt')
						try:
							self.sftp.stat('history.txt')
						except IOError:
							pass
						else:
							files.append('history.txt')
						for file in files:
							if os.access(file, os.R_OK):
								os.remove(file)
							self.sftp.get(file, file)																		
				if os.access(result_file, os.R_OK):
					new_mtime = os.path.getmtime(result_file)
					if new_mtime > mtime:
						mtime = new_mtime
						self.result = pd.read_csv(result_file, sep='; \t ', engine='python')
						names = list(self.result['name'])
						if names:
							self.GEN=int(names[-1].split('_')[0])
						if self.GEN > GEN_old:
							self.progress = float(self.GEN)/self.GEN_max*100
							self.ProgressBar['value'] = self.progress
						fitnesses = list(self.result['fitness'])

						bestCounts = []
						bests = []
						counts = []
						count = 1
						for fitness in fitnesses:
							if count == 1:
								best = fitnesses[0]
								bestCounts.append(1)
								bests.append(best)
								counts.append(1)
							else:
								counts.append(count)
								if fitness>best:
									bestCounts.append(count)
									bestCounts.append(count)
									bests.append(best)
									bests.append(fitness)
									best = fitness
								else:
									bestCounts.append(count)
									bests.append(best)
							count += 1
						try:
							self.a.clear()
							self.a.plot(counts,fitnesses, 'bo', label='evaluated solutions')
							self.a.plot(bestCounts, bests, 'r-', label='the best found')
							self.a.legend(loc=0)
							self.a.set_xlabel('number of evaluations')
							self.a.set_ylabel('fitness')
							self.a.set_xlim(0, int(max(counts))*1.2)
							self.a.set_ylim(min(bests)-0.2*abs(max(bests)-min(bests)), max(bests)+0.2*abs(max(bests)-min(bests)))
							self.updateprint(self.result)
							self.canvas.draw()
						except:
							break
				if self.viewresults:
					self.switch = 0
				sleep(1)				

		else:
			flag = 1
			result_max = 1
			final_max = 1
			while self.switch:
				if self.cluster:
					try:
						new_mtime_cluster = self.sftp.stat('valid_ind.txt').st_mtime
					except:
						if self.viewresults:
							new_mtime_cluster = 0
						else:
							sleep(1)
							continue
					if new_mtime_cluster > mtime_cluster:
						mtime_cluster = new_mtime_cluster
						offsprings = []
						populations = []
						finals = []
						results = []
						allfiles=self.sftp.listdir()
						for file in allfiles:
							if file[:10]=='population':
								populations.append(file)
							elif file[:9]=='offspring':
								offsprings.append(file)
							elif file[:5] == 'final':
								finals.append(file)
							elif file[:6] == 'result':
								results.append(file)
						offspring_max_new = len(offsprings)
						population_max_new = len(populations)
						result_max_new = len(results)
						final_max_new = len(finals)
						files = []
						for i in range(offspring_max-1, offspring_max_new):
							files.append('offspring_Gen_%d.txt' % i)
						for i in range(population_max-1, population_max_new):
							files.append('population_Gen_%d.txt' % i)
						for i in range(final_max-1, final_max_new):
							files.append('final_GEN%d.txt' % i)
						for i in range(result_max-1, result_max_new):
							files.append('result_GEN%d.txt' % i)
						offspring_max = offspring_max_new
						if population_max_new:
							population_max = population_max_new
						result_max = result_max_new
						if final_max_new:
							final_max = final_max_new
						files.append('valid_ind.txt')
						sleep(0.1)
						for file in files:
							if os.access(file, os.R_OK):
								os.remove(file)
							self.sftp.get(file, file)
								
				final_GEN = glob('final_GEN*')
				self.GEN = len(final_GEN)					
				if self.GEN > GEN_old:
					self.progress = float(self.GEN)/self.GEN_max*100
					self.ProgressBar['value'] = self.progress
					if self.GEN == self.GEN_max and not self.viewresults:
						self.plot_GEN = self.GEN-1
						self.replot()
						break
					self.generations = tuple(['generation %d' % i for i in range(self.GEN+1)])
					if self.viewresults:
						self.generations = self.generations[:-1]
						self.plot_GEN = self.GEN - 1
					self.CmbGen['values'] = self.generations
					if self.plot_GEN == GEN_old:
						self.lock.acquire()
						self.plot_GEN = self.GEN
						self.lock.release()
						self.CmbGen.current(self.plot_GEN)
					GEN_old = self.GEN
				if self.plot_GEN == self.GEN:
					result_file = 'result_GEN%d.txt' % self.GEN
					if os.access(result_file, os.R_OK):
						new_mtime = os.path.getmtime(result_file)
						if new_mtime > mtime:
							mtime = new_mtime
							if self.plot_GEN:
								final_file = 'final_GEN%d.txt' % (self.GEN-1)
								self.final = pd.read_csv(final_file, sep='; \t ', engine='python')
								x_final = self.final[self.horAxis]
								y_final = self.final[self.verAxis]
								self.a.clear()
								self.a.plot(x_final, y_final, 'ro', label='Pareto front - GEN %d' % (self.GEN-1))
							self.result = pd.read_csv('result_GEN%d.txt' % self.GEN, sep='; \t ', engine='python')

							x_result = self.result[self.horAxis]
							y_result = self.result[self.verAxis]
							if self.GEN==0:
								self.a.clear()
							self.a.plot(x_result, y_result, 'bo', label='Population - GEN %d' % self.GEN)			
					self.a.legend(loc=0)
					self.a.set_xlabel(self.horAxis)
					self.a.set_ylabel(self.verAxis)		
					try:
						self.canvas.draw()
					except:
						break
					if self.PrintR:
						self.updateprint(self.result)
				if self.plot_GEN and flag:
					self.CmbGen.config(state='readonly')
					self.ButtonL.config(state='normal')	
					flag = 0	
				if self.viewresults:
					self.switch = 0
				sleep(2)
		

	def set_gen(self, event=None):
		self.lock.acquire()
		self.plot_GEN = self.generations.index(self.CmbGen.get())
		self.lock.release()
		if self.plot_GEN == self.GEN:
			self.ButtonR.config(state='disabled')
		elif self.plot_GEN == 0:
			self.ButtonL.config(state='disabled')
		else: 
			self.ButtonR.config(state='normal')
			self.ButtonL.config(state='normal')
		self.replot()
		if self.PrintR:
			if self.plot_GEN == self.GEN:
				self.updateprint(self.result)
			else:
				self.updateprint(self.final)
			self.PrintR.title("Population of generation %d" % self.plot_GEN)
		
	def set_ver(self, event=None):
		self.verAxis = self.CmbVer.get()
		self.CmbHor['values'] = tuple([i for i in self.objectives if i != self.verAxis])
		self.CmbHor.set(self.horAxis)
		self.CmbVer['values'] = tuple([i for i in self.objectives if i != self.horAxis])
		self.CmbVer.set(self.verAxis)	
		self.replot()			
		
	def set_hor(self, event=None):
		self.horAxis = self.CmbHor.get()
		self.CmbVer['values'] = tuple([i for i in self.objectives if i != self.horAxis])
		self.CmbVer.set(self.verAxis)
		self.CmbHor['values'] = tuple([i for i in self.objectives if i != self.verAxis])
		self.CmbHor.set(self.horAxis)	
		self.replot()
		 	
	def buttonl(self):	
		if self.plot_GEN == self.GEN or self.plot_GEN == (self.GEN_max-1):
			self.ButtonR.config(state='normal')
		self.lock.acquire()
		self.plot_GEN -= 1
		self.lock.release()
		self.CmbGen.current(self.plot_GEN)
		if self.plot_GEN == 0:
			self.ButtonL.config(state='disabled')
		self.replot()
		if self.PrintR:
			if self.plot_GEN == self.GEN:
				self.updateprint(self.result)
			else:
				self.updateprint(self.final)
			self.PrintR.title("Population of generation %d" % self.plot_GEN)
	
	def buttonr(self):
		if self.plot_GEN == 0:
			self.ButtonL.config(state='normal')
		self.lock.acquire()
		self.plot_GEN += 1
		self.lock.release()
		self.CmbGen.current(self.plot_GEN)
		if self.plot_GEN == self.GEN or self.plot_GEN == (self.GEN_max-1):
			self.ButtonR.config(state='disabled')
		self.replot()
		if self.PrintR:
			if self.plot_GEN == self.GEN:
				self.updateprint(self.result)
			else:
				self.updateprint(self.final)
			self.PrintR.title("Population of generation %d" % self.plot_GEN)

	def printR(self):
		if self.PrintR is None:
			self.PrintR=Toplevel(self.parent)
			if self.parameters['Case']['type'] == 'single-objective':
				self.PrintR.title("Evaluated individuals")					
			else:
				self.PrintR.title("Population of generation %d" % self.plot_GEN)
			self.PrintRF = Frame(self.PrintR)
			self.PrintRF.pack(expand=1)
			if self.parameters['Case']['type'] == 'single-objective':
				columns = ['phenotype', 'fitness']
			else:
				columns = ['phenotype']+[objective for objective in self.objectives]
			self.PrintFrame = Frame(self.PrintRF)
			self.PrintFrame.pack(expand=1, fill='both')
			self.Tree = Treeview(self.PrintFrame, height=20, columns=columns)
			self.Tree.column('#0', width= 150, anchor = 'center')
			self.Tree.heading('#0', text='name')
			self.Tree.column('phenotype', width=500, anchor='center')
			self.Tree.heading('phenotype', text='values of variables')
			if self.parameters['Case']['type'] == 'single-objective':
				self.Tree.column('fitness', width=150, anchor='center')
				self.Tree.heading('fitness', text='fitness')
			else:
				for objective in self.objectives:
					self.Tree.column(objective, width=150, anchor='center')
					self.Tree.heading(objective, text=objective)			
			self.Tree.grid(row=0, column=0, pady=5, sticky='wsne')
			self.ScrollBar = Scrollbar(self.PrintFrame, command=self.Tree.yview)
			self.ScrollBar.grid(row=0, column=1,  pady=5, sticky='ns')
			self.Tree['yscrollcommand'] = self.ScrollBar.set
			self.ScrollBar_x = Scrollbar(self.PrintFrame, orient=HORIZONTAL, command=self.Tree.xview)
			self.ScrollBar_x.grid(row=1, column=0,  pady=5, sticky='we')
			self.Tree['xscrollcommand'] = self.ScrollBar.set
			self.SortFrame=Frame(self.PrintRF)
			self.SortFrame.pack(fill='x')
			self.Descending=Pmw.OptionMenu(self.SortFrame,              
				labelpos='w',
				label_text='descending:',
				items=['True', 'False'],
				menubutton_textvariable=self.descending,
				menubutton_width=7,
				command=self.order)
			self.Descending.pack(side='right', anchor='e')
			self.Sortedby=Combobox(self.SortFrame, state='readonly')
			if self.parameters['Case']['type'] == 'single-objective':
				self.Sortedby['values'] = tuple(['name','fitness'])
			else:
				self.Sortedby['values'] = tuple(['name']+self.objectives)
			self.Sortedby.set('name')
			self.Sortedby.bind('<<ComboboxSelected>>', self.sort)
			self.Sortedby.pack(side='right',anchor='e')
			self.Label = Label(self.SortFrame, text='sorted by:')
			self.Label.pack(side='right',anchor='e')
			Separator(self.PrintRF, orient='horizontal').pack(side='top', padx=5, fill='x')
			self.Dismiss = Button(self.PrintRF, text='Dismiss', command=self.dismiss)
			self.Dismiss.pack(side='top')
			self.PrintR.protocol("WM_DELETE_WINDOW", self.dismiss)
			if self.parameters['Case']['type'] == 'single-objective':
				self.updateprint(self.result)
			else:
				if self.plot_GEN == self.GEN:
					self.updateprint(self.result)
				else:
					self.updateprint(self.final)


	def updateprint(self, data):
		if data is not None and self.PrintR is not None:
			try:
				items = self.Tree.get_children()
			except:
				items = []
			for item in items:
				self.Tree.delete(item)
			column = self.Sortedby.get()
			TF = {'True':0, 'False':1}
			ascending = TF[self.descending.get()]
			data = data.sort_values(by=column, ascending=ascending)
			for i in range(len(data)):
				item = data.iloc[i].tolist()
				item[1]=item[1][1:-1]
				self.Tree.insert('', 'end', text=item[0], values=item[1:])

		

	def sort(self, event=None):
		if self.parameters['Case']['type'] == 'single-objective' or self.plot_GEN == self.GEN:
			self.updateprint(self.result)
		else:
			self.updateprint(self.final)	

	def order(self, value='name'):
		self.sortedby.set(value)
		if self.parameters['Case']['type'] == 'single-objective' or self.plot_GEN == self.GEN:
			self.updateprint(self.result)
		else:
			self.updateprint(self.final)	

	def dismiss(self):
		self.PrintR.destroy()
		self.PrintR=None
		

	def replot(self):
		if self.plot_GEN == self.GEN:
			if self.GEN:
				final_file = 'final_GEN%d.txt' % (self.GEN-1)
				self.final = pd.read_csv(final_file, sep='; \t ', engine='python')
				x_final = self.final[self.horAxis]
				y_final = self.final[self.verAxis]
				self.a.clear()
				self.a.plot(x_final, y_final, 'ro', label='Population - GEN %d' % (self.GEN-1))

			result_file = 'result_GEN%d.txt' % self.GEN
			if os.access(result_file, os.R_OK):
				self.result = pd.read_csv(result_file, sep='; \t ', engine='python')
				x_result = self.result[self.horAxis]
				y_result = self.result[self.verAxis]
				self.a.plot(x_result, y_result, 'bo', label='Population - GEN %d' % self.GEN)
		else:
			final_file = 'final_GEN%d.txt' % self.plot_GEN
			self.final = pd.read_csv(final_file, sep='; \t ', engine='python')
			x_final = self.final[self.horAxis]
			y_final = self.final[self.verAxis]
			self.a.clear()
			self.a.plot(x_final, y_final, 'ro', label='Population - GEN %d' % self.plot_GEN)
		
		self.a.legend(loc=0)
		self.a.set_xlabel(self.horAxis)
		self.a.set_ylabel(self.verAxis)	
		try:
			self.canvas.draw()	
		except:
			pass
		
if __name__ == "__main__":
	root = Tk()
	from cPickle import load
	f = open('optimization/case2.opt', 'rb')
	opt = load(f)
	R=Result(root, opt, None, 0)
	root.mainloop()

