
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
import gui.siI_eval as sig

nucset={"A","C","G","T","U","N"}
idset = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0","_","-"}
intListset = {"1","2","3","4","5","6","7","8","9","0"," ",","}
hexset = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0"}

defaultColours = ["#ff0000","#00ff00","#0000ff","#ffff00","#00ffff","#ff00ff","#ddaa00","#aaff00","#00dddd"]#,"#","#","#"]



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
	execPath = main.PM.get("execPath")
	
	pp=os.path.join(projectParentPath,name)
	print(f"\n\n[main func] Creating new project {name} at {projectParentPath}: {pp}\n\n")
	Path(pp).mkdir(parents=True, exist_ok=True)
	
	main.reset()
	showAllTabs(main)
	main.mainNotebook.select(0)
	initProject(main,pp)
	saveSettings(main)

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

def loadProject(main,pp):
	settingsFile = os.path.join(pp,"ProjectSettings.json")
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
			#["Parameters:",main.PM.getDict(),"Input files:",main.IM.serialize()]
			_,parameterDict,_,inputDict = json.loads(jsonstr)
		main.PM.setAll(parameterDict)
		main.PM.loadParameterSets()
		main.IM.setAll(inputDict,main=main)
		updateTargetListFrame(main)
		
		for child in main.pairListFrame.pairChildren:child.destroy()
		main.pairList = list()
		libPairs = main.IM.getSIIPairs()
		#print(f"[main func] LibPairs: {libPairs}")
		for pair in libPairs:
			sig.addPair(main,pairLoad=pair)
		
		for module in main.moduleDict.values():
			module.after_project_load(main)
		
		main.mainNotebook.select(0)
	else:
		print(f"[main func] ERROR, File {settingsFile} not found.")

def saveSettings(main):
	pp = main.PM.get("projectPath")
	print(f"[main func] Saving settings to {pp}")
	lastProjects = [pp]
	lppath = os.path.join(main.PM.get("execPath"),".lastProjects")
	try:
		with open(lppath,"r") as lpr:
			for line in lpr:
				ppath = line.strip()
				if ppath not in lastProjects:	#list search is slow, but doesnt matter for 10 entries and we want to keep order consistent
					lastProjects.append(ppath)
	except:
		pass
	with open(lppath,"w") as lpw: lpw.write("\n".join(lastProjects[:10]))
	
	#updateSeqFiles(main)
	saveSeqFiles(main)
	#print(main.PM.toString())
	#print(main.IM.toString())
	saveConstruct = ["Parameters:",main.PM.getDict(),"Input files:",main.IM.serialize()]
	with open(os.path.join(pp,"ProjectSettings.json"),"w") as jw:
		json.dump(saveConstruct,jw,indent="\t",sort_keys=True)

def openProjectList():
	print("[main func] [WIP] Showing project list")
def openSettingsMenu():
	print("[main func] [WIP] Showing settings")
def openAboutMenu():
	print("[main func] [WIP] Showing About")

def loadDataIntoGUI(main):
	if not main.PM.validateTags(["graphics"]):
		main.writeWarning("Error validating graphic parameters.")
		return False
	
	#delete existing graphs (composition may have changed)
	main.comboGraphs = dict()
	main.outputGroups = dict()	#just delete everything
	for child in main.outputGraphicsNotebook.winfo_children():child.destroy()
	
	b1=sig.loadData(main,export=False,gui=False)
	main.showTextOutputTab()
	main.resetTextOutput()
	
	import gui.dsP_eval as dspg
	b2=dspg.loadData(main,export=False,gui=False)
	import evaluation.dsP_eval as dspe
	main.mainWindow.after(1000,lambda main=main: dspe.displayGraphs(main))
	
	#print(f"[main func] {b1} {b2}")
	return b1 and b2

def exportGraphs(main):
	import evaluation.dsP_eval as dspe
	dspe.exportGraphs(main)

