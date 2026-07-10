
import json
import os.path
from datetime import datetime
from pathlib import Path
from importlib import import_module

from tkinter import BooleanVar
from tkinter import StringVar
from tkinter import IntVar
from tkinter.ttk import Notebook
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Scrollbar as ThemedScrollbar
from tkinter.ttk import Entry as ThemedEntry
from tkinter import Toplevel
from tkinter.filedialog import askdirectory

import iostuff.seqFiles as seqIO
from gui.inputSelection import updateSeqFiles,updateTargetListFrame,saveSeqFiles
#import gui.siI_eval as sig
from gui.SettingsMenu import SettingsMenu
from gui.ScrollableNotebook import ScrollableNotebook

#Serves as container for functions that work on/with main

def createNewProjectMenu(main):
	#------------------------- new Project --------------------------------------------------
	projectParentPath = askdirectory(title="Select location for project",initialdir=main.execPath)
	if projectParentPath is None: return
	if not isinstance(projectParentPath,str):return
	
	newWindow = Toplevel()
	newWindow.projectNameVar = StringVar()
	newWindow.projectNameVar.set("NewProject")	#TODO validation? & check for collisions with other projects
	newWindow.title("Create new project")
	#newWindowBorder = ThemedFrame(newWindow,style="gBorder.TFrame")
	#newWindowBorder.pack(fill="both",expand=True)
	newWindowFrame = ThemedFrame(newWindow)
	newWindowFrame.pack(padx=5,pady=5,fill="both",expand=True)
	
	ThemedLabel(newWindowFrame,text="Create new project",style="Medium.TLabel",anchor="n").grid(column=0,row=0,columnspan=2,sticky="news")
	ThemedLabel(newWindowFrame,text="Name:").grid(column=0,row=1,sticky="news")
	pnentry = ThemedEntry(newWindowFrame,textvariable=newWindow.projectNameVar)
	pnentry.grid(column=1,row=1,sticky="news",columnspan=2)
	#also bind ENTER in this entry to create new project
	pnentry.bind("<Return>",lambda event, main=main,projectParentPath=projectParentPath,newWindow=newWindow:createNewProject(main,projectParentPath,newWindow))
	
	ThemedLabel(newWindowFrame,text="Project location:  ").grid(column=0,row=2,sticky="news")
	ThemedLabel(newWindowFrame,text="..."+projectParentPath[-30:]).grid(column=1,row=2,sticky="news")
	
	ThemedButton(newWindowFrame,text="New project",
		command=lambda main=main,projectParentPath=projectParentPath,newWindow=newWindow:createNewProject(main,projectParentPath,newWindow)
		).grid(column=1,row=3,sticky="news")
	ThemedButton(newWindowFrame,text="Cancel",command=newWindow.destroy).grid(column=0,row=3,sticky="news")
	newWindowFrame.columnconfigure(0,weight=0,uniform="fred")
	newWindowFrame.columnconfigure(0,weight=1,uniform="fred")
	newWindowFrame.rowconfigure(0,weight=1)
	newWindowFrame.rowconfigure(1,weight=1,uniform="fred")
	newWindowFrame.rowconfigure(2,weight=1,uniform="fred")
	newWindowFrame.rowconfigure(3,weight=1)
	main.mainWindow.eval(f'tk::PlaceWindow {str(newWindow)} center')

def showAllTabs(main):
	for index,frame in sorted(main.mainNotebooktabs.items()):
		#print(f"[main func] Adding tab ID {index} to notebook")
		main.mainNotebook.add(frame)

def createNewProject(main,projectParentPath,newWindow):
	name = newWindow.projectNameVar.get()
	newWindow.destroy()
	execPath = main.execPath
	
	pp=os.path.join(projectParentPath,name)
	print(f"\n\n[main func] Creating new project {name} at {projectParentPath}: {pp}\n\n")
	Path(pp).mkdir(parents=True, exist_ok=True)
	
	main.reset()
	showAllTabs(main)
	main.mainNotebook.select(0)
	initProject(main,pp)
	saveSettings(main)
	for module in main.moduleDict.values():
		module.after_project_load(main)

