
from tkinter import OptionMenu
from tkinter import StringVar
#from tkinter import IntVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
#from tkinter.ttk import Scrollbar as ThemedScrollbar
from tkinter.ttk import Entry as ThemedEntry

from evaluation.siI_eval import loadDataIntoGUI

def updateSIILibPairs(main):
	main.IM.resetLibPairs()
	for pairDesc in main.pairList:
		if pairDesc is None:continue
		_,pair,startVar,endVar,pairLabelVar,select_TPS_var = pairDesc
		selectedTPS = select_TPS_var.get()
		if selectedTPS == "-":continue
		libPos = list(pair[0].keys())
		libNeg = list(pair[1].keys())
		#TODO validate startVar.get() and endVar.get() and also supply them to IM	#re-implement region selection for pairs
		#try:
		#	regionStart = int(startVar.get())
		#except:
		#	main.writeError(f"Region start for {libPos}-{libNeg} needs to be an integer!")
		#	continue
		#try:
		#	regionEnd = int(endVar.get())
		#except:
		#	main.writeError(f"Region end for {libPos}-{libNeg} needs to be an integer!")
		#	continue
		main.IM.addSIIPair(libPos,libNeg,pairLabelVar.get(),main.IM.getTPSTuple(selectedTPS))

def loadData(main,export=True,gui=True):
	updateSIILibPairs(main)
	libPairs = main.IM.getSIIPairs()	#[(libPos,libNeg,label,TPS)]
	#print(f"[siI GUI] LibPairs: {libPairs}")
	main.projectPath =main.PM.get("projectPath")
	return loadDataIntoGUI(main,libPairs,export=export,gui=gui)

def deleteLibIDPair(main,index):
	print(f"[siI GUI] Deleting libID-pair {index}: {main.pairList[index][4].get()}")
	main.pairList[index][0].destroy()
	main.pairList[index]=None

def deleteLibFromPair(libID,pair,isControl):
	pair[isControl][libID].destroy()
	del pair[isControl][libID]

def addLibToPair(main,libID,pair,isControl,parentWidget,libVar=None):
	if not libVar is None:libVar.set("+")
	container = ThemedFrame(parentWidget)
	container.pack(fill="x",anchor="nw")
	#print(f"Adding {libID} to pair!")
	pair[isControl][libID] = container
	#print("Pairlist:\n"+"\n".join([ "\t"+pair[4].get()+"\t"+"\t".join([",".join(sorted(side.keys())) for side in pair[1]])for pair in main.pairList]))
	ThemedLabel(container,text=libID).pack(side="left",fill="x",anchor="nw")
	ThemedButton(container,image=main.xImage,
		command = lambda libID=libID,pair=pair,isControl=isControl:deleteLibFromPair(libID,pair,isControl),style="Exit.TButton").pack(side="right",anchor="ne")

