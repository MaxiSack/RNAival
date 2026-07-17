
import time
from datetime import datetime
from tkinter import Tk
from queue import Queue

import os
import os.path
import subprocess
import platform

from gui.Definition import defineGUI
from gui.StyleManager import StyleManager
from gui.ParameterManager import ParameterManager
from gui.InputManager import InputManager
import gui.functions as functions
from functions.commandManager import runCommand
from gui.inputSelection import updateTargetListFrame


class Main():
	def __init__(self,title,execPath=""):
		self.execPath = execPath
		print("[Main] Execution path: "+str(self.execPath))
		self.mainWindow = Tk(className="RNAival")
		#self.mainWindow.attributes("-fullscreen", True)
		self.mainWindow.title(title)
		self.logFile = "log.txt"
		#windowWidth = 0.95 * self.mainWindow.winfo_screenwidth()
		windowWidth = self.mainWindow.winfo_screenwidth()
		#windowHeight = 0.90 * self.mainWindow.winfo_screenheight()
		windowHeight = self.mainWindow.winfo_screenheight()
		self.mainWindow.geometry(str(int(windowWidth))+"x"+str(int(windowHeight))+"+0+0")
		
		self.runningThreads = list()	#TODO move to extra threat manager
		self.commsQueue = Queue()
		self.killSignal = [False]
		self.mainWindow.protocol("WM_DELETE_WINDOW",self.closeWindow)
		self.pipelineError = False
		
		self.globalProgramSettingsKey = "global_program"
		self.localProjectSettingsKey = "local_project"
		
		#------- defines before building anything else! ------
		self.inputVars = dict()
		self.varTags = dict()
		self.numberEntryWidth = 8
		self.foldoutFrameReferenceList = list()
		self.foldoutStates = list()
		self.toggleButtonReferenceDict=dict()
		
		self.mainNotebooktabs = dict()
		self.comboGraphs = dict()
		
		self.mapTargets = list()	#filled by adding targets!
		self.evalTypes = list()		#added by siI_eval and dsP_eval or other evaluation scripts
		
		self.PM = ParameterManager(self)
		self.IM = InputManager()
		
		#Program settings
		self.PM.add("RNAival-max_threads_to_use","int",16,"Threads error","Number of threads used by external tools.",tag=self.globalProgramSettingsKey)
		self.PM.add("RNAival-load_last_project_on_startup","bool",True,"Bool error","Wether to load the last project on startup or not.",tag=self.globalProgramSettingsKey)
		self.PM.add("RNAival-show_graphs_on_project_load","bool",True,"Bool error","Wether to generate the graphs on project load or not.",tag=self.globalProgramSettingsKey)
		
		self.PM.add("currentTheme","text","light","Theme select error","Which theme the application should use by default.",tag=self.globalProgramSettingsKey)
		
		self.PM.add("RNAival-hide_Labels_Legends","bool",False,"boolerror","Wether to hide axis labels and legends in graphs",tag=self.localProjectSettingsKey)
		self.PM.add("RNAival-font_multiplier_GUI","float",1.0,"","",tag=self.localProjectSettingsKey)
		self.PM.add("RNAival-export_width","int",1500,"","",tag=self.localProjectSettingsKey)
		self.PM.add("RNAival-export_height","int",500,"","",tag=self.localProjectSettingsKey)
		self.PM.add("RNAival-font_multiplier_SVG","float",1.0,"","",tag=self.localProjectSettingsKey)
		
		
		functions.loadProgramSettings(self)
		self.styleman = StyleManager(self,initialTheme=self.PM.get("currentTheme"),execPath=self.execPath)
		
		
		self.PM.add("projectPath","path","","Project path error","Directory where the project is stored",tag=self.localProjectSettingsKey)
		
		defineGUI(self)
		
		#self.PM.printVarsOfType("bool")
		
	def reset(self):
		print("\n[Main] resetting everything")
		self.foldoutFrameReferenceList = list()
		self.styleman.reset()
		self.PM.reset(notTags=[self.globalProgramSettingsKey])
		self.PM.clearPS()
		self.IM.reset()
		self.resetTextOutput()
		updateTargetListFrame(self)
		functions.clearGraphics(self)
		print("[Main] done.\n")
	def saveProgramSettings(self):
		functions.saveProgramSettings(self)
	def saveProjectSettings(self):
		functions.saveProjectSettings(self)
	def getMain(self):
		return self.mainWindow
	def writeLog(self,text,error=False,warn=False,terminalPrefix=""):
		functions.writeLog(self,text,error=error,warn=warn,terminalPrefix=terminalPrefix)
	def writeError(self,text,terminalPrefix=""):
		functions.writeError(self,text,terminalPrefix=terminalPrefix)
	def writeWarning(self,text,terminalPrefix=""):
		functions.writeWarning(self,text,terminalPrefix=terminalPrefix)
	def getGraphicsOutput(self):
		return self.outputGraphicsNotebook
	def showGraphicsTab(self):
		self.mainNotebook.add(self.graphicsFrame)
	def showTextOutputTab(self):
		self.mainNotebook.add(self.outputTextField)
	def writeTextOutput(self,text):
		self.outputTextField["state"]="normal"
		self.outputTextField.insert("end","\n"+text)
		self.outputTextField["state"]="disabled"
	def resetTextOutput(self):
		self.outputTextField["state"]="normal"
		self.outputTextField.delete('1.0',"end")
		self.outputTextField["state"]="disabled"
	def saveSettings(self):	#Dummy function
		functions.saveSettings(self)
	def loadDataIntoGUI(self):
		return functions.loadDataIntoGUI(self)
	def exportGraphs(self):
		return functions.exportGraphs(self)
	def terminateThreads(self):
		self.killSignal[0] = True
		if len(self.runningThreads)>0:
			print("Killing all running threads: "+str(self.killSignal[0]))
			for (t,c) in self.runningThreads: t.join()
			print("All threads closed")
			self.runningThreads = list()
			self.writeWarning("All Threads killed")
			self.commsQueue.put(("WARN","All Threads killed"))
	def closeWindow(self):
		self.terminateThreads()
		print("[Main] Exiting")
		self.saveProgramSettings()
		self.getMain().destroy()
	
	def runPipeline(main):
		main.saveSettings()
		main.writeLog("-"*100,terminalPrefix="---")
		main.writeLog(f"Processing all files ...",terminalPrefix="[Main] ")
		main.writeLog("-"*100,terminalPrefix="---")
		main.pipeStartTime = time.time()
		usedParameterSets = set()
		for libID,lib in main.IM.getLibraries().items():
			if lib.ppt=="-":continue
			usedParameterSets.add(lib.ppt)	#only process the currently selected Parameterset
		print(f"[main run] Found PS: {usedParameterSets}")
		neededModules = set()
		for psname in usedParameterSets:
			neededModules.add(main.PM.getParameterSet(psname)[".moduleID"])
		
		main.tmp_run_modules = sorted(neededModules)
		print(f"[main run] Needed modules: {main.tmp_run_modules}")
		main.tmp_run_modules_index = 0
		main.nextPPTModule()
	
	def nextPPTModule(main):
		if main.tmp_run_modules is None or main.tmp_run_modules_index is None:return False
		if main.tmp_run_modules_index >= len(main.tmp_run_modules):	#ran all modules
			main.tmp_run_modules = None
			main.tmp_run_modules_index = None
			
			pipetime = time.time() - main.pipeStartTime
			if pipetime <300:timeText = f"{int(pipetime)} seconds"
			elif pipetime<11700:timeText = f"{round(pipetime/60,1)} minutes"
			else:timeText = f"{round(pipetime/3600,1)} hours"
			main.writeLog("-"*100,terminalPrefix="---")
			main.writeLog(f"Processing all files done in {timeText}.",terminalPrefix="[Main] ")
			main.writeLog("-"*100,terminalPrefix="---")
			
			main.saveSettings()
			main.loadDataIntoGUI()
		else:
			module = main.tmp_run_modules[main.tmp_run_modules_index]
			main.tmp_run_modules_index+=1
			try:
				main.moduleDict[module].process(main)
			except Exception as e:
				main.writeError(f"[Error][Func] Processing module \"{main.moduleDict[module].moduleID}\" does not implement the function \"process(main)\".")
				main.writeError(f"[Error][Func] Or a different error occured during execution:")
				main.writeError(str(e))
	
	def runCommand(self,stepID,commands,reqFiles,genFiles,libIDs,stdoutFiles=None,stderrFiles=None,grep=[],grepRequireOr=[],force=False,libraries=None):	#new thread
		if force:
			self.commsQueue.put(("WARN","Warning: Forcing the step overwrites all existing output for that step"))
			self.commsQueue.put(("WARN","         Please run all other steps with force to ensure that the results are updated"))
		runCommand(self.commsQueue,stepID,commands,reqFiles,genFiles,libIDs,killSignal=self.killSignal,stdoutFiles=stdoutFiles,stderrFiles=stderrFiles,
			grep=grep,grepRequireOr=grepRequireOr,force=force,libraries=libraries)
		if force:
			self.commsQueue.put(("WARN","Warning: Forcing the step overwrites all existing output for that step"))
			self.commsQueue.put(("WARN","         Please run all other steps with force to ensure that the results are updated"))
	
	def checkForLogUpdates(self):	#TODO actually checks for all kinds of updates, i.e. queueUpdates; move to dedicated class
		#print(f"\t\t[Main] Checking for updates {time.ctime()} {self.runningThreads}")
		while not self.commsQueue.empty():
			item = self.commsQueue.get()
			#print("\t"+str(item))
			if item[0] == "FINISHED":	#removes threads that are finished from the list
				for i in range(len(self.runningThreads)):
					if self.runningThreads[i][1] == item[1]:
						del self.runningThreads[i]
						break
			elif item[0] == "pipeERROR":
				self.pipelineError = True
				self.writeError(item[1])
			elif item[0] == "ERROR":self.writeError(item[1])
			elif item[0] == "WARN":self.writeWarning(item[1])
			elif item[0] == "LOG":self.writeLog(item[1])
				
		if len(self.runningThreads)>0:		#runs comms between the threads and the GUI as long as there are some (should only ever be one anyway)
			self.getMain().after(300,self.checkForLogUpdates)
		elif len(self.runningThreads)==0:	# if ~runPipeline, start the next step...
			pass				# OR use extra thread that waits ? and also listens to the kill?
	
	
	def isStepRunning(self):
		if len(self.runningThreads)>0:
			self.writeError("A step is already running; please wait until it completes or stop it manually.")
			return True
		else:
			self.killSignal[0] = False
			return False
	def openManual(main):
		try:
			system=platform.system()
			if system=="Darvin":
				subprocess.call(("open",os.path.join(main.execPath,"Manual.pdf")))
			elif system=="Windows":
				os.startfile(os.path.join(main.execPath,"Manual.pdf"))
			else:
				subprocess.call(("xdg-open",os.path.join(main.execPath,"Manual.pdf")))
		except Exception as e:
			main.writeError(str(e))
			main.writeError("Problem with opening the Manual.")
			main.writeError("You can instead find it in the program directory and open it manually.")

def launch(execPath=None):
	Main("RNAival - None",execPath=execPath).mainWindow.mainloop()
	print("[Main] Done with RNAival GUI")
