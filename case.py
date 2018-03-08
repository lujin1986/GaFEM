#from mttkinter.mtTkinter import *
from ttk import *
import ttk
from PIL import Image, ImageTk 
from set_obj import SetObj
import tkFileDialog

class Case:
	def __init__(self, parent, parameters):
		parent.__init__
		self.parameters = parameters
		self.style = ttk.Style()
		self.style.configure('Title.TLabelframe', font=('Times New Roman', 11))
		self.style.configure('directory.TButton', borderwidth=0.01)
		self.parent = parent
		self.name = StringVar()
		self.type = StringVar()
		self.type.set('single-objective')
		self.name.set('')
		self.WD = StringVar()
		self.WD.set('')
		self.Frame = Frame(parent)
		self.Frame.pack()
		image1 = Image.open('images/logo.jpg')
		image1 = image1.resize((330, 42), Image.ANTIALIAS)
		self.logoImage = ImageTk.PhotoImage(image1)
		self.Logo = Label(self.Frame, image=self.logoImage)
		self.Logo.image=self.logoImage
		self.Logo.pack(pady=5,fill=X)
		self.CaseFrame = LabelFrame(self.Frame, text = 'Optimization case', style='Title.TLabelframe')
		self.CaseFrame.pack(fill=X)
		self.LabelName = Label(self.CaseFrame, text = 'name:')
		self.LabelName.grid(row=1, column=0, sticky='e', padx=5)
		self.EntryName = Entry(self.CaseFrame,justify = "left", width = 24, textvariable=self.name)
		self.EntryName.grid(row=1, column=1, sticky='w')
		self.LabelWD = Label(self.CaseFrame, text = 'WD:')
		self.LabelWD.grid(row=2, column=0, sticky='e', padx=5)
		self.EntryWD = Entry(self.CaseFrame, justify = 'left', width = 24, textvariable=self.WD)
		self.EntryWD.grid(row=2, column=1, sticky='w')
		image2 = Image.open('images/directory.png')
		image2 = image2.resize((40, 16), Image.ANTIALIAS)
		self.directoryImage = ImageTk.PhotoImage(image2)
		self.ButtonWD = Button(self.CaseFrame, image = self.directoryImage, style='directory.TButton', command=self.setWD)
		self.ButtonWD.image=self.directoryImage
		self.ButtonWD.grid(row=2, column=2, sticky='w')
		self.Label3 = Label(self.CaseFrame, text = 'type:')
		self.Label3.grid(row=3, column=0, sticky='e', padx=5)
		self.radios = []
		for radio, i, row in zip(('single-objective optimization', 'multi-objective optimization'), ('single-objective', 'multi-objective'), (4, 5)):
			r = Radiobutton(self.CaseFrame, text=radio, variable=self.type, value=i, command=self.set_obj)
			r.grid(row=row, column=1, padx=10, sticky='wens')
			self.radios.append(r)
		self.radios[0].invoke()


	def pack(self, side='top', fill=None, expand=None, padx=0, pady=0):
		self.Frame.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)

	def setWD(self):
		file = tkFileDialog.askdirectory()
		if file:
			self.WD.set(file)	

	def set_obj(self):
		if self.type.get() == 'multi-objective':
			SetObj(self.parent, self.parameters)	
		
if __name__ == "__main__":
	root = Tk()
	Case(root)
	root.mainloop()	
