
from tkinter import Toplevel
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry

from gui.ParameterManager import ParameterManager

class SettingsMenu():
	def __init__(self,main):
		self.main=main
		self.window = Toplevel(main.mainWindow)
		self.window.title("RNAival - Settings")
		self.window.attributes("-topmost",True)	#always have this on top
		self.window.protocol("WM_DELETE_WINDOW",self.closeWindow)
		
		mainframeBase = ThemedFrame(self.window,style="gBorder.TFrame")
		mainframeBase.pack(fill="both",expand=True,anchor="nw")
		
		mainframe = ThemedFrame(mainframeBase)
		mainframe.pack(padx=main.frameBorderSize,pady=main.frameBorderSize,fill="both",expand=True,anchor="nw")
		
		ThemedLabel(mainframe,text="General settings",anchor="nw",style="Medium.TLabel").grid(row=0,column=0,columnspan=4,sticky="news",padx=main.frameBorderSize)
		
		self.PM = ParameterManager(main)	#this gets its own PM so that the keys are the same	(but pass main for error messages)
		
		#loadlastproject: radio
		ThemedLabel(mainframe,text="Load last project on startup:",anchor="w").grid(column=0,row=1,columnspan=1,sticky="ew",padx=main.frameBorderSize)
		loadLastVar = self.PM.add("loadLastProjectOnStartup","bool",main.PM.get("loadLastProjectOnStartup"),
					"Bool error","Wether to load the last project on startup or not.",tag="general")
		ThemedRadioButton(mainframe,text="Yes",variable=loadLastVar,value=True).grid(column=1,row=1,sticky="w",padx=main.frameBorderSize)
		ThemedRadioButton(mainframe,text="No",variable=loadLastVar,value=False).grid(column=2,row=1,sticky="w",padx=main.frameBorderSize)
		
		#threads: entry
		threadsVar = self.PM.add("threadsVar","int",main.PM.get("threadsVar"),"Threads needs to be an integer!","Number of threads used by external tools.",tag="general")
		ThemedLabel(mainframe,text="Threads to use:",anchor="w").grid(column=0,row=2,columnspan=1,sticky="w",padx=main.frameBorderSize)
		ThemedEntry(mainframe,textvariable=threadsVar).grid(column=1,row=2,columnspan=2,sticky="ew",padx=main.frameBorderSize)
		
		#Theme: radio
		ThemedLabel(mainframe,text="Default theme:",anchor="w").grid(column=0,row=3,columnspan=1,sticky="ew",padx=main.frameBorderSize)
		defThemeVar = self.PM.add("defaultTheme","text",main.PM.get("defaultTheme"),"Theme select error","Which theme the application should use by default.",tag="general")
		ThemedRadioButton(mainframe,text="Light",variable=defThemeVar,value="light").grid(column=1,row=3,sticky="w",padx=main.frameBorderSize)
		ThemedRadioButton(mainframe,text="Dark",variable=defThemeVar,value="dark").grid(column=2,row=3,sticky="w",padx=main.frameBorderSize)
		
		#save: button (also validate these settings and error if problem)
		ThemedButton(mainframeBase,text="Save & Close",command=self.trySaveParameters).pack(fill="both",anchor="nw")
		
		mainframe.rowconfigure(0,weight=1)
		mainframe.rowconfigure(1,weight=0,uniform="fred")
		mainframe.rowconfigure(2,weight=0,uniform="fred")
		mainframe.rowconfigure(3,weight=0,uniform="fred")
		
		mainframe.columnconfigure(0,weight=1)
		mainframe.columnconfigure(2,weight=0)
		mainframe.columnconfigure(3,weight=0)
		
		self.window.update()	#this draws the window , making winfo available for centering
		self.center()
	
	def center(self):
		self.window.geometry(f"+{int(self.main.mainWindow.winfo_width()/2-self.window.winfo_width()/2)}+{int(self.main.mainWindow.winfo_height()/2-self.window.winfo_height()/2)}")
	
	def closeWindow(self):	#destroys settings GUI and removes references to self. Does not save settings!
		self.main.settingsMenu = None
		self.window.destroy()
	
	def trySaveParameters(self):
		allGood = self.PM.validateTags(["general"])
		if allGood:
			self.saveParametersToMain()
			self.main.writeLog("Saved settings.")
			self.closeWindow()
			return
		else:
			self.main.writeError("Error, settings are not correct!")
	
	def saveParametersToMain(self):
		self.main.PM.setAll(self.PM.getDict(tag="general"))
		self.main.saveProgramSettings()
