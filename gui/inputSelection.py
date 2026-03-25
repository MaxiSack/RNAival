
import os
import os.path
from pathlib import Path

from tkinter import Tk

from tkinter import Text
from tkinter import Menu
from tkinter import OptionMenu

from tkinter import BooleanVar
from tkinter import StringVar

from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry

from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askopenfilename

import processing.sR_processing as srp
import gui.functions as gfs
import iostuff.seqFiles as seqIO

def findFilesInDir(main):
	inputFileDir = askdirectory(title="Select directory",initialdir=main.execPath)	#returns None or "" or () if canceled
	if inputFileDir is None or inputFileDir == "":return	#canceled selection
	if not isinstance(inputFileDir,str):return	#other cases
	files = os.listdir(inputFileDir)
	if files is None:return	#no files in selected dir
	inputFileList = [os.path.join(inputFileDir,ifile) for ifile in files if ifile.endswith(".fastq.gz") or ifile.endswith(".fastq") ]
	addSeqFiles(main,inputFileList)

def findFilesSelect(main):
	inputFileList = askopenfilenames(filetypes=[("FastQ",".fastq.gz .fastq")],title="Select sequencing files",initialdir=main.execPath)	#returns None or () if canceled
	if inputFileList is None or len(inputFileList)==0:return	#canceled selection or nothing selected
	addSeqFiles(main,inputFileList)


def addSeqFiles(main,inputFileList):
	if inputFileList is None or len(inputFileList)==0:return
	print(f"Adding seqfiles {inputFileList}")
	main.IM.addSeqFiles(inputFileList)
	updateSeqFiles(main)
	updateSeqFileList(main)

def updateSeqFiles(main):
	print("[input] Saving changes to seqFileList")
	for libKey,fields in main.seqFileDict.items():
		main.IM.updateLib(libKey,ppt=fields["ppt"].get(),label=fields["label"].get(),comment=fields["comment"].get(),
			mapTarget=fields["mapTargets"].get(),evalType=fields["evalTypes"].get())

def saveSeqFiles(main):
	updateSeqFiles(main)
	updateSeqFileList(main)

def deleteLibrary(main,key):
	print(f"Deleting libarary {key}")
	updateSeqFiles(main)
	main.IM.removeLib(key)
	updateSeqFiles(main)
	updateSeqFileList(main)