def writeLog(main,text,error=False,warn=False):
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
			if error: logWriter.write("[ERROR] "+str(text)+"\n")
			elif warn: logWriter.write("[WARNING] "+str(text)+"\n")
			else: logWriter.write(str(text)+"\n")
	except:
		print("[main func] ERROR while writing log to disk!\nCheck your available disk space!")
		main.outputTextLog["state"]="normal"
		main.outputTextLog.insert("end","\n"+"ERROR while writing log to disk!")
		if error:main.outputTextLog.tag_add("error","end-1c linestart","end-1c lineend")
		main.outputTextLog.insert("end","\n"+"Check your available disk space!")
		if error:main.outputTextLog.tag_add("error","end-1c linestart","end-1c lineend")
		main.outputTextLog["state"]="disabled"
		main.outputTextLog.see("end")
	
def writeError(main,text):
	writeLog(main,text,error=True)
	main.mainNotebook.select(main.logTabIndex)
	print("[main func] [ERROR] "+text)
def writeWarning(main,text):
	writeLog(main,text,warn=True)
	
def getStyledText(main,parent):
	return main.styleman.getStyledText(parent)
	
def switchTheme(main):
	if main.theme == "light":main.theme="dark"
	else:main.theme="light"
	main.styleman.applyTheme(main.theme)

def addInputVar(main,name,var,vartype,default,errormessage,desc,tag=None):
	return main.PM.add(name,vartype,default,errormessage,desc,tags=None,tag=tag)
def addGraphicVar(main,name,var,vartype,default,errormessage,desc):
	return main.PM.add(name,vartype,default,errormessage,desc,tags=None,tag="graphics")
	
def toggleBoolButton(main,ID):
	#print(f"[main func] Set: {ID} {main.toggleButtonReferenceDict[ID][1]}")
	if main.toggleButtonReferenceDict[ID][1].get():
		for button in main.toggleButtonReferenceDict[ID][0]:
			button["image"]=main.boxImage
		main.toggleButtonReferenceDict[ID][1].set(False)
	else:
		for button in main.toggleButtonReferenceDict[ID][0]:
			button["image"]=main.xBoxImage
		main.toggleButtonReferenceDict[ID][1].set(True)
	#print("[main func] Set bool to "+str(main.toggleButtonReferenceDict[ID][1].get()))
	#print(main.libOverrides)

def createTogglebutton(main,parent,boolVar,syncKey=None):
	#boolVar.get()
	ID = len(main.toggleButtonReferenceDict.keys()) if syncKey is None else syncKey
	tb = ThemedButton(parent,command=lambda main=main,i=ID: toggleBoolButton(main,i),style="internalDropClosed.TButton",image=main.boxImage)
	if not ID in main.toggleButtonReferenceDict:main.toggleButtonReferenceDict[ID] = [list(),boolVar]
	main.toggleButtonReferenceDict[ID][0].append(tb)
	if boolVar.get():
		tb["image"]=main.xBoxImage
	print(f"[main func] TB:  {ID} {boolVar.get()}")
	#print(f"[main func] Set: {ID} {main.toggleButtonReferenceDict[ID][1]}")
	return tb

	
def openInternalFoldout(main,foldoutID):	#call to toggle thefoldout buttons with ID
	fouldoutFrameTuple = main.foldoutFrameReferenceList[foldoutID]
	#print(f"\nFoldout: {fouldoutFrameTuple}")
	print(f"[func] opening fouldout with ID {foldoutID} and open-state {main.foldoutStates[foldoutID]}")
	
	if main.foldoutStates[foldoutID]:
		main.foldoutStates[foldoutID]=False
		fouldoutFrameTuple[0].configure(style="internalDropClosed.TButton")
		fouldoutFrameTuple[1].configure(style="internalDropClosed.TButton")
		fouldoutFrameTuple[2].configure(style="internalDropClosed.TButton")
		fouldoutFrameTuple[2]["image"]=main.triDown
		fouldoutFrameTuple[3].pack_forget()
		#fouldoutFrameTuple[4].configure(style="Raised.TFrame")	#change relief of frame where all the buttons and foldou are on
	else:
		main.foldoutStates[foldoutID]=True
		fouldoutFrameTuple[0].configure(style="internalDropOpen.TButton")
		fouldoutFrameTuple[1].configure(style="internalDropOpen.TButton")
		fouldoutFrameTuple[2].configure(style="internalDropOpen.TButton")
		fouldoutFrameTuple[2]["image"]=main.triUp
		fouldoutFrameTuple[3].pack(anchor="n",expand=True,fill="x",side="top",padx=main.frameBorderSize,pady=main.frameBorderSize)
		#fouldoutFrameTuple[4].configure(style="Raised.TFrame")
	
	#main.mainWindow.after(10,self.updateParamScroll)	#Because the window isnt actually resized until the function ends, so call the update after that
	
