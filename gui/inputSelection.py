
import os
import os.path

import time

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

def updateSeqFiles(main):	#Update the internally stored libaries with the selected values
	print("[input] Saving changes to seqFileList")
	starttime = time.time()
	for libKey,fields in main.seqFileDict.items():
		targetValue = fields["mapTargets"].get()
		if targetValue == "-":
			main.writeWarning(f"Warning, no target selected for library {libKey}")
			continue
		main.IM.updateLib(libKey,ppt=None,label=fields["label"].get(),comment=fields["comment"].get(),
			psname=fields["PS"].get(),mapTarget=main.IM.getTarget(targetValue).bundleID,evalType=fields["evalTypes"].get())
			#fields["ppt"]	#remove this and make sure that parametersets are split by ppt and evaltype
	#print(f"[input][Debug] updateSeqFiles took {time.time()-starttime} seconds\n")

def saveSeqFiles(main):
	updateSeqFiles(main)
	updateSeqFileList(main)

def deleteLibrary(main,key):
	print(f"[input] Deleting library {key}")
	updateSeqFiles(main)	#save changes
	main.IM.removeLib(key)	#remove lib
	updateSeqFileList(main)	#update list

def updateSeqFileList(main):
	print("[input] Updating input file list")
	starttime = time.time()
	#updateSeqFiles(main)
	#print(main.IM.toString())
	main.seqFileDict = dict()
	for child in main.seqFileListFrame.winfo_children():child.destroy()	#delete all existing widgeds, then re-add them	#TODO instead update them
	
	row=0
	desc=["Label","Comment","Pre-processing","Targets","Evaluation"]
	for column,colDesc in enumerate(desc):
		ThemedLabel(main.seqFileListFrame,text=colDesc,anchor="w").grid(column=column,row=row,sticky="ew")
	fieldKeys=["label","comment","PS","mapTargets","evalTypes"]
	print(f"[Input] PS-keys: {main.PM.getParameterSetKeys()}")
	targetLabels = [main.IM.getTarget(bundleID).bundleID for bundleID in main.mapTargets]
	PSkeys = main.PM.getParameterSetKeys()
	psCount = len(PSkeys)
	print(f"[Input] Target-labels: {targetLabels}")
	#print(f"[input][Debug] updateSeqFileList init took {time.time()-starttime} seconds\n")
	lasttime = time.time()
	for libKey,library in sorted(main.IM.getLibraries().items(),key=lambda x:x[0]):
		row+=1
		libVals = library.serialize()
		main.seqFileDict[libKey] = dict()
		for column,fkey in enumerate(fieldKeys):	#TODO give dropdowns a command to update the affected library immediatly
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
			if fkey == "PS":
				#print(f"[Input] PS-keys: {keys}")
				if psCount < 1:	#shouldnt happen, since sRP has a default PS
					print("\n\n[Input selection] ERROR, no parametersets to select!\n\n")
					continue
				print(f"PPT in lib {libKey}: {libVals["ppt"]}")
				psVar = StringVar(value=PSkeys[0] if libVals["ppt"]=="" else libVals["ppt"])	#new libraries have their ppt="" until something is selected and saved
				main.seqFileDict[libKey][fkey] = psVar
				if psCount==1:
					ThemedLabel(main.seqFileListFrame,text=psVar.get(),anchor="w").grid(column=column,row=row,sticky="ew")
				else:
					mm=OptionMenu(main.seqFileListFrame,psVar,*PSkeys)
					main.styleman.registredOptionMenus.append(mm)	#TODO causes problems when re-gening!! (because previous additions arent removed) 
											#~will be fixed fixed when widgets are updated instead of deleted
											# just also update the "delete library" command with this!
					mm.grid(column=column,row=row,sticky="ew")
					#TODO make function in styleman to create (and update) menus !!!
					mm.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,
						activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
					mm["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,
						activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
			
			if fkey == "mapTargets":
				targetVar = StringVar(value="-")
				if len(libVals[fkey])>0:targetVar.set(main.IM.getTarget(libVals[fkey][0]).bundleID)
				main.seqFileDict[libKey][fkey] = targetVar
				if len(targetLabels)==0:continue
				mm2=OptionMenu(main.seqFileListFrame,targetVar,*targetLabels)	# Target label is now also their ID
				main.styleman.registredOptionMenus.append(mm2)
				mm2.grid(column=column,row=row,sticky="ew")
				mm2.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,
					activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
				mm2["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,
					activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
			
			if fkey == "evalTypes":
				evalVar = StringVar(value="-")
				if len(libVals[fkey])>0:evalVar.set(libVals[fkey][0])
				main.seqFileDict[libKey][fkey] = evalVar
				mm2=OptionMenu(main.seqFileListFrame,evalVar,*main.evalTypes)
				main.styleman.registredOptionMenus.append(mm2)
				mm2.grid(column=column,row=row,sticky="ew")
				mm2.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,
					activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
				mm2["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,
					activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
		
		ThemedButton(main.seqFileListFrame,image=main.xImage_small,command = lambda main=main,key = libKey: deleteLibrary(main,key)
			,style="Exit.TButton").grid(column=len(fieldKeys),row=row,sticky="ew")
		#print(f"[input][Debug] adding {libKey} took {time.time()-lasttime} seconds")
		lasttime = time.time()
	#print(f"[input][Debug] updateSeqFileList took {time.time()-starttime} seconds\n")	#TODO do this in another update!

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
	menu.offTargets = targetFileList	#TODO this replaces previously selected targets - should implement a better (more GUI complex) way to do this
	print(f"Selected {menu.offTargets}")
	menu.offTargetTextfield["text"]="\n".join([os.path.basename(path) for path in menu.offTargets])

class TargetBundleMenu():
	def __init__(self, parent, main):
		self.labelVar = StringVar(value="NewTarget")
		self.commentVar = StringVar(value="")
		self.mainIDVar = StringVar(value="")
		self.mainTargetPath = None
		self.mainLengthVar = StringVar(value="0")
		self.offTargets = list()
		self.offTargetTextfield = None
		self.annotation = None

def addNewTargetBundleFromMenu(main,menu):
	#make sure that all critical values are filled and not None !!!
	if menu.mainTargetPath is None or menu.mainTargetPath == "":
		main.writeError("ERROR, No target sequence selected!")
		return
	targetLabel = menu.labelVar.get()
	if targetLabel is None or targetLabel=="":
		main.writeError("ERROR, Set a label for the new Target!")
		return
	error = main.PM.checkVar("id",targetLabel)
	if error:
		main.writeError("ERROR, The label for the new Target needs to conform to the naming rules (letters,numbers, \"_\" and \"-\" are allowed)")
		return
	if main.IM.hasTarget(targetLabel):
		main.writeError(f"ERROR, label \"{targetLabel}\" already in use, please choose another one!")
		return
	main.IM.addTargetBundle(main,targetLabel,menu.mainTargetPath,menu.commentVar.get(),offTargets=menu.offTargets)
	updateTargetListFrame(main)
	gfs.saveSettings(main)
	#maybe store targets and libraries as separate files in folders !?!

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
	ThemedLabel(addBundleMenu,textvariable=menu.mainIDVar,anchor="w").grid(row=3,column=1,columnspan=1,sticky="news")	#TODO read-only entry instead of label?
	ThemedLabel(addBundleMenu,text="Main length:",anchor="w").grid(row=4,column=0,columnspan=1,sticky="news")#mainLength
	ThemedLabel(addBundleMenu,textvariable=menu.mainLengthVar,anchor="w").grid(row=4,column=1,columnspan=1,sticky="news")
	#add Annotation dropdown if available
	#ThemedLabel(addBundleMenu,text="Annotation:",anchor="w").grid(row=5,column=0,columnspan=2,sticky="news")#mainLength
	ThemedLabel(addBundleMenu,text="Background sequences:",anchor="w").grid(row=3,column=2,columnspan=2,sticky="news")#backgrounds
	menu.offTargetTextfield = ThemedLabel(addBundleMenu,text="\n".join([os.path.basename(path) for path in menu.offTargets]),anchor="nw")
	menu.offTargetTextfield.grid(row=4,column=2,rowspan=3,columnspan=2,sticky="news")
	
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
			ThemedLabel(annotFrame,text=str(esiRNA[5]),justify="left").grid(column=6,row=trow,sticky="we",padx=15)
			trow+=1
	if not annotCount is None: annotCount.set(sum([len(a) for a in annotation]))

def addTargetBundleFoldout(main,targetBundle):
	bundleDescriptionFrameOuter = ThemedFrame(main.inputFrame_targetFilesList,style="gBorder.TFrame")
	bundleDescriptionFrameOuter.pack(fill="x",anchor="nw",padx=5,pady=5)
	
	bundleDescriptionFrame = ThemedFrame(bundleDescriptionFrameOuter,style="TFrame")
	bundleDescriptionFrame.pack(fill="x",expand=True,anchor="nw",padx=5,pady=5)
	#getStyledText(main,main.mainNotebook)	#contents should be selectable for copy
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.bundleID,anchor="w",style="Medium.TLabel").grid(row=0,column=0,columnspan=4,sticky="new")
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.comment,anchor="w").grid(row=1,column=0,columnspan=4,sticky="new")
	ThemedLabel(bundleDescriptionFrame,text="Main target:",anchor="w").grid(row=2,column=0,columnspan=1,sticky="new")
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.mainSeqID,anchor="w").grid(row=2,column=1,columnspan=1,sticky="new")
	ThemedLabel(bundleDescriptionFrame,text="Main length:",anchor="w").grid(row=3,column=0,columnspan=1,sticky="new")
	ThemedLabel(bundleDescriptionFrame,text=targetBundle.mainLength,anchor="w").grid(row=3,column=1,columnspan=1,sticky="new")
	
	if not targetBundle.annotation is None:	#add Annotation dropdown if available
		totalFrame,annotFrame,annotCount = gfs.makeInternalFoldoutFrame(main,bundleDescriptionFrame,"Annotations:",isOpen=False)
		totalFrame.grid(row=4,column=0,columnspan=2,sticky="new")
		showAnnotation(annotFrame,targetBundle.annotation,annotCount)
		
		annotFrame.columnconfigure(0,weight=4)
		annotFrame.columnconfigure(1,weight=2)
		annotFrame.columnconfigure(2,weight=2)
		annotFrame.columnconfigure(3,weight=1)
		annotFrame.columnconfigure(4,weight=1)
		annotFrame.columnconfigure(5,weight=4)
		ThemedFrame(bundleDescriptionFrame,style="TFrame").grid(row=5,column=0,columnspan=2,sticky="news")	#Buffering for longer lists of backgroundsequences
	else:
		ThemedFrame(bundleDescriptionFrame,style="TFrame").grid(row=4,column=0,columnspan=2,rowspan=2,sticky="news")
	
	ThemedLabel(bundleDescriptionFrame,text="Background sequences:",anchor="w").grid(row=2,column=2,columnspan=3,sticky="new")
	ThemedLabel(bundleDescriptionFrame,text="\n".join([os.path.basename(path) for path in targetBundle.offTargets])
		,anchor="nw").grid(row=3,column=2,rowspan=3,columnspan=2,sticky="news")
	
	bundleDescriptionFrame.columnconfigure(0,weight=1,uniform="fred")
	bundleDescriptionFrame.columnconfigure(1,weight=1,uniform="fred")
	bundleDescriptionFrame.columnconfigure(2,weight=1,uniform="fred")
	bundleDescriptionFrame.columnconfigure(3,weight=1,uniform="fred")
	
	bundleDescriptionFrame.rowconfigure(0,weight=0)
	bundleDescriptionFrame.rowconfigure(1,weight=0)
	bundleDescriptionFrame.rowconfigure(2,weight=0)
	bundleDescriptionFrame.rowconfigure(3,weight=0)
	bundleDescriptionFrame.rowconfigure(4,weight=0)
	bundleDescriptionFrame.rowconfigure(5,weight=1)

