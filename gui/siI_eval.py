

from tkinter import OptionMenu
from tkinter import BooleanVar
from tkinter import StringVar
from tkinter import IntVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Scrollbar as ThemedScrollbar
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry

from evaluation.siI_eval import loadDataIntoGUI
from evaluation.dsP_eval import exportGraphs
from graphs.drawGraphics import multiplyColour,isHexColour

def loadData(main,export=True,gui=True):
	
	main.IM.resetLibPairs()
	#main.pairList.append([pairFrame,pair,startVar,endVar])
	for pairDesc in main.pairList:
		if pairDesc is None:continue
		_,pair,startVar,endVar,pairLabelVar = pairDesc
		#pair[isControl][libID] = container
		libPos = list(pair[0].keys())
		libNeg = list(pair[1].keys())
		#TODO validate startVar.get() and endVar.get() and also supply them to IM
		try:
			regionStart = int(startVar.get())
		except:
			main.writeError(f"Region start for {libPos}-{libNeg} needs to be an integer!")
			continue
		try:
			regionEnd = int(endVar.get())
		except:
			main.writeError(f"Region end for {libPos}-{libNeg} needs to be an integer!")
			continue
		main.IM.addSIIPair(libPos,libNeg,label=pairLabelVar.get())
	
	libPairs = main.IM.getSIIPairs()
	print(f"[siI GUI] LibPairs: {libPairs}")
	
	main.projectPath =main.PM.get("projectPath")
	
	return loadDataIntoGUI(main,libPairs,export=export,gui=gui)
	

def deleteLibIDPair(main,index):
	print(f"[siI GUI] Deleting libID-pair {index}: {main.pairList[index][4].get()}")
	main.pairList[index][0].destroy()
	main.pairList[index]=None
	print(main.pairList)

def deleteLibFromPair(libID,pair,isControl):
	pair[isControl][libID].destroy()
	del pair[isControl][libID]

def addLibToPair(main,libID,pair,isControl,parent):	#TODO check that newly added libIDs have the same target!!!
	container = ThemedFrame(parent)
	container.pack(fill="x",anchor="nw")
	pair[isControl][libID] = container
	ThemedLabel(container,text=libID).pack(side="left",fill="x",anchor="nw")
	ThemedButton(container,image=main.xImage,
		command = lambda libID=libID,pair=pair,isControl=isControl:deleteLibFromPair(libID,pair,isControl),style="Exit.TButton").pack(side="right",anchor="ne")

