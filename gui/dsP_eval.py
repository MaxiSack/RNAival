
from tkinter import BooleanVar
from tkinter import StringVar
from tkinter import IntVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry
from gui.functions import *
from evaluation.dsP_eval import loadDataIntoGUI,exportGraphs
from graphs.drawGraphics import multiplyColour,isHexColour


def getColours(main):	# ------------------ colours ------------------------
	esiGSC=main.PM.get("esiGSCVar")
	esiPSC=main.PM.get("esiPSCVar")
	pseudoGSC=main.PM.get("pseudoGSCVar")
	pseudoPSC=main.PM.get("pseudoPSCVar")
		
	if not isHexColour(esiGSC):
		main.writeError("ERROR esiGS is not a valid Hex-Colour")
		return False
	if not isHexColour(esiPSC):
		main.writeError("ERROR esiPS is not a valid Hex-Colour")
		return False
	if not isHexColour(pseudoGSC):
		main.writeError("ERROR pseudoGS is not a valid Hex-Colour")
		return False
	if not isHexColour(pseudoPSC):
		main.writeError("ERROR pseudoPS is not a valid Hex-Colour")
		return False
	
	highlightStyles = dict()
	highlightStyles["esiGS"]=(esiGSC,multiplyColour(0.7,esiGSC),1)
	highlightStyles["esiPS"]=(esiPSC,multiplyColour(0.7,esiPSC),1)
	highlightStyles["pseudoGS"]=(pseudoGSC,multiplyColour(0.7,pseudoGSC),1)
	highlightStyles["pseudoPS"]=(pseudoPSC,multiplyColour(0.7,pseudoPSC),1)
	return highlightStyles

