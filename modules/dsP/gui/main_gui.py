
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Radiobutton as ThemedRadioButton

from gui.functions import createTogglebutton,makeParameterToggleFrame
from graphs.drawGraphics import multiplyColour
from gui.ScrollableFrame import ScrollableFrame

from ..dsP_evaluation import loadDataIntoGUI
from ..static import moduleID

defaultColours = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]

def getColours(main):	# ------------------ colours ------------------------
	colour_primary_guide=main.PM.get("dsP-_colour_primary_guide")
	colour_primary_passenger=main.PM.get("dsP-_colour_primary_passenger")
	colour_secondary_guide=main.PM.get("dsP-_colour_secondary_guide")
	colour_secondary_passenger=main.PM.get("dsP-_colour_secondary_passenger")
	
	highlightStyles = dict()
	highlightStyles["colour_primary_guide"]=(colour_primary_guide,multiplyColour(0.7,colour_primary_guide),1)
	highlightStyles["colour_primary_passenger"]=(colour_primary_passenger,multiplyColour(0.7,colour_primary_passenger),1)
	highlightStyles["colour_secondary_guide"]=(colour_secondary_guide,multiplyColour(0.7,colour_secondary_guide),1)
	highlightStyles["colour_secondary_passenger"]=(colour_secondary_passenger,multiplyColour(0.7,colour_secondary_passenger),1)
	return highlightStyles