def initProject(main,pp):
	initText = f"Initialising project {pp}"
	bufferSize = max(1,(100-len(initText)))
	print(f"\n{'#'*103}\n#{' '*101}#\n# {initText}{' '*bufferSize}#\n#{' '*101}#\n{'#'*103}\n")
	main.PM.set("projectPath",pp)
	logDir = os.path.join(pp,"Logs")
	Path(logDir).mkdir(parents=True, exist_ok=True)
	main.logFile = os.path.join(logDir,"log_"+str(datetime.now()).replace(" ","_")+".txt")
	main.mainWindow.title(f"RNAival - {os.path.basename(pp)}")
	for module in main.moduleDict.values():
		module.init_project(main)
		#module.after_project_load(main)

def loadProject(main,pp):
	settingsFile = os.path.join(pp,"ProjectSettings.json")
	try:
		if os.path.isfile(settingsFile):
			
			main.reset()
			
			print("[main func] loading project "+pp)
			initProject(main,pp)
			
			parameterDict = dict()
			inputDict = dict()
			print(f"[main func] Loading settings from {settingsFile}")
			showAllTabs(main)
			with open(settingsFile,"r") as jr:
				jsonstr = jr.read()
				
				settingsObject = json.loads(jsonstr)
				
				if isinstance(settingsObject, dict):	#new(er) storage system, split by type of data/setting
					parameterDict = settingsObject	#currently only contains the project-path, which is only used for validation
					inputListFile = os.path.join(pp,"InputFiles.json")
					with open(inputListFile,"r") as jr:
						jsonstr = jr.read()
						inputDict = json.loads(jsonstr)
				elif isinstance(settingsObject, list):	#Old storage system; backwards compatibility
					#["Parameters:",main.PM.getDict(),"Input files:",main.IM.serialize()]
					_,parameterDict,_,inputDict = json.loads(jsonstr)
			
			main.PM.setAll(parameterDict)
			main.PM.loadParameterSets()
			main.IM.setAll(inputDict,main=main)
			updateTargetListFrame(main)
			
			for module in main.moduleDict.values():
				try:
					module.after_project_load(main)
				except Exception as e:
					main.writeError(f"Error running after_project_load from module \"{module.moduleID}\".")
					main.writeError(str(e))
					
			main.mainNotebook.select(0)
			
			for buttonList,boolVar in main.toggleButtonReferenceDict.values():	#update the Icons on togglebuttons to reflect their states AFTER laoding vars
				for button in buttonList:
					if boolVar.get():button["image"]=main.xBoxImage
					else:button["image"]=main.boxImage
			
			if main.PM.get("showGraphsOnProjectLoad"):
				main.loadDataIntoGUI()
		else:
			print(f"[main func] ERROR, Project {settingsFile} not found.")
			return False
	except Exception as e:
		main.writeError(f"Error loading project from \"{settingsFile}\".")
		main.writeError(str(e))
		return False

def updateLastProjectsFile(currentProject,execPath):
	lastProjects = [currentProject]
	lppath = os.path.join(execPath,".lastProjects")
	try:
		with open(lppath,"r") as lpr:
			for line in lpr:
				ppath = line.strip()
				if ppath not in lastProjects:	#list search is slow, but doesnt matter for 10 entries and we want to keep order consistent
					lastProjects.append(ppath)
	except:
		pass
	with open(lppath,"w") as lpw: lpw.write("\n".join(lastProjects[:10]))

def saveSettings(main):
	if not main.PM.validate():
		main.writeError("")
		main.writeError("#################################################")
		main.writeError("#   Error validating parameters, cannot save.   #")
		return False
	print(f"[main func] Saving settings to {main.PM.get("projectPath")}")
	
	updateLastProjectsFile(main.PM.get("projectPath"),main.execPath)
	
	#print(main.PM.toString())
	#main.PM.printTags()
	
	projectSettings = main.PM.getDict(tags=["project","graphics"])
	projectSettingsPath = os.path.join(main.PM.get("projectPath"),"ProjectSettings.json")
	try:
		with open(projectSettingsPath,"w") as jw:
			json.dump(projectSettings,jw,indent="\t",sort_keys=True)
	except Exception as e:
		main.writeError(f"Error saving project settings to \"{projectSettingsPath}\".")
		main.writeError(str(e))
		return False
	
	saveSeqFiles(main)
	
	for module in main.moduleDict.values():
		module.save_data(main)
	
	#print(main.IM.toString())
	inputSettingsPath = os.path.join(main.PM.get("projectPath"),"InputFiles.json")
	try:
		with open(inputSettingsPath,"w") as jw:
			json.dump(main.IM.serialize(),jw,indent="\t",sort_keys=True)
	except Exception as e:
		main.writeError(f"Error saving input settings to \"{inputSettingsPath}\".")
		main.writeError(str(e))
		return False
	
