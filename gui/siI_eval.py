
from tkinter import OptionMenu
from tkinter import StringVar
#from tkinter import IntVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Radiobutton as ThemedRadioButton

from evaluation.siI_eval import loadDataIntoGUI
from gui.ScrollableFrame import ScrollableFrame

def updateSIILibPairs(main):
	main.IM.resetLibPairs()
	for pairDesc in main.pairList:
		if pairDesc is None:continue
		_,pair,startVar,endVar,pairLabelVar,select_TPS_var = pairDesc
		selectedTPS = select_TPS_var.get()
		if selectedTPS == "-":continue
		libPos = list(pair[0].keys())
		libNeg = list(pair[1].keys())
		
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
		
		main.IM.addSIIPair(libPos,libNeg,pairLabelVar.get(),main.IM.getTPSTuple(selectedTPS),regionStart,regionEnd)

def loadData(main,export=True,gui=True):
	updateSIILibPairs(main)
	libPairs = main.IM.getSIIPairs()	#[(libPos,libNeg,label,TPS)]
	#print(f"[siI GUI] LibPairs: {libPairs}")
	#main.PM.get("siI-siRNAlength")
	#main.PM.get("siI-strand")
	params = main.PM.getDict(tag="siI")
	print(f"\n{params}\n")
	return loadDataIntoGUI(main,libPairs,params,export=export,gui=gui)

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

def updatePairLibSelection(main,pair,selectedTPS,positiveLibsFrame,negativeLibsFrame,startVar,endVar):
	if not main.IM.hasTPS(selectedTPS):return
	availableLibIDs = main.IM.getTPSLibIDs(selectedTPS)
	startVar.set(1)
	endVar.set(main.IM.getTarget(main.IM.getTPSTuple(selectedTPS)[0]).mainLength)
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

