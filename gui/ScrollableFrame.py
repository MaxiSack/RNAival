
from tkinter import Canvas
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Scrollbar as ThemedScrollbar

class AutoHide_ThemedScrollbar(ThemedScrollbar):
	def __init__(self,master,*args,**kwargs):
		super().__init__(master,*args,**kwargs)
		self.lo = 0.0
		self.hi = 1.0
	
	def set(self, lo, hi):	#called when the scrollbar is adjusted
		self.lo = float(lo)	#store the last state of the bounds
		self.hi = float(hi)	#so that this class knows if the scrollbar needs to be visible or not
		if self.canScroll():
			#self.grid()
			self.pack(side="left",fill="y")
		else:
			#self.grid_remove()
			self.pack_forget()
		super().set(lo,hi)
	
	def canScroll(self):
		return not (self.lo<=0.0 and self.hi>=1.0)

class ScrollableFrame(ThemedFrame):
	def __init__(self,master,*args,**kwargs):
		super().__init__(master,*args,**kwargs)

		#tk.ScrollBar works with width=50 and also affects the arrows
		self.scrollbar = AutoHide_ThemedScrollbar(self,orient="vertical")
		self.canvas = Canvas(self,highlightthickness=0)
		
		self.scrollbar.pack(side="left",fill="y")
		self.canvas.pack(side="right",fill="both",expand=True)
		
		self.scrollbar.config(command=self.canvas.yview)
		self.canvas.config(yscrollcommand = self.scrollbar.set)

		self.inner_frame = ThemedFrame(self.canvas)
		self.inner_frame_ID = self.canvas.create_window((0,0),window=self.inner_frame,anchor="nw")
		
		self.inner_frame.bind("<Configure>",self._on_frame_configure)
		self.canvas.bind("<Configure>",self._on_canvas_configure)
		
		self.canvas.bind("<Enter>",self._on_enter)
		self.canvas.bind("<Leave>",self._on_leave)
	
	def setCanvasBG(self,colour):
		self.canvas.config(bg=colour)
	
	def getInnerFrame(self):
		return self.inner_frame
	
	def _on_frame_configure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
	
	def _on_canvas_configure(self, event):
		self.canvas.itemconfig(self.inner_frame_ID,width=event.width)
	
	def _on_enter(self, event):
		self.canvas.bind_all("<Button-4>",self._scroll)
		self.canvas.bind_all("<Button-5>",self._scroll)
	
	def _on_leave(self, event):
		self.canvas.unbind_all("<Button-4>")
		self.canvas.unbind_all("<Button-5>")
	
	def _scroll(self,event):
		if not self.scrollbar.canScroll():return
		if event.num==5:self.canvas.yview_scroll(1,"units")
		elif event.num==4:self.canvas.yview_scroll(-1,"units")
