
import os.path

from tkinter import PhotoImage
from tkinter import Text
from tkinter import Menu
from tkinter.font import Font
from tkinter.ttk import Style

class StyleManager:
	def __init__(self,main,initialTheme="light",execPath=""):
		
		self.main = main
		self.mainWindow = self.main.mainWindow
		
		self.registredStyledTextFields = list()
		self.registredMenus = list()
		self.registredBG = list()
		self.registredOptionMenus = list()
		self.registredOptionMenuButtons = list()
		
		self.main.headerfont = "System 24 bold"
		self.main.notebookTextFont = "System 14 bold"
		self.main.buttonTextFont = "System 12 bold"
		self.main.textFont = "System 12"
		self.main.logFont = "Mono 10"
		self.main.errorLogFont = "Mono 10 bold"
		
		#----------------------- figure out OS-based scaling -----------------------
		fontObj = Font(root=self.mainWindow,font="System 10")
		standardSize = fontObj.measure("0")
		#print("[Style] Standardsize (0): "+str(standardSize))
		self.main.osScaleFactor = (standardSize/8.0)	#this seems to be a good estimate of how the OS+TKinter automatically scale fonts for 4k displays
		#print("[Style] Scalefactor detected: "+str(self.main.osScaleFactor))	#but all other margins ans paddings need to be scaled manually
		self.main.osScaleFactorInt = int(round(self.main.osScaleFactor,0))
		#print("[Style] Scalefactor int: "+str(self.main.osScaleFactorInt))
		self.main.standardFontWidth = int(round(fontObj.measure("0")/self.main.osScaleFactor,0))
		self.main.frameBorderSize = int(round(4 * self.main.osScaleFactor,0))
		self.main.notebookPadding = int(round(2 * self.main.osScaleFactor,0))
		#print("[Style] Borderwidth: "+str(self.main.frameBorderSize))
		
		#----------------------- load sprites -----------------------
		#these are self stored and access is regulated based on light/dark mode
		self.triangle_down_black = PhotoImage(file = os.path.join(execPath,"sprites/triangle_down_black.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.triangle_down_white = PhotoImage(file = os.path.join(execPath,"sprites/triangle_down_white.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.triangle_up_black = PhotoImage(file = os.path.join(execPath,"sprites/triangle_up_black.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.triangle_up_white = PhotoImage(file = os.path.join(execPath,"sprites/triangle_up_white.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		
		self.box_empty_black = PhotoImage(file = os.path.join(execPath,"sprites/box_empty_black.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.box_empty_white = PhotoImage(file = os.path.join(execPath,"sprites/box_empty_white.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.box_filled_black = PhotoImage(file = os.path.join(execPath,"sprites/box_filled_black.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.box_filled_white = PhotoImage(file = os.path.join(execPath,"sprites/box_filled_white.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		
		self.x_black = PhotoImage(file = os.path.join(execPath,"sprites/x_black.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		main.xImage = self.x_black	#no style change here
		main.emptyImage = PhotoImage(file = os.path.join(execPath,"sprites/empty.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		
		#----------------------- Style -----------------------
		self.mystyle = Style()
		self.mystyle.theme_use("alt")	#'clam', 'alt', 'default', 'classic'	#clam has no relief options
		
		self.availableThemes = ["light","dark","grey"]
		self.applyTheme(initialTheme)
		
	
	def applyTheme(self, theme):
		#----------------------- Colours -----------------------
		if theme == "light" or theme == "dark" or theme == "grey":
			self.textSelectedColour = "#000000"
			self.textSelectedBackgroundColour = "#22dd77"
			self.buttonTextColour = "#ffffff"
			self.radioUnselectedColour = "#000000"
			self.radioSelectedColour = "#00ff00"
				
			if theme == "light":#sky+juicy green
				self.buttonColour = "#339966"
				self.buttonDarkColour = "#0f7040"
				self.buttonHighlightColour = "#33aa77"
				
				self.textColour = "#000000"
				self.textBackgroundColour = "#ffffff"
				self.textReadonlyBackgroundColour = "#d4cccc"
				self.backgroundColour = "#e2e2f2"
				
				self.main.graphBackgroundColour = "#ffffff"
				self.main.graphLineColour = "#000000"
				self.main.graphBarColour = "#444444"
				
				self.exitCol = "#aa0000"
				self.highlightExitCol = "#ff4444"
				
				self.main.triangle_down = self.triangle_down_black
				self.main.triangle_up = self.triangle_up_black
				self.main.box_empty = self.box_empty_black
				self.main.box_filled = self.box_filled_black
				
			elif theme == "dark":#black+dark turquoise
				self.buttonColour = "#226955"
				self.buttonDarkColour = "#0d4530"
				self.buttonHighlightColour = "#207f66"
				
				self.textColour = "#e6e6e6"
				self.textBackgroundColour = "#111111"
				self.textReadonlyBackgroundColour = "#443333"
				self.backgroundColour = "#222222"
				
				self.main.graphBackgroundColour = "#111111"
				self.main.graphLineColour = "#f1f1f1"
				self.main.graphBarColour = "#666666"
				
				self.exitCol = "#ff5555"
				self.highlightExitCol = "#ff0000"
				
				self.main.triangle_down = self.triangle_down_white
				self.main.triangle_up = self.triangle_up_white
				self.main.box_empty = self.box_empty_white
				self.main.box_filled = self.box_filled_white
			
			elif theme == "grey":#grey-scaled GUI
				self.textSelectedBackgroundColour = "#aaaaaa"
				self.buttonTextColour = "#ffffff"
				self.radioUnselectedColour = "#ffffff"
				self.radioSelectedColour = "#000000"
				
				self.buttonColour = "#777777"
				self.buttonDarkColour = "#555555"
				self.buttonHighlightColour = "#999999"
				
				self.textColour = "#000000"
				self.textBackgroundColour = "#ffffff"
				self.textReadonlyBackgroundColour = "#cccccc"
				self.backgroundColour = "#e2e2e2"
				
				self.main.graphBackgroundColour = "#ffffff"
				self.main.graphLineColour = "#000000"
				self.main.graphBarColour = "#444444"
				
				self.exitCol = "#ffffff"
				self.highlightExitCol = "#cccccc"
				
				self.main.triangle_down = self.triangle_down_black
				self.main.triangle_up = self.triangle_up_black
				self.main.box_empty = self.box_empty_black
				self.main.box_filled = self.box_filled_black
			
			#----------------------- Styles -----------------------
			self.mystyle.configure("TFrame",background=self.backgroundColour,highlightthickness=0)
			self.mystyle.configure("Border.TFrame",relief="flat",borderwidth=self.main.frameBorderSize)
			self.mystyle.configure("gBorder.TFrame",relief="flat",background=self.buttonColour,borderwidth=self.main.frameBorderSize)
			self.mystyle.configure("wBorder.TFrame",relief="flat",background=self.textBackgroundColour,borderwidth=self.main.frameBorderSize)
			self.mystyle.configure("Raised.TFrame",relief="raised",borderwidth=self.main.frameBorderSize)
			self.mystyle.configure("Sunken.TFrame",relief="sunken",borderwidth=self.main.frameBorderSize)
			self.mystyle.configure("TEST.TFrame",relief="raised",background="#ff0000",borderwidth=20)
			self.mystyle.configure("TLabel",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour)
			self.mystyle.configure("Header.TLabel",font=self.main.headerfont)
			self.mystyle.configure("Medium.TLabel",font="System 14 bold")
			self.mystyle.configure("TEST.TLabel",background="#ff0000")
			self.mystyle.configure("TButton",font=self.main.buttonTextFont,foreground=self.buttonTextColour,background=self.buttonColour,relief="raised",borderwidth=self.main.frameBorderSize-1)#,lightcolor="DarkGreen",darkcolor="LightGreen")
			self.mystyle.map("TButton",background=[("active",self.buttonHighlightColour)])
			self.mystyle.configure("Selected.TButton",font=self.main.buttonTextFont,foreground=self.buttonTextColour,background=self.buttonColour,relief="sunken",borderwidth=self.main.frameBorderSize-1)#,lightcolor="DarkGreen",darkcolor="LightGreen")
			self.mystyle.map("Selected.TButton",background=[("active",self.buttonHighlightColour)])
			self.mystyle.configure("Exit.TButton",background=self.exitCol)
			self.mystyle.map("Exit.TButton",background=[("active",self.highlightExitCol)])
			self.mystyle.configure("FlatText.TButton",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour,relief="flat",anchor="w")
			self.mystyle.map("FlatText.TButton",background=[("active",self.backgroundColour)],relief=[("active","flat")])
			
			self.mystyle.configure("TRadiobutton",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour,indicatorcolor=self.radioUnselectedColour)#,indicatorrelief="raise")#,highlightcolor=buttonHighlightColour)
			self.mystyle.map("TRadiobutton",background=[("active",self.buttonHighlightColour)],indicatorcolor=[("selected",self.radioSelectedColour)])	#,indicatorbackground=buttonHighlightColour doesnt work
			self.mystyle.configure("TEntry",font=self.main.textFont,foreground=self.textColour,fieldbackground=self.textBackgroundColour,insertcolor=self.textSelectedBackgroundColour,
				selectbackground=self.textSelectedBackgroundColour,selectforeground=self.textSelectedColour,insertwidth=3)
			self.mystyle.map("TEntry",fieldbackground=[("readonly",self.textReadonlyBackgroundColour)])
			self.mystyle.configure("RText.TEntry",font=self.main.textFont,foreground=self.textColour,fieldbackground=self.textBackgroundColour,insertcolor=self.textSelectedBackgroundColour,
				selectbackground=self.textSelectedBackgroundColour,selectforeground=self.textSelectedColour,insertwidth=3)
			self.mystyle.map("RText.TEntry",fieldbackground=[("readonly",self.textBackgroundColour)])
			self.mystyle.configure("TScrollbar",background=self.buttonColour,arrowcolor=self.buttonHighlightColour,troughcolor=self.backgroundColour)#,lightcolor="red",darkcolor="green",relief="raised",borderwidth=10)
			self.mystyle.map("TScrollbar",background=[("active",self.buttonHighlightColour)])
			
			self.mystyle.configure("TNotebook",background=self.backgroundColour)	#Padding here pads the notebook in its parent
			self.mystyle.configure("TNotebook.Tab",foreground=self.buttonTextColour,background=self.buttonDarkColour,font=self.main.notebookTextFont,
				padding = (self.main.notebookPadding*4,0,self.main.notebookPadding*4,0))	#padding here pads the text in tabs	#padding is w,n,e,s
			self.mystyle.map("TNotebook.Tab",background = [("selected",self.buttonColour)],
				padding = [("selected",(self.main.notebookPadding*6,self.main.notebookPadding*2,self.main.notebookPadding*6,0))])#,foreground = [("selected",self.buttonTextColour)])
			
			#file select menue is partially styled ~ bg + fg + fontsize
			#self.mystyle.configure("Treeview",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour)
		
		self.mainWindow.configure(background=self.backgroundColour)
		for textfield in self.registredStyledTextFields:
			textfield.configure(bg=self.textBackgroundColour,fg=self.textColour,selectbackground=self.textSelectedBackgroundColour,
				selectforeground=self.textSelectedColour)
		
		#These are used by parameters and are not project dependent (static), but do get generated and deleted with the settingsmenu!
		#for tbl,boolVar in self.main.toggleButtonReferenceDict.values():
		for key in list(self.main.toggleButtonReferenceDict.keys()):
			tbl,boolVar = self.main.toggleButtonReferenceDict[key]
			try:
				if boolVar.get(): 
					for tb in tbl:
						tb["image"]=self.main.box_filled
				else: 
					for tb in tbl:
						tb["image"]=self.main.box_empty
			except Exception as e:
				if "invalid command name" in str(e):	#widget doesnt exist anymore
					#tkinter.TclError: invalid command name
					del self.main.toggleButtonReferenceDict[key]	#dirty fix for not properly removing togglebuttons from this dict #TODO
				else:
					print(f"[Styleman][Error] Error setting style of togglebutton with key {key}:")
					print(e)
				
		
		#These are only used for annotation and therefore project-dependent (dynamic)
		for foldoutID,frameRef in enumerate(self.main.foldoutFrameReferenceList):
			if len(frameRef)==4:
				fbi = frameRef[1]
				if self.main.foldoutStates[foldoutID]: fbi["image"]=self.main.box_filled
				else: fbi["image"]=self.main.box_empty
			else:
				fbi = frameRef[2]
				if self.main.foldoutStates[foldoutID]: fbi["image"]=self.main.triangle_up
				else: fbi["image"]=self.main.triangle_down
		
		#These are only used for the menubar and therefore project independent (static)
		for menu in self.registredMenus:
			menu.config(fg=self.textColour,bg=self.backgroundColour,activeforeground=self.textColour,activebackground=self.textBackgroundColour)
		
		#These are only used for the menubar and therefore project independent (static)
		for scrollFrame in self.registredBG:
			scrollFrame.setCanvasBG(self.backgroundColour)
		
		#These are only used for libraries and therefore project-dependent (dynamic)
		for optionMenu in self.registredOptionMenus:
			optionMenu.config(bg=self.backgroundColour,fg=self.textColour,activeforeground=self.textColour,activebackground=self.textBackgroundColour)
			optionMenu["menu"].config(bg=self.backgroundColour,fg=self.textColour,activeforeground=self.textColour,activebackground=self.textBackgroundColour)
		
		#These are only used for siI eval and therefore project-dependent (dynamic)
		for optionMenu in self.registredOptionMenuButtons:
			optionMenu.config(bg=self.buttonColour,fg=self.buttonTextColour,activeforeground=self.textColour,activebackground=self.buttonHighlightColour)
			optionMenu["menu"].config(bg=self.backgroundColour,fg=self.textColour,activeforeground=self.textColour,activebackground=self.textBackgroundColour)
	
	def reset(self):
		self.registredOptionMenus = list()
		self.registredOptionMenuButtons = list()
	
	def getStyledText(self,parent):
		textfield = Text(parent,state="disabled",font=self.main.logFont,bg=self.textBackgroundColour,fg=self.textColour,selectbackground=self.textSelectedBackgroundColour,
			selectforeground=self.textSelectedColour,borderwidth=0,highlightthickness=0)
		self.registredStyledTextFields.append(textfield)
		return textfield
	
	def removeStyledText(self,textfield):
		self.registredStyledTextFields.remove(textfield)
	
	def getStyledMenu(self,parent):
		menubar = Menu(parent)
		menubar.config(font=self.main.textFont,fg=self.textColour,bg=self.backgroundColour,
				activeforeground=self.textColour,activebackground=self.textBackgroundColour)
		self.registredMenus.append(menubar)
		return menubar
	