def openProjectList():
	print("[main func] [WIP] Showing project list")
def openSettingsMenu():
	print("[main func] [WIP] Showing settings")
def openAboutMenu():
	print("[main func] [WIP] Showing About")

def clearGraphics(main):
	#delete existing graphs (composition may have changed)
	main.comboGraphs = dict()
	main.outputGroups = dict()
	for child in main.outputGraphicsNotebook.winfo_children():child.destroy()	#just delete everything

def loadDataIntoGUI(main):
	if not main.PM.validate():
		main.writeError("")
		main.writeError("########################################################")
		main.writeError("#   Error validating parameters, cannot load graphs.   #")
		return False
	
	clearGraphics(main)
	main.showTextOutputTab()
	main.resetTextOutput()
	
	for module in main.moduleDict.values():
		if module.moduleType=="evaluation":
			try:
				module.evaluate(main)
			except Exception as e:
				main.writeError(f"[Error][Func] Evaluation module \"{module.moduleID}\" does not implement the function \"evaluate(main)\".")
				main.writeError(f"[Error][Func] Or a different error occured during execution:")
				main.writeError(str(e))
	
	displayGraphs(main)
	
def displayGraphs(main):
	print("\n[main func] Displaying graphs")
	main.writeLog("\n-------------------------------------------------------\nDisplaying graphs")
	if main.comboGraphs is None or len(main.comboGraphs.keys())==0:
		main.writeWarning("Nothing to display")
		return False
		
	if not main.PM.validateTags(["graphics"]):
		main.writeWarning("Error validating graphic parameters.")
		return False
	main.mainNotebook.select(main.graphicsTabIndex)			#select before graph generation to make scrollbars of graphs behave nicely
	
	if main.comboGraphs is None or len(main.comboGraphs.keys())==0:
		main.writeWarning("\tNo graphs to display")
		return False
	
	for graph in main.comboGraphs.values():
		#print("[Debug] displaying "+str(graph.title))
		resultDir = os.path.join(main.PM.get("projectPath"),"Graphics",graph.bundleID,graph.psname)
		Path(resultDir).mkdir(parents=True, exist_ok=True)
		graph.generateIGs(main,resultDir)
	
	for graph in main.comboGraphs.values():	#reset the selected tab back to the first one
		if graph.isScrollGraph:graph.parentnotebook.finish()
	main.outputGraphicsNotebook.select(0)
	
	fontMultiplier = main.PM.get("fontMultiplierGUI")
	#TODO seperate into re-draw function with other settings to re-apply
	for graph in main.comboGraphs.values():
		graph.drawOntoGui(fontMultiplier=fontMultiplier)
		
	#main.mainNotebook.select(main.graphicsTabIndex)	#only select later once all graphs have been generated
	main.writeLog("...done.")
	print("\n[main func] ...done.")
	return True

def exportGraphs(main):
	print("\n[main func] Exporting graphs")
	main.writeLog("\n-------------------------------------------------------\nExporting graphs")
	
	if not main.PM.validateTags(["graphics"]):
		main.writeWarning("Error validating graphic parameters.")
		return False
	if main.comboGraphs is None:
		main.writeError("\tERROR Data not loaded!")
		print("[LoadGraphs] ERROR Data not loaded!")
		return False
	
	exportW = main.PM.get("exportOverrideWidth")
	exportH = main.PM.get("exportOverrideHeight")
	fontMultiplier = main.PM.get("fontMultiplierSVG")
	for graph in main.comboGraphs.values():
		resultDir = os.path.join(main.PM.get("projectPath"),"Graphics",graph.bundleID,graph.psname)
		Path(resultDir).mkdir(parents=True, exist_ok=True)
		graph.exportAsSVG(resultDir,exportW,exportH,fontMultiplier)
	
	main.writeLog("...done.")
	print("\n[main func] ...done.")
	return True