def makeInternalFoldoutFrame(main,parent,buttonText,isOpen=False):	#only used by input selection annotation for targets
	totalFrame = ThemedFrame(parent,style="gBorder.TFrame")
	ID = len(main.foldoutFrameReferenceList)
	
	iconButtonFA = ThemedFrame(totalFrame)
	iconButtonFA.pack(fill="x",expand=False,padx=main.frameBorderSize,pady=main.frameBorderSize)	#With themed widgeds THIS (padding) is necessary to SEE the border
	
	fbl = ThemedButton(iconButtonFA,text=buttonText,command=lambda i=ID: openInternalFoldout(main,i),style="internalDropClosed.TButton")
	fbl.bind("<Return>",lambda event, i=ID: main.openFoldout(i))	#Space is bound by default to activate buttons, return is not!
	fbl.pack(anchor="w",expand=True,fill="both",side="left")	#,padx=0,pady=0 buttons (the text within them) are naturally padded
	
	internalTextvar = StringVar()		
	fbv = ThemedButton(iconButtonFA,textvariable=internalTextvar,command=lambda i=ID: openInternalFoldout(main,i),style="internalDropClosed.TButton")
	fbv.bind("<Return>",lambda event, i=ID: main.openFoldout(i))
	fbv.pack(anchor="e",fill="y",side="left")
	fbi = ThemedButton(iconButtonFA,command=lambda i=ID: openInternalFoldout(main,i),style="internalDropClosed.TButton",image=main.triDown)
	fbi.bind("<Return>",lambda event, i=ID: main.openFoldout(i))
	fbi.pack(anchor="e",fill="y",side="left")
	
	foldOutFrame = ThemedFrame(totalFrame)
	
	main.foldoutFrameReferenceList.append((fbl,fbv,fbi,foldOutFrame,totalFrame))
	main.foldoutStates.append(False)
	#print(f"[func] Created fouldout with ID {ID} and open-state {main.foldoutStates[ID]}")
	if isOpen: openInternalFoldout(main,ID)
	parent.internalTextvar = internalTextvar
	return totalFrame,foldOutFrame,internalTextvar

