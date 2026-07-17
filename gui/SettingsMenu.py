
from tkinter import Toplevel
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry

from gui.ParameterManager import ParameterManager
#from gui.functions import createTogglebutton	#TODO circular import! fix by splitting functions into: widget-generating functions and executing functions !!
import gui.functions as gfs	#tmp solution

class SettingsMenu():
	def __init__(self,main):
		self.main=main
		self.window = Toplevel(main.mainWindow)
		self.window.title("RNAival - Settings")
		self.window.attributes("-topmost",True)	#always have this on top
		self.window.protocol("WM_DELETE_WINDOW",self.closeWindow)
		
		mainframeBase = ThemedFrame(self.window,style="gBorder.TFrame")
		mainframeBase.pack(fill="both",expand=True,anchor="nw")
		
		self.PM = ParameterManager(main)	#this gets its own PM so that the keys are the same	(but pass main for error messages)
		
		
		generalSettingsFrame = ThemedFrame(mainframeBase,style="TFrame")
		generalSettingsFrame.pack(padx=main.frameBorderSize,pady=main.frameBorderSize,fill="both",expand=True,anchor="nw")
		
		ThemedLabel(generalSettingsFrame,text="General settings",anchor="nw",style="Medium.TLabel").grid(row=0,column=0,columnspan=4,sticky="news",padx=main.frameBorderSize)
		
		ThemedLabel(generalSettingsFrame,text="Load last project on startup:",anchor="w").grid(column=0,row=1,columnspan=1,sticky="ew",padx=main.frameBorderSize)
		gfs.createTogglebutton(main,generalSettingsFrame,self.PM.add("RNAival-load_last_project_on_startup","bool",main.PM.get("RNAival-load_last_project_on_startup"),
					"Bool error","Wether to load the last project on startup or not.",tag=main.globalProgramSettingsKey)).grid(column=1,row=1,sticky="e")
		ThemedLabel(generalSettingsFrame,text="Show graphs on project load:",anchor="w").grid(column=0,row=2,columnspan=1,sticky="ew",padx=main.frameBorderSize)
		gfs.createTogglebutton(main,generalSettingsFrame,self.PM.add("RNAival-show_graphs_on_project_load","bool",main.PM.get("RNAival-show_graphs_on_project_load"),
					"Bool error","Wether to generate the graphs on project load or not.",tag=main.globalProgramSettingsKey)).grid(column=1,row=2,sticky="e")
		ThemedLabel(generalSettingsFrame,text="Threads to use:",anchor="w").grid(column=0,row=3,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
		ThemedEntry(generalSettingsFrame,textvariable=self.PM.add("RNAival-max_threads_to_use","int",main.PM.get("RNAival-max_threads_to_use"),
				"Threads needs to be an integer!","Number of threads used by external tools.",tag=main.globalProgramSettingsKey)
					).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
		
		generalSettingsFrame.rowconfigure(0,weight=0)
		generalSettingsFrame.rowconfigure(1,weight=0)
		generalSettingsFrame.rowconfigure(2,weight=0)
		generalSettingsFrame.rowconfigure(3,weight=0)
		
		generalSettingsFrame.columnconfigure(0,weight=1)
		generalSettingsFrame.columnconfigure(2,weight=0)
		
		
		# ------------------ Graph settings ------------------------
		projectSettingsFrame = ThemedFrame(mainframeBase,style="TFrame")
		projectSettingsFrame.pack(padx=main.frameBorderSize,pady=(0,main.frameBorderSize),fill="both",expand=True,anchor="nw")
		
		ThemedLabel(projectSettingsFrame,text="Graph settings [Project specific]",anchor="w",style="Medium.TLabel"
			).grid(column=0,row=0,columnspan=2,sticky="w",padx=main.frameBorderSize)
		
		ThemedLabel(projectSettingsFrame,text="Hide Labels and Legends",anchor="w").grid(column=0,row=1,sticky="ew",padx=main.frameBorderSize)
		gfs.createTogglebutton(main,projectSettingsFrame,self.PM.add("RNAival-hide_Labels_Legends","bool",main.PM.get("RNAival-hide_Labels_Legends"),"boolerror",
			"Wether to hide axis labels and legends in graphs",tag=main.localProjectSettingsKey)).grid(column=1,row=1,sticky="e")
		
		ThemedLabel(projectSettingsFrame,text="Font multiplier (GUI)",anchor="w").grid(column=0,row=2,sticky="w",padx=main.frameBorderSize)
		ThemedEntry(projectSettingsFrame,textvariable=self.PM.add("RNAival-font_multiplier_GUI","float",main.PM.get("RNAival-font_multiplier_GUI"),
			"","",tag=main.localProjectSettingsKey)).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
		
		ThemedLabel(projectSettingsFrame,text="Export width",anchor="w").grid(column=0,row=3,sticky="w",padx=main.frameBorderSize)
		ThemedEntry(projectSettingsFrame,textvariable=self.PM.add("RNAival-export_width","int",main.PM.get("RNAival-export_width"),
			"","",tag=main.localProjectSettingsKey)).grid(column=1,row=3,sticky="e",padx=main.frameBorderSize)
		ThemedLabel(projectSettingsFrame,text="Export heigth",anchor="w").grid(column=0,row=4,sticky="w",padx=main.frameBorderSize)
		ThemedEntry(projectSettingsFrame,textvariable=self.PM.add("RNAival-export_height","int",main.PM.get("RNAival-export_height"),
			"","",tag=main.localProjectSettingsKey)).grid(column=1,row=4,sticky="e",padx=main.frameBorderSize)
		ThemedLabel(projectSettingsFrame,text="Font multiplier (SVG)",anchor="w").grid(column=0,row=5,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
		ThemedEntry(projectSettingsFrame,textvariable=self.PM.add("RNAival-font_multiplier_SVG","float",main.PM.get("RNAival-font_multiplier_SVG"),
			"","",tag=main.localProjectSettingsKey)).grid(column=1,row=5,sticky="e",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
		
		projectSettingsFrame.columnconfigure(0,weight=1)
		projectSettingsFrame.columnconfigure(1,weight=0)
		
		projectSettingsFrame.rowconfigure(0,weight=0)
		projectSettingsFrame.rowconfigure(1,weight=0)
		projectSettingsFrame.rowconfigure(2,weight=0)
		projectSettingsFrame.rowconfigure(3,weight=0)
		projectSettingsFrame.rowconfigure(4,weight=0)
		projectSettingsFrame.rowconfigure(5,weight=0)
		
		
		#save: button (also validate these settings and error if problem)
		ThemedButton(mainframeBase,text="Save & Close",command=self.trySaveParameters).pack(fill="both",anchor="nw")
		
		self.window.update()	#this draws the window , making winfo available for centering
		self.center()
	
	def center(self):
		self.window.geometry(f"+{int(self.main.mainWindow.winfo_width()/2-self.window.winfo_width()/2)}"
			+f"+{int(self.main.mainWindow.winfo_height()/2-self.window.winfo_height()/2)}")
	
	def closeWindow(self):	#destroys settings GUI and removes references to self. Does not save settings!
		self.main.settingsMenu = None
		self.window.destroy()
	
	def trySaveParameters(self):
		allGood = self.PM.validateTags([self.main.globalProgramSettingsKey,self.main.localProjectSettingsKey])
		if allGood:
			self.saveParametersToMain()
			self.main.writeLog("Saved settings.")
			self.closeWindow()
			return
		else:
			self.main.writeError("Error, settings are not correct!")
	
	def saveParametersToMain(self):	#update the main PM with the parameters set in ths PM
		self.main.PM.setAll(self.PM.getDict(tags=[self.main.globalProgramSettingsKey,self.main.localProjectSettingsKey]))
		self.main.saveProgramSettings()
		self.main.saveProjectSettings()
