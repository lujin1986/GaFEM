from tkinter import *
from tkinter.ttk import *
import Pmw
import tkinter.messagebox as tkMessageBox


class SetObj:
	def __init__(self, parent, parameters):
		self.parent = parent
		self.parameters = parameters
		self.name = StringVar()
		self.type = StringVar()
		self.type.set('maximization')
		if 'obj_setting' in self.parameters.keys():
			labels = {1:'maximization', -1:'minimization'}
			self.objectives = [[i[0], labels[i[1]]] for i in self.parameters['obj_setting']]
		else:
			self.objectives = []
		self.newwindow = Pmw.Dialog(self.parent,
					title='Set objectives',
					buttons = ('OK', 'Cancel'),
					command=self.set)
		self.Frame = Frame(self.newwindow.interior())
		self.Frame.pack()
		self.EntryFrame = Frame(self.Frame)
		self.EntryFrame.pack(fill='x')
		self.Name = Pmw.EntryField(self.EntryFrame, labelpos='w', label_text='name of the objective:',
						entry_width=14, entry_textvariable=self.name)
		self.Name.pack(side='left')
		self.Type = Pmw.OptionMenu(self.EntryFrame, labelpos='w', label_text='type:',
					items=['maximization', 'minimization'],
					menubutton_textvariable=self.type,
					menubutton_width=12)
		self.Type.pack(side='left', padx = 10)
		self.DisplayFrame = Frame(self.Frame)
		self.DisplayFrame.pack(fill='x')
		self.Tree = Treeview(self.DisplayFrame, height=5, columns=['type'])
		self.Tree.column('#0', width= 150, anchor = 'center')
		self.Tree.heading('#0', text='name')
		self.Tree.column('type', width=150, anchor='center')
		self.Tree.heading('type', text='type')	
		self.Tree.grid(row=0, column=0, rowspan=2, pady=5)
		self.ScrollBar = Scrollbar(self.DisplayFrame, command=self.Tree.yview)
		self.ScrollBar.grid(row=0, column=1, rowspan=2, pady=5, sticky='ns')
		self.Tree['yscrollcommand'] = self.ScrollBar.set
		self.Add = Button(self.DisplayFrame, text='add', command=self.add)
		self.Add.grid(row=0, column=2, pady=5, sticky='ne')
		self.Delete = Button(self.DisplayFrame,  text= 'delete', command=self.delete)
		self.Delete.grid(row=1, column=2, pady=5, sticky='se')
		self.view_records()

	def add(self):
		a = [self.name.get(), self.type.get()]
		if a[0]:
			flag = 0
			for i in self.objectives:
				if a[0] == i[0]:
					flag = 1
					break
			if flag:
				tkMessageBox.showerror(title='Error', message='The name of the objective must be unique.')
			else:
				self.objectives.append(a)		
				self.view_records()	
		else:
			tkMessageBox.showerror(title='Error', message='The field for the name of the objective can not be empty.')

	def delete(self):
		labels = [self.Tree.item(i)['text'] for i in self.Tree.selection()]
		for label in labels:
			ind = [self.objectives.index(i) for i in self.objectives if i[0] == label]
			del self.objectives[ind[0]]
		self.view_records()		
	
	def view_records(self):
		items = self.Tree.get_children()
		for item in items:
			self.Tree.delete(item)
		for objective in self.objectives:
			self.Tree.insert('', 'end', text=objective[0], values=[objective[1]])	

	def set(self, result):
		if result == 'OK':
			if len(self.objectives) < 2:
				tkMessageBox.showerror(title='Error', message='The minimum number of objectives is 2.')
			else:
				self.parameters['obj_setting'] = []
				weight = {'maximization':1, 'minimization':-1}

				for objective in self.objectives:
					self.parameters['obj_setting'].append([objective[0], weight[objective[1]]])
				self.newwindow.destroy()
		else:
			self.newwindow.destroy()
			
			
if __name__ == "__main__":
		
	root = Tk()
	Pmw.initialise(root)
	SetObj(root, {})
	root.mainloop()			