def makeParameterToggleFrame(main,parent,heading):	#only used by dsp_eval, but doesnt need to be foldouts anymore
	totalFrame = ThemedFrame(parent,style="wBorder.TFrame")
	insetFrame = ThemedFrame(totalFrame,style="wBorder.TFrame")
	insetFrame.pack(expand=True,fill="both",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	headerFrame = ThemedFrame(insetFrame)
	headerFrame.pack(fill="x",expand=True)#,padx=main.frameBorderSize,pady=main.frameBorderSize)	#With themed widgeds THIS (padding) is necessary to SEE the border
	
	ThemedLabel(headerFrame,text=heading,style="Medium.TLabel",anchor="w").pack(anchor="w",expand=True,fill="both",side="left")
	
	wantGraphVar = BooleanVar(value=True)
	createTogglebutton(main,headerFrame,wantGraphVar).pack(anchor="e",fill="y",side="left")
	
	parameterFrame = ThemedFrame(insetFrame)
	parameterFrame.pack(anchor="n",expand=True,fill="x",side="top")
	return totalFrame,parameterFrame,wantGraphVar

def addOutputGraphicsGroup(main,key):	#add new notebook for graphs with the same target/key to the graphicla output
	#print(f"\n[Fun] Output Graphics Groups: {main.outputGroups}\n")
	#print(f"\n[Fun] New Key: {key}\n")
	if not key in main.outputGroups:	#but dont overwrite existing; just add graphs to the notebook (that was created by another function)
		keyBaseFrame = ThemedFrame(main.outputGraphicsNotebook,style="TEST.TFrame")
		main.outputGraphicsNotebook.add(keyBaseFrame,text=str(key),sticky="news")
		#keyNotebook = Notebook(main.outputGraphicsNotebook)
		#main.outputGraphicsNotebook.add(keyNotebook,text=str(key))
		keyScrollbar = ThemedScrollbar(keyBaseFrame,orient="vertical",command=lambda *args, main=main,key=key:scrollGraphicsOutput(main,key,*args))
		keyScrollbarCanvasList = list()	#TODO also add mouse wheel scrolling...	~figure out how that works with multiple windows....
		keyScrollbar.pack(side="left",fill="y")
		keyNotebook = Notebook(keyBaseFrame)
		keyNotebook.pack(side="left",fill="both",expand=True)
		#new graphs added to [0], canvas for scrolling in those tabs listen to [1] and updated with [2]	#TODO there are some sync issues with unselected tabs....or not?
		main.outputGroups[key] = [keyNotebook, keyScrollbar, keyScrollbarCanvasList]
	return main.outputGroups[key]

def scrollGraphicsOutput(main,key,*args):
	for canvas in main.outputGroups[key][2]:
		canvas.yview(*args)

def deleteLenCovColPair(main,index):
	#print("[main func] Deleting libID-pair "+str(index)+": "+str(pairList[index][1].get())+" "+str(pairList[index][2].get()))
	main.multiCovColpairList[index][0].destroy()
	main.multiCovColpairList[index]=None
	#main.getMain().after(10,main.updateParamScroll)	#thisframe also needs a scrollbar

def addLenCovColPair(main,length=None, colour=None, updateView=True):
	pairList=main.multiCovColpairList
	pairListFrame=main.multiCovColpairListFrame
	pairFrame = ThemedFrame(pairListFrame)
	
	pairID = len(pairList)
	
	lenVar = addGraphicVar(main,"multiCovCol_length-"+str(pairID),StringVar(),"int","0",
		"Length be an integer!","Length of reads to display coverage for.")
	if not length is None:lenVar.set(str(length))
	
	defaultColour = defaultColours[len(pairList)] if len(pairList)<len(defaultColours) else "#000000"
	colVar = addGraphicVar(main,"multiCovCol_colour-"+str(pairID),StringVar(),"colour",defaultColour,
		"Colour for coverage needs to be a valid hexadecimal colour!","Colour for coverage")
	if not colour is None:colVar.set(str(colour))
	
	ThemedEntry(pairFrame,textvariable=lenVar).grid(column=0,row=0,sticky="ew")#,width=numberEntryWidth
	ThemedEntry(pairFrame,textvariable=colVar).grid(column=1,row=0,sticky="ew")
	
	ThemedButton(pairFrame,image=main.xImage_small,command = lambda main=main,i = len(pairList): deleteLenCovColPair(main,i),style="Exit.TButton").grid(column=3,row=0,sticky="ew")
	
	pairFrame.columnconfigure(0,weight=1,uniform="fred")
	pairFrame.columnconfigure(1,weight=1,uniform="fred")
	pairFrame.columnconfigure(4,weight=0)
	
	pairFrame.pack(fill="x",side="top",padx=main.frameBorderSize)#,pady=main.frameBorderSize)
	pairList.append([pairFrame,lenVar,colVar])	#frame to delete from gui, vars to build graphs; when deleted is set to None

def loadModules(main):
	try:
		moduleDir = os.path.join(main.execPath,"processing")
		files = os.listdir(moduleDir)
	except Exception as e:
		main.writeError("ERROR! Exception getting processing modules from "+str(main.execdir))
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
					main.writeError("ERROR! Found a module, but no main file "+str(moduleMain))
					return False
				moduleName = f"processing.{entry}.main"
				module = import_module(moduleName)
				moduleID = module.moduleID
				moduleDict[moduleID] = module
				
				main.writeLog(f"Imported module {moduleID} from {moduleName}")
		except Exception as e:
			main.writeError("ERROR! Exception with "+str(os.path.join(moduleDir,entry)))
			main.writeError(str(e))
			continue
	return moduleDict

