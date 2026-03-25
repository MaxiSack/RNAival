
from tkinter import StringVar
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Button as ThemedButton
from gui.functions import addInputVar
import processing.sR_processing as srp

def resetIndex(main):
	main.PM.reset(tag="index")

def createIndexForce(main):
	createIndexMan(main,force=True)

def createIndexMan(main,force=False):
	main.saveSettings()
	createIndex(main,force=force)

def createIndex(main,force=False):
	if main.isStepRunning():return False
	if not main.checkInputParams():return False
	parameters = main.PM.getDict(tags=["index","general","project"])
	selectedLibIDs = [key for key,value in main.sRPLibIDSelection.items() if value.get()]
	grouping = dict()
	for libID in selectedLibIDs:
		try:
			target = main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).bundleID
		except:
			print(f"Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; {main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}")
		print(target)
		if not target in grouping:grouping[target] = list()
		grouping[target].append(libID)
	print(f"[sRP Index] Groups: {grouping}")
	parameters["targets"] = list(grouping.keys())
	print(f"[sRP Index] Params:\n"+"\n".join([f"{k}: {v}" for k,v in parameters.items()]))
	return srp.createIndex(parameters,main,force=force)

def resetMap(main):
	parameters["mapExtraVar"][0].set("")

def mapReadsForce(main):
	mapReadsMan(main,force=True)

def mapReadsMan(main,force=False):
	main.saveSettings()
	mapReads(main,force=force)
	
def mapReads(main,force=False):
	if main.isStepRunning():return False
	
	if len(main.mapTmp) == 0:	#collect params and store as tmp file
		if not main.checkInputParams():return False,False
		
		parameters = main.PM.getDict(tags=["bowtie","general","project"])
		main.mapTmpParams = parameters
		selectedLibIDs = [key for key,value in main.sRPLibIDSelection.items() if value.get()]
		grouping = dict()
		for libID in selectedLibIDs:
			try:
				target = main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).bundleID
			except:
				print(f"""[sRP Map] Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; 
					{main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}""")
			#print(target)
			if not target in grouping:grouping[target] = list()
			grouping[target].append(libID)
		print(f"[sRP Map] Groups: {grouping}")
		#indexID = main.IM.getTarget(target).bundleID
		main.mapTmp = [[main.IM.getTarget(target).bundleID,main.IM.getTarget(target).mainSeqID,main.IM.getTarget(target).mainLength,libIDs] for target,libIDs in grouping.items()]
		#run for each target
		#queue all map runs and only put "DONE" into comsqueue when the last one finishes
		return True,True	#Setup successful, repeat to start processing the groups
	else:
		group = main.mapTmp[0]
		del main.mapTmp[0]
		repeat = len(main.mapTmp)>0	#repeat this step until all map runs have been completed
		print(f"[sRP Map] {group} {repeat}")
		return srp.mapReads(main.mapTmpParams,group,main,force=force),repeat

def add_sRP_bowtie_GUI(main,parent):
	bowtieBaseFrame = ThemedFrame(parent)
	ThemedLabel(bowtieBaseFrame,text="Step 3: Map reads to the target RNA",anchor="w",style="Medium.TLabel").pack(fill="both",expand=True,anchor="nw")
	mapFoldOutFrame = ThemedFrame(bowtieBaseFrame)
	mapFoldOutFrame.pack(fill="both",expand=True,anchor="nw")
	#Step3: Mapping -------------------------------------------------------------------------------------------------------------------
	ThemedLabel(mapFoldOutFrame,text="Step 3.1: Create an index of the target RNA (using bowtielbuild)",anchor="w").grid(column=0,row=0,columnspan=3,sticky="ew")
	#Doesnt really have any paramters ?
	ThemedLabel(mapFoldOutFrame,text="Extra parameters:",anchor="w").grid(column=0,row=1,sticky="ew")
	ThemedEntry(mapFoldOutFrame,textvariable=addInputVar(main,"indexExtraVar",StringVar(),"text","",
		"Free text ?","Extra parameters for bowtiebuild.",tag="index")).grid(column=1,row=1,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	ThemedButton(mapFoldOutFrame,text="Reset to defaults",command=lambda main=main: srp.resetIndex(main)).grid(column=0,row=2,sticky="ew")
	ThemedButton(mapFoldOutFrame,text="Force create the index",command=lambda main=main: srp.createIndexForce(main)).grid(column=1,row=2,columnspan=2,sticky="ew")
	
	ThemedLabel(mapFoldOutFrame,text="Step 3.2: Map the reads onto the index (using bowtie)",anchor="w").grid(column=0,row=4,columnspan=3,sticky="ew")
	ThemedLabel(mapFoldOutFrame,text="Align full reads:",anchor="w").grid(column=0,row=5,columnspan=2,sticky="ew")
	ThemedLabel(mapFoldOutFrame,text="Yes",anchor="w").grid(column=2,row=5,sticky="ew")	#--end-to-end parameter in bowtie2
	#anyting else we want as standard variable params?
	#--no-unal #reported in output, no need to write the seqs
	#--best --tryhard -n 3 --chunkmbs 512
	ThemedLabel(mapFoldOutFrame,text="Extra parameters:",anchor="w").grid(column=0,row=6,sticky="ew")
	ThemedEntry(mapFoldOutFrame,textvariable=addInputVar(main,"mapExtraVar",StringVar(),"text","",
		"Free text ?","Extra parameters for bowtie.",tag="bowtie")).grid(column=1,row=6,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	main.mapTmp=list()	#needs to be added for mapping later
	ThemedButton(mapFoldOutFrame,text="Reset to defaults",command=lambda main=main: srp.resetMap(main)).grid(column=0,row=7,sticky="ew")
	ThemedButton(mapFoldOutFrame,text="Force map the reads",command=lambda main=main: srp.mapReadsForce(main)).grid(column=1,row=7,columnspan=2,sticky="ew")
	#ThemedButton(mapFoldOutFrame,text="Run only this step",command=mapReadsMan).grid(column=2,row=11,sticky="ew")
	
	mapFoldOutFrame.columnconfigure(0,weight=0)
	mapFoldOutFrame.columnconfigure(1,weight=1,uniform="fred")
	mapFoldOutFrame.columnconfigure(2,weight=1,uniform="fred")
	
	mapFoldOutFrame.rowconfigure(0,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(1,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(2,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(3,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(4,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(5,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(6,weight=1,uniform="fred")
	mapFoldOutFrame.rowconfigure(7,weight=1,uniform="fred")
	
	return bowtieBaseFrame