def updateSeqFileList(main):
	print("[input] Updating seq file list")
	#updateSeqFiles(main)
	#print(main.IM.toString())
	main.seqFileDict = dict()
	for child in main.seqFileListFrame.winfo_children():child.destroy()
	row=0
	#desc=["libID","Path_R1","Path_R2","Label","Comment","Pre-processing","Targets","Evaluation"]
	desc=["Label","Comment","Pre-processing","Targets","Evaluation"]
	for column,colDesc in enumerate(desc):
		ThemedLabel(main.seqFileListFrame,text=colDesc,anchor="w").grid(column=column,row=row,sticky="ew")
	fieldKeys=["label","comment","ppt","mapTargets","evalTypes"]
	for libKey,library in sorted(main.IM.getLibraries().items(),key=lambda x:x[0]):	#TODO evalType(s) ! fix / decide! 
		row+=1
		libVals = library.serialize()
		main.seqFileDict[libKey] = dict()
		for column,fkey in enumerate(fieldKeys):
			if fkey == "libID":
				ThemedLabel(main.seqFileListFrame,text=libVals[fkey],anchor="w").grid(column=column,row=row,sticky="ew")
			if fkey == "label":
				labelVar = StringVar(value=libVals[fkey])
				main.seqFileDict[libKey][fkey] = labelVar
				ThemedEntry(main.seqFileListFrame,textvariable=labelVar).grid(column=column,row=row,sticky="ew")
			if fkey == "comment":
				commentVar = StringVar(value=libVals[fkey])
				main.seqFileDict[libKey][fkey] = commentVar
				ThemedEntry(main.seqFileListFrame,textvariable=commentVar).grid(column=column,row=row,sticky="ew")
			if fkey == "ppt":
				pptVar = StringVar(value="-")
				if len(libVals[fkey])>0:pptVar.set(libVals[fkey][0])
				main.seqFileDict[libKey][fkey] = pptVar
				if len(main.pptList)==1:
					pptVar.set(main.pptList[0])
					ThemedLabel(main.seqFileListFrame,text=main.pptList[0],anchor="w").grid(column=column,row=row,sticky="ew")
				else:	#TODO else dropdown; implement later for other pre-processing types
					ThemedLabel(main.seqFileListFrame,text=libVals[fkey],anchor="w").grid(column=column,row=row,sticky="ew")
			if fkey == "mapTargets":
				targetVar = StringVar(value="-")
				if len(libVals[fkey])>0:targetVar.set(libVals[fkey][0])
				main.seqFileDict[libKey][fkey] = targetVar
				mm2=OptionMenu(main.seqFileListFrame,targetVar,*main.mapTargets)	#TODO map targets should use label in GUI but ID in real...
				mm2.grid(column=column,row=row,sticky="ew")
				mm2.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
				mm2["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	
			if fkey == "evalTypes":
				evalVar = StringVar(value="-")
				if len(libVals[fkey])>0:evalVar.set(libVals[fkey][0])
				main.seqFileDict[libKey][fkey] = evalVar
				mm2=OptionMenu(main.seqFileListFrame,evalVar,*main.evalTypes)
				mm2.grid(column=column,row=row,sticky="ew")
				mm2.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
				mm2["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
		
		ThemedButton(main.seqFileListFrame,image=main.xImage_small,command = lambda main=main,key = libKey: deleteLibrary(main,key),style="Exit.TButton").grid(column=len(fieldKeys),row=row,sticky="ew")
	
	updateLibSelection(main)
	
def updateLibSelection(main):
	#also update all libIDSelectioNFrames
	#main.libOverrides = dict()
	#print(main.IM.getLibIDs())
	#print(main.libIDSelectionFrames)
	if len(main.IM.getLibIDs())==0:	#reset everytihng
		print("[input] Reseting lib selections")
		for frame in main.libIDSelectionFrames:
			for child in frame.winfo_children():child.destroy()
	else:
		print("[input] Updating lib selections")
		for frame in main.libIDSelectionFrames:	#TODO pupolation should depend on processtype and evaltype!	#TODO question this!
			#frame.valueDict = dict()
			for key in list(frame.valueDict.keys()):del frame.valueDict[key]
			#frame.ppt
			#frame.evalType
			for row,libID in enumerate(main.IM.getLibIDs()):
				print(f"{libID} {main.IM.getLib(libID).ppt} {main.IM.getLib(libID).evalTypes}")
				if not frame.ppt is None and frame.ppt != main.IM.getLib(libID).ppt:continue	#TODO this prevents libIDs from appearing when they just got their type
				if not frame.evalType is None and not frame.evalType in main.IM.getLib(libID).evalTypes:continue	#press "save changes"
				#if not libID in main.libOverrides: main.libOverrides[libID] = BooleanVar(value=True)
				#if not libID in frame.valueDict: 
				frame.valueDict[libID] = BooleanVar(value=True)
				ThemedLabel(frame,text=libID,anchor="w").grid(column=0,row=row,sticky="w")
				#print(f"Lib: {libID} {main.libOverrides[libID]}")
				#gfs.createTogglebutton(main,frame,main.libOverrides[libID],syncKey=libID).grid(column=1,row=row,sticky="e")
				gfs.createTogglebutton(main,frame,frame.valueDict[libID]).grid(column=1,row=row,sticky="e")
				frame.rowconfigure(row,weight=1,uniform="fred")
			#print(frame.valueDict)
		#print(main.libOverrides.items())


def selectMainTarget(main,menu):
	mainTargetPath = askopenfilename(filetypes=[("EMBL",".embl"),("Fasta",".fasta .fa")],title="Select the main target",initialdir=main.execPath)
	menu.mainTargetPath = mainTargetPath
	print(f"[input] Selected {menu.mainTargetPath}")
	
	if menu.mainTargetPath.endswith(".embl"):
		mainID,mainSequence,menu.annotation = seqIO.loadEMBL(menu.mainTargetPath,main=main)
	else:
		mainID,mainSequence = seqIO.loadFasta(menu.mainTargetPath,main=main)
	if not mainSequence is None:
		menu.mainIDVar.set(mainID)
		menu.mainLengthVar.set(len(mainSequence))
	

def addBackgroundTargets(main,menu):
	targetFileList = askopenfilenames(filetypes=[("Fasta",".fasta .fa .fna .fna.gz"),("EMBL",".embl")],title="Select background sequences",initialdir=main.execPath)
	#returns None or () if canceled
	if targetFileList is None or len(targetFileList)==0:return	#canceled selection or nothing selected
	#addSeqFiles(main,inputFileList)
	menu.offTargets = targetFileList
	print(f"Selected {menu.offTargets}")
	menu.offTargetTextfield["text"]="\n".join([os.path.basename(path) for path in menu.offTargets])

class TargetBundleMenu():
	def __init__(self, parent, main):
		self.labelVar = StringVar(value="New target")
		self.commentVar = StringVar(value="")
		self.mainIDVar = StringVar(value="")
		self.mainTargetPath = None
		self.mainLengthVar = StringVar(value="0")
		self.offTargets = list()
		self.offTargetTextfield = None
		self.annotation = None

def addNewTargetBundleFromMenu(main,menu):
	#make sure that all critical values are filled and not None !!!
	if menu.mainTargetPath is None or menu.mainTargetPath == "": return
	#TODO also pop an error !
	main.IM.addTargetBundle(main,menu.mainTargetPath,menu.labelVar.get(),menu.commentVar.get(),offTargets=menu.offTargets)
	updateTargetListFrame(main)

def addTargetBundleMenu(main):
	
	#remove newButton or not?
	
	menu = TargetBundleMenu(main.inputFrame_targetFilesList,main)
	addBundleMenuOuter = ThemedFrame(main.inputFrame_targetFilesList,style="gBorder.TFrame")
	addBundleMenuOuter.pack(fill="x",expand=True,anchor="nw",padx=5,pady=5)
	addBundleMenu = ThemedFrame(addBundleMenuOuter,style="wBorder.TFrame")
	addBundleMenu.pack(fill="x",expand=True,anchor="nw",padx=5,pady=5)
	
	#mainpath,label,offTargets
	ThemedLabel(addBundleMenu,text="Name:",anchor="w").grid(row=0,column=0,columnspan=1,sticky="news")
	ThemedEntry(addBundleMenu,textvariable=menu.labelVar).grid(row=0,column=1,columnspan=3,sticky="news")	#label
	ThemedLabel(addBundleMenu,text="Description:",anchor="w").grid(row=1,column=0,columnspan=1,sticky="news")
	ThemedEntry(addBundleMenu,textvariable=menu.commentVar).grid(row=1,column=1,columnspan=3,sticky="news")	#comment
	
	ThemedButton(addBundleMenu,text="Select main target",
		command = lambda main=main,menu=menu:selectMainTarget(main,menu)
		).grid(row=2,column=0,columnspan=2,sticky="ew")
	ThemedButton(addBundleMenu,text="Select background",
		command = lambda main=main,menu=menu:addBackgroundTargets(main,menu)
		).grid(row=2,column=2,columnspan=2,sticky="ew")
	
	ThemedLabel(addBundleMenu,text="Main target:",anchor="w").grid(row=3,column=0,columnspan=1,sticky="news")#mainID
	ThemedLabel(addBundleMenu,textvariable=menu.mainIDVar,anchor="w").grid(row=3,column=1,columnspan=1,sticky="news")#mainID	#TODO read-only entry?
	ThemedLabel(addBundleMenu,text="Main length:",anchor="w").grid(row=4,column=0,columnspan=1,sticky="news")#mainLength
	ThemedLabel(addBundleMenu,textvariable=menu.mainLengthVar,anchor="w").grid(row=4,column=1,columnspan=1,sticky="news")#mainLength
	#add Annotation dropdown if available
	#ThemedLabel(addBundleMenu,text="Annotation:",anchor="w").grid(row=5,column=0,columnspan=2,sticky="news")#mainLength
	ThemedLabel(addBundleMenu,text="Background sequences:",anchor="w").grid(row=3,column=2,columnspan=2,sticky="news")#backgrounds
	menu.offTargetTextfield = ThemedLabel(addBundleMenu,text="\n".join([os.path.basename(path) for path in menu.offTargets]),anchor="nw")
	menu.offTargetTextfield.grid(row=4,column=2,rowspan=3,columnspan=2,sticky="news")#backgrounds
	
	ThemedButton(addBundleMenu,text="Add",command = lambda main=main,menu=menu: addNewTargetBundleFromMenu(main,menu)).grid(column=2,row=6,columnspan=2,sticky="ew")
	
	ThemedButton(addBundleMenu,text="Cancel",
		command = addBundleMenuOuter.destroy,
		style="Exit.TButton").grid(column=0,row=6,columnspan=2,sticky="ew")
	
	addBundleMenu.columnconfigure(0,weight=1,uniform="fred")
	addBundleMenu.columnconfigure(1,weight=1,uniform="fred")
	addBundleMenu.columnconfigure(2,weight=1,uniform="fred")
	addBundleMenu.columnconfigure(3,weight=1,uniform="fred")
	
	addBundleMenu.rowconfigure(0,weight=1)
	addBundleMenu.rowconfigure(1,weight=1,uniform="fred")
	addBundleMenu.rowconfigure(2,weight=1,uniform="fred")
	addBundleMenu.rowconfigure(3,weight=1,uniform="fred")
	addBundleMenu.rowconfigure(4,weight=1,uniform="fred")
	addBundleMenu.rowconfigure(5,weight=2)
	addBundleMenu.rowconfigure(6,weight=1,uniform="fred")

def showAnnotation(annotFrame,annotation,annotCount=None):	#just adds widgets displaying annotaiton onto frame and setting annotcount
	for child in annotFrame.winfo_children():child.destroy()
	
	ThemedLabel(annotFrame,text="Name",justify="left").grid(column=0,row=0,sticky="we",padx=15)
	ThemedLabel(annotFrame,text="Type",justify="left").grid(column=1,row=0,sticky="we",padx=15)
	ThemedLabel(annotFrame,text="Duplex",justify="left").grid(column=2,row=0,sticky="we",padx=15)
	ThemedLabel(annotFrame,text="Strand",justify="left").grid(column=3,row=0,sticky="we",padx=15)
	ThemedLabel(annotFrame,text="Start",justify="left").grid(column=4,row=0,sticky="we",padx=15)
	ThemedLabel(annotFrame,text="Length",justify="left").grid(column=5,row=0,sticky="we",padx=15)
	ThemedLabel(annotFrame,text="Description",justify="left").grid(column=6,row=0,sticky="we",padx=15)
	trow=1
	for strand in [0,1]:
		for esiRNA in annotation[strand]:
			ThemedLabel(annotFrame,text=str(esiRNA[3]),justify="left").grid(column=0,row=trow,sticky="we",padx=15)
			ThemedLabel(annotFrame,text=str(esiRNA[2]),justify="left").grid(column=1,row=trow,sticky="we",padx=15)
			ThemedLabel(annotFrame,text=str(esiRNA[4]),justify="left").grid(column=2,row=trow,sticky="we",padx=15)
			ThemedLabel(annotFrame,text=str("sense" if strand == 0 else "anti"),justify="left").grid(column=3,row=trow,sticky="we",padx=15)
			ThemedLabel(annotFrame,text=str(esiRNA[0]),justify="left").grid(column=4,row=trow,sticky="we",padx=15)
			ThemedLabel(annotFrame,text=str(esiRNA[1]),justify="left").grid(column=5,row=trow,sticky="we",padx=15)
			ThemedLabel(annotFrame,text=str(esiRNA[5]),justify="left").grid(column=6,row=trow,sticky="we",padx=15)	#,wraplength=400 ; Parameter for label
			#annotFrame.rowconfigure(trow,weight=1,uniform="fred")	#this would screw with textwraping and is otherwise just not necessary
			trow+=1
	if not annotCount is None: annotCount.set(sum([len(a) for a in annotation]))

def addTargetBundleFoldout(main,targetBundle):
	bundleDescriptionFrameOuter = ThemedFrame(main.inputFrame_targetFilesList,style="gBorder.TFrame")
	bundleDescriptionFrameOuter.pack(fill="x",anchor="nw",padx=5,pady=5)
	
	bundleDescriptionFrame = ThemedFrame(bundleDescriptionFrameOuter,style="wBorder.TFrame")
	bundleDescriptionFrame.pack(fill="x",expand=True,anchor="nw",padx=5,pady=5)
	#getStyledText(main,main.mainNotebook)	#contents should be selectable for copy
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.label,anchor="w",style="Medium.TLabel").grid(row=0,column=0,columnspan=3,sticky="new")#name
	#ThemedLabel(bundleDescriptionFrame,text=targetBundle.totalLength,anchor="w",style="Medium.TLabel").grid(row=0,column=3,columnspan=1,sticky="news")#length
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.comment,anchor="w").grid(row=1,column=0,columnspan=4,sticky="new")#comment
	ThemedLabel(bundleDescriptionFrame,text="Main target:",anchor="w").grid(row=2,column=0,columnspan=1,sticky="new")#mainID
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.mainSeqID,anchor="w").grid(row=2,column=1,columnspan=1,sticky="new")#mainID
	ThemedLabel(bundleDescriptionFrame,text="Main length:",anchor="w").grid(row=3,column=0,columnspan=1,sticky="new")#mainLength
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.mainLength,anchor="w").grid(row=3,column=1,columnspan=1,sticky="new")#mainLength
	#add Annotation dropdown if available
	if not targetBundle.annotation is None:
		#ThemedLabel(bundleDescriptionFrame,text="Annotation:",anchor="w").grid(row=4,column=0,columnspan=2,sticky="news")#mainLength
		#~Foldoutframe !
		
	
		totalFrame,annotFrame,annotCount = gfs.makeInternalFoldoutFrame(main,bundleDescriptionFrame,"Annotations:",isOpen=False)
		totalFrame.grid(row=4,column=0,columnspan=2,sticky="news")
		showAnnotation(annotFrame,targetBundle.annotation,annotCount)
		
		annotFrame.columnconfigure(0,weight=4)
		annotFrame.columnconfigure(1,weight=2)
		annotFrame.columnconfigure(2,weight=2)
		annotFrame.columnconfigure(3,weight=1)
		annotFrame.columnconfigure(4,weight=1)
		annotFrame.columnconfigure(5,weight=4)
		
	ThemedLabel(bundleDescriptionFrame,text="Background sequences:",anchor="w").grid(row=2,column=2,columnspan=2,sticky="new")#backgrounds
	ThemedLabel(bundleDescriptionFrame,text="\n".join([os.path.basename(path) for path in targetBundle.offTargets]),anchor="nw").grid(row=3,column=2,rowspan=3,columnspan=2,sticky="news")#backgrounds	#TODO update 
	
	bundleDescriptionFrame.columnconfigure(0,weight=1,uniform="fred")
	bundleDescriptionFrame.columnconfigure(1,weight=1,uniform="fred")
	bundleDescriptionFrame.columnconfigure(2,weight=1,uniform="fred")
	bundleDescriptionFrame.columnconfigure(3,weight=1,uniform="fred")
	
	bundleDescriptionFrame.rowconfigure(0,weight=0)
	bundleDescriptionFrame.rowconfigure(1,weight=0)
	bundleDescriptionFrame.rowconfigure(2,weight=0)
	bundleDescriptionFrame.rowconfigure(3,weight=0)
	bundleDescriptionFrame.rowconfigure(4,weight=0)
	bundleDescriptionFrame.rowconfigure(5,weight=0)

