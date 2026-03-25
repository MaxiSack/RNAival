
from tkinter import StringVar
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Button as ThemedButton
from gui.functions import addInputVar
import processing.sR_processing as srp

def countReadsForce(main):
	countReadsMan(main,force=True)

def countReadsMan(main,force=False):
	main.saveSettings()
	countReads(main,force=force)

def countReads(main,force=False):
	if main.isStepRunning():return False
	
	if len(main.countTmp) == 0:	#collect params and store as tmp file
		if not main.checkInputParams():return False,False
		
		parameters = main.PM.getDict(tags=["count","general","project"])
		main.countTmpParams = parameters
		selectedLibIDs = [key for key,value in main.sRPLibIDSelection.items() if value.get()]
		grouping = dict()
		for libID in selectedLibIDs:
			try:
				target = main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).bundleID
			except:
				print(f"""[sRP Count] Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; 
					{main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}""")
			#print(target)
			if not target in grouping:grouping[target] = list()
			grouping[target].append(libID)
		print(f"[sRP Count] Groups: {grouping}")
		
		#indexID = main.IM.getTarget(target).bundleID
		main.countTmp = [[main.IM.getTarget(target).bundleID,main.IM.getTarget(target).mainSeqID,main.IM.getTarget(target).mainLength,libIDs]
					 for target,libIDs in grouping.items()]
		#Same system as for mapping
		return True,True	#Setup successful, repeat to start processing the groups
	else:
		group = main.countTmp[0]
		del main.countTmp[0]
		repeat = len(main.countTmp)>0
		print(f"[sRP Count] {group} {repeat}")
		return srp.countReads(main.countTmpParams,group,main,force=force),repeat
	

def add_sRP_count_GUI(main,parent):
	countBaseFrame = ThemedFrame(parent)
	ThemedLabel(countBaseFrame,text="Step 4: Count reads",anchor="w",style="Medium.TLabel").pack(fill="both",expand=True,anchor="nw")
	countFoldOutFrame = ThemedFrame(countBaseFrame)
	countFoldOutFrame.pack(fill="both",expand=True,anchor="nw")
	#Step4: Counting -------------------------------------------------------------------------------------------------------------------
	ThemedLabel(countFoldOutFrame,text="Minimum read length",anchor="w").grid(column=0,row=0,sticky="w")
	ThemedEntry(countFoldOutFrame,textvariable=addInputVar(main,"countMinLen",StringVar(),"int",15,
		"Minimum length needs to be an integer!","Minimum length of reads to count",tag="count")).grid(column=1,row=0,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(countFoldOutFrame,text="Maximum read length",anchor="w").grid(column=0,row=1,sticky="w")
	ThemedEntry(countFoldOutFrame,textvariable=addInputVar(main,"countMaxLen",StringVar(),"int",30,
		"Maximum length needs to be an integer!","Maximum length of reads to count",tag="count")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	main.countTmp=list()	#needed for runnung this step
	ThemedButton(countFoldOutFrame,text="Force run this step",command=lambda main=main: srp.countReadsForce(main)).grid(column=0,row=2,columnspan=2,sticky="ew")
	
	countFoldOutFrame.columnconfigure(0,weight=0,uniform="fred")
	countFoldOutFrame.columnconfigure(1,weight=1,uniform="fred")
	
	countFoldOutFrame.rowconfigure(0,weight=1,uniform="fred")
	countFoldOutFrame.rowconfigure(1,weight=1,uniform="fred")
	countFoldOutFrame.rowconfigure(2,weight=1,uniform="fred")
	
	return countBaseFrame
