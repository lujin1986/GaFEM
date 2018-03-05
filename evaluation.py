from mttkinter.mtTkinter import *
from ttk import *
import Pmw
import tkFileDialog
from glob import glob
from PIL import Image, ImageTk 
import os

class Evaluation:
	def __init__(self, parent,  allunits):
		parent.__init__
		self.allunits = allunits
		self.padx=10
		self.style = Style()
		self.style.configure('Title.TLabelframe', font=('Times New Roman', 11, 'bold'))
		self.style.configure('directory.TButton', borderwidth=0.01)
		image = Image.open('images/directory.png')
		image = image.resize((40, 16), Image.ANTIALIAS)
		self.directoryImage = ImageTk.PhotoImage(image)
		self.parent = parent
		self.grow = StringVar()
		self.template = StringVar()
		self.objective = StringVar()
		self.EvaluationFrame = LabelFrame(parent, text="Evaluation")
		self.EvaluationFrame.pack()
		self.Frame= Frame(self.EvaluationFrame)
		self.Frame.pack(side='top')
		self.GrowInput= Pmw.EntryField(self.Frame,
				labelpos='w', 
				label_text='grow:',
				entry_width=30,
				entry_textvariable=self.grow)
		self.GrowInput.grid(row=0, column=0, padx=self.padx)
		self.GrowButton = Button(self.Frame,  image= self.directoryImage, command=self.setGrow)
		self.GrowButton.grid(row=0, column=1)		
		self.TemplateInput= Pmw.EntryField(self.Frame,
				labelpos='w', 
				label_text='template:',
				entry_width=30,
				entry_textvariable=self.template)
		self.TemplateInput.grid(row=1, column=0, padx=self.padx)
		self.TemplateButton = Button(self.Frame,  image= self.directoryImage, command=self.setTemplate)
		self.TemplateButton.grid(row=1, column=1)				
		self.ObjectiveInput= Pmw.EntryField(self.Frame,
				labelpos='w', 
				label_text='objective:',
				entry_width=30,
				entry_textvariable=self.objective)
		self.ObjectiveInput.grid(row=2, column=0, padx=self.padx)
		self.ObjectiveButton = Button(self.Frame,  image= self.directoryImage, command=self.setObjective)
		self.ObjectiveButton.grid(row=2, column=1)
		self.Automatic = Button(self.Frame, text = 'auto-fill', command=self.auto)
		self.Automatic.grid(row=0, column=2,rowspan=3, sticky='nse', padx=self.padx)				
		Pmw.alignlabels([self.GrowInput, self.TemplateInput, self.ObjectiveInput], sticky='e')

	def pack(self, side='top', fill=None, expand=None, padx=0, pady=0):
		self.EvaluationFrame.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)	


	def setGrow(self):
		file = tkFileDialog.askopenfilenames(filetypes=[('All files','*')])
		if len(file) < 2:
			if file:
				self.template.set(file[0])
		else:
			text = ''
			for item in file:
				text += ', %s' % str(item)
			self.grow.set(text)


	def setTemplate(self):
		file = tkFileDialog.askopenfilenames(filetypes=[('All files','*')])
		if len(file) < 2:
			if file:
				self.template.set(file[0])
		else:
			text = ''
			for item in file:
				text += ', %s' % str(item)
			self.template.set(text)

		
	def setObjective(self):
		file = tkFileDialog.Open(filetypes=[('Python script','*.py')]).show()
		if file:
			self.objective.set(file)
		
	def auto(self):	
		self.WD = self.allunits['Case'].WD.get()
		if os.path.exists(self.WD):
			os.chdir(self.WD)
			file = glob("*template*")
			if len(file) < 2:
				if file:
					self.template.set("%s/%s" % (self.WD,file[0]))
			else:
				text = ''
				for item in file:
					text += ', %s/%s' % (self.WD,item)
				text=text[2:]
				self.template.set(text)
				
			file = glob("*grow*")
			if len(file) < 2:
				if file:
					self.grow.set("%s/%s" % (self.WD,file[0]))
			else:
				text = ''
				for item in file:
					text += ', %s/%s' % (self.WD,item)
				text=text[2:]
				self.grow.set(text)
			if os.path.exists(os.path.join(self.WD,'objective.py')):
				self.objective.set("%s/%s" % (self.WD,'objective.py'))
			

if __name__ == "__main__":	
	root = Tk()
	Pmw.initialise(root)
	Evaluation(root)
	root.mainloop()