def setStyles(main,highlightStyles):	#unused
	if main.comboGraphs is None:
		main.writeError("\tERROR Data not loaded!")
		print("[LoadGraphs] ERROR Data not loaded!")
		return False
	for graph in main.comboGraphs.values():
		graph.setStyles(highlightStyles)
	return True

def writeLog(main,text,error=False,warn=False,terminalPrefix=""):
	if error:print(terminalPrefix+"[ERROR] "+text)
	elif warn:print(terminalPrefix+"[WARNING] "+text)
	elif not terminalPrefix == "":print(terminalPrefix+text)
	
	main.outputTextLog["state"]="normal"
	main.outputTextLog.insert("end","\n"+str(text))
	#TODO loop over lines to handle multi-line errors	#But what about empty lines? do they cause errors with split("\n") ?
	#instead of relying on seperate log queue entries!
	if error:main.outputTextLog.tag_add("error","end-1c linestart","end-1c lineend")#only works with one-line output.....
	if warn:main.outputTextLog.tag_add("warn","end-1c linestart","end-1c lineend")
	main.outputTextLog["state"]="disabled"
	main.outputTextLog.see("end")
	try:
		with open(main.logFile,"a") as logWriter:
			if error: logWriter.write(terminalPrefix+"[ERROR] "+str(text)+"\n")
			elif warn: logWriter.write(terminalPrefix+"[WARNING] "+str(text)+"\n")
			else: logWriter.write(terminalPrefix+str(text)+"\n")
	except:
		print("[main func] ERROR while writing log to disk!\nCheck your available disk space!")
		main.outputTextLog["state"]="normal"
		main.outputTextLog.insert("end","\n"+"ERROR while writing log to disk!")
		if error:main.outputTextLog.tag_add("error","end-1c linestart","end-1c lineend")
		main.outputTextLog.insert("end","\n"+"Check your available disk space!")
		if error:main.outputTextLog.tag_add("error","end-1c linestart","end-1c lineend")
		main.outputTextLog["state"]="disabled"
		main.outputTextLog.see("end")
	
def writeError(main,text,terminalPrefix=""):
	writeLog(main,text,error=True,terminalPrefix=terminalPrefix)
	main.mainNotebook.select(main.logTabIndex)
def writeWarning(main,text,terminalPrefix=""):
	writeLog(main,text,warn=True,terminalPrefix=terminalPrefix)
	
def getStyledText(main,parent):
	return main.styleman.getStyledText(parent)
	
def switchTheme(main):
	if main.currentTheme == "light":
		main.currentTheme="dark"
		main.menubar.entryconfigure(3,label=" Lightmode ")
	else:
		main.currentTheme="light"
		main.menubar.entryconfigure(3,label=" Darkmode ")
	main.styleman.applyTheme(main.currentTheme)
	
# ------------------------ Toggle Button + ToggleParameterFrame ------------------------
def _toggleBoolButton(main,ID):	#Switches all buttons from the same group
	if main.toggleButtonReferenceDict[ID][1].get():
		for button in main.toggleButtonReferenceDict[ID][0]:
			button["image"]=main.boxImage
		main.toggleButtonReferenceDict[ID][1].set(False)
	else:
		for button in main.toggleButtonReferenceDict[ID][0]:
			button["image"]=main.xBoxImage
		main.toggleButtonReferenceDict[ID][1].set(True)

def createTogglebutton(main,parent,boolVar,syncKey=None):	#Button the switches state when pressed
	ID = len(main.toggleButtonReferenceDict.keys()) if syncKey is None else syncKey	#Can be synchronised with other buttons
	tb = ThemedButton(parent,command=lambda main=main,i=ID: _toggleBoolButton(main,i),style="internalDropClosed.TButton",image=main.boxImage)
	if not ID in main.toggleButtonReferenceDict:main.toggleButtonReferenceDict[ID] = [list(),boolVar]
	main.toggleButtonReferenceDict[ID][0].append(tb)
	if boolVar.get():tb["image"]=main.xBoxImage	#does not update when the underlying var changes state!
	return tb

