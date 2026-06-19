
from tkinter import Canvas
from tkinter.ttk import Notebook
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Scrollbar as ThemedScrollbar

class AutoHide_ThemedScrollbar(ThemedScrollbar):
	def __init__(self,master,*args,autohide=True,side="left",**kwargs):
		super().__init__(master,*args,**kwargs)
		self.lo = 0.0
		self.hi = 1.0
		self.autohide = autohide
		self.side = side
	
	def set(self, lo, hi):	#called when the scrollbar is adjusted
		self.lo = float(lo)	#store the last state of the bounds
		self.hi = float(hi)	#so that this class knows if the scrollbar needs to be visible or not
		if self.autohide:
			if self.canScroll():
				self.pack(side=self.side,fill="y")
			else:
				self.pack_forget()
		super().set(lo,hi)
	
	def canScroll(self):
		return not (self.lo<=0.0 and self.hi>=1.0)

class ScrollableNotebook(ThemedFrame):	#A themed notebook within a frame and a (vertical) auto-hide scrollbar next to it that scrolls the contents of all tabs
	def __init__(self,master,*args,scrollbar_autohide=True,scrollbar_side="left",canvasBG="white",**kwargs):
		#the object is actually a ttk ThemedFrame, tabs can be added to the notebook with addScrollTab()
		super().__init__(master,*args,**kwargs)
		self.tabs = dict()
		#tk.ScrollBar works with width=50 and also affects the arrows
		self.scrollbar = AutoHide_ThemedScrollbar(self,autohide = scrollbar_autohide,side=scrollbar_side,orient="vertical")
		self.scrollbar.pack(side=scrollbar_side,fill="y")
		canvas_side = "right" if scrollbar_side=="left" else "left"
		self.notebook = Notebook(self)
		self.notebook.pack(side=canvas_side,fill="both",expand=True)
		self.scrollbar.config(command=self._bar_scroll)	#extra function to prevent scrolling if frame small enough, instead of directly calling self.canvas.yview

		self.bind("<Enter>",self._on_enter)	#when cursor enters canvas, bind mousewheel to canvas-scroll
		self.bind("<Leave>",self._on_leave)	#unbind on leave
	
	def configureNotebook(self,*kwargs):
		self.notebook.configure(*kwargs)
	
	def addScrollTab(self,tabName,outer_frame_style="TFrame",canvasBG="white",inner_frame_style="TFrame"):	#Adds a tab to this notebook that is scrollable
		if not tabName in self.tabs:
			tabFrame = ThemedFrame(self.notebook,style=outer_frame_style)
			self.notebook.add(tabFrame,text=tabName)
			tabCanvas = Canvas(tabFrame,bg=canvasBG)
			tabCanvas.config(yscrollcommand = self.scrollbar.set)
			#tabCanvas has to be packed from outside to allow customisation of tabFrame / positioning other widgets on tabFrame
			
			tabScrollFrame = ThemedFrame(tabCanvas,style=inner_frame_style)
			scrollFrameID = tabCanvas.create_window((0,0),window=tabScrollFrame,anchor="nw")
			
			#if the scrollable frame gets changed, update the scrollable area accordingly
			tabScrollFrame.bind("<Configure>",lambda event,canvas=tabCanvas: _on_frame_configure(canvas,event))
			#if canvas changes size, set width of the inner frame to account for that
			tabCanvas.bind("<Configure>",lambda event,canvas=tabCanvas,frameID=scrollFrameID: _on_canvas_configure(canvas,frameID, event))
			
			#tabFrame so that you can place static objects around the scrollable area
			#tabcanvas for reference and stuff
			#tabScrollFrame to place stuff on that should be scrolled
			self.tabs[tabName] = [tabFrame,tabCanvas,tabScrollFrame]
			self.notebook.update()	#required to update and properly gen&sync all tabs and avoid issues with the scrollbar!
			self.notebook.select(len(self.tabs.keys())-1)
		
		return self.tabs[tabName]
	
	def finish(self):	#called after all tabs have been finished
		self.notebook.update()#dragging the handle is still weird... IF not all habs have been selected beforehand.. IF dragging too far down
		self.notebook.select(0)	#this fixes the draggin issue, but the gen now takes longer and looks weird...
	
	def getTab(self,tabName):
		if tabName in self.tabs:
			return self.tabs[tabName]
		else:
			print(f"[ERROR][ScrollableNotebook] No tab with the name \"{tabName}\" found!")
			return None
	
	def _on_enter(self, event):	#TODO might need extra windows/mac handling
		self.bind_all("<Button-4>",self._wheel_scroll)
		self.bind_all("<Button-5>",self._wheel_scroll)
	
	def _on_leave(self, event):
		self.unbind_all("<Button-4>")
		self.unbind_all("<Button-5>")
	
	def _wheel_scroll(self,event):
		if not self.scrollbar.canScroll():return
		for tabName,(tabFrame,tabCanvas,tabScrollFrame) in self.tabs.items():
			if event.num==5:tabCanvas.yview_scroll(1,"units")	#this doesnt work with tabs that havent been rendered in GUI yet
			elif event.num==4:tabCanvas.yview_scroll(-1,"units")	#thats why the various tabs are selected and updated during creation
	
	def _bar_scroll(self,*args):
		if not self.scrollbar.canScroll():return
		for tabName,(tabFrame,tabCanvas,tabScrollFrame) in self.tabs.items():
			tabCanvas.yview(*args)

def _on_frame_configure(canvas, event):
	canvas.configure(scrollregion=canvas.bbox("all"))

def _on_canvas_configure(canvas,inner_frame_ID, event):
	canvas.itemconfig(inner_frame_ID,width=event.width)
	