def updateTargetListFrame(main):
	print("[input] Updating target list frame")
	for child in main.inputFrame_targetFilesList.winfo_children():child.destroy()
	
	#print(main.IM.toString())
	addNewBundleButton = ThemedButton(main.inputFrame_targetFilesList,text="Add new target",command = lambda main=main:addTargetBundleMenu(main))
	addNewBundleButton.pack(fill="x")
	
	for targetBundle in main.IM.getTargets():
		#print(targetBundle)
		print(targetBundle.toString())
		addTargetBundleFoldout(main,targetBundle)#
	
	main.mapTargets = ["-"]
	main.mapTargets.extend(main.IM.getTargetIDs())
	updateSeqFileList(main)

def runPipeline(main):
	saveSeqFiles(main)
	srp.runPipeline(main)

def add_inputGUI(main):
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[input Selection] adding GUI at {notebookIndex}")
	
	#Step0: input -------------------------------------------------------------------------------------------------------------------
	main.inputFrame = ThemedFrame(main.mainNotebook)
	main.mainNotebook.add(main.inputFrame,text="Input selection")
	main.mainNotebooktabs[notebookIndex] = main.inputFrame
	
	inputFrame_main = ThemedFrame(main.inputFrame)
	inputFrame_main.pack(fill="both",expand=True,anchor="nw")
	
	
	# --------------------- read libraries ----------------
	inputFrame_seqFiles = ThemedFrame(inputFrame_main)
	inputFrame_seqFiles.grid(row=0,column=0,sticky="new")
	ThemedLabel(inputFrame_seqFiles,text="Select sequencing libraries",anchor="w",style="Medium.TLabel").grid(column=0,row=0,columnspan=2,sticky="ew")#.pack(fill="both",expand=True,anchor="nw")
	
	ThemedButton(inputFrame_seqFiles,text="Select directory",command=lambda main=main:findFilesInDir(main)).grid(column=0,row=1,sticky="ew")
	ThemedButton(inputFrame_seqFiles,text="Select files",command=lambda main=main:findFilesSelect(main)).grid(column=1,row=1,sticky="ew")
	
	inputFrame_seqFiles.columnconfigure(0,weight=1,uniform="fred")
	inputFrame_seqFiles.columnconfigure(1,weight=1,uniform="fred")
	
	inputFrame_seqFiles.rowconfigure(0,weight=1,uniform="fred")
	inputFrame_seqFiles.rowconfigure(1,weight=1,uniform="fred")
	inputFrame_seqFiles.rowconfigure(2,weight=2)
	inputFrame_seqFiles.rowconfigure(3,weight=1,uniform="fred")
	
	
	main.seqFileDict = dict()
	main.seqFileListFrame = ThemedFrame(inputFrame_seqFiles,style="wBorder.TFrame")	#maybe style="gBorder.TFrame" ?
	main.seqFileListFrame.grid(column=0,row=2,columnspan=2,sticky="ew")
	#TODO scrollbar!	~vertical grid?
	#inputFrame_seqFiles.rowconfigure(0,weight=0)
	#inputFrame_seqFiles.columnconfigure(1,weight=1,uniform="fred")
	main.seqFileListFrame.columnconfigure(0,weight=2)
	main.seqFileListFrame.columnconfigure(1,weight=2)
	main.seqFileListFrame.columnconfigure(2,weight=0)
	main.seqFileListFrame.columnconfigure(3,weight=0)
	main.seqFileListFrame.columnconfigure(4,weight=0)
	main.seqFileListFrame.columnconfigure(5,weight=0)
	#{"libID":self.libID,"r1":self.r1,"r2":self.r2,"ppt":self.ppt,"label":self.label,"comment":self.comment,
	#		"mapTargets":sorted(self.mapTargets),"evalTypes":sorted(self.evalTypes)}
	
	#row=0
	#desc=["libID","Path_R1","Path_R2","Label","Comment","Pre-processing","Targets","Evaluation"]
	#for column,colDesc in enumerate(desc):
	#	ThemedLabel(main.seqFileListFrame,text=colDesc,anchor="w").grid(column=column,row=row,sticky="ew")
		
	updateSeqFileList(main)
	ThemedButton(inputFrame_seqFiles,text="Save Changes",command=lambda main=main:saveSeqFiles(main)).grid(column=0,row=3,columnspan=2,sticky="ew")
	
	
	# --------------------- construct/targets ----------------
	inputFrame_targetFiles = ThemedFrame(inputFrame_main)
	inputFrame_targetFiles.grid(row=0,column=1,sticky="new")
	
	
	ThemedLabel(inputFrame_targetFiles,text="Select targets for mapping",anchor="w",style="Medium.TLabel").pack(fill="x",expand=True,anchor="nw")
	main.inputFrame_targetFilesList = ThemedFrame(inputFrame_targetFiles,style="wBorder.TFrame")
	main.inputFrame_targetFilesList.pack(fill="x",expand=False,anchor="nw")
	
	updateTargetListFrame(main)
	
	
	inputFrame_main.rowconfigure(0,weight=1)
	inputFrame_main.columnconfigure(0,weight=1,uniform="fred")
	inputFrame_main.columnconfigure(1,weight=1,uniform="fred")
	#TODO make sure that this doesnt create new graphs, but updates them ! ~~
	ThemedButton(main.inputFrame,text="Run entire pipeline",command=lambda main=main:runPipeline(main)).pack(fill="x",anchor="nw")