def updatePairLibSelection(main,pair,availableLibIDs,positiveLibsFrame,negativeLibsFrame):
	for isControl in [0,1]:
		for libID in pair[isControl].keys():
			pair[isControl][libID].destroy()
	pair[0] = dict()
	pair[1] = dict()
	for child in positiveLibsFrame.winfo_children():child.destroy()
	for child in negativeLibsFrame.winfo_children():child.destroy()
	if len(availableLibIDs)>0:
		libPosVar = StringVar(value="+")
		#lambda in OptionMenu ovewrites the first arguments, catch with an unused argument (same with bind)
		#the arguments contains the value (.get()) of the OptionMenu's variable
		mm1 = OptionMenu(positiveLibsFrame,libPosVar,*availableLibIDs,command = lambda libID,main=main,pair=pair,positiveLibsFrame=positiveLibsFrame:addLibToPair(main,libID,pair,0,positiveLibsFrame,libVar=libPosVar))
		mm1.pack(fill="x",anchor="nw")
		main.styleman.registredOptionMenuButtons.append(mm1)
		mm1.config(bg=main.styleman.buttonColour,fg=main.styleman.buttonTextColour,font=main.buttonTextFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.buttonHighlightColour)
		mm1["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
		
		libNegVar = StringVar(value="+")
		mm2 = OptionMenu(negativeLibsFrame,libNegVar,*availableLibIDs,command = lambda libID,main=main,pair=pair,negativeLibsFrame=negativeLibsFrame:addLibToPair(main,libID,pair,1,negativeLibsFrame,libVar=libNegVar))
		mm2.pack(fill="x",anchor="nw")
		main.styleman.registredOptionMenuButtons.append(mm2)
		mm2.config(bg=main.styleman.buttonColour,fg=main.styleman.buttonTextColour,font=main.buttonTextFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.buttonHighlightColour)
		mm2["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	
	pass

def addPair(main,pairLoad=None,updateView=True):
	TPSlist = main.IM.getTPSList()
	if len(TPSlist)==0:
		main.writeError("Error, please run the pipeline befor selecting siI pairs.")
		return
	#print(f"[siI GUI] Adding pair: {pairLoad}")
	pairFrame = ThemedFrame(main.pairListFrame)
	main.pairListFrame.pairChildren.append(pairFrame)
	
	pair = [dict(),dict()]
	
	ThemedLabel(pairFrame,text="Label:",style="TLabel").grid(column=0,row=0,columnspan=1,sticky="news",padx=(main.frameBorderSize,0))
	labelVar = StringVar(value="New pairing")
	ThemedEntry(pairFrame,textvariable=labelVar).grid(column=1,row=0,columnspan=1,sticky="ew")
	
	ThemedLabel(pairFrame,text="Enriched:",style="TLabel").grid(column=2,row=0,columnspan=1,sticky="news",padx=main.frameBorderSize*2)
	ThemedLabel(pairFrame,text="Control:").grid(column=3,row=0,columnspan=1,sticky="news",padx=main.frameBorderSize*2)
	
	ThemedLabel(pairFrame,text="Target:",style="TLabel").grid(column=0,row=1,columnspan=1,sticky="news",padx=(main.frameBorderSize,0))
	
	positiveLibsFrame = ThemedFrame(pairFrame,style="TFrame")
	positiveLibsFrame.grid(column=2,row=1,rowspan=2,sticky="new",padx=(main.frameBorderSize*2,main.frameBorderSize))
	negativeLibsFrame = ThemedFrame(pairFrame)
	negativeLibsFrame.grid(column=3,row=1,rowspan=2,sticky="new",padx=(main.frameBorderSize,main.frameBorderSize*2))
	
	select_TPS_var = StringVar(value="-")
	select_TPS = OptionMenu(pairFrame,select_TPS_var,*TPSlist,command = lambda selectedTPS,main=main,pair=pair:updatePairLibSelection(main,pair,main.IM.getTPSLibIDs(selectedTPS),positiveLibsFrame,negativeLibsFrame))
	select_TPS.grid(column=1,row=1,columnspan=1,sticky="news")
	main.styleman.registredOptionMenus.append(select_TPS)
	select_TPS.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	select_TPS["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	ThemedFrame(pairFrame,style="TFrame").grid(column=0,row=2,columnspan=2,sticky="news")
	
	#TODO unused right now
	startVar = StringVar(value="1")	#validate when adding pair ~ and add start-end into IM
	#startVar.set("1")
	#if not start is None:startVar.set(start)	#use pair
	#ThemedEntry(pairFrame,textvariable=startVar,width=main.numberEntryWidth).grid(column=2,row=1,sticky="new")
	endVar = StringVar(value="1000")
	#endVar.set(str(basegui.targetLenVar.get()))	#set target per pairs (implicitely ? or explicitly? )
	#if not end is None:endVar.set(end)
	#ThemedEntry(pairFrame,textvariable=endVar,width=main.numberEntryWidth).grid(column=3,row=1,sticky="new")
	
	ThemedButton(pairFrame,image=main.xImage_small,command = lambda main=main,i = len(main.pairList): deleteLibIDPair(main,i),style="Exit.TButton").grid(column=4,row=0,rowspan=2,sticky="new",padx=(0,main.frameBorderSize*2),pady=main.frameBorderSize*2)
	
	
	pairFrame.rowconfigure(0,weight=0,uniform="fred")
	pairFrame.rowconfigure(1,weight=0,uniform="fred")
	pairFrame.rowconfigure(2,weight=1)
	
	pairFrame.columnconfigure(0,weight=1)
	pairFrame.columnconfigure(1,weight=3)
	pairFrame.columnconfigure(2,weight=4,uniform="fred")
	pairFrame.columnconfigure(3,weight=4,uniform="fred")
	pairFrame.columnconfigure(4,weight=0)
	
	pairFrame.pack(fill="x",side="top",padx=main.frameBorderSize*2,pady=main.frameBorderSize)
	main.pairList.append([pairFrame,pair,startVar,endVar,labelVar,select_TPS_var])	#frame to delete from gui, vars to build graphs; when deleted is set to None
	
	if not pairLoad is None:
		if len(pairLoad)>2:
			labelVar.set(pairLoad[2])
		if len(pairLoad)>3:
			selectedTPS = main.IM.TPSToString(pairLoad[3])
			select_TPS_var.set(selectedTPS)
			updatePairLibSelection(main,pair,main.IM.getTPSLibIDs(selectedTPS),positiveLibsFrame,negativeLibsFrame)
		for isControl in [0,1]:
			for libID in pairLoad[isControl]:
				if not isControl:addLibToPair(main,libID,pair,isControl,positiveLibsFrame)
				else:addLibToPair(main,libID,pair,isControl,negativeLibsFrame)

def add_siI_eval_GUI(main):
	if not "siI" in main.evalTypes:main.evalTypes.append("siI")
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[siI GUI] adding GUI at {notebookIndex}")
	siIEvalFrame = ThemedFrame(main.mainNotebook,style="gBorder.TFrame")
	main.mainNotebook.add(siIEvalFrame,	text="siI eval")
	main.mainNotebooktabs[notebookIndex] = siIEvalFrame
	
	ThemedLabel(siIEvalFrame,text="siRNA candidate identification",anchor="w",style="Header.TLabel"
		).grid(row=0,column=0,columnspan=3,sticky="news",padx=main.frameBorderSize*2,pady=(main.frameBorderSize*2,main.frameBorderSize))
	pairingFrame = ThemedFrame(siIEvalFrame)
	pairingFrame.grid(row=1,column=0,columnspan=3,sticky="news",padx=main.frameBorderSize*2,pady=(main.frameBorderSize,main.frameBorderSize*2))
	
	siIEvalFrame.columnconfigure(0,weight=1,uniform="fred")
	siIEvalFrame.columnconfigure(1,weight=1,uniform="fred")
	siIEvalFrame.columnconfigure(2,weight=1,uniform="fred")
	siIEvalFrame.rowconfigure(0,weight=0)
	siIEvalFrame.rowconfigure(1,weight=1)
	
	# ------------------- Library Pairing -----------------------
	ThemedLabel(pairingFrame,text="Select pairs of libraries",anchor="nw",style="Medium.TLabel").pack(fill="x",anchor="nw")
	main.pairList = list()
	pairingBufferFrame = ThemedFrame(pairingFrame,style="wBorder.TFrame")
	pairingBufferFrame.pack(fill="x",side="top",pady=main.frameBorderSize)
	main.pairListFrame = ThemedFrame(pairingBufferFrame,style="wBorder.TFrame")
	main.pairListFrame.pairChildren = list()
	
	ThemedButton(main.pairListFrame,text="+",command = lambda main=main: 
		addPair(main),style="TButton").pack(fill="x",side="bottom",padx=main.frameBorderSize*2,pady=main.frameBorderSize)
	
	main.pairListFrame.pack(fill="x",side="top",pady=main.frameBorderSize)
	