def updateTargetListFrame(main):
	print("[input] Updating target list frame")
	for child in main.inputFrame_targetFilesList.winfo_children():child.destroy()
	
	#print(main.IM.toString())
	
	for targetBundle in main.IM.getTargets():
		#print(targetBundle)
		#print(targetBundle.toString())
		addTargetBundleFoldout(main,targetBundle)#
	
	main.mapTargets = list()	#["-"]
	main.mapTargets.extend(main.IM.getTargetIDs())
	updateSeqFileList(main)

def add_inputGUI(main):
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[input Selection] adding GUI at {notebookIndex}")
	
	#Step0: input -------------------------------------------------------------------------------------------------------------------
	main.inputFrame = ThemedFrame(main.mainNotebook,style="gBorder.TFrame")
	main.mainNotebook.add(main.inputFrame,text="Input selection")
	main.mainNotebooktabs[notebookIndex] = main.inputFrame
	
	inputFrame_main = ThemedFrame(main.inputFrame,style="gBorder.TFrame")
	inputFrame_main.pack(fill="both",expand=True,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	
	# --------------------- read libraries ----------------
	inputFrame_seqFiles = ThemedFrame(inputFrame_main,style="TFrame")
	inputFrame_seqFiles.grid(row=0,column=0,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(inputFrame_seqFiles,text="Select sequencing libraries",anchor="w",style="Medium.TLabel").grid(column=0,row=0,columnspan=2,sticky="news",padx=main.frameBorderSize)
	
	ThemedButton(inputFrame_seqFiles,text="Select directory",command=lambda main=main:findFilesInDir(main)).grid(column=0,row=1,sticky="news")
	ThemedButton(inputFrame_seqFiles,text="Select files",command=lambda main=main:findFilesSelect(main)).grid(column=1,row=1,sticky="news")
	
	
	
	main.seqFileDict = dict()	#TODO this needs a scrollbar!; more accurately: place this on a canvas which is next to a scrollbar on a frame
	main.seqFileListFrame = ThemedFrame(inputFrame_seqFiles,style="TFrame")
	main.seqFileListFrame.grid(column=0,row=2,columnspan=2,sticky="news")
	
	main.seqFileListFrame.columnconfigure(0,weight=2)
	main.seqFileListFrame.columnconfigure(1,weight=2)
	main.seqFileListFrame.columnconfigure(2,weight=0)
	main.seqFileListFrame.columnconfigure(3,weight=0)
	main.seqFileListFrame.columnconfigure(4,weight=0)
	main.seqFileListFrame.columnconfigure(5,weight=0)
		
	updateSeqFileList(main)
	ThemedButton(inputFrame_seqFiles,text="Save Changes",command=lambda main=main:saveSeqFiles(main)).grid(column=0,row=3,columnspan=2,sticky="news")
	
	inputFrame_seqFiles.columnconfigure(0,weight=1,uniform="fred")
	inputFrame_seqFiles.columnconfigure(1,weight=1,uniform="fred")
	
	inputFrame_seqFiles.rowconfigure(0,weight=0,uniform="fred")
	inputFrame_seqFiles.rowconfigure(1,weight=0,uniform="fred")
	inputFrame_seqFiles.rowconfigure(2,weight=1)
	inputFrame_seqFiles.rowconfigure(3,weight=0,uniform="fred")
	
	# --------------------- construct/targets ----------------
	inputFrame_targetFiles = ThemedFrame(inputFrame_main,style="TFrame")
	inputFrame_targetFiles.grid(row=0,column=1,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	
	ThemedLabel(inputFrame_targetFiles,text="Select targets for mapping",anchor="w",style="Medium.TLabel").grid(row=0,column=0,sticky="news",padx=main.frameBorderSize)
	ThemedButton(inputFrame_targetFiles,text="Add new target",command = lambda main=main:addTargetBundleMenu(main)).grid(row=1,column=0,sticky="news")
	main.inputFrame_targetFilesList = ThemedFrame(inputFrame_targetFiles,style="TFrame")	#TODO this also needs a scrollbar!
	main.inputFrame_targetFilesList.grid(row=2,column=0,sticky="news")
	
	inputFrame_targetFiles.rowconfigure(0,weight=0,uniform="fred")
	inputFrame_targetFiles.rowconfigure(1,weight=0,uniform="fred")
	inputFrame_targetFiles.rowconfigure(2,weight=1)
	inputFrame_targetFiles.columnconfigure(0,weight=1)
	
	updateTargetListFrame(main)
	
	# --------------------- main ----------------
	inputFrame_main.rowconfigure(0,weight=1)
	inputFrame_main.columnconfigure(0,weight=1,uniform="fred")
	inputFrame_main.columnconfigure(1,weight=1,uniform="fred")

