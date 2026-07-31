
from tkinter import OptionMenu	#
from tkinter import StringVar	#
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Radiobutton as ThemedRadioButton

from ..siI_evaluation import loadDataIntoGUI
from gui.ScrollableFrame import ScrollableFrame
from .siIPair import siIPair

def getLibraryPairsFromGUI(main):
	siI_Pairs_data = list()
	for pair in main.siI_pairList:
		if pair is None:continue	#skip deleted pairs
		data = pair.getData()
		if data is None:
			main.writeError("Error while getting data from pair {pair.pairID}",terminalPrefix="[siI module][ERROR]")
			continue
		else:
			siI_Pairs_data.append(data)
	return siI_Pairs_data

def loadData(main,export=True,gui=True):
	libPairs = getLibraryPairsFromGUI(main)
	params = main.PM.getDict(tag="siI-general")
	return loadDataIntoGUI(main,libPairs,params,export=export,gui=gui)

def resetPairs(main):
	for pair in main.siI_pairList:
		if pair is None:
			print("None")
			continue
		pair._deleteYourself()
	main.siI_pairList = list()

def addPair(main,pairLoad=None,updateView=True):
	TPSlist = main.IM.getTPSList()
	if len(TPSlist)==0:
		main.writeError("Cannot add siI pairs until the pipeline has finished!")
		return
	pair = siIPair(main,main.siI_pairListFrame,pairID=len(main.siI_pairList))
	main.siI_pairList.append(pair)
	
	if not pairLoad is None:pair.loadPair(pairLoad)

def add_siIGUI(main):	#add_siI_eval_GUI
	if not "siI" in main.evalTypes:main.evalTypes.append("siI")
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[siI GUI] adding GUI at {notebookIndex}")
	siIEvalFrame = ThemedFrame(main.mainNotebook,style="gBorder.TFrame")
	main.mainNotebook.add(siIEvalFrame, text="siI eval")
	main.mainNotebooktabs[notebookIndex] = siIEvalFrame
	
	
	main.siI_Pairs_data = list()
	
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
		"siRNA length needs to be an integer!","Length of reads to analyse",tag="siI-general"),width=6).grid(column=2,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(settingsFrame,text="Strand:",anchor="w").grid(column=0,row=2,columnspan=3,sticky="w",padx=main.frameBorderSize)
	strandVar = main.PM.add("siI-strand","text","reverse","siRNA length needs to be an integer!","Length of reads to analyse",tag="siI-general")
	ThemedRadioButton(settingsFrame,text="Forward",variable=strandVar,value="forward").grid(column=0,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedRadioButton(settingsFrame,text="Reverse",variable=strandVar,value="reverse").grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedRadioButton(settingsFrame,text="Both",variable=strandVar,value="both",state="disabled").grid(column=2,row=3,sticky="ew",padx=main.frameBorderSize)
	
	# ------------------- Library Pairing -----------------------
	pairingFrame = ThemedFrame(siIEvalFrame)
	pairingFrame.grid(row=1,column=1,sticky="news",padx=main.frameBorderSize*2,pady=(main.frameBorderSize,main.frameBorderSize*2))
	ThemedLabel(pairingFrame,text="Select pairs of libraries",anchor="nw",style="Medium.TLabel").pack(fill="x",anchor="nw")
	main.siI_pairList = list()
	
	pairListFrameBase = ScrollableFrame(pairingFrame,style="TFrame")
	pairListFrameBase.pack(fill="both",side="top",pady=main.frameBorderSize,expand=True)
	pairListFrameBase.setCanvasBG(main.styleman.backgroundColour)
	main.styleman.registredBG.append(pairListFrameBase)
	main.siI_pairListFrame = pairListFrameBase.getInnerFrame()
	
	#TODO disable this button and add disclaimer "No libraries available, run the pipeline" when no TPS are available!
	#TODO need callback from sRP for that ?!?
	ThemedButton(main.siI_pairListFrame,text="+",command = lambda main=main: 
		addPair(main),style="TButton").pack(fill="x",side="bottom",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