def makeParameterToggleFrame(main,parent,title,toggleVar=None):	#only used by dsp_eval, but can be used by other modules as well
	# Create a Frame with a Title, a togglebutton and a body, return all 3
	totalFrame = ThemedFrame(parent,style="wBorder.TFrame")
	
	headerFrame = ThemedFrame(totalFrame,style="TFrame")
	headerFrame.pack(fill="x",pady=(0,main.frameBorderSize))	#Horizontal separator after the title, before the body
	ThemedLabel(headerFrame,text=title,style="Medium.TLabel",anchor="w").pack(anchor="w",fill="both",side="left",padx=main.frameBorderSize)
	toggleSelectedVar = BooleanVar(value=True) if toggleVar is None else toggleVar
	createTogglebutton(main,headerFrame,toggleSelectedVar).pack(anchor="e",fill="y",side="right")
	
	parameterFrame = ThemedFrame(totalFrame)
	parameterFrame.pack(anchor="n",fill="both",expand=True,side="top")
	return totalFrame,parameterFrame,toggleSelectedVar

# ------------------------ Foldout ------------------------
def _openFoldoutFrame(main,foldoutID):	#call to toggle the foldout buttons with ID
	fouldoutFrameTuple = main.foldoutFrameReferenceList[foldoutID]
	#print(f"\n[func] Foldout: {fouldoutFrameTuple}")
	#print(f"[func] opening fouldout with ID {foldoutID} and open-state {main.foldoutStates[foldoutID]}")
	
	if main.foldoutStates[foldoutID]:
		main.foldoutStates[foldoutID]=False
		fouldoutFrameTuple[0].configure(style="internalDropClosed.TButton")
		fouldoutFrameTuple[1].configure(style="internalDropClosed.TButton")
		fouldoutFrameTuple[2].configure(style="internalDropClosed.TButton")
		fouldoutFrameTuple[2]["image"]=main.triDown
		fouldoutFrameTuple[3].pack_forget()
		#fouldoutFrameTuple[4].configure(style="Raised.TFrame")	#change relief of frame where all the buttons and foldout are on
	else:
		main.foldoutStates[foldoutID]=True
		fouldoutFrameTuple[0].configure(style="internalDropOpen.TButton")
		fouldoutFrameTuple[1].configure(style="internalDropOpen.TButton")
		fouldoutFrameTuple[2].configure(style="internalDropOpen.TButton")
		fouldoutFrameTuple[2]["image"]=main.triUp
		fouldoutFrameTuple[3].pack(anchor="n",expand=True,fill="x",side="top",padx=main.frameBorderSize,pady=main.frameBorderSize)
		#fouldoutFrameTuple[4].configure(style="Raised.TFrame")