def addPair(main,pairLoad=None,updateView=True):
	TPSlist = main.IM.getTPSList()
	if len(TPSlist)==0:
		main.writeError("Error, please run the pipeline befor selecting siI pairs.")
		return
	#print(f"[siI GUI] Adding pair: {pairLoad}")
	pairFrameBase = ThemedFrame(main.pairListFrame,style="wBorder.TFrame")
	main.pairListFrame.pairChildren.append(pairFrameBase)
	pairFrameBase.pack(fill="x",side="top",padx=main.frameBorderSize,pady=(main.frameBorderSize,0))
	
	pairFrame = ThemedFrame(pairFrameBase)
	pairFrame.pack(fill="x",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	pair = [dict(),dict()]
	
	ThemedLabel(pairFrame,text="Label:",style="TLabel").grid(column=0,row=0,columnspan=1,sticky="news",padx=(main.frameBorderSize,0))
	labelVar = StringVar(value="New pairing")
	ThemedEntry(pairFrame,textvariable=labelVar).grid(column=1,row=0,columnspan=1,sticky="ew")
	
	ThemedLabel(pairFrame,text="Enriched:",style="TLabel").grid(column=2,row=0,columnspan=1,sticky="news",padx=main.frameBorderSize*2)
	ThemedLabel(pairFrame,text="Control:").grid(column=3,row=0,columnspan=1,sticky="news",padx=main.frameBorderSize*2)
	
	ThemedLabel(pairFrame,text="Target:",style="TLabel").grid(column=0,row=1,columnspan=1,sticky="news",padx=(main.frameBorderSize,0))
	
	positiveLibsFrame = ThemedFrame(pairFrame,style="TFrame")
	positiveLibsFrame.grid(column=2,row=1,rowspan=4,sticky="new",padx=(main.frameBorderSize*2,main.frameBorderSize))
	negativeLibsFrame = ThemedFrame(pairFrame)
	negativeLibsFrame.grid(column=3,row=1,rowspan=4,sticky="new",padx=(main.frameBorderSize,main.frameBorderSize*2))
	
	startVar = StringVar(value="-")
	endVar = StringVar(value="-")
	
	select_TPS_var = StringVar(value="-")
	select_TPS = OptionMenu(pairFrame,select_TPS_var,*TPSlist,command = lambda selectedTPS,main=main,pair=pair,startVar=startVar,endVar=endVar:
		updatePairLibSelection(main,pair,selectedTPS,positiveLibsFrame,negativeLibsFrame,startVar,endVar))
	select_TPS.grid(column=1,row=1,columnspan=1,sticky="news")
	main.styleman.registredOptionMenus.append(select_TPS)
	select_TPS.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	select_TPS["menu"].config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.logFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	
	ThemedLabel(pairFrame,text="Region-start:",style="TLabel").grid(column=0,row=2,sticky="news",padx=(main.frameBorderSize,0))
	ThemedEntry(pairFrame,textvariable=startVar,width=10).grid(column=1,row=2,sticky="w")
	ThemedLabel(pairFrame,text="Region-end:",style="TLabel").grid(column=0,row=3,sticky="news",padx=(main.frameBorderSize,0))
	ThemedEntry(pairFrame,textvariable=endVar,width=10).grid(column=1,row=3,sticky="w")
	ThemedFrame(pairFrame,style="TFrame").grid(column=0,row=4,columnspan=2,sticky="news")
	
	ThemedButton(pairFrame,image=main.xImage_small,command = lambda main=main,i = len(main.pairList): deleteLibIDPair(main,i),style="Exit.TButton").grid(column=4,row=0,rowspan=2,sticky="new",padx=(0,main.frameBorderSize*2),pady=main.frameBorderSize*2)
	
	
	pairFrame.rowconfigure(0,weight=0,uniform="fred")
	pairFrame.rowconfigure(1,weight=0,uniform="fred")
	pairFrame.rowconfigure(2,weight=0,uniform="fred")
	pairFrame.rowconfigure(3,weight=0,uniform="fred")
	pairFrame.rowconfigure(4,weight=1)
	
	pairFrame.columnconfigure(0,weight=1)
	pairFrame.columnconfigure(1,weight=3)
	pairFrame.columnconfigure(2,weight=4,uniform="fred")
	pairFrame.columnconfigure(3,weight=4,uniform="fred")
	pairFrame.columnconfigure(4,weight=0)
	
	main.pairList.append([pairFrameBase,pair,startVar,endVar,labelVar,select_TPS_var])	#frame to delete from gui, vars to build graphs; when deleted is set to None
	
	if not pairLoad is None:
		if len(pairLoad)>2:
			labelVar.set(pairLoad[2])
		if len(pairLoad)>3:
			selectedTPS = main.IM.TPSToString(pairLoad[3])
			select_TPS_var.set(selectedTPS)
			updatePairLibSelection(main,pair,selectedTPS,positiveLibsFrame,negativeLibsFrame,startVar,endVar)
		if len(pairLoad)>4:	#(libPos,libNeg,label,TPS,regionStart,regionEnd)
			if pairLoad[4]!= "-": startVar.set(int(pairLoad[4]))
			if pairLoad[5]!= "-": endVar.set(int(pairLoad[5]))
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
		).grid(row=0,column=0,columnspan=2,sticky="news",padx=main.frameBorderSize*2,pady=(main.frameBorderSize*2,main.frameBorderSize))
	
	siIEvalFrame.columnconfigure(0,weight=0)
	siIEvalFrame.columnconfigure(1,weight=1)
	siIEvalFrame.rowconfigure(0,weight=0)
	siIEvalFrame.rowconfigure(1,weight=1)
	
	# ------------------- siI settings -----------------------
	settingsFrame = ThemedFrame(siIEvalFrame)
	settingsFrame.grid(row=1,column=0,columnspan=1,sticky="news",padx=(main.frameBorderSize*2,0),pady=(main.frameBorderSize,main.frameBorderSize*2))
	settingsFrame.columnconfigure(0,weight=1,uniform="fred")
	settingsFrame.columnconfigure(1,weight=1,uniform="fred")
	settingsFrame.columnconfigure(2,weight=1,uniform="fred")
	settingsFrame.rowconfigure(0,weight=0)
	settingsFrame.rowconfigure(1,weight=0,uniform="fred")
	settingsFrame.rowconfigure(2,weight=0,uniform="fred")
	settingsFrame.rowconfigure(3,weight=0,uniform="fred")
	ThemedLabel(settingsFrame,text="Settings",anchor="nw",style="Medium.TLabel").grid(row=0,column=0,columnspan=2,sticky="news")
	
	ThemedLabel(settingsFrame,text="siRNA length:",anchor="w").grid(column=0,row=1,columnspan=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(settingsFrame,textvariable=main.PM.add("siI-siRNAlength","int",21,
		"siRNA length needs to be an integer!","Length of reads to analyse",tag="siI"),width=6).grid(column=2,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(settingsFrame,text="Strand:",anchor="w").grid(column=0,row=2,columnspan=3,sticky="w",padx=main.frameBorderSize)
	strandVar = main.PM.add("siI-strand","text","reverse","siRNA length needs to be an integer!","Length of reads to analyse",tag="siI")
	ThemedRadioButton(settingsFrame,text="Forward",variable=strandVar,value="forward").grid(column=0,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedRadioButton(settingsFrame,text="Reverse",variable=strandVar,value="reverse").grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedRadioButton(settingsFrame,text="Both",variable=strandVar,value="both",state="disabled").grid(column=2,row=3,sticky="ew",padx=main.frameBorderSize)
	
	# ------------------- Library Pairing -----------------------
	pairingFrame = ThemedFrame(siIEvalFrame)
	pairingFrame.grid(row=1,column=1,sticky="news",padx=main.frameBorderSize*2,pady=(main.frameBorderSize,main.frameBorderSize*2))
	ThemedLabel(pairingFrame,text="Select pairs of libraries",anchor="nw",style="Medium.TLabel").pack(fill="x",anchor="nw")
	main.pairList = list()
	
	pairListFrameBase = ScrollableFrame(pairingFrame,style="TFrame")
	pairListFrameBase.pack(fill="both",side="top",pady=main.frameBorderSize,expand=True)
	main.pairListFrame = pairListFrameBase.getInnerFrame()
	pairListFrameBase.setCanvasBG(main.styleman.backgroundColour)
	main.styleman.registredBG.append(pairListFrameBase)
	
	main.pairListFrame.pairChildren = list()
	
	ThemedButton(main.pairListFrame,text="+",command = lambda main=main: 
		addPair(main),style="TButton").pack(fill="x",side="bottom",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
