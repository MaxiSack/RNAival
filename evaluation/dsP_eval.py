
import os.path
from pathlib import Path

import evaluation.loadGraphs as lg
from functions.baseFunctions import getReverseSeq

# execution related functions ---------------------------------------------------------------

def exportGraphs(main):
	print("\n[siGUI] Exporting graphs")
	main.writeLog("\n-------------------------------------------------------\nExporting graphs")
	resultDir = os.path.join(main.PM.get("projectPath"),"5_graphics")
	Path(resultDir).mkdir(parents=True, exist_ok=True)
	
	if not main.checkInputParams():return False
	#lg.setStyles(main,getColours(main))
	lg.exportGraphs(main,resultDir,main.PM.get("exportOverrideWidth"),main.PM.get("exportOverrideHeight"),
		main.PM.get("exportFontsizeVar"))
	print("\n[siGUI] ...done.")
	
def displayGraphs(main):
	print("\n[siGUI] Displaying graphs")
	main.writeLog("\n-------------------------------------------------------\nDisplaying graphs")
	resultDir = os.path.join(main.PM.get("projectPath"),"5_graphics")
	
	if not main.checkInputParams():return False
	#main.resetGraphicsOutput()	#TODO keep track of generated graphics and reset only the ones that are re-generated..
	#lg.setStyles(main,getColours(main))	#TODO is for update...
	if lg.showGraphs(main,resultDir,main.PM.get("fontMultiplier")):
		main.mainNotebook.select(main.graphicsTabIndex)
	print("\n[siGUI] ...done.")

def giveTextOutput(basegui,countData,resultDir,selectedLibIDs,export=True):	#TODO unused!
	if export:
		Path(resultDir).mkdir(parents=True, exist_ok=True)
	
	#---------------------- Create tabular output -------------------
	print("[siGUI] Writing esiRNA expression stats")
	#ID	pos	strand	length	count	c/c@len	c/c@pos
	header = "ID\tpos\tstrand\tlength\tcount\tc/c@len\tc/c@pos\tsequence"
	outText = ""+header
	for libID in selectedLibIDs:
		outText+="\n"+libID
		esiList = list()
		for strand in [0,1]:
			for esiRNA in basegui.annotation[strand]:	#start	length	label
				#print(esiRNA)
				#if "_gs" in esiRNA[2] or "_ps" in esiRNA[2]:
				if esiRNA[4] == "Guide" or esiRNA[4] == "Passenger":
					try:
						totalOfLength = countData.getLengthCount(libID,0,esiRNA[1])+countData.getLengthCount(libID,1,esiRNA[1])
						count = countData.getReadCount(libID,strand,esiRNA[1],esiRNA[0]-strand*(esiRNA[1]-1))
						totalPos = countData.getPosCount(libID,strand,esiRNA[0])
						siSeq = basegui.constructSeq[esiRNA[0]-1:esiRNA[0]+esiRNA[1]-1]
						if strand==1: siSeq = getReverseSeq(basegui.constructSeq[esiRNA[0]-esiRNA[1]:esiRNA[0]],main=basegui)
						esiList.append([esiRNA[2],str(esiRNA[0]),"sense" if strand==0 else "anti",str(esiRNA[1]),str(count),
							str(0 if totalOfLength==0 else round(count/totalOfLength,5)),str(0 if totalPos==0 else round(count/totalPos,5)),
							siSeq])
					except Exception as e:
						print(e)
						print("error with esiRNA annotation: "+str(esiRNA)) #?????
		tmpText = ""+header
		for stats in esiList:
			tmpText+="\n"+"\t".join(stats)
		outText+="\n"+tmpText
		
		if export:
			with open(os.path.join(resultDir,libID+"_esiRNA.tsv"),"w") as esiWriter:
				esiWriter.write(tmpText)
	basegui.writeTextOutput(outText)
	print("Done")
	
	print("[siGUI] Writing esiRNA degradation stats")
	for libID in selectedLibIDs:
		#length	esi1_gs-5	esi1_gs-3	esi1_ps-5	esi1_ps-3
		header = "\nlength"
		for strand in [0,1]:
			for esiRNA in basegui.annotation[strand]:	#start	length	label
				if "_gs" in esiRNA[2] or "_ps" in esiRNA[2]:
					header+="\t"+esiRNA[2]+"-5\t"+esiRNA[2]+"-3"
		outText = ""+header
		for lenOffset in range(5,-6,-1):	#TODO parameter
			outText+="\n"+str(21+lenOffset)	#TODO
			for strand in [0,1]:
				for esiRNA in basegui.annotation[strand]:	#start	length	label
					#if "_gs" in esiRNA[2] or "_ps" in esiRNA[2]:
					if esiRNA[4] == "Guide" or esiRNA[4] == "Passenger":
						try:
							count5p = countData.getReadCount(libID,strand,esiRNA[1]+lenOffset,esiRNA[0]-strand*(esiRNA[1]-1+lenOffset))
							count3p = countData.getReadCount(libID,strand,esiRNA[1]+lenOffset,esiRNA[0]-(1-strand)*(lenOffset)-strand*(esiRNA[1]-1))
							outText+="\t"+str(count5p)+"\t"+str(count3p)
						except:
							print("error with esiRNA annotation: "+str(esiRNA))
		#basegui.writeTextOutput(outText)
		if export:
			with open(os.path.join(resultDir,libID+"_esiRNA_degrade.tsv"),"w") as esiWriter:
				esiWriter.write(outText)
	print("Done")

