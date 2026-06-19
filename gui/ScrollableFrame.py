
from tkinter import Canvas
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

class ScrollableFrame(ThemedFrame):	#A themed frame within a frame that can be scrolled (vertically) by a auto-hide scrollbar
	def __init__(self,master,*args,scrollbar_autohide=True,scrollbar_side="left",canvasBG="white",innerFrame_style="TFrame",**kwargs):
		super().__init__(master,*args,**kwargs)

		#tk.ScrollBar works with width=50 and also affects the arrows
		self.scrollbar = AutoHide_ThemedScrollbar(self,autohide = scrollbar_autohide,side=scrollbar_side,orient="vertical")
		self.canvas = Canvas(self,highlightthickness=0,bg=canvasBG)
		
		self.scrollbar.pack(side=scrollbar_side,fill="y")
		canvas_side = "right" if scrollbar_side=="left" else "left"
		self.canvas.pack(side=canvas_side,fill="both",expand=True)
		
		self.scrollbar.config(command=self._bar_scroll)	#extra function to prevent scrolling if frame small enough, instead of directly calling self.canvas.yview
		self.canvas.config(yscrollcommand = self.scrollbar.set)

		self.inner_frame = ThemedFrame(self.canvas,style=innerFrame_style)
		self.inner_frame_ID = self.canvas.create_window((0,0),window=self.inner_frame,anchor="nw")
		
		self.inner_frame.bind("<Configure>",self._on_frame_configure)	#if the scrollable frame gets changed, update the scrollable area accordingly
		self.canvas.bind("<Configure>",self._on_canvas_configure)	#if canvas changes size, set width of the inner frame to account for that
		
		self.canvas.bind("<Enter>",self._on_enter)	#when cursor enters canvas, bind mousewheel to canvas-scroll
		self.canvas.bind("<Leave>",self._on_leave)	#unbind on leave
	
	def setCanvasBG(self,colour):
		self.canvas.config(bg=colour)
	
	def getInnerFrame(self):
		return self.inner_frame
	
	def _on_frame_configure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
	
	def _on_canvas_configure(self, event):
		self.canvas.itemconfig(self.inner_frame_ID,width=event.width)
	
	def _on_enter(self, event):	#TODO might need windows/mac alternative ...
		self.canvas.bind_all("<Button-4>",self._wheel_scroll)
		self.canvas.bind_all("<Button-5>",self._wheel_scroll)
	
	def _on_leave(self, event):
		self.canvas.unbind_all("<Button-4>")
		self.canvas.unbind_all("<Button-5>")
	
	def _wheel_scroll(self,event):
		if not self.scrollbar.canScroll():return
		if event.num==5:self.canvas.yview_scroll(1,"units")
		elif event.num==4:self.canvas.yview_scroll(-1,"units")
	
	def _bar_scroll(self,*args):
		if not self.scrollbar.canScroll():return
		self.canvas.yview(*args)
	