def getWantedgraphs(main):
	
	#Graphs to generate, "Esi" graphs highlight the esiRNAs using the annotations
	wantedgraphs = list()
	
	# ------------------ colours ------------------------
	highlightStyles = getColours(main)
	
	hideLL = main.PM.get("hideLabelsLegends")
	
	# ------------------- length distribution -------------------
	if main.selectedDSPGraphTypes["graphLenDistID"].get():
		graphDef=dict()
		graphDef[0]="lendist"
		graphDef["minL"] = int(main.PM.get("lenDistMinLen"))
		graphDef["maxL"] = int(main.PM.get("lenDistMaxLen"))
		graphDef["xlab"] = main.PM.get("lenDistXLab")
		graphDef["ylab"] = main.PM.get("lenDistYLab")
		graphDef["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0]]	#TODO replace! ?
		graphDef["percent"] = False
		wantedgraphs.append(graphDef)
		
		if False:	#Also make percent	#TODO add parameter for this!
			graphDef2=dict()
			graphDef2[0]="lendist"
			graphDef2["minL"] = int(main.PM.get("lenDistMinLen"))
			graphDef2["maxL"] = int(main.PM.get("lenDistMaxLen"))
			graphDef2["xlab"] = main.PM.get("lenDistXLab")
			graphDef2["ylab"] = main.PM.get("lenDistYLabPercent")
			graphDef2["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0]]
			graphDef2["percent"] = True
			wantedgraphs.append(graphDef2)		#This does work
	
	#TODO save with different names depending on params??
	
	# ------------------- esiRNA counts -------------------
	if main.selectedDSPGraphTypes["esiCountGraphID"].get():
		graphDef=dict()
		graphDef[0]="esiCounts"
		graphDef["xlabSpace"] = int(main.PM.get("esiCountXLabSpace"))
		graphDef["xlab"] = main.PM.get("esiCountXLab")
		graphDef["ylab"] = main.PM.get("esiCountYLab")
		graphDef["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0],highlightStyles["pseudoGS"][0],highlightStyles["pseudoPS"][0]]
		graphDef["percent"] = False
		wantedgraphs.append(graphDef)
		
		if False:	#Also make percent
			graphDef2=dict()
			graphDef2[0]="esiCounts"
			graphDef2["xlabSpace"] = int(main.PM.get("esiCountXLabSpace"))
			graphDef2["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0],highlightStyles["pseudoGS"][0],highlightStyles["pseudoPS"][0]]
			graphDef2["xlab"] = main.PM.get("esiCountXLab")
			graphDef2["ylab"] = main.PM.get("esiCountYLabPercent")
			graphDef2["percent"] = True
			wantedgraphs.append(graphDef2)
	
	# ------------------- single-length startPos -------------------
	if main.selectedDSPGraphTypes["graphStartLengthID"].get():
		for lenStr in main.PM.get("startPosLengths"):
			graphDef=dict()
			graphDef[0]="countsSingle"
			graphDef["xlab"] = main.PM.get("startPosXLab")
			graphDef["ylab"] = main.PM.get("startPosYLab")
			graphDef["targetlen"] = lenStr
			graphDef["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0],highlightStyles["pseudoGS"][0],highlightStyles["pseudoPS"][0]]
			graphDef["percent"] = False
			wantedgraphs.append(graphDef)
			if False:	#Also make percent
				graphDef2=dict()
				graphDef2[0]="countsSingle"
				graphDef2["xlab"] = main.PM.get("startPosXLab")
				graphDef2["targetlen"] = lenStr
				graphDef2["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0],highlightStyles["pseudoGS"][0],highlightStyles["pseudoPS"][0]]
				graphDef2["ylab"] = main.PM.get("startPosYLabPercent")
				graphDef2["percent"] = True
				wantedgraphs.append(graphDef2)
	
	# ------------------- single-length Coverage -------------------
	if main.selectedDSPGraphTypes["graphCoverageLenID"].get():
		for lenStr in main.PM.get("lencovLengths"):	#For coverage the highlighting "just works" because i also check the lengths
			graphDef=dict()
			graphDef[0]="coverageSingleEsi"
			graphDef["xlab"] = main.PM.get("lencovXLab")
			graphDef["ylab"] = main.PM.get("lencovYLab")
			graphDef["targetlen"] = lenStr
			graphDef["cols"] = [highlightStyles["esiGS"][0],highlightStyles["esiPS"][0],highlightStyles["pseudoGS"][0],highlightStyles["pseudoPS"][0]]
			wantedgraphs.append(graphDef)
			
	if main.selectedDSPGraphTypes["graphCoverageMultiID"].get():
		targetlist = list()
		for i,pair in enumerate(main.multiCovColpairList):
			if pair is None:continue
			targetlist.append((int(pair[1].get()),pair[2].get()))
		if len(targetlist)>0:
			graphDef=dict()
			graphDef[0]="coverageMulti"
			graphDef["xlab"] = main.PM.get("multicovXLab")
			graphDef["ylab"] = main.PM.get("multicovYLab")
			graphDef["targets"] = targetlist
			wantedgraphs.append(graphDef)
	
	# ------------------- Coverage all lengths -------------------
	if False:	#not used anymore, we have multi-line coverage graph
		graphDef=dict()
		graphDef[0]="coverageAll"
		graphDef["xlab"] = "position"
		graphDef["ylab"] = "coverage"
		wantedgraphs.append(graphDef)
		
	# ------------------- Heatmap -------------------
	if main.selectedDSPGraphTypes["graphHeatmapID"].get():
		graphDef=dict()
		graphDef[0]="heapmapEsi"
		graphDef["highlightEsis"] = main.PM.get("heatmapHighlightEsiRNABool")
		graphDef["highlightFrames"] = list()
		graphDef["highlightFrames"] = main.PM.get("heatmapHighlightFrames")
		graphDef["minLen"] = int(main.PM.get("heatmapMinLen"))
		graphDef["maxLen"] = int(main.PM.get("heatmapMaxLen"))
		graphDef["middlePercentile"] = int(main.PM.get("heatmapMiddlePercentile"))
		graphDef["xlab"] = main.PM.get("heatXLab")
		graphDef["ylab"] = main.PM.get("heatYLab")
		wantedgraphs.append(graphDef)
	
	if hideLL:	#hide all Labels and Legends ... by deleting them
		for graphDef in wantedgraphs:
			graphDef["xlab"] = None
			graphDef["ylab"] = None
			graphDef["hideLegend"] = True
	
	return wantedgraphs

def loadData(main,export=True,gui=True):
	# ------------------- Graph definition -------------------
	wantedgraphs = getWantedgraphs(main)
	if not wantedgraphs: 
		main.writeError("Error with graph definitions!")
		return False
	print("[siGUI Debug] wanted graphs:\n"+str("\n".join(["\t"+str(graph) for graph in wantedgraphs])))
	
	
	# ------------------- Library Selection -----------------------
	selectedLibIDs = [libID for libID,lib in main.IM.getLibraries().items() if "dsP" in lib.evalTypes]
	print(f"Selected Libraries:\n{selectedLibIDs}")
	
	highlightStyles=getColours(main)
	main.projectPath =main.PM.get("projectPath")
	return loadDataIntoGUI(main,wantedgraphs,selectedLibIDs,export=export,highlightStyles=highlightStyles,gui=gui)

def add_dsP_eval_GUI(main):
	if not "dsP" in main.evalTypes:main.evalTypes.append("dsP")
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[dsP eval] adding GUI at {notebookIndex}")
	dsPEvalFrame = ThemedFrame(main.mainNotebook)
	main.mainNotebook.add(dsPEvalFrame,	text="dsP eval")
	main.mainNotebooktabs[notebookIndex] = dsPEvalFrame
	
	ThemedLabel(dsPEvalFrame,text="Step 5: Generate graphics",anchor="w",style="Medium.TLabel").grid(row=0,column=0,columnspan=3,sticky="news")
	outputFoldOutFrame1 = ThemedFrame(dsPEvalFrame)
	outputFoldOutFrame1.grid(row=1,column=0,sticky="news")
	outputFoldOutFrame2 = ThemedFrame(dsPEvalFrame)
	outputFoldOutFrame2.grid(row=1,column=1,sticky="news")
	outputFoldOutFrame3 = ThemedFrame(dsPEvalFrame)
	outputFoldOutFrame3.grid(row=1,column=2,sticky="news")
	
	dsPEvalFrame.columnconfigure(0,weight=1,uniform="fred")
	dsPEvalFrame.columnconfigure(1,weight=1,uniform="fred")
	dsPEvalFrame.columnconfigure(2,weight=1,uniform="fred")
	dsPEvalFrame.rowconfigure(0,weight=0)
	dsPEvalFrame.rowconfigure(1,weight=1)
	dsPEvalFrame.rowconfigure(2,weight=0)
	dsPEvalFrame.rowconfigure(3,weight=0)
	
	ThemedLabel(dsPEvalFrame,text="Select types of graphs to generate",anchor="w").grid(row=0,column=0,columnspan=3,sticky="news")
	
	main.selectedDSPGraphTypes = dict()
	# also save which graphs and libraries have been selected!
	
	
	# ------------------- Library-Result Selection -----------------------
	#just load all that have this evaltype
	#TODO add better selection with LibID-PS-Target
	#libSelectionFrame = ThemedFrame(outputFoldOutFrame1)
	#libSelectionFrame.pack(fill="both")
	
	# ------------------- length distribution -------------------
	lcountTotalFrame,lcountOptionsFrame,main.selectedDSPGraphTypes["graphLenDistID"] = makeParameterToggleFrame(main,outputFoldOutFrame1,"Length distribution")
	lcountTotalFrame.pack(fill="both")
	
	ThemedLabel(lcountOptionsFrame,text="Minimum length",anchor="w").grid(column=0,row=0,sticky="w")
	ThemedEntry(lcountOptionsFrame,textvariable=addGraphicVar(main,"lenDistMinLen",StringVar(),"int",15,
		"Minimum length needs to be an integer!","Minimum length of reads to display")).grid(column=1,row=0,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="Maximum length",anchor="w").grid(column=0,row=1,sticky="w")
	ThemedEntry(lcountOptionsFrame,textvariable=addGraphicVar(main,"lenDistMaxLen",StringVar(),"int",30,
		"Maximum length needs to be an integer!","Maximum length of reads to display")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="X-label",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(lcountOptionsFrame,textvariable=addGraphicVar(main,"lenDistXLab",StringVar(),"text","Read length (nt)",
		"Free Text","X-Label")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="Y-label abundance",anchor="w").grid(column=0,row=3,sticky="w")
	ThemedEntry(lcountOptionsFrame,textvariable=addGraphicVar(main,"lenDistYLab",StringVar(),"text","Abundance",
		"Free Text","Y-Label for abundance")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="Y-label percent",anchor="w").grid(column=0,row=3,sticky="w")
	ThemedEntry(lcountOptionsFrame,textvariable=addGraphicVar(main,"lenDistYLabPercent",StringVar(),"text","Percent",
		"Free Text","Y-Label for percent")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	
	lcountOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	lcountOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	lcountOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	lcountOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	lcountOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	lcountOptionsFrame.rowconfigure(3,weight=1,uniform="fred")
	
	# ------------------- esiRNA counts -------------------
	esiCountGraphTotalFrame,esiCountGraphOptionsFrame,main.selectedDSPGraphTypes["esiCountGraphID"] = makeParameterToggleFrame(main,outputFoldOutFrame1,"Abundance of esiRNAs")
	esiCountGraphTotalFrame.pack(fill="both")
	ThemedLabel(esiCountGraphOptionsFrame,text="X-label extra space",anchor="w").grid(column=0,row=0,sticky="w")
	ThemedEntry(esiCountGraphOptionsFrame,textvariable=addGraphicVar(main,"esiCountXLabSpace",StringVar(),"int",100,
		"esiCountXLabSpace to be an integer!","Extra space for the x-axis labels")).grid(column=1,row=0,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="X-label",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(lcountOptionsFrame,textvariable=addGraphicVar(main,"esiCountXLab",StringVar(),"text","esiRNAs",
		"Free Text","X-Label")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(esiCountGraphOptionsFrame,text="Y-label abundance",anchor="w").grid(column=0,row=1,sticky="w")
	ThemedEntry(esiCountGraphOptionsFrame,textvariable=addGraphicVar(main,"esiCountYLab",StringVar(),"text","Abundance",
		"Free Text","Y-Label for Abundance")).grid(column=1,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(esiCountGraphOptionsFrame,text="Y-label percent",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(esiCountGraphOptionsFrame,textvariable=addGraphicVar(main,"esiCountYLabPercent",StringVar(),"text","Percent",
		"Free Text","Y-Label for percent")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	
	esiCountGraphOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	esiCountGraphOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	esiCountGraphOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	esiCountGraphOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	esiCountGraphOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	
	
	# ------------------- single-length startPos -------------------
	startPosTotalFrame,startPosOptionsFrame,main.selectedDSPGraphTypes["graphStartLengthID"] = makeParameterToggleFrame(main,outputFoldOutFrame2,"Read distribution for specific length")
	startPosTotalFrame.pack(fill="both")
	startPosHighlightEsiRNABool = BooleanVar()
	startPosHighlightEsiRNABool.set(True)
	ThemedLabel(startPosOptionsFrame,text="Highlight esiRNAs (Always on)",anchor="w").grid(column=0,row=0,sticky="w")#TODO ?????
	createTogglebutton(main,startPosOptionsFrame,startPosHighlightEsiRNABool).grid(column=1,row=0,sticky="e")
	ThemedLabel(startPosOptionsFrame,text="Lengths",anchor="w").grid(column=0,row=1,columnspan=2,sticky="w")
	ThemedEntry(startPosOptionsFrame,textvariable=addGraphicVar(main,"startPosLengths",StringVar(),"intList","21",
		"Startpos-lengths needs to be a comma separeted list of to be integers!","Comma separated list of lengths to dispaly")).grid(
			column=1,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(startPosOptionsFrame,text="X-label",anchor="w").grid(column=0,row=2,columnspan=2,sticky="w")
	ThemedEntry(startPosOptionsFrame,textvariable=addGraphicVar(main,"startPosXLab",StringVar(),"text","5\'position",
		"Free Text","X-Label")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(startPosOptionsFrame,text="Y-label abundance",anchor="w").grid(column=0,row=3,columnspan=2,sticky="w")
	ThemedEntry(startPosOptionsFrame,textvariable=addGraphicVar(main,"startPosYLab",StringVar(),"text","Abundance",
		"Free Text","Y-Label for Abundance")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(startPosOptionsFrame,text="Y-label percent",anchor="w").grid(column=0,row=4,columnspan=2,sticky="w")
	ThemedEntry(startPosOptionsFrame,textvariable=addGraphicVar(main,"startPosYLabPercent",StringVar(),"text","Percent",
		"Free Text","Y-Label for percent")).grid(column=1,row=4,sticky="ew",padx=main.frameBorderSize)
	
	startPosOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	startPosOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	startPosOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	startPosOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	startPosOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	startPosOptionsFrame.rowconfigure(3,weight=1,uniform="fred")
	startPosOptionsFrame.rowconfigure(4,weight=1,uniform="fred")
	
	
	# ------------------- single-length Coverage -------------------
	coverageLenTotalFrame,coverageLenOptionsFrame,main.selectedDSPGraphTypes["graphCoverageLenID"] = makeParameterToggleFrame(main,outputFoldOutFrame2,"Coverage for individual lengths")
	coverageLenTotalFrame.pack(fill="both")
	ThemedLabel(coverageLenOptionsFrame,text="Highlight esiRNAs",anchor="w").grid(column=0,row=0,sticky="w")#TODO ?????
	createTogglebutton(main,coverageLenOptionsFrame,addGraphicVar(main,"lenCovHighlightEsiRNABool",BooleanVar(),"bool",True,
		"","")).grid(column=1,row=0,sticky="e")
	ThemedLabel(coverageLenOptionsFrame,text="Lengths",anchor="w").grid(column=0,row=1,columnspan=2,sticky="w")
	ThemedEntry(coverageLenOptionsFrame,textvariable=addGraphicVar(main,"lencovLengths",StringVar(),"intList","21",
		"Coverage-lengths needs to be a comma separeted list of to be integers!","Comma separated list of lengths to dispaly")).grid(
			column=1,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(coverageLenOptionsFrame,text="X-label",anchor="w").grid(column=0,row=2,columnspan=2,sticky="w")
	ThemedEntry(coverageLenOptionsFrame,textvariable=addGraphicVar(main,"lencovXLab",StringVar(),"text","Position",
		"Free Text","X-Label")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(coverageLenOptionsFrame,text="Y-label",anchor="w").grid(column=0,row=3,columnspan=2,sticky="w")
	ThemedEntry(coverageLenOptionsFrame,textvariable=addGraphicVar(main,"lencovYLab",StringVar(),"text","Coverage",
		"Free Text","Y-Label")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	
	coverageLenOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	coverageLenOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	coverageLenOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	coverageLenOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	coverageLenOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	coverageLenOptionsFrame.rowconfigure(3,weight=1,uniform="fred")
	
	# ------------------- multi-length Coverage -------------------
	coverageMultiTotalFrame,coverageMultiOptionsFrame,main.selectedDSPGraphTypes["graphCoverageMultiID"] = makeParameterToggleFrame(main,
		outputFoldOutFrame2,"Coverage for multiple lengths")
	coverageMultiTotalFrame.pack(fill="both")
	
	ThemedLabel(coverageMultiOptionsFrame,text="Select lengths and colour",anchor="w").grid(column=0,row=0,columnspan=2,sticky="w")
	main.multiCovColpairList = list()
	main.multiCovColpairListFrame = ThemedFrame(coverageMultiOptionsFrame,style="wBorder.TFrame")	#maybe style="gBorder.TFrame" ?
	
	pairDescFrame = ThemedFrame(main.multiCovColpairListFrame)	#TODO scrollbar!
	ThemedLabel(pairDescFrame,text="Length").grid(column=0,row=0,sticky="ew")
	ThemedLabel(pairDescFrame,text="Colour (hex)").grid(column=1,row=0,sticky="ew")
	ThemedButton(pairDescFrame,image=main.emptyImage,style="bg.TButton").grid(column=3,row=0,sticky="e")
	
	pairDescFrame.columnconfigure(0,weight=1,uniform="fred")
	pairDescFrame.columnconfigure(1,weight=1,uniform="fred")
	pairDescFrame.columnconfigure(4,weight=0)
	pairDescFrame.pack(fill="x",side="top",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	#filled procedurally with libID pairs
	ThemedButton(main.multiCovColpairListFrame,text="+",command = lambda main=main: 
		addLenCovColPair(main),style="bg.TButton").pack(fill="x",side="bottom",padx=main.frameBorderSize)
	
	main.multiCovColpairListFrame.grid(column=0,row=1,columnspan=4,sticky="ew")
	
	addLenCovColPair(main,length=21)
	addLenCovColPair(main,length=22)
	addLenCovColPair(main,length=23)
	addLenCovColPair(main,length=24)
	addLenCovColPair(main,length=25,colour="#777777")
	addLenCovColPair(main,length=26,colour="#444444")
	addLenCovColPair(main,length=20,colour="#999999")
	addLenCovColPair(main,length=19,colour="#bbbbbb")
	
	
	ThemedLabel(coverageMultiOptionsFrame,text="X-label",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(coverageMultiOptionsFrame,textvariable=addGraphicVar(main,"multicovXLab",StringVar(),"text","Position",
		"Free Text","X-Label")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(coverageMultiOptionsFrame,text="Y-label",anchor="w").grid(column=0,row=3,sticky="w")
	ThemedEntry(coverageMultiOptionsFrame,textvariable=addGraphicVar(main,"multicovYLab",StringVar(),"text","Coverage",
		"Free Text","Y-Label")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	
	coverageMultiOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	coverageMultiOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	coverageMultiOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	#coverageLenOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	coverageMultiOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	coverageMultiOptionsFrame.rowconfigure(3,weight=1,uniform="fred")
	
	# ------------------- Heatmap -------------------
	heatmapTotalFrame,heatmapOptionsFrame,main.selectedDSPGraphTypes["graphHeatmapID"] = makeParameterToggleFrame(main,outputFoldOutFrame3,"Heatmap")
	heatmapTotalFrame.pack(fill="both")
	ThemedLabel(heatmapOptionsFrame,text="Highlight esiRNAs",anchor="w").grid(column=0,row=0,sticky="w")
	createTogglebutton(main,heatmapOptionsFrame,addGraphicVar(main,"heatmapHighlightEsiRNABool",BooleanVar(),"bool",True,
		"","")).grid(column=1,row=0,sticky="e")
	ThemedLabel(heatmapOptionsFrame,text="Highlight other phase",anchor="w").grid(column=0,row=1,sticky="w")
	ThemedEntry(heatmapOptionsFrame,textvariable=addGraphicVar(main,"heatmapHighlightFrames",StringVar(),"intList","",
		"heatmapHighlightFrames needs to be a comma separeted list of to be integers!","Comma separated list of frames to highlight")).grid(
			column=1,row=1,sticky="e",padx=main.frameBorderSize)	
	ThemedLabel(heatmapOptionsFrame,text="Minimum length",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(heatmapOptionsFrame,textvariable=addGraphicVar(main,"heatmapMinLen",StringVar(),"int",15,
		"Minimum length needs to be an integer!","Minimum length of reads to display")).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(heatmapOptionsFrame,text="Maximum length",anchor="w").grid(column=0,row=3,sticky="w")
	ThemedEntry(heatmapOptionsFrame,textvariable=addGraphicVar(main,"heatmapMaxLen",StringVar(),"int",30,
		"Maximum length needs to be an integer!","Maximum length of reads to display")).grid(column=1,row=3,sticky="e",padx=main.frameBorderSize)
	#TODO colourscale function
	ThemedLabel(heatmapOptionsFrame,text="Midpoint percentile",anchor="w").grid(column=0,row=4,sticky="w")
	ThemedEntry(heatmapOptionsFrame,textvariable=addGraphicVar(main,"heatmapMiddlePercentile",StringVar(),"int",95,
		"Percentile needs to be an integer!","Percentile for the colouring function")).grid(column=1,row=4,sticky="e",padx=main.frameBorderSize)
		
	ThemedLabel(heatmapOptionsFrame,text="X-label",anchor="w").grid(column=0,row=5,sticky="w")
	ThemedEntry(heatmapOptionsFrame,textvariable=addGraphicVar(main,"heatXLab",StringVar(),"text","5'Position",
		"Free Text","X-Label")).grid(column=1,row=5,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(heatmapOptionsFrame,text="Y-label",anchor="w").grid(column=0,row=6,sticky="w")
	ThemedEntry(heatmapOptionsFrame,textvariable=addGraphicVar(main,"heatYLab",StringVar(),"text","Read length (nt)",
		"Free Text","Y-Label")).grid(column=1,row=6,sticky="ew",padx=main.frameBorderSize)
	
	heatmapOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	heatmapOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	heatmapOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	heatmapOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	heatmapOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	heatmapOptionsFrame.rowconfigure(3,weight=1,uniform="fred")
	heatmapOptionsFrame.rowconfigure(4,weight=1,uniform="fred")
	heatmapOptionsFrame.rowconfigure(5,weight=1,uniform="fred")
	heatmapOptionsFrame.rowconfigure(6,weight=1,uniform="fred")
	
	
	# ------------------- colour Overrides -------------------
	colourTotalFrame,colourOptionsFrame,colourOptionsID = makeParameterToggleFrame(main,outputFoldOutFrame3,"Colours")
	colourTotalFrame.pack(fill="both")
	ThemedLabel(colourOptionsFrame,text="esiRNA guide strand colour",anchor="w").grid(column=0,row=0,sticky="w")
	ThemedEntry(colourOptionsFrame,textvariable=addGraphicVar(main,"esiGSCVar",StringVar(),"colour","#44aaff",
		"esiGS colour needs to be a valid hexadecimal colour!","Colour for esiGS")).grid(column=1,row=0,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(colourOptionsFrame,text="esiRNA passenger strand colour",anchor="w").grid(column=0,row=1,sticky="w")
	ThemedEntry(colourOptionsFrame,textvariable=addGraphicVar(main,"esiPSCVar",StringVar(),"colour","#3355cc",
		"esiPS colour needs to be a valid hexadecimal colour!","Colour for esiPS")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(colourOptionsFrame,text="pseudo guide strand colour",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(colourOptionsFrame,textvariable=addGraphicVar(main,"pseudoGSCVar",StringVar(),"colour","#88ff88",
		"pseudoGS colour needs to be a valid hexadecimal colour!","Colour for pseudoGS")).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(colourOptionsFrame,text="pseudo passenger strand colour",anchor="w").grid(column=0,row=3,sticky="w")
	ThemedEntry(colourOptionsFrame,textvariable=addGraphicVar(main,"pseudoPSCVar",StringVar(),"colour","#22aa22",
		"pseudoPS colour needs to be a valid hexadecimal colour!","Colour for pseudoPS")).grid(column=1,row=3,sticky="e",padx=main.frameBorderSize)
	
	colourOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	colourOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	colourOptionsFrame.rowconfigure(0,weight=1,uniform="fred")
	colourOptionsFrame.rowconfigure(1,weight=1,uniform="fred")
	colourOptionsFrame.rowconfigure(2,weight=1,uniform="fred")
	colourOptionsFrame.rowconfigure(3,weight=1,uniform="fred")
	
	hideLLFrame = ThemedFrame(outputFoldOutFrame3)
	ThemedLabel(hideLLFrame,text="Hide Labels and Legends",anchor="w").grid(column=0,row=0,columnspan=3,sticky="ew")
	createTogglebutton(main,hideLLFrame,addGraphicVar(main,"hideLabelsLegends",BooleanVar(),"bool",False,
		"","")).grid(column=3,row=0,sticky="e")
	hideLLFrame.columnconfigure(0,weight=1,uniform="fred")
	hideLLFrame.columnconfigure(1,weight=1,uniform="fred")
	hideLLFrame.columnconfigure(2,weight=1,uniform="fred")
	hideLLFrame.columnconfigure(3,weight=1,uniform="fred")
	hideLLFrame.pack(fill="both")
	
	# ------------------ Export overrides ------------------------
	exportOverrideTotalFrame,exportOverrideFrame,main.selectedDSPGraphTypes["exportOverrideID"] = makeParameterToggleFrame(main,outputFoldOutFrame3,"Export overrides")
	exportOverrideTotalFrame.pack(fill="both")
	ThemedLabel(exportOverrideFrame,text="Individual Y-Axis scale",anchor="w").grid(column=0,row=0,columnspan=3,sticky="w")
	createTogglebutton(main,exportOverrideFrame,addGraphicVar(main,"exportOverrideLocalYScale",BooleanVar(),"bool",True,
		"","")).grid(column=3,row=0,sticky="e")
	ThemedLabel(exportOverrideFrame,text="Width",anchor="w").grid(column=0,row=1,sticky="w")
	ThemedEntry(exportOverrideFrame,textvariable=addGraphicVar(main,"exportOverrideWidth",IntVar(),"int",1500,
		"","")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(exportOverrideFrame,text="Heigth",anchor="w").grid(column=2,row=1,sticky="w")
	ThemedEntry(exportOverrideFrame,textvariable=addGraphicVar(main,"exportOverrideHeight",IntVar(),"int",500,
		"","")).grid(column=3,row=1,sticky="e",padx=main.frameBorderSize)
	#ThemedLabel(exportOverrideFrame,text="Font size [SVG]",anchor="w").grid(column=0,row=2,sticky="w")
	#ThemedEntry(exportOverrideFrame,textvariable=addGraphicVar(main,"exportFontsizeVar",IntVar(),"int",22,
	#	"","")).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(exportOverrideFrame,text="Font multiplier [GUI]",anchor="w").grid(column=0,row=2,sticky="w")
	ThemedEntry(exportOverrideFrame,textvariable=addGraphicVar(main,"fontMultiplierGUI",StringVar(),"float",1.0,
		"","")).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(exportOverrideFrame,text="Font multiplier [SVG]",anchor="w").grid(column=0,row=3,sticky="w")
	ThemedEntry(exportOverrideFrame,textvariable=addGraphicVar(main,"fontMultiplierSVG",StringVar(),"float",1.0,
		"","")).grid(column=1,row=3,sticky="e",padx=main.frameBorderSize)
	
	exportOverrideFrame.columnconfigure(0,weight=1,uniform="fred")
	exportOverrideFrame.columnconfigure(1,weight=1,uniform="fred")
	exportOverrideFrame.columnconfigure(2,weight=1,uniform="fred")
	exportOverrideFrame.columnconfigure(3,weight=1,uniform="fred")
	
	exportOverrideFrame.rowconfigure(0,weight=1,uniform="fred")
	exportOverrideFrame.rowconfigure(1,weight=1,uniform="fred")
	exportOverrideFrame.rowconfigure(2,weight=1,uniform="fred")
	