def getWantedgraphs(main):
	wantedgraphs = list()	#Graphs to generate
	
	# ------------------ colours ------------------------
	highlightStyles = getColours(main)	#TODO update/unify this in loadGraphs with cols and styles
	
	hideLL = main.PM.get("RNAival-hide_Labels_Legends")
	yAxisScale = main.PM.get("dsP-_yaxis")
	doYAaxisAbundance = yAxisScale == "abundance" or yAxisScale == "both"
	doYAaxisPercent = yAxisScale == "percent" or yAxisScale == "both"
	
	
	# ------------------- length distribution -------------------
	if main.PM.get("dsP-lenDist__doGraph"):
		if doYAaxisAbundance:	#make graph with abundance yaxis
			graphDef=dict()
			graphDef[0]="lendist"
			graphDef["minL"] = int(main.PM.get("dsP-lenDist_minLen"))
			graphDef["maxL"] = int(main.PM.get("dsP-lenDist_maxLen"))
			graphDef["xlab"] = main.PM.get("dsP-lenDist_xLab")
			graphDef["ylab"] = main.PM.get("dsP-lenDist_yLab")
			graphDef["cols"] = [highlightStyles["colour_primary_guide"][0],highlightStyles["colour_primary_passenger"][0]]
			graphDef["percent"] = False
			wantedgraphs.append(graphDef)
		
		if doYAaxisPercent:		#make graph with percent yaxis
			graphDef2=dict()
			graphDef2[0]="lendist"
			graphDef2["minL"] = int(main.PM.get("dsP-lenDist_minLen"))
			graphDef2["maxL"] = int(main.PM.get("dsP-lenDist_maxLen"))
			graphDef2["xlab"] = main.PM.get("dsP-lenDist_xLab")
			graphDef2["ylab"] = main.PM.get("dsP-lenDist_yLabPercent")
			graphDef2["cols"] = [highlightStyles["colour_primary_guide"][0],highlightStyles["colour_primary_passenger"][0]]
			graphDef2["percent"] = True
			wantedgraphs.append(graphDef2)		#This does work
	
	# ------------------- annotation counts -------------------
	if main.PM.get("dsP-annotCount__doGraph"):
		if doYAaxisAbundance:
			graphDef=dict()
			graphDef[0]="annotCount"
			graphDef["xlab"] = main.PM.get("dsP-annotCount_xLab")
			graphDef["ylab"] = main.PM.get("dsP-annotCount_yLab")
			graphDef["cols"] = [
						highlightStyles["colour_primary_guide"][0],
						highlightStyles["colour_primary_passenger"][0],
						highlightStyles["colour_secondary_guide"][0],
						highlightStyles["colour_secondary_passenger"][0]
						]
			graphDef["percent"] = False
			wantedgraphs.append(graphDef)
		
		if doYAaxisPercent:
			graphDef2=dict()
			graphDef2[0]="annotCount"
			graphDef2["cols"] = [
						highlightStyles["colour_primary_guide"][0],
						highlightStyles["colour_primary_passenger"][0],
						highlightStyles["colour_secondary_guide"][0],
						highlightStyles["colour_secondary_passenger"][0]
						]
			graphDef2["xlab"] = main.PM.get("dsP-annotCount_xLab")
			graphDef2["ylab"] = main.PM.get("dsP-annotCount_yLabPercent")
			graphDef2["percent"] = True
			wantedgraphs.append(graphDef2)
	
	# ------------------- single-length startPos -------------------
	if main.PM.get("dsP-startPos__doGraph"):
		for lenStr in main.PM.get("dsP-startPos_lengths"):
			if doYAaxisAbundance:
				graphDef=dict()
				graphDef[0]="startPos"
				graphDef["xlab"] = main.PM.get("dsP-startPos_xLab")
				graphDef["ylab"] = main.PM.get("dsP-startPos_yLab")
				graphDef["targetlen"] = lenStr
				graphDef["cols"] = [
							highlightStyles["colour_primary_guide"][0],
							highlightStyles["colour_primary_passenger"][0],
							highlightStyles["colour_secondary_guide"][0],
							highlightStyles["colour_secondary_passenger"][0]
							]
				graphDef["percent"] = False
				wantedgraphs.append(graphDef)
			
			if doYAaxisPercent:
				graphDef2=dict()
				graphDef2[0]="startPos"
				graphDef2["xlab"] = main.PM.get("dsP-startPos_xLab")
				graphDef2["targetlen"] = lenStr
				graphDef2["cols"] = [
							highlightStyles["colour_primary_guide"][0],
							highlightStyles["colour_primary_passenger"][0],
							highlightStyles["colour_secondary_guide"][0],
							highlightStyles["colour_secondary_passenger"][0]
							]
				graphDef2["ylab"] = main.PM.get("dsP-startPos_yLabPercent")
				graphDef2["percent"] = True
				wantedgraphs.append(graphDef2)
	
	# ------------------- single-length Coverage -------------------
	if main.PM.get("dsP-singleCov__doGraph"):
		for lenStr in main.PM.get("dsP-singleCov_lengths"):
			graphDef=dict()
			graphDef[0]="singleCov"
			graphDef["xlab"] = main.PM.get("dsP-singleCov_xLab")
			graphDef["ylab"] = main.PM.get("dsP-singleCov_yLab")
			graphDef["targetlen"] = lenStr
			graphDef["cols"] = [
						highlightStyles["colour_primary_guide"][0],
						highlightStyles["colour_primary_passenger"][0],
						highlightStyles["colour_secondary_guide"][0],
						highlightStyles["colour_secondary_passenger"][0]
						]
			wantedgraphs.append(graphDef)
			
	# ------------------- multi-length Coverage -------------------
	if main.PM.get("dsP-multiCov__doGraph"):
		targetlist = list()
		for i,pair in enumerate(main.dsP_multiCovPairListWidgets):
			if pair is None:continue
			targetlist.append((int(pair[1].get()),pair[2].get()))
		if len(targetlist)>0:
			graphDef=dict()
			graphDef[0]="multiCov"
			graphDef["xlab"] = main.PM.get("dsP-multiCov_xLab")
			graphDef["ylab"] = main.PM.get("dsP-multiCov_yLab")
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
	if main.PM.get("dsP-heatmap__doGraph"):
		graphDef=dict()
		graphDef[0]="heapmap"
		graphDef["highlightEsis"] = main.PM.get("dsP-heatmap_highlightEsiRNABool")
		graphDef["highlightFrames"] = list()
		graphDef["highlightFrames"] = main.PM.get("dsP-heatmap_highlightFrames")
		graphDef["minLen"] = int(main.PM.get("dsP-heatmap_minLen"))
		graphDef["maxLen"] = int(main.PM.get("dsP-heatmap_maxLen"))
		graphDef["middlePercentile"] = int(main.PM.get("dsP-heatmap_middlePercentile"))
		graphDef["xlab"] = main.PM.get("dsP-heatmap_xLab")
		graphDef["ylab"] = main.PM.get("dsP-heatmap_yLab")
		wantedgraphs.append(graphDef)
	
	if hideLL:	#hide all Labels and Legends ... by deleting them
		for graphDef in wantedgraphs:
			graphDef["xlab"] = None
			graphDef["ylab"] = None
			graphDef["hideLegend"] = True
	
	globalYScale =  main.PM.get("dsP-_globalYScale")
	for graphDef in wantedgraphs:
		graphDef["globalYScale"] = globalYScale
	
	return wantedgraphs

