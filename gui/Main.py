
import time
from datetime import datetime
from tkinter import Tk
from queue import Queue

from gui.Definition import defineGUI
from gui.StyleManager import StyleManager
from gui.ParameterManager import ParameterManager
from gui.InputManager import InputManager
import gui.functions as functions
#from gui.functions import *
from functions.commandManager import runCommand
from gui.inputSelection import updateTargetListFrame


class Main():
	def __init__(self,title,initialTheme="light",execPath="",projectPath=None):
		self.theme = initialTheme
		self.execPath = execPath
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
		
		#------- defines before building anything else! ------
		self.inputVars = dict()
		self.varTags = dict()
		self.numberEntryWidth = 8
		self.foldoutFrameReferenceList = list()
		self.foldoutStates = list()
		#self.toggleButtonReferenceList=list()
		self.toggleButtonReferenceDict=dict()
		
		self.mainNotebooktabs = dict()
		self.libIDSelectionFrames = list()
		self.libOverrides = dict()	#TODO maybe replace all these with a single dict.....
		self.comboGraphs = dict()
		
		self.pptList = list()	#added by sR_processing_GUI or other pre-processing scripts
		self.mapTargets = ["-"]	#filled by adding targets!
		self.evalTypes = ["-"]	#added by siI_eval and dsP_eval or other evaluation scripts
		
		self.PM = ParameterManager(self)
		self.IM = InputManager()
		#initialTheme="dark"
		self.styleman = StyleManager(self,initialTheme=initialTheme,execPath=execPath)
		
		defineGUI(self)
		
		print("[Main] Execution path: "+str(self.execPath))
		if not projectPath is None:
			self.PM.set("projectPath",projectPath)
			functions.saveSettings(self)
		
		#self.loadDataIntoGUI()
	
	def reset(self):
		print("\n[Main] resetting everything")
		self.PM.reset()
		self.IM.reset()
		updateTargetListFrame(self)
		print("[Main] done.\n")
	
	def getMain(self):
		return self.mainWindow
	def writeLog(self,text,error=False,warn=False):
		functions.writeLog(self,text,error=error,warn=warn)
	def writeError(self,text):
		functions.writeError(self,text)
	def writeWarning(self,text):
		functions.writeWarning(self,text)
	def checkInputParams(self,inputDict=None):
		return functions.checkInputParams(self,inputDict=inputDict)
	def getGraphicsOutput(self):
		return self.outputGraphicsNotebook
	def showGraphicsTab(self):
		self.mainNotebook.add(self.graphicsFrame)
	def resetGraphicsOutput(self):
		self.showGraphicsTab()
		for tab in list(self.outputGraphicsNotebook.tabs()):
			self.outputGraphicsNotebook.forget(tab)
	def mouseWheelScroll(self,event):	#TODO re-implement
		#check if the graphic output is active
		if self.mainNotebook.index(self.mainNotebook.select())==self.graphicsTabIndex:
			for canvas in self.outputGraphicsScrollCanvasList:	#Doesnt work anymore
				if event.num==5:canvas.yview_scroll(1,"units")
				elif event.num==4:canvas.yview_scroll(-1,"units")
		return "break"
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
	def fitCanvasWidthGraph(self,canvas):
		boundBox = canvas.bbox("all")
		#print("Canvas bounding box: "+str(boundBox))
		canvas.configure(width = boundBox[2])
		boundsAd = (boundBox[0],boundBox[1],boundBox[2],max(boundBox[3],self.mainNotebook.winfo_height()-100))	#2 because borders...
		#print("DEBUG Output "+str(self.mainNotebook.winfo_height()))
		canvas.configure(scrollregion = boundsAd)
	
	def fitCanvasWidth(self):
		#boundBox = self.paramCanvas.bbox("all")
		#print("Canvas bounding box: "+str(boundBox))
		#self.paramCanvas.configure(width = boundBox[2])
		pass
	def saveSettings(self):	#Dummy function
		functions.saveSettings(self)
	def loadDataIntoGUI(self):
		#TODO make sure that this doesnt create new graphs, but updates them !
		#TODO  ~ if loaded, update instead?
		#or check them?
		#or just delete them and make an extra button for displayupdates, but pipe always creates new ones?
		return functions.loadDataIntoGUI(self)
	def terminateThreads(self):
		self.killSignal[0] = True
		print("Killing all running threads: "+str(self.killSignal[0]))
		for (t,c) in self.runningThreads: t.join()
		print("All threads closed")
		self.runningThreads = list()
		#self.killSignal[0] = False	#????
		#print(len(self.runningThreads))
		self.writeWarning("All Threads killed")
		self.commsQueue.put(("WARN","All Threads killed"))
	def exitProgramm(self):
		self.terminateThreads()
		print("exiting")
		self.getMain().destroy()
	def closeWindow(self):
		self.terminateThreads()
		print("exiting")
		self.getMain().destroy()
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
		print(f"\t\tChecking for updates {time.ctime()} {self.runningThreads}")
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
			self.getMain().after(200,self.checkForLogUpdates)
		elif len(self.runningThreads)==0:	# if ~runPipeline, start the next step...
			pass				# OR use extra thread that waits ? and also listens to the kill?
	
	
	def isStepRunning(self):
		if len(self.runningThreads)>0:
			self.writeError("A step is already running; please wait until it completes or stop it manually.")
			return True
		else:
			self.killSignal[0] = False
			return False
def launch(execPath=None):
	Main("RNAival - None",execPath=execPath).mainWindow.mainloop()
	print("Done with siRNA analysis")
