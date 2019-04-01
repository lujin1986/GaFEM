from tkinter import *
from pickle import dump, load
from tkinter.ttk import *
from time import sleep
import tkinter.messagebox as tkMessageBox
import threading
import paramiko
import Pmw
import os
from datetime import datetime


class Login:
	def __init__(self, parent, parameters, all):
		parent.__init__
		self.parent = parent
		self.allunits = all
		self.parameters = parameters
		self.parameters['Login']['cluster']= 0
		self.sAddress = StringVar()
		self.p = self.params()
		self.username = StringVar()
		self.password = StringVar()
		self.checkb = IntVar()
		self.server = None
		self.abqLicense_on = False
		self.licenseThread = None
		self.cwd = os.getcwd()
		if self.p['checkb']:
			self.username.set(self.p['username'])
			self.password.set(self.p['password'])
			self.checkb.set(self.p['checkb'])
			self.sAddress.set(self.p['server'])
			self.parameters['Login']['server']=self.p['server']
		else:
			self.username.set('')
			self.password.set('')
		self.license = StringVar()
		self.license.set('--')	
		self.LoginFrame = LabelFrame(parent, text='Login')		
		self.user = Frame(self.LoginFrame, borderwidth=2, relief='groove')
		self.user.grid(row=0, column=0, padx=5)
		self.labelUsername = Label(self.user, text = 'Username:')
		self.labelUsername.grid(row=0, column=0, sticky= 'E')
		self.labelPassword = Label(self.user, text = 'Password:')
		self.labelPassword.grid(row=1, column=0, sticky='E')
		self.entryUser = Entry(self.user, textvariable=self.username)
		self.entryUser.grid(row=0, column=1, columnspan=2, sticky='WE')
		self.entryPass= Entry(self.user, show='*', textvariable=self.password)
		self.entryPass.grid(row=1, column=1, columnspan=2, sticky='WE')
		self.cbutton = Checkbutton(self.user, text = "Remember me", variable=self.checkb)
		self.cbutton.grid(row=2, column=0, sticky='E')
		#lgbutton = Button(self.use,  text= self.buttonl.get(), command=self.buttonPress)
		self.lgibutton = Button(self.user,  text= 'Login', command=self.buttonLogin)
		self.lgibutton.grid(row=2, column=1, sticky='W')
		self.lgobutton = Button(self.user,  text= 'Logout', command=self.buttonLogout, state = 'disabled')
		self.lgobutton.grid(row=2, column=2, sticky='E')		
		self.display = Frame(self.LoginFrame, borderwidth=2, relief='groove')
		self.display.grid(row=1, column=0, ipady=12, padx=5, sticky='wens')
		self.radio_var = IntVar()
		self.radios = []
		for radio, i in zip(('Run computations on PC', 'Run computations on cluster'), (0, 1)):
			r = Radiobutton(self.display, text=radio, variable=self.radio_var, value=i, command=self.switchmode)
			r.grid(row=i, columnspan=2, sticky='w')
			self.radios.append(r)
		self.radios[1].config(state='disabled')
		self.labelLicense = Label(self.display, text = 'ABAQUS license:')
		self.labelLicense.grid(row=3, column=0, sticky= 'w', padx=12)
		self.showLicense = Label(self.display, text = self.license.get())
		self.showLicense.grid(row=3, column=1, sticky= 'w', padx=12)

	def pack(self, side='top', fill=None, expand=None, padx=0, pady=0):
		self.LoginFrame.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)		

	def switchmode(self):
		self.parameters['Login']['cluster']=self.radio_var.get()

	def buttonLogin(self):
		if 'server' in self.parameters['Login'].keys() and self.parameters['Login']['server']:
			self.lgibutton.config(state='disabled')
			self.lgobutton.config(state='normal')
			try:
				server = paramiko.Transport((self.parameters['Login']['server'], 22))
				server.connect(username=self.username.get(), password=self.password.get())
				self.server = server
				if self.checkb.get():
					self.p = {'username': self.username.get(), 'password':self.password.get(), 'checkb':self.checkb.get(), 'server':self.sAddress.get()}
					f = open('%s/login.txt' % self.cwd, 'wb')
					dump(self.p, f)
					f.close()
				else:
					self.p = {'username': '', 'password':'', 'checkb':0, 'server':''}
					f = open('%s/login.txt' % self.cwd, 'wb')
					dump(self.p, f)
					f.close()
				self.abqLicense_on=True
				self.licenseThread = threading.Thread(target=self.abqLicense)
				self.licenseThread.start()
				self.radios[1].config(state='normal')
			except:
				self.lgobutton.config(state='disabled')
				self.lgibutton.config(state='normal')
				tkMessageBox.showerror(title='Error', message="Login fail! Please check the username and password as well as the setting about the server." )
		else:
			self.setServer()
		
	def abqLicense(self):
		while self.abqLicense_on:
			try: 
				channel = self.server.open_session()
				try:		
					channel.exec_command('cat output')
					output = channel.makefile('rb', -1).readlines()
					if output[1] == 'Viewer licenses:\n':
						for i in output:
							if 'available.' in i.split():
								available = int(i.split()[-4])
							if 'issued:' in i.split():
								issued = int(i.split()[-1])					
						total = available+issued
						self.showLicense.config(text="%d / %d licenses available" % (available, total))				
						#self.license.set("%d / %d" % (available, total))
						sleep(1)
				except:
					pass 
			except:	

				self.lgobutton.config(state='disabled')
				self.lgibutton.config(state='normal')
				self.abqLicense_on=False
				self.server.close()
				self.showLicense.config(text="--")
				self.radios[1].config(state='disabled')		
				self.radio_var.set(0)
				if self.allunits['Control'].Optimize.cget('text') != "      Start   \nOptimization" and self.radio_var.get():
					self.allunits['Control'].start()
					tkMessageBox.showerror(title='Error', message="The connection with the server has been lost!. The optimization has been stopped automatically. (%s)" % str(datetime.now()))
				else:
					tkMessageBox.showerror(title='Error', message="The connection with the server has been lost!")
				
	def buttonLogout(self):
		if self.allunits['Control'].ResultWidget and self.allunits['Control'].ResultWidget.switch and self.allunits['Control'].ResultWidget.cluster:
			tkMessageBox.showerror(title='Error', message="Optimization (cluster mode) is still running! Please stop the optimization first." )
		else:
			self.lgobutton.config(state='disabled')
			self.lgibutton.config(state='normal')
			self.abqLicense_on=False
			self.server.close()
			self.showLicense.config(text="--")
			self.radios[1].config(state='disabled')		
			self.radio_var.set(0)
		
	def params(self):
		try:
			f = open('login.txt', 'rb')
		except IOError:
			p = {'username': '', 'password':'', 'checkb': 0, 'server':''}
		else:
			p = load(f)
			f.close()
		return p
		
	def setServer(self):
		self.SetServer = Pmw.Dialog(self.parent, 
				buttons=('OK', 'Cancel'),
				command = self.actionSetServer)
		self.Instruction = Label(self.SetServer.interior(), text="Input the name or the IP address of the server:")
		self.Instruction.pack()
		self.SAddress = Entry(self.SetServer.interior(), textvariable=self.sAddress)
		self.SAddress.pack()

	def actionSetServer(self, result):
		if result == 'OK':
			self.parameters['Login']['server']=self.sAddress.get()
		self.SetServer.destroy()

				
if __name__ == "__main__":		
				
	root = Tk()
	login = Login(root, None)
	root.mainloop()