def loadData(main,export=True,gui=True):
	# ------------------- Graph definition -------------------
	wantedgraphs = getWantedgraphs(main)
	if not wantedgraphs: 
		main.writeError("Error with graph definitions!")
		return False
	#print("[dsP Debug] wanted graphs:\n"+str("\n".join(["\t"+str(graph) for graph in wantedgraphs])))
	
	# ------------------- Library Selection -----------------------
	selectedLibIDs = [libID for libID,lib in main.IM.getLibraries().items() if moduleID in lib.evalTypes]
	#print(f"Selected Libraries:\n{selectedLibIDs}")
	
	highlightStyles=getColours(main)
	return loadDataIntoGUI(main,wantedgraphs,selectedLibIDs,export=export,highlightStyles=highlightStyles,gui=gui)


def deleteLenCovColPair(main,index):
	#print("[main func] Deleting libID-pair "+str(index)+": "+str(pairList[index][1].get())+" "+str(pairList[index][2].get()))
	main.dsP_multiCovPairListWidgets[index][0].destroy()
	main.dsP_multiCovPairListWidgets[index]=None
	main.PM.deleteParameter("dsP-multiCov_length-"+str(index))
	main.PM.deleteParameter("dsP-multiCov_colour-"+str(index))

def addLenCovColPair(main,length=None, colour=None):
	pairFrame = ThemedFrame(main.dsP_multiCovPairListFrame)
	pairID = len(main.dsP_multiCovPairListWidgets)
	
	lenVar = main.PM.add("dsP-multiCov_length-"+str(pairID),"int","0",	#Add to PM for automatic validation and error reporting, but dont save to file
		f"Length for multi-coverage length {length} needs to be an integer!","Length of reads to display coverage for.",tag="dsP-multiCoverage-tmp")
	if not length is None:lenVar.set(str(length))
	
	defaultColour = defaultColours[pairID] if pairID<len(defaultColours) else "#000000"
	colVar = main.PM.add("dsP-multiCov_colour-"+str(pairID),"colour",defaultColour,
		f"Colour for multi-coverage length {length} needs to be a valid hexadecimal colour!","Colour for coverage",tag="dsP-multiCoverage-tmp")
	if not colour is None:colVar.set(str(colour))
	
	ThemedEntry(pairFrame,textvariable=lenVar).grid(column=0,row=0,sticky="ew",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedEntry(pairFrame,textvariable=colVar).grid(column=1,row=0,sticky="ew",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedButton(pairFrame,image=main.xImage,command = lambda main=main,i = pairID: deleteLenCovColPair(main,i),style="Exit.TButton").grid(column=3,row=0,sticky="ew")
	
	pairFrame.columnconfigure(0,weight=1,uniform="fred")
	pairFrame.columnconfigure(1,weight=1,uniform="fred")
	pairFrame.columnconfigure(4,weight=0)
	
	pairFrame.pack(fill="x",side="top",pady=(0,main.frameBorderSize))
	main.dsP_multiCovPairListWidgets.append([pairFrame,lenVar,colVar])	#frame to delete from gui, vars to build graphs; when deleted is set to None

def setMultiCovPairs(main,multiCoverageList=None):
	for pairFrame,_,_ in main.dsP_multiCovPairListWidgets:	#delete previous widgets
		pairFrame.destroy()
	main.dsP_multiCovPairListWidgets = list()
	
	if not multiCoverageList is None and len(multiCoverageList)>0:	#load list from project
		for (length,colour) in multiCoverageList:
			addLenCovColPair(main,length=length, colour=colour)
	else:	#Provide default lengths 20-25
		for length in range(20,26):
			addLenCovColPair(main,length=length)

def add_dsP_eval_GUI(main):
	if not "dsP" in main.evalTypes:main.evalTypes.append("dsP")
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[dsP module] adding GUI at {notebookIndex}")
	dsPEvalFrame = ThemedFrame(main.mainNotebook,style="gBorder.TFrame")
	main.mainNotebook.add(dsPEvalFrame, text="dsP eval")
	main.mainNotebooktabs[notebookIndex] = dsPEvalFrame
	
	ThemedLabel(dsPEvalFrame,text="dsRNA processing evaluation",anchor="w",style="Header.TLabel"
		).grid(row=0,column=0,columnspan=3,sticky="news",padx=main.frameBorderSize*2,pady=(main.frameBorderSize*2,main.frameBorderSize*2))
	#ThemedLabel(dsPEvalFrame,text="Select types of graphs to generate and set their parameters",anchor="w",style="Medium.TLabel"
	#	).grid(row=1,column=0,columnspan=3,sticky="news",padx=main.frameBorderSize*2,pady=(0,main.frameBorderSize))
	graphSettingsColumn_1 = ThemedFrame(dsPEvalFrame,style="gBorder.TFrame")
	graphSettingsColumn_1.grid(row=2,column=0,sticky="news",padx=(main.frameBorderSize*2,main.frameBorderSize),pady=(0,main.frameBorderSize*2))
	graphSettingsColumn_2 = ThemedFrame(dsPEvalFrame,style="gBorder.TFrame")
	graphSettingsColumn_2.grid(row=2,column=1,sticky="news",padx=(main.frameBorderSize,main.frameBorderSize),pady=(0,main.frameBorderSize*2))
	graphSettingsColumn_3 = ThemedFrame(dsPEvalFrame,style="gBorder.TFrame")
	graphSettingsColumn_3.grid(row=2,column=2,sticky="news",padx=(main.frameBorderSize,main.frameBorderSize*2),pady=(0,main.frameBorderSize*2))
	
	dsPEvalFrame.columnconfigure(0,weight=1,uniform="fred")
	dsPEvalFrame.columnconfigure(1,weight=1,uniform="fred")
	dsPEvalFrame.columnconfigure(2,weight=1,uniform="fred")
	dsPEvalFrame.rowconfigure(0,weight=0)
	dsPEvalFrame.rowconfigure(1,weight=0)
	dsPEvalFrame.rowconfigure(2,weight=1)
	#dsPEvalFrame.rowconfigure(3,weight=0)
	
	# ------------------- length distribution -------------------
	wantLendistGraphVar = main.PM.add("dsP-lenDist__doGraph","bool",True,"Boolerror","Wether to generate length-distribution graphs or not.",tag="dsP-lenDist")
	lcountTotalFrame,lcountOptionsFrame,_ = makeParameterToggleFrame(
		main,graphSettingsColumn_1,"Length distribution",toggleVar=wantLendistGraphVar)
	lcountTotalFrame.pack(fill="both",pady=(0,main.frameBorderSize*2))
	
	ThemedLabel(lcountOptionsFrame,text="Minimum length",anchor="w").grid(column=0,row=0,sticky="w",padx=main.frameBorderSize,pady=(main.frameBorderSize,0))
	ThemedEntry(lcountOptionsFrame,textvariable=main.PM.add("dsP-lenDist_minLen","int",15,
		"Minimum length needs to be an integer!","Minimum length of reads to display",tag="dsP-lenDist")).grid(
			column=1,row=0,sticky="e",padx=main.frameBorderSize,pady=(main.frameBorderSize,0))
	ThemedLabel(lcountOptionsFrame,text="Maximum length",anchor="w").grid(column=0,row=1,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(lcountOptionsFrame,textvariable=main.PM.add("dsP-lenDist_maxLen","int",30,
		"Maximum length needs to be an integer!","Maximum length of reads to display",tag="dsP-lenDist")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="X-label",anchor="w").grid(column=0,row=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(lcountOptionsFrame,textvariable=main.PM.add("dsP-lenDist_xLab","text","Read length (nt)",
		"Free Text","X-Label",tag="dsP-lenDist")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="Y-label abundance",anchor="w").grid(column=0,row=3,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(lcountOptionsFrame,textvariable=main.PM.add("dsP-lenDist_yLab","text","Abundance",
		"Free Text","Y-Label for abundance",tag="dsP-lenDist")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(lcountOptionsFrame,text="Y-label percent",anchor="w").grid(column=0,row=4,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(lcountOptionsFrame,textvariable=main.PM.add("dsP-lenDist_yLabPercent","text","Percent of all reads",
		"Free Text","Y-Label for percent",tag="dsP-lenDist")).grid(column=1,row=4,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	lcountOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	lcountOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	lcountOptionsFrame.rowconfigure(0,weight=0)
	lcountOptionsFrame.rowconfigure(1,weight=0)
	lcountOptionsFrame.rowconfigure(2,weight=0)
	lcountOptionsFrame.rowconfigure(3,weight=0)
	lcountOptionsFrame.rowconfigure(4,weight=0)
	
	# ------------------- annotation counts -------------------
	wantLendistGraphVar = main.PM.add("dsP-annotCount__doGraph","bool",True,"Boolerror","Wether to generate annotation count graphs or not.",tag="dsP-annotCount")
	esiCountGraphTotalFrame,esiCountGraphOptionsFrame,_ = makeParameterToggleFrame(
		main,graphSettingsColumn_1,"Abundance of annotated RNAs",toggleVar=wantLendistGraphVar)
	esiCountGraphTotalFrame.pack(fill="both",pady=(0,main.frameBorderSize*2))
	
	ThemedLabel(esiCountGraphOptionsFrame,text="X-label",anchor="w").grid(column=0,row=0,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(esiCountGraphOptionsFrame,textvariable=main.PM.add("dsP-annotCount_xLab","text","esiRNAs",
		"Free Text","X-Label",tag="dsP-annotCount")).grid(column=1,row=0,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(esiCountGraphOptionsFrame,text="Y-label abundance",anchor="w").grid(column=0,row=1,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(esiCountGraphOptionsFrame,textvariable=main.PM.add("dsP-annotCount_yLab","text","Abundance",
		"Free Text","Y-Label for Abundance",tag="dsP-annotCount")).grid(column=1,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(esiCountGraphOptionsFrame,text="Y-label percent",anchor="w").grid(column=0,row=2,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(esiCountGraphOptionsFrame,textvariable=main.PM.add("dsP-annotCount_yLabPercent","text","Percent of 21nt reads",
		"Free Text","Y-Label for percent",tag="dsP-annotCount")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	esiCountGraphOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	esiCountGraphOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	esiCountGraphOptionsFrame.rowconfigure(0,weight=0)
	esiCountGraphOptionsFrame.rowconfigure(1,weight=0)
	esiCountGraphOptionsFrame.rowconfigure(2,weight=0)
	
	
	# ------------------- single-length startPos -------------------
	wantStartPosGraphVar = main.PM.add("dsP-startPos__doGraph","bool",True,"Boolerror","Wether to generate start position graphs or not.",tag="dsP-startPos")
	startPosTotalFrame,startPosOptionsFrame,_ = makeParameterToggleFrame(
		main,graphSettingsColumn_1,"Read distribution for specific length",toggleVar=wantStartPosGraphVar)
	startPosTotalFrame.pack(fill="both",pady=(0,main.frameBorderSize*2))
	
	ThemedLabel(startPosOptionsFrame,text="Lengths (comma separated)",anchor="w").grid(column=0,row=0,columnspan=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(startPosOptionsFrame,textvariable=main.PM.add("dsP-startPos_lengths","intList","21",
		"Startpos-lengths needs to be a comma separeted list of to be integers!","Comma separated list of lengths to dispaly",tag="dsP-startPos")).grid(
			column=1,row=0,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(startPosOptionsFrame,text="X-label",anchor="w").grid(column=0,row=1,columnspan=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(startPosOptionsFrame,textvariable=main.PM.add("dsP-startPos_xLab","text","5\'position",
		"Free Text","X-Label",tag="dsP-startPos")).grid(column=1,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(startPosOptionsFrame,text="Y-label abundance",anchor="w").grid(column=0,row=2,columnspan=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(startPosOptionsFrame,textvariable=main.PM.add("dsP-startPos_yLab","text","Abundance",
		"Free Text","Y-Label for Abundance",tag="dsP-startPos")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(startPosOptionsFrame,text="Y-label percent",anchor="w").grid(column=0,row=3,columnspan=2,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(startPosOptionsFrame,textvariable=main.PM.add("dsP-startPos_yLabPercent","text","Percent of 21nt reads",
		"Free Text","Y-Label for percent",tag="dsP-startPos")).grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	startPosOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	startPosOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	startPosOptionsFrame.rowconfigure(0,weight=0)
	startPosOptionsFrame.rowconfigure(1,weight=0)
	startPosOptionsFrame.rowconfigure(2,weight=0)
	startPosOptionsFrame.rowconfigure(3,weight=0)
	
	# ------------------- single-length Coverage -------------------
	wantSingleLengthCoverageGraphVar = main.PM.add("dsP-singleCov__doGraph","bool",True,"Boolerror","Wether to generate start position graphs or not.",tag="dsP-singleCoverage")
	coverageLenTotalFrame,coverageLenOptionsFrame,_ = makeParameterToggleFrame(
		main,graphSettingsColumn_2,"Coverage for individual lengths",toggleVar=wantSingleLengthCoverageGraphVar)
	coverageLenTotalFrame.pack(fill="both",pady=(0,main.frameBorderSize*2))
	
	ThemedLabel(coverageLenOptionsFrame,text="Lengths (comma separated)",anchor="w").grid(column=0,row=0,columnspan=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(coverageLenOptionsFrame,textvariable=main.PM.add("dsP-singleCov_lengths","intList","21",
		"Coverage-lengths needs to be a comma separeted list of to be integers!","Comma separated list of lengths to dispaly",tag="dsP-singleCoverage")).grid(
			column=1,row=0,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(coverageLenOptionsFrame,text="X-label",anchor="w").grid(column=0,row=1,columnspan=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(coverageLenOptionsFrame,textvariable=main.PM.add("dsP-singleCov_xLab","text","Position",
		"Free Text","X-Label",tag="dsP-singleCoverage")).grid(column=1,row=1,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(coverageLenOptionsFrame,text="Y-label",anchor="w").grid(column=0,row=2,columnspan=2,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(coverageLenOptionsFrame,textvariable=main.PM.add("dsP-singleCov_yLab","text","Coverage",
		"Free Text","Y-Label",tag="dsP-singleCoverage")).grid(column=1,row=2,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	coverageLenOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	coverageLenOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	coverageLenOptionsFrame.rowconfigure(0,weight=0)
	coverageLenOptionsFrame.rowconfigure(1,weight=0)
	coverageLenOptionsFrame.rowconfigure(2,weight=0)
	
	# ------------------- multi-length Coverage -------------------
	wantStartPosGraphVar = main.PM.add("dsP-multiCov__doGraph","bool",True,"Boolerror","Wether to generate start position graphs or not.",tag="dsP-multiCoverage")
	coverageMultiTotalFrame,coverageMultiOptionsFrame,_ = makeParameterToggleFrame(main,
		graphSettingsColumn_2,"Coverage for multiple lengths",toggleVar=wantStartPosGraphVar)
	coverageMultiTotalFrame.pack(fill="both",expand=True)
	
	ThemedLabel(coverageMultiOptionsFrame,text="X-label",anchor="w").grid(column=0,row=0,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(coverageMultiOptionsFrame,textvariable=main.PM.add("dsP-multiCov_xLab","text","Position",
		"Free Text","X-Label",tag="dsP-multiCoverage")).grid(column=1,row=0,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(coverageMultiOptionsFrame,text="Y-label",anchor="w").grid(column=0,row=1,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(coverageMultiOptionsFrame,textvariable=main.PM.add("dsP-multiCov_yLab","text","Coverage",
		"Free Text","Y-Label",tag="dsP-multiCoverage")).grid(column=1,row=1,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	pairDescFrame = ThemedFrame(coverageMultiOptionsFrame,style="wBorder.TFrame")
	pairDescFrame.grid(column=0,row=2,columnspan=2,sticky="news")
	ThemedLabel(pairDescFrame,text=" Length").grid(column=0,row=0,sticky="news",pady=main.frameBorderSize)
	ThemedLabel(pairDescFrame,text=" Colour (hex)").grid(column=1,row=0,sticky="news",pady=main.frameBorderSize)
	ThemedButton(pairDescFrame,image=main.emptyImage,style="FlatText.TButton",state="disabled").grid(column=2,row=0,sticky="news",pady=main.frameBorderSize)
		
	main.dsP_multiCovPairListWidgets = list()
	dsP_multiCovPairListWidgetsOuterFrame = ScrollableFrame(coverageMultiOptionsFrame,style="wBorder.TFrame",innerFrame_style="wBorder.TFrame")
	dsP_multiCovPairListWidgetsOuterFrame.grid(column=0,row=3,columnspan=2,sticky="news")
	main.dsP_multiCovPairListFrame = dsP_multiCovPairListWidgetsOuterFrame.getInnerFrame()
	dsP_multiCovPairListWidgetsOuterFrame.setCanvasBG(main.styleman.backgroundColour)
	main.styleman.registredBG.append(dsP_multiCovPairListWidgetsOuterFrame)
	
	pairDescFrame.columnconfigure(0,weight=1,uniform="fred")
	pairDescFrame.columnconfigure(1,weight=1,uniform="fred")
	pairDescFrame.columnconfigure(2,weight=0)
	
	ThemedButton(main.dsP_multiCovPairListFrame,text="+",command = lambda main=main: 
		addLenCovColPair(main),style="TButton").pack(fill="x",side="bottom")
	
	coverageMultiOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	coverageMultiOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	coverageMultiOptionsFrame.rowconfigure(0,weight=0)
	coverageMultiOptionsFrame.rowconfigure(1,weight=0)
	coverageMultiOptionsFrame.rowconfigure(2,weight=0)
	coverageMultiOptionsFrame.rowconfigure(3,weight=1)
	
	# ------------------- Heatmap -------------------
	wantStartPosGraphVar = main.PM.add("dsP-heatmap__doGraph","bool",True,"Boolerror","Wether to generate start position graphs or not.",tag="dsP-heatmap")
	heatmapTotalFrame,heatmapOptionsFrame,_ = makeParameterToggleFrame(
		main,graphSettingsColumn_3,"Heatmap",toggleVar=wantStartPosGraphVar)
	heatmapTotalFrame.pack(fill="both",pady=(0,main.frameBorderSize*2))
	ThemedLabel(heatmapOptionsFrame,text="Highlight esiRNAs",anchor="w").grid(column=0,row=0,sticky="w",padx=main.frameBorderSize)
	createTogglebutton(main,heatmapOptionsFrame,main.PM.add("dsP-heatmap_highlightEsiRNABool","bool",True,
		"","",tag="dsP-heatmap")).grid(column=1,row=0,sticky="e")
	ThemedLabel(heatmapOptionsFrame,text="Highlight other phase",anchor="w").grid(column=0,row=1,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(heatmapOptionsFrame,textvariable=main.PM.add("dsP-heatmap_highlightFrames","intList","",
		"heatmapHighlightFrames needs to be a comma separeted list of to be integers!","Comma separated list of frames to highlight",tag="dsP-heatmap")).grid(
			column=1,row=1,sticky="e",padx=main.frameBorderSize)	
	ThemedLabel(heatmapOptionsFrame,text="Minimum length",anchor="w").grid(column=0,row=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(heatmapOptionsFrame,textvariable=main.PM.add("dsP-heatmap_minLen","int",15,
		"Minimum length needs to be an integer!","Minimum length of reads to display",tag="dsP-heatmap")).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(heatmapOptionsFrame,text="Maximum length",anchor="w").grid(column=0,row=3,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(heatmapOptionsFrame,textvariable=main.PM.add("dsP-heatmap_maxLen","int",30,
		"Maximum length needs to be an integer!","Maximum length of reads to display",tag="dsP-heatmap")).grid(column=1,row=3,sticky="e",padx=main.frameBorderSize)
	#TODO colourscale function
	ThemedLabel(heatmapOptionsFrame,text="Colourscale midpoint percentile",anchor="w").grid(column=0,row=4,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(heatmapOptionsFrame,textvariable=main.PM.add("dsP-heatmap_middlePercentile","int",95,
		"Percentile needs to be an integer!","Percentile for the colouring function",tag="dsP-heatmap")).grid(column=1,row=4,sticky="e",padx=main.frameBorderSize)
		
	ThemedLabel(heatmapOptionsFrame,text="X-label",anchor="w").grid(column=0,row=5,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(heatmapOptionsFrame,textvariable=main.PM.add("dsP-heatmap_xLab","text","5'Position",
		"Free Text","X-Label",tag="dsP-heatmap")).grid(column=1,row=5,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(heatmapOptionsFrame,text="Y-label",anchor="w").grid(column=0,row=6,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(heatmapOptionsFrame,textvariable=main.PM.add("dsP-heatmap_yLab","text","Read length (nt)",
		"Free Text","Y-Label",tag="dsP-heatmap")).grid(column=1,row=6,sticky="ew",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	heatmapOptionsFrame.columnconfigure(0,weight=1,uniform="fred")
	heatmapOptionsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	heatmapOptionsFrame.rowconfigure(0,weight=0)
	heatmapOptionsFrame.rowconfigure(1,weight=0)
	heatmapOptionsFrame.rowconfigure(2,weight=0)
	heatmapOptionsFrame.rowconfigure(3,weight=0)
	heatmapOptionsFrame.rowconfigure(4,weight=0)
	heatmapOptionsFrame.rowconfigure(5,weight=0)
	heatmapOptionsFrame.rowconfigure(6,weight=0)
	
	# ---------------- global settings ---------------------
	dsP_globalSettings = ThemedFrame(graphSettingsColumn_3)
	dsP_globalSettings.pack(fill="both",pady=(0,main.frameBorderSize*2))
	ThemedLabel(dsP_globalSettings,text="Global settings",anchor="w",style="Medium.TLabel").grid(column=0,row=0,columnspan=4,sticky="w",padx=main.frameBorderSize)
	
	ThemedLabel(dsP_globalSettings,text="Synchronise Y-Axes between graphs",anchor="w").grid(column=0,row=2,columnspan=3,sticky="ew",padx=main.frameBorderSize)
	createTogglebutton(main,dsP_globalSettings,main.PM.add("dsP-_globalYScale","bool",False,
		"boolerror","Wether to synchronise Y-Axes between graphs of the same type",tag="dsP-general")).grid(column=3,row=2,sticky="e")
	
	ThemedLabel(dsP_globalSettings,text="Y-Axes (where applicable):",anchor="w").grid(column=0,row=3,columnspan=1,sticky="ew",padx=main.frameBorderSize)
	strandVar = main.PM.add("dsP-_yaxis","text","abundance","Stringerror","Yaxis shows abundance, percent or make both graphs",tag="dsP-general")
	ThemedRadioButton(dsP_globalSettings,text="Abundance",variable=strandVar,value="abundance").grid(column=1,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedRadioButton(dsP_globalSettings,text="Percent",variable=strandVar,value="percent").grid(column=2,row=3,sticky="ew",padx=main.frameBorderSize)
	ThemedRadioButton(dsP_globalSettings,text="Both",variable=strandVar,value="both").grid(column=3,row=3,sticky="ew",padx=main.frameBorderSize)
	
	dsP_globalSettings.rowconfigure(0,weight=0)
	dsP_globalSettings.rowconfigure(1,weight=0)
	dsP_globalSettings.rowconfigure(2,weight=0)
	dsP_globalSettings.rowconfigure(3,weight=0)
	dsP_globalSettings.rowconfigure(4,weight=0)
	dsP_globalSettings.columnconfigure(0,weight=1)
	dsP_globalSettings.columnconfigure(1,weight=0,uniform="fred")
	dsP_globalSettings.columnconfigure(2,weight=0,uniform="fred")
	dsP_globalSettings.columnconfigure(3,weight=0,uniform="fred")
	
	# ------------------- colour Overrides -------------------
	colourOptionsFrame = ThemedFrame(graphSettingsColumn_3)
	colourOptionsFrame.pack(fill="both",pady=(0,main.frameBorderSize*2))
	ThemedLabel(colourOptionsFrame,text="Annotation colours",anchor="w",style="Medium.TLabel").grid(column=0,row=0,columnspan=2,sticky="w",padx=main.frameBorderSize)
	
	ThemedLabel(colourOptionsFrame,text="Primary guide strand colour",anchor="w").grid(column=0,row=1,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(colourOptionsFrame,textvariable=main.PM.add("dsP-_colour_primary_guide","colour","#44aaff",
		"colour_primary_guide colour needs to be a valid hexadecimal colour!","Colour for colour_primary_guide",tag="dsP-general")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(colourOptionsFrame,text="Primary passenger strand colour",anchor="w").grid(column=0,row=2,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(colourOptionsFrame,textvariable=main.PM.add("dsP-_colour_primary_passenger","colour","#3355cc",
		"colour_primary_passenger colour needs to be a valid hexadecimal colour!","Colour for colour_primary_passenger",tag="dsP-general")).grid(column=1,row=2,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(colourOptionsFrame,text="Secondary guide strand colour",anchor="w").grid(column=0,row=3,sticky="w",padx=main.frameBorderSize)
	ThemedEntry(colourOptionsFrame,textvariable=main.PM.add("dsP-_colour_secondary_guide","colour","#88ff88",
		"colour_secondary_guide colour needs to be a valid hexadecimal colour!","Colour for colour_secondary_guide",tag="dsP-general")).grid(column=1,row=3,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(colourOptionsFrame,text="Secondary passenger strand colour",anchor="w").grid(column=0,row=4,sticky="w",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	ThemedEntry(colourOptionsFrame,textvariable=main.PM.add("dsP-_colour_secondary_passenger","colour","#22aa22",
		"colour_secondary_passenger colour needs to be a valid hexadecimal colour!","Colour for colour_secondary_passenger",tag="dsP-general")).grid(
			column=1,row=4,sticky="e",padx=main.frameBorderSize,pady=(0,main.frameBorderSize))
	
	colourOptionsFrame.columnconfigure(0,weight=1)
	colourOptionsFrame.columnconfigure(1,weight=0)
	
	colourOptionsFrame.rowconfigure(0,weight=0)
	colourOptionsFrame.rowconfigure(1,weight=0)
	colourOptionsFrame.rowconfigure(2,weight=0)
	colourOptionsFrame.rowconfigure(3,weight=0)
	colourOptionsFrame.rowconfigure(4,weight=0)
	
	#column_1_buffer
	ThemedFrame(graphSettingsColumn_1).pack(fill="both",expand=True)
	#column_2_buffer
	#ThemedFrame(graphSettingsColumn_2).pack(fill="both",expand=True)
	#column_3_buffer
	ThemedFrame(graphSettingsColumn_3).pack(fill="both",expand=True)
	