def loadDataIntoGUI(main,wantedgraphs,selectedLibIDs,gui=True,export=True,highlightStyles=None):
	if not main.checkInputParams():return False
	
	countDir = os.path.join(main.projectPath,"4_results")
	resultDir = os.path.join(main.projectPath,"5_graphics")
	
	print("\n[siGUI] Loading data")
	main.writeLog("\n-------------------------------------------------------\nLoading data")
	#main.resetGraphicsOutput()	#dont delete everything
	main.showTextOutputTab()
	#main.resetTextOutput()
	
	grouping = dict()
	for libID in selectedLibIDs:
		try:
			targetBundleIDs = main.IM.getLib(libID).mapTargets
			for bundleID in targetBundleIDs:
				target = main.IM.getTarget(bundleID).bundleID
				print(target)
				if not target in grouping:grouping[target] = list()
				grouping[target].append(libID)
		except:
			print(f"Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; {main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}")
		
	print(f"\n[dsP eval] Groups: \n"+"\n".join([f"{key}:\t{value}" for key,value in sorted(grouping.items())])+"\n")
	for bundleID,libIDs in sorted(grouping.items()):
		countFile = os.path.join(countDir,bundleID+"_$libID_readcounts.tsv")
		print(f"Countfile: {countFile}")
		print(main.IM.getLib(libIDs[0]).mapTargets[0])
		print(main.IM.getTarget(main.IM.getLib(libIDs[0]).mapTargets[0]).mainLength)
		countData = lg.loadCounts(main,countFile,libIDs,main.IM.getTarget(main.IM.getLib(libIDs[0]).mapTargets[0]).mainLength)
		if countData is None or countData is False: 
			print("Error, data is None!")
			main.writeError("Error while reading counts from file! {countFile}")
			continue
		
		siRNAPos = [dict(),dict()]	#TODO remove this! probably and just use the annotation
		if not main.IM.getTarget(main.IM.getLib(libIDs[0]).mapTargets[0]).annotation is None:
			for strand,entrylist in enumerate(main.IM.getTarget(main.IM.getLib(libIDs[0]).mapTargets[0]).annotation):
				for feature in entrylist:
					#start,length,class,id,ps/gs,label
					#if "gs" in feature[2] or "ps" in feature[2]:
					if feature[4] == "Guide" or feature[4] == "Passenger":
						siRNAPos[strand][feature[0]]=feature[1]
					else:
						print(feature[1])
		for dic in wantedgraphs:
			dic["mainTargetSeqID"] = main.IM.getTarget(bundleID).mainSeqID	#mainTarget
			dic["bundleID"] = bundleID	#mainTarget
		#TODO fix highlightStyles, do we still need that?	highlightStyles is used to colour the bars, cols from graphdef is used for the legend. ????
		lg.loadGraphs(main,countData,libIDs,wantedgraphs,siRNAPos,annotation=main.IM.getTarget(main.IM.getLib(libIDs[0]).mapTargets[0]).annotation,highlightStyles=highlightStyles)
		
		#giveTextOutput(main,countData,resultDir,selectedLibIDs,export=export)	#TODO test and re-activate
		
	if gui:displayGraphs(main)
	return True