def addPair(main,pairLoad=None,updateView=True):
	#print(f"[siI GUI] Adding pair: {pairLoad}")
	pairFrame = ThemedFrame(main.pairListFrame)
	main.pairListFrame.pairChildren.append(pairFrame)
	#print(main.IM.getLibraries())
	availableLibIDs = [lib.libID for lib in main.IM.getLibraries().values() if "siI" in lib.evalTypes]
	pair = [dict(),dict()]
	#print(availableLibIDs)
	#TODO need a datastructure that contains all pairs, and all libs for each side of a pair
	#list of pairs; list: [positive,negative]; list of libIDs
	#now just need to correctly acces this.... #~or maybe make small classes isntead that contian this stuff??? !!!
	# pairList could be a list of pair classes....
	
	labelVar = StringVar(value="New pairing")
	#ThemedLabel(pairFrame,text="Label").grid(column=0,row=0,sticky="new")
	ThemedEntry(pairFrame,textvariable=labelVar).grid(column=0,row=0,columnspan=5,sticky="new")
	
	positiveLibsFrame = ThemedFrame(pairFrame)
	positiveLibsFrame.grid(column=0,row=1,sticky="new")
	negativeLibsFrame = ThemedFrame(pairFrame)
	negativeLibsFrame.grid(column=1,row=1,sticky="new")
	if len(availableLibIDs)>0:
		libPosVar = StringVar(value="-")
		#lambda in OptionMenu ovewrites the first arguments, catch with an unused argument (same with bind)
		#the arguments contains the value (.get()) of the OptionMenu's variable
		mm1 = OptionMenu(positiveLibsFrame,libPosVar,*availableLibIDs,command = lambda libID,main=main,pair=pair,positiveLibsFrame=positiveLibsFrame:addLibToPair(main,libID,pair,0,positiveLibsFrame))
		mm1.pack(fill="x",anchor="nw")
		main.styleman.registredOptionMenus.append(mm1)
		mm1.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
		mm1["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
		
		libNegVar = StringVar(value="-")
		mm2 = OptionMenu(negativeLibsFrame,libNegVar,*availableLibIDs,command = lambda libID,main=main,pair=pair,negativeLibsFrame=negativeLibsFrame:addLibToPair(main,libID,pair,1,negativeLibsFrame))
		mm2.pack(fill="x",anchor="nw")
		main.styleman.registredOptionMenus.append(mm2)
		mm2.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
		mm2["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	
	#TODO unused right now
	startVar = StringVar(value="1")	#validate when adding pair ~ and add start-end into IM
	#startVar.set("1")
	#if not start is None:startVar.set(start)	#use pair
	#ThemedEntry(pairFrame,textvariable=startVar,width=main.numberEntryWidth).grid(column=2,row=1,sticky="new")
	endVar = StringVar(value="1000")
	#endVar.set(str(basegui.targetLenVar.get()))	#set target per pairs (implicitely ? or explicitly? )
	#if not end is None:endVar.set(end)
	#ThemedEntry(pairFrame,textvariable=endVar,width=main.numberEntryWidth).grid(column=3,row=1,sticky="new")
	
	ThemedButton(pairFrame,image=main.xImage_small,command = lambda main=main,i = len(main.pairList): deleteLibIDPair(main,i),style="Exit.TButton").grid(column=4,row=1,sticky="new")
	
	pairFrame.columnconfigure(0,weight=3,uniform="fred")
	pairFrame.columnconfigure(1,weight=3,uniform="fred")
	pairFrame.columnconfigure(2,weight=1,uniform="fred")
	pairFrame.columnconfigure(3,weight=1,uniform="fred")
	pairFrame.columnconfigure(4,weight=0)
	
	pairFrame.pack(fill="x",side="top",padx=main.frameBorderSize,pady=main.frameBorderSize)
	main.pairList.append([pairFrame,pair,startVar,endVar,labelVar])	#frame to delete from gui, vars to build graphs; when deleted is set to None
	
	if not pairLoad is None:
		for isControl in [0,1]:
			for libID in pairLoad[isControl]:
				if not isControl:addLibToPair(main,libID,pair,isControl,positiveLibsFrame)
				else:addLibToPair(main,libID,pair,isControl,negativeLibsFrame)
		if len(pairLoad)>2:
			labelVar.set(pairLoad[2])

def add_siI_eval_GUI(main):
	if not "siI" in main.evalTypes:main.evalTypes.append("siI")
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[siI GUI] adding GUI at {notebookIndex}")
	siIEvalFrame = ThemedFrame(main.mainNotebook)
	main.mainNotebook.add(siIEvalFrame,	text="siI eval")
	main.mainNotebooktabs[notebookIndex] = siIEvalFrame
	
	ThemedLabel(siIEvalFrame,text="Generate graphics",anchor="w",style="Medium.TLabel").grid(row=0,column=0,columnspan=3,sticky="news")
	outputFoldOutFrame1 = ThemedFrame(siIEvalFrame)
	outputFoldOutFrame1.grid(row=1,column=0,sticky="news")
	outputFoldOutFrame2 = ThemedFrame(siIEvalFrame)
	outputFoldOutFrame2.grid(row=1,column=1,sticky="news")
	outputFoldOutFrame3 = ThemedFrame(siIEvalFrame)
	outputFoldOutFrame3.grid(row=1,column=2,sticky="news")
	
	siIEvalFrame.columnconfigure(0,weight=1,uniform="fred")
	siIEvalFrame.columnconfigure(1,weight=1,uniform="fred")
	siIEvalFrame.columnconfigure(2,weight=1,uniform="fred")
	siIEvalFrame.rowconfigure(0,weight=0)
	siIEvalFrame.rowconfigure(1,weight=1)
	siIEvalFrame.rowconfigure(2,weight=0)
	siIEvalFrame.rowconfigure(3,weight=0)
	
	ThemedLabel(siIEvalFrame,text="siRNA identification",anchor="w").grid(row=0,column=0,columnspan=3,sticky="news")
	
	# ------------------- Library Pairing -----------------------
	ThemedLabel(outputFoldOutFrame2,text="Select pairs of libraries",anchor="nw").pack(fill="x",anchor="nw")
	main.pairList = list()
	main.pairListFrame = ThemedFrame(outputFoldOutFrame2,style="wBorder.TFrame")
	main.pairListFrame.pairChildren = list()
	
	pairDescFrame = ThemedFrame(main.pairListFrame)
	ThemedLabel(pairDescFrame,text="Enriched esiRNAs").grid(column=0,row=0,sticky="ew")
	ThemedLabel(pairDescFrame,text="Control").grid(column=1,row=0,sticky="ew")
	ThemedLabel(pairDescFrame,text="Start",anchor="w").grid(column=2,row=0,sticky="ew")
	ThemedLabel(pairDescFrame,text="End",anchor="w").grid(column=3,row=0,sticky="ew")
	ThemedButton(pairDescFrame,image=main.emptyImage,style="bg.TButton").grid(column=4,row=0,sticky="e")
	
	pairDescFrame.columnconfigure(0,weight=3,uniform="fred")
	pairDescFrame.columnconfigure(1,weight=3,uniform="fred")
	pairDescFrame.columnconfigure(2,weight=1,uniform="fred")
	pairDescFrame.columnconfigure(3,weight=1,uniform="fred")
	pairDescFrame.columnconfigure(4,weight=0)
	pairDescFrame.pack(fill="x",side="top",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	ThemedButton(main.pairListFrame,text="+",command = lambda main=main: 
		addPair(main),style="bg.TButton").pack(fill="x",side="bottom",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	main.pairListFrame.pack(fill="x",side="top",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	#ThemedButton(siIEvalFrame,text="Load data",command=lambda main=main,export = False: loadData(main,export=export)).grid(row=2,column=0,columnspan=3,sticky="news")
	#ThemedButton(siIEvalFrame,text="Export graphs",command=lambda main=main:exportGraphs(main)).grid(row=3,column=0,columnspan=3,sticky="news")
	
	
