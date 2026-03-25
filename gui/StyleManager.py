
import os.path

from tkinter import PhotoImage
from tkinter import Text
from tkinter.font import Font
from tkinter.ttk import Style

class StyleManager:
	def __init__(self,main,initialTheme="light",execPath=""):
		
		self.main = main
		self.mainWindow = self.main.mainWindow
		
		self.registredStyledTextFields = list()
		
		self.main.headerfont = "System 24 bold"
		self.main.notebookTextFont = "System 14 bold"
		self.main.buttonTextFont = "System 12 bold"
		self.main.textFont = "System 12"
		self.main.logFont = "Mono 10"
		self.main.errorLogFont = "Mono 10 bold"
		
		#----------------------- figure out OS-based scaling -----------------------
		fontObj = Font(root=self.mainWindow,font="System 10")
		standardSize = fontObj.measure("0")
		print("[Style] Standardsize (0): "+str(standardSize))
		self.main.osScaleFactor = (standardSize/8.0)	#this seems to be a good estimate of how the OS+TKinter automatically scale fonts for 4k displays
		print("[Style] Scalefactor detected: "+str(self.main.osScaleFactor))	#but all other margins ans paddings need to be scaled manually
		self.main.osScaleFactorInt = int(round(self.main.osScaleFactor,0))
		print("[Style] Scalefactor int: "+str(self.main.osScaleFactorInt))
		self.main.standardFontWidth = int(round(fontObj.measure("0")/self.main.osScaleFactor,0))
		self.main.frameBorderSize = int(round(4 * self.main.osScaleFactor,0))
		self.main.notebookPadding = int(round(2 * self.main.osScaleFactor,0))
		print("[Style] Borderwidth: "+str(self.main.frameBorderSize))
		
		#----------------------- load sprites -----------------------
		self.triDownW = PhotoImage(file = os.path.join(execPath,"sprites/ArrowDownWhite.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.triUpW = PhotoImage(file = os.path.join(execPath,"sprites/ArrowUpWhite.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.triDownB = PhotoImage(file = os.path.join(execPath,"sprites/ArrowDownBlack.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.triUpB = PhotoImage(file = os.path.join(execPath,"sprites/ArrowUpBlack.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.main.triDown = self.triDownB
		self.main.triUp = self.triUpB
		
		#these are self stored and acces is regulated based on light(dark mode
		self.boxImage_b = PhotoImage(file = os.path.join(execPath,"sprites/Box.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.xBoxImage_b = PhotoImage(file = os.path.join(execPath,"sprites/xBox.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.boxImage_w = PhotoImage(file = os.path.join(execPath,"sprites/Box_w.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.xBoxImage_w = PhotoImage(file = os.path.join(execPath,"sprites/xBox_w.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		self.main.boxImage = self.boxImage_b
		self.main.xBoxImage = self.xBoxImage_b
		
		main.xImage = PhotoImage(file = os.path.join(execPath,"sprites/x20.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		main.xImage_small = PhotoImage(file = os.path.join(execPath,"sprites/x16.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		main.emptyImage = PhotoImage(file = os.path.join(execPath,"sprites/empty20.png")).zoom(self.main.osScaleFactorInt,self.main.osScaleFactorInt)
		
		
		#----------------------- Style -----------------------
		self.mystyle = Style()
		print("[Style] Available themes: "+str(self.mystyle.theme_names()))
		self.mystyle.theme_use("alt")	#('clam', 'alt', 'default', 'classic')	#clam has no relief options
		print("[Style] Theme selected: "+str(self.mystyle.theme_use()))
		self.applyTheme(initialTheme)
		
	
	def applyTheme(self, theme):
		#----------------------- Colours -----------------------
		if theme == "light" or theme == "dark":
			self.textSelectedColour = "#000000"
			self.textSelectedBackgroundColour = "#22dd77"
			self.buttonTextColour = "#ffffff"
			self.buttonColour = "#339966"		#"#00c878"	#too bright
			self.buttonHighlightColour = "#33aa77"	#"#6bffc4"
			self.foldoutButtonClosed = "#228855"
			self.foldoutButtonOpen = "#22aa55"
			self.radioUnselectedColour = "#000000"
			self.radioSelectedColour = "#00ff00"
				
			if theme == "light":#sky+juicy green
				self.textColour = "#000000"
				self.textBackgroundColour = "#ffffff"
				self.backgroundColour = "#ddddee"
				
				self.main.graphBackgroundColour = "#ffffff"
				self.main.graphLineColour = "#000000"
				self.main.graphBarColour = "#444444"
				self.main.graphBarFillColour = "#ccccff"
				
				self.exitCol = "#aa0000"#"#cc0000"
				self.highlightExitCol = "#ff4444"
				
				self.main.boxImage = self.boxImage_b
				self.main.xBoxImage = self.xBoxImage_b
				self.main.triDown = self.triDownB
				self.main.triUp = self.triUpB
				
			elif theme == "dark":#dark
				self.textColour = "#e2e2e2"
				self.textBackgroundColour = "#111111"
				self.backgroundColour = "#222222"
				
				self.main.graphBackgroundColour = "#111111"
				self.main.graphLineColour = "#f1f1f1"
				self.main.graphBarColour = "#666666"
				self.main.graphBarFillColour = "#ccccff"
				
				self.exitCol = "#ff5555"
				self.highlightExitCol = "#ff0000"
				
				self.main.boxImage = self.boxImage_w
				self.main.xBoxImage = self.xBoxImage_w
				self.main.triDown = self.triDownW
				self.main.triUp = self.triUpW
			
			self.internalFoldoutButtonClosed = self.backgroundColour
			self.internalFoldoutButtonOpen = self.backgroundColour
			
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
			self.mystyle.configure("TButton",font=self.main.buttonTextFont,foreground=self.buttonTextColour,background=self.buttonColour,relief="raised",borderwidth=self.main.frameBorderSize-1)#,lightcolor="DarkGreen",darkcolor="LightGreen")
			self.mystyle.map("TButton",background=[("active",self.buttonHighlightColour)])
			self.mystyle.configure("Exit.TButton",background=self.exitCol)
			self.mystyle.map("Exit.TButton",background=[("active",self.highlightExitCol)])
			
			self.mystyle.configure("bg.TButton",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour,relief="raised",borderwidth=self.main.frameBorderSize-1)#,lightcolor="DarkGreen",darkcolor="LightGreen")
			self.mystyle.map("bg.TButton",background=[("active",self.textBackgroundColour)])
			#self.mystyle.configure("TMenubutton",relief="raised",borderwidth=self.main.frameBorderSize-1)
			#self.mystyle.configure("TCombobox",fieldbackground="red",background="blue",foreground="green",padding=5,font=("Helvetica",12))
			#self.mystyle.configure("TMenubutton",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour)
			#self.mystyle.map("TMenubutton",background=[("active",self.backgroundColour)])
			#TMenubutton popup is still unstyled!
			
			self.mystyle.configure("DropClosed.TButton",font=self.main.buttonTextFont,foreground=self.buttonTextColour,background=self.foldoutButtonClosed,relief="flat",anchor="w")
			self.mystyle.configure("DropOpen.TButton",font=self.main.buttonTextFont,foreground=self.buttonTextColour,background=self.foldoutButtonOpen,relief="flat",anchor="w")
			self.mystyle.map("DropClosed.TButton",background=[("active",self.foldoutButtonClosed)],relief=[("active","flat")])
			self.mystyle.map("DropOpen.TButton",background=[("active",self.foldoutButtonOpen)],relief=[("active","flat")])
			self.mystyle.configure("internalDropClosed.TButton",font=self.main.textFont,foreground=self.textColour,background=self.internalFoldoutButtonClosed,relief="flat",anchor="w")
			self.mystyle.configure("internalDropOpen.TButton",font=self.main.textFont,foreground=self.textColour,background=self.internalFoldoutButtonOpen,relief="flat",anchor="w")
			self.mystyle.map("internalDropClosed.TButton",background=[("active",self.internalFoldoutButtonClosed)],relief=[("active","flat")])
			self.mystyle.map("internalDropOpen.TButton",background=[("active",self.internalFoldoutButtonOpen)],relief=[("active","flat")])
			self.mystyle.configure("optionDropClosed.TButton",font=self.main.buttonTextFont,foreground=self.textColour,background=self.internalFoldoutButtonClosed,relief="flat",anchor="w")
			self.mystyle.configure("optionDropOpen.TButton",font=self.main.buttonTextFont,foreground=self.textColour,background=self.internalFoldoutButtonOpen,relief="flat",anchor="w")
			self.mystyle.map("optionDropClosed.TButton",background=[("active",self.internalFoldoutButtonClosed)],relief=[("active","flat")])
			self.mystyle.map("optionDropOpen.TButton",background=[("active",self.internalFoldoutButtonOpen)],relief=[("active","flat")])
			
			self.mystyle.configure("TRadiobutton",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour,indicatorcolor=self.radioUnselectedColour)#,indicatorrelief="raise")#,highlightcolor=buttonHighlightColour)
			self.mystyle.map("TRadiobutton",background=[("active",self.buttonHighlightColour)],indicatorcolor=[("selected",self.radioSelectedColour)])	#,indicatorbackground=buttonHighlightColour doesnt work
			self.mystyle.configure("TEntry",font=self.main.textFont,foreground=self.textColour,fieldbackground=self.textBackgroundColour,insertcolor=self.textSelectedBackgroundColour,
				selectbackground=self.textSelectedBackgroundColour,selectforeground=self.textSelectedColour,insertwidth=3)
			self.mystyle.map("TEntry",fieldbackground=[("readonly",self.textBackgroundColour)])
			self.mystyle.configure("TScrollbar",background=self.buttonColour,arrowcolor=self.buttonHighlightColour,troughcolor=self.backgroundColour)#,lightcolor="red",darkcolor="green",relief="raised",borderwidth=10)
			self.mystyle.map("TScrollbar",background=[("active",self.buttonHighlightColour)])
			
			self.mystyle.configure("TNotebook",background=self.backgroundColour)
			self.mystyle.configure("TNotebook.Tab",foreground=self.buttonTextColour,background=self.buttonColour,font=self.main.notebookTextFont,
				padding = (self.main.notebookPadding*2,0,self.main.notebookPadding*2,0))
				#padding = (self.main.notebookPadding,self.main.notebookPadding,self.main.notebookPadding,self.main.notebookPadding))#self.main.notebookPadding)	#padding is w,n,e,s
			self.mystyle.map("TNotebook.Tab",background = [("selected",self.buttonHighlightColour)],
				padding = [("selected",(self.main.notebookPadding*4,self.main.notebookPadding,self.main.notebookPadding*4,self.main.notebookPadding))])#,foreground = [("selected",self.buttonTextColour)])
			
			#file select menue is partially styled ~ bg + fg + fontsize
			#self.mystyle.configure("Treeview",font=self.main.textFont,foreground=self.textColour,background=self.backgroundColour)
		
		self.mainWindow.configure(background=self.backgroundColour)
		for textfield in self.registredStyledTextFields:
			textfield.configure(bg=self.textBackgroundColour,fg=self.textColour,selectbackground=self.textSelectedBackgroundColour,
				selectforeground=self.textSelectedColour)
		
		for tbl,boolVar in self.main.toggleButtonReferenceDict.values():
			if boolVar.get(): 
				for tb in tbl:
					tb["image"]=self.main.xBoxImage
			else: 
				for tb in tbl:
					tb["image"]=self.main.boxImage
		for foldoutID,frameRef in enumerate(self.main.foldoutFrameReferenceList):
			if len(frameRef)==4:
				fbi = frameRef[1]
				if self.main.foldoutStates[foldoutID]: fbi["image"]=self.main.xBoxImage
				else: fbi["image"]=self.main.boxImage
			else:
				fbi = frameRef[2]
				if self.main.foldoutStates[foldoutID]: fbi["image"]=self.main.triUp
				else: fbi["image"]=self.main.triDown
	
	
	def getStyledText(self,parent):
		textfield = Text(parent,state="disabled",font=self.main.logFont,bg=self.textBackgroundColour,fg=self.textColour,selectbackground=self.textSelectedBackgroundColour,
			selectforeground=self.textSelectedColour,borderwidth=0,highlightthickness=0)
		self.registredStyledTextFields.append(textfield)
		return textfield
