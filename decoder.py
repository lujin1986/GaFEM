from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
from pickle import dump, load
import Pmw
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk 
class InputVar:
	def __init__(self, parent, parameters):
		parent.__init__
		self.parent = parent
		self.parameters = parameters
		self.style = ttk.Style()
		self.style.configure('Title.TLabelframe', font=('Times New Roman', 11))
		self.style.configure('directory.TButton', borderwidth=0.01)
		self.choice = StringVar()
		self.choice.set('')
		self.label = StringVar()
		self.label.set('')
		self.type = StringVar()
		self.type.set('continuous')	
		self.type_ = StringVar()
		self.digit = StringVar()
		self.digit.set('')
		self.max = StringVar()
		self.max.set('')
		self.min = StringVar()
		self.min.set('')
		self.candidate = StringVar()
		self.candidate.set('')
		self.candidates = []
		self.candidates1 = []
		self.index = None
		self.list=['label', 'type', 'digit', 'min', 'max', 'candidate']
		self.listC = ['digit', 'max', 'min']
		self.variableList = []
		self.choice.set('continuous')
		self.checkb = IntVar()
		self.checkb.set(0)
		self.constraint = StringVar()
		self.constraint.set('')
		self.EditDialog=None
		self.SetCandidates=None
		
		self.ParametersFrame = LabelFrame(parent, text='Variables to be Optimized', style='Title.TLabelframe')
		self.ParametersFrame.pack()
		self.Input = Frame(self.ParametersFrame)
		self.Input.pack(side='top')
		self.Label= Pmw.EntryField(self.Input,
                        labelpos='w', 
                        label_text='label: ',
                        entry_width=15,
                        entry_textvariable=self.label)
		self.Label.grid(row=0, column=0,padx=2)
		self.Type =Pmw.OptionMenu(self.Input,              
				labelpos='w',  # n, nw, ne, e, and so on
				label_text='type:',
				items=['continuous', 'discrete'],
				menubutton_textvariable=self.choice,
				menubutton_width=9,
				command=self.chooseType)	
		self.Type.grid(row=1, column=0,padx=2)
		Pmw.alignlabels([self.Label, self.Type], sticky='e')
		self.Max= Pmw.EntryField(self.Input,
				labelpos='w', 
				label_text='max: ',
				entry_width=14,
				validate={'validator':'real'},
				entry_textvariable=self.max)
		self.Max.grid(row=0, column=1,padx=4)	
		self.Min= Pmw.EntryField(self.Input,
				labelpos='w', 
				label_text='min: ',
				entry_width=14,
				validate={'validator':'real'},
				entry_textvariable=self.min)
		Pmw.alignlabels([self.Max, self.Min], sticky='e')
		self.Min.grid(row=1, column=1,padx=4)
		self.Digit= Pmw.EntryField(self.Input,
				labelpos='w', 
				label_text='digit:',
				entry_width=6,
				validate={'validator':'integer'},
				entry_textvariable=self.digit)
		self.Digit.grid(row=0, column=2,padx=4)
		self.Candidates = Button(self.Input,  text= 'candidates', command=self.setCandidates, state = 'disabled')
		self.Candidates.grid(row=1, column=2)
		self.Add = Button(self.Input,  text= 'add', command=self.addItem)		
		self.Add.grid(row=0, column=3,rowspan=2, sticky = 'ns', padx=4, pady=2)	
		self.DisplayFrame = Frame(self.ParametersFrame)
		self.DisplayFrame.pack()
		self.Tree = ttk.Treeview(self.DisplayFrame, height=5, columns=self.list[1:])
		self.Tree.column('#0', width= 100, anchor = 'center')
		self.Tree.heading('#0', text='label')
		for column in self.list[1:]:
			self.Tree.column(column, width=100, anchor='center')
			self.Tree.heading(column, text=column)		
		self.Tree.pack(side='left', pady=5)
		self.ScrollBar = Scrollbar(self.DisplayFrame, command=self.Tree.yview)
		self.ScrollBar.pack(side = 'left', pady=5, fill='y')
		self.Tree['yscrollcommand'] = self.ScrollBar.set
		self.Buttons = Frame(self.ParametersFrame)
		self.Buttons.pack(side = 'top')
		self.Constraints = Frame(self.Buttons)
		self.Constraints.pack(side='left')
		self.Constraint1 = Checkbutton(self.Constraints, text = "constraint", variable=self.checkb, command=self.checkbStatus)	
		self.Constraint1.pack(side='left', anchor='w')
		self.ConstraintE = Entry(self.Constraints, width=21, state='disabled', textvariable=self.constraint)
		self.ConstraintE.pack(side='left', anchor='w', padx=5)
		image = Image.open('images/directory.png')
		image = image.resize((40, 16), Image.ANTIALIAS)
		self.directoryImage = ImageTk.PhotoImage(image)
		self.Constraint2 = Button(self.Constraints,  image= self.directoryImage, state='disabled', command=self.setConstraint)
		self.Constraint2.pack(side='left', anchor='w')
		self.Tools = Frame(self.Buttons)
		self.Tools.pack(side='right')
		self.Delete = Button(self.Tools,  text= 'delete', command=self.delete_record)
		self.Delete.pack(side='right',anchor='e')
		self.Edit = Button(self.Tools,  text= 'modify', command=self.edit_record)
		self.Edit.pack(side='right',anchor='e')
		self.Separator = Separator(self.Tools, orient='vertical').pack(side='right', fill=Y, padx=10)


	def pack(self, side='top', fill=None, expand=None, padx=0, pady=0):
		self.ParametersFrame.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)

		
	def chooseType(self, value):
		if value == 'continuous':
			self.Candidates.config(state='disabled')
			for item in [self.digit, self.max, self.min]:
				item.set('')
			for item in [self.Digit, self.Max, self.Min]:
				item.component('entry').config(state='normal')
			self.type.set('continuous')
			self.candidates = []
		if value == 'discrete':
			self.Candidates.config(state='normal')				
			for item in [self.Digit, self.Max, self.Min]:
				item.component('entry').config(state='disabled')
			self.type.set('discrete')
			for item in self.listC:
				getattr(self, item).set('--')	
			if not self.EditDialog:
				self.setCandidates()	
				
	def addItem(self):
		a = []
		for i in self.list[:-1]:
			a.append(getattr(self, i).get())
		if a[1] == 'continuous':
			a.append([])
		else:
			a.append(self.candidates)
		if a[0]:
			flag = 0
			for i in self.variableList:
				if a[0] == i[0]:
					flag = 1
					break
			if flag:
				tkMessageBox.showerror(title='Error', message='The label must be unique.')
			else:
				if a[1] == 'continuous':
					if a[2] and a[3] and a[4]:
						self.variableList.append(a)		
						self.view_records()
					else:
						tkMessageBox.showerror(title='Error', message='The fields for digit, max and min can not be empty.')
				else:
					if len(a[5]) >= 2:
						self.variableList.append(a)		
						self.view_records()
					else:
						tkMessageBox.showerror(title='Error', message='The input for candidates should contain at least 2 items.')	
		else:
			tkMessageBox.showerror(title='Error', message='The field for label can not be empty.')
				
		
		
	def view_records(self):
		items = self.Tree.get_children()
		for item in items:
			self.Tree.delete(item)
		for parameter in self.variableList:
			if parameter[1] == 'continuous':
				values = parameter[:-1]
				values.append('--')
			else:
				values = parameter[:-1]
				values.append(str(len(parameter[-1])))
			self.Tree.insert('', 'end', text=values[0], values=values[1:])	
			
	def delete_record(self):
		labels = [self.Tree.item(i)['text'] for i in self.Tree.selection()]
		for label in labels:
			ind = [self.variableList.index(i) for i in self.variableList if i[0] == label]
			del self.variableList[ind[0]]
		self.view_records()
		

	def edit_record(self):
		try:
			label = self.Tree.item(self.Tree.selection()[0])['text']
			values = self.Tree.item(self.Tree.selection()[0])['values']
			self.index = [self.variableList.index(i) for i in self.variableList if i[0] == label]	
			for i, item in zip(self.list[:-1], self.variableList[self.index[0]][:-1]):
				getattr(self, i).set(item)
			self.candidates = self.variableList[self.index[0]][-1]
			self.dialogEdit()
			self.view_records()
		except:
			pass
		
	def dialogEdit(self):
		if self.EditDialog:
			self.EditDialog.destroy()
		self.EditDialog = Pmw.Dialog(self.parent,
				  title='Edit the variable',
				  buttons=('OK', 'Cancel'),
				  #defaultbutton='OK',
				  command=self.actionEdit)
		self.Label_= Pmw.EntryField(self.EditDialog.interior(),
                        labelpos='w', 
                        label_text='label: ',
                        entry_width=14,
                        entry_textvariable=self.label)
		self.Label_.pack(side='left')
		self.Type_ =Pmw.OptionMenu(self.EditDialog.interior(),              
				labelpos='w',  
				label_text='type:',
				items=['continuous', 'discrete'],
				menubutton_textvariable=self.choice,
				menubutton_width=8,
				command=self.chooseType_)	
		self.Type_.pack(side='left')

		self.Max_= Pmw.EntryField(self.EditDialog.interior(),
				labelpos='w', 
				label_text='max: ',
				entry_width=14,
				entry_textvariable=self.max)
		self.Max_.pack(side='left')
		self.Min_= Pmw.EntryField(self.EditDialog.interior(),
				labelpos='w', 
				label_text='min: ',
				entry_width=14,
				entry_textvariable=self.min)
		self.Min_.pack(side='left')
		self.Digit_= Pmw.EntryField(self.EditDialog.interior(),
				labelpos='w', 
				label_text='digit:',
				entry_width=14,
				entry_textvariable=self.digit)
		self.Digit_.pack(side='left')		
		self.Candidates_ = Button(self.EditDialog.interior(),  text= 'candidates', command=self.setCandidates, state = 'disabled')
		self.Candidates_.pack(side='left')
		if self.type.get() == 'continuous':
			self.Candidates_.config(state='disabled')
			for item in [self.Digit_, self.Max_, self.Min_]:
				item.component('entry').config(state='normal')
			self.Type_.setvalue('continuous')
		else:
			self.Candidates_.config(state='normal')				
			for item in [self.Digit_, self.Max_, self.Min_]:
				item.component('entry').config(state='disabled')
			self.Type_.setvalue('discrete')	
			self.setCandidates()	
	def chooseType_(self, value):
		if value == 'continuous':
			self.Candidates_.config(state='disabled')
			for item in [self.digit, self.max, self.min]:
				item.set('')
			for item in [self.Digit_, self.Max_, self.Min_]:
				item.component('entry').config(state='normal')
			self.type.set('continuous')
			self.candidates = []
		if value == 'discrete':
			self.Candidates_.config(state='normal')				
			for item in [self.Digit_, self.Max_, self.Min_]:
				item.component('entry').config(state='disabled')
			self.type.set('discrete')
			for item in self.listC:
				getattr(self, item).set('--')	
						  
	def actionEdit(self, result):
		if result == 'OK':
			a = []
			for i in self.list[:-1]:
				a.append(getattr(self, i).get())
			a.append(self.candidates)
			flag = 0
			others = [i for i in self.variableList if i!= self.variableList[self.index[0]]]
			for i in others:
				if i[0] == a[0]:
					flag=1
					break
			if flag:
				tkMessageBox.showerror(title='Error', message='The label must be unique')	
			else:
				self.variableList[self.index[0]]=a	
				self.view_records()	
				self.chooseType(self.type.get())
				self.EditDialog.destroy()
				self.EditDialog = None
		else:	
			self.chooseType(self.type.get())
			self.EditDialog.destroy()
			self.EditDialog=None
			
	def setCandidates(self):
		self.candidates1= self.candidates[:]
		if self.SetCandidates:
			self.SetCandidates.destroy()
		self.SetCandidates = Pmw.Dialog(self.parent,
				  title='Input candidate values',
				  buttons=('OK', 'Cancel'),
				  #defaultbutton='Cancel',
				  command=self.actionCandidate)
		self.SetCandidates.protocol("WM_DELETE_WINDOW", self.closeSC)
		self.EntryCandidate= Pmw.EntryField(self.SetCandidates.interior(),
				labelpos='w', 
				label_text='add a candidate value: ',
				entry_width=14,
				entry_textvariable=self.candidate)
		self.EntryCandidate.grid(row=0, column=0, columnspan=3)
		self.AddCandidate = Button(self.SetCandidates.interior(),  text= 'add', command=self.add_candidate)
		self.AddCandidate.grid(row=1, column=0)
		self.DeleteCandidate = Button(self.SetCandidates.interior(),  text= 'delete', command=self.delete_candidate)
		self.DeleteCandidate.grid(row=1, column=1)
		self.DeleteCandidate = Button(self.SetCandidates.interior(),  text= 'clear', command=self.clear_candidate)
		self.DeleteCandidate.grid(row=1, column=2)
		self.TreeCandidates = ttk.Treeview(self.SetCandidates.interior(), height=5)
		self.TreeCandidates.grid(row=2, column=0, columnspan=3)
		self.TreeCandidates.column('#0', width= 500, anchor = 'w')
		self.TreeCandidates.heading('#0', text='candidates')	
		self.view_candidates()
		
	def closeSC(self):
		self.SetCandidates.destroy()		
			
	def view_candidates(self):
		items = self.TreeCandidates.get_children()
		for item in items:
			self.TreeCandidates.delete(item)
		if self.candidates:
			for candidate in self.candidates:
				self.TreeCandidates.insert('', 'end', text=candidate)	
				
	def add_candidate(self):
		self.candidates.append(self.candidate.get())
		self.view_candidates()
				
	def delete_candidate(self):
		labels = [self.TreeCandidates.item(i)['text'] for i in self.TreeCandidates.selection()]
		for label in labels:
			ind = [self.candidates.index(i) for i in self.candidates if i == label]
			del self.candidates[ind[0]]
		self.view_candidates()		

	def clear_candidate(self):
		self.candidates = []
		self.view_candidates()		
		
	def actionCandidate(self, result):
		if result=='Cancel':
			self.candidates=self.candidates1[:]
			self.SetCandidates.destroy()
			self.SetCandidates=None
		else:
			if len(self.candidates) < 2:
				tkMessageBox.showerror(title='Error', message='The input for candidates should contain at least 2 items.')
			else:	
				if self.EditDialog:
					self.SetCandidates.destroy()
					self.SetCandidates=None 
					self.actionEdit('OK')
				else:
					self.addItem()
					self.SetCandidates.destroy()
					self.SetCandidates=None 	
					
	def checkbStatus(self):
		if self.checkb.get():
			self.ConstraintE.config(state='normal')
			self.Constraint2.config(state='normal')
		else:
			self.ConstraintE.config(state='disabled')
			self.Constraint2.config(state='disabled')
	def setConstraint(self):
		file = tkFileDialog.Open(filetypes=[('Python script','*.py')]).show()
		if file:
			self.constraint.set(file)

if __name__ == "__main__":
		
	root = Tk()
	Pmw.initialise(root)
	InputVar(root)
	root.mainloop()	