def makeFoldoutFrame(main,parent,buttonText,isOpen=False):	#only used by input selection annotation for targets
	# Creates a Frame with buttons that can foldout a body
	totalFrame = ThemedFrame(parent,style="gBorder.TFrame")
	ID = len(main.foldoutFrameReferenceList)
	
	headerFrame = ThemedFrame(totalFrame)
	headerFrame.pack(fill="x",expand=False,padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	header_label = ThemedButton(headerFrame,text=buttonText,command=lambda i=ID: _openFoldoutFrame(main,i),style="internalDropClosed.TButton")
	header_label.bind("<Return>",lambda event, i=ID: main.openFoldout(i))	#Space is bound by default to activate buttons, return is not!
	header_label.pack(anchor="w",expand=True,fill="both",side="left")
	internalTextvar = StringVar()		#Var that stores and controls the number next to the description
	header_var = ThemedButton(headerFrame,textvariable=internalTextvar,command=lambda i=ID: _openFoldoutFrame(main,i),style="internalDropClosed.TButton")
	header_var.bind("<Return>",lambda event, i=ID: main.openFoldout(i))
	header_var.pack(anchor="e",fill="y",side="left")
	header_icon = ThemedButton(headerFrame,command=lambda i=ID: _openFoldoutFrame(main,i),style="internalDropClosed.TButton",image=main.triDown)
	header_icon.bind("<Return>",lambda event, i=ID: main.openFoldout(i))
	header_icon.pack(anchor="e",fill="y",side="left")
	
	foldOutFrame = ThemedFrame(totalFrame)	#the body frame
	
	main.foldoutFrameReferenceList.append((header_label,header_var,header_icon,foldOutFrame,totalFrame))
	main.foldoutStates.append(False)
	#print(f"[func] Created fouldout with ID {ID} and open-state {main.foldoutStates[ID]}")
	if isOpen: _openFoldoutFrame(main,ID)
	parent.internalTextvar = internalTextvar
	return totalFrame,foldOutFrame,internalTextvar

# ------------------------
def addOutputGraphicsGroup(main,key,isScrollGraph=True):	#add new notebook for graphs with the same target/key to the graphicla output
	if not key in main.outputGroups:	#check if a group-notebook with that key already exists
		#Add new Tab to Main Graphics Notebook with padding
		paddingkeyBaseFrame = ThemedFrame(main.outputGraphicsNotebook,style="gBorder.TFrame")
		main.outputGraphicsNotebook.add(paddingkeyBaseFrame,text=str(key),sticky="news")
		keyBaseFrame = ThemedFrame(paddingkeyBaseFrame)
		keyBaseFrame.pack(fill="both",expand=True,pady=(main.frameBorderSize*2,0))
		
		if isScrollGraph:
			keyNotebook = ScrollableNotebook(keyBaseFrame)
		else:
			keyNotebook = Notebook(keyBaseFrame)
		keyNotebook.pack(side="left",fill="both",expand=True)
		keyNotebook_ID = len(main.outputGroups)
		main.outputGroups[key] = (keyNotebook,keyNotebook_ID)
	
	main.outputGraphicsNotebook.select(main.outputGroups[key][1])	#select tab to prevent scrollbar issues
	return main.outputGroups[key][0]	#return notebook

def scrollGraphicsOutput(main,key,*args):
	for canvas in main.outputGroups[key][2]:
		canvas.yview(*args)

def loadModules(main):
	try:
		moduleDir = os.path.join(main.execPath,"modules")
		files = os.listdir(moduleDir)
	except Exception as e:
		main.writeError("ERROR! Exception getting modules from "+str(main.execdir))
		main.writeError(str(e))
		return False
	print(f"[main func] loading modules from {moduleDir}")
	moduleDict = dict()
	for entry in files:
		try:
			if os.path.isfile(os.path.join(moduleDir,entry)):
				main.writeWarning("Warning! The module directory should not contain files! "+str(entry))
				continue
			elif entry.startswith("__"):continue
			else:
				moduleBase = os.path.join(moduleDir,entry)
				moduleMain = os.path.join(moduleBase,"main.py")
				if not os.path.isfile(moduleMain):
					main.writeError(f"ERROR! Found module {entry}, but it contains no main file \"{os.path.join(entry,"main.py")}\""
						,terminalPrefix="[main func][loadModules]")
					continue
				moduleName = f"modules.{entry}.main"
				module = import_module(moduleName)
				moduleID = module.moduleID
				moduleDict[moduleID] = module
				
				main.writeLog(f"Imported module {moduleID} from {moduleName}")
		except Exception as e:
			main.writeError("ERROR! Exception with "+str(os.path.join(moduleDir,entry)))
			main.writeError(str(e))
			continue
	return moduleDict

def loadProgramSettings(main):
	settingsFile = os.path.join(main.execPath,"Settings.json")
	try:
		if os.path.isfile(settingsFile):
			with open(settingsFile,"r") as jr:
				jsonstr = jr.read()
				generalSettingsDict = json.loads(jsonstr)
				main.PM.setAll(generalSettingsDict)
	except Exception as e:
		main.writeError(f"Error reading program settings from \"{settingsFile}\".")
		main.writeError(str(e))
		return False

def saveProgramSettings(main):	#save is called only when you manually change the settings, otherwise it just uses the defautls (?)
	generalSettingsDict = main.PM.getDict(tag="general")
	settingsFile = os.path.join(main.execPath,"Settings.json")
	try:
		with open(settingsFile,"w") as jw:
			json.dump(generalSettingsDict,jw,indent="\t",sort_keys=True)
	except Exception as e:
		main.writeError(f"Error saving program settings to \"{settingsFile}\".")
		main.writeError(str(e))
		return False
	
def openSettingsMenu(main):
	if main.settingsMenu is None:	#If it doesnt exist, create it
		main.settingsMenu = SettingsMenu(main)	
	else: #otherwise, it is always on top, so just center it
		main.settingsMenu.center()
