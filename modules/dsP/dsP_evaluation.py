
import os.path
from pathlib import Path

from .loadGraphs import loadGraphs
from functions.baseFunctions import getReverseSeq
from iostuff.loadCounts import loadCounts

def writeRNAExpressionStats(main,resultDir,countData,libIDs,bundleTarget,dsP_RNAExpressionGUI = True,dsP_RNAExpressionFile = True):
	if dsP_RNAExpressionGUI or dsP_RNAExpressionFile:
		print("[siGUI] Writing RNA expression stats...",end="")
		header = "libID\tRNA-ID\tpos\tstrand\tlength\tcount\tc/c@len\tc/c@pos\tsequence"
		if dsP_RNAExpressionGUI:main.writeTextOutput(header)
		for libID in libIDs:
			libText=""
			for strand in [0,1]:
				for RNA_annot in bundleTarget.annotation[strand]:
					if RNA_annot[4] == "Guide" or RNA_annot[4] == "Passenger":
						try:
							totalOfLength = countData.getLengthCount(libID,0,RNA_annot[1])+countData.getLengthCount(libID,1,RNA_annot[1])
							count = countData.getReadCount(libID,strand,RNA_annot[1],RNA_annot[0]-strand*(RNA_annot[1]-1))
							totalPos = countData.getPosCount(libID,strand,RNA_annot[0])
							if strand==1: sequence = getReverseSeq(bundleTarget.mainSequence[RNA_annot[0]-RNA_annot[1]:RNA_annot[0]],main=main)
							else: sequence = bundleTarget.mainSequence[RNA_annot[0]-1:RNA_annot[0]+RNA_annot[1]-1]
							stats=[
								libID,
								RNA_annot[3],
								str(RNA_annot[0]),
								"sense" if strand==0 else "anti",
								str(RNA_annot[1]),
								str(count),
								str(0 if totalOfLength==0 else round(count/totalOfLength,5)),
								str(0 if totalPos==0 else round(count/totalPos,5)),
								sequence]
							libText+="\n"+"\t".join(stats)
						except Exception as e:
							print(e)
							print("error with esiRNA annotation: "+str(RNA_annot))
			if dsP_RNAExpressionGUI:main.writeTextOutput(libText)
			if dsP_RNAExpressionFile:
				with open(os.path.join(resultDir,libID+"_esiRNA.tsv"),"w") as esiWriter:
					esiWriter.write(header+libText)
		print("done.")

def writeRNADegradeStats(main,resultDir,countData,libIDs,bundleTarget,dsP_RNADegradeGUI = True,dsP_RNADegradeFile = True,dsP_RNADegrade_min = 15,dsP_RNADegrade_max = 17):
	if dsP_RNADegradeGUI or dsP_RNADegradeFile:
		print("[siGUI] Writing esiRNA degradation stats...",end="")
		for libID in libIDs:
			if dsP_RNADegradeGUI:main.writeTextOutput(f"\n{libID}")
			header = "length"
			for strand in [0,1]:
				for esiRNA in bundleTarget.annotation[strand]:
					if esiRNA[4] == "Guide" or esiRNA[4] == "Passenger":
						header+="\t"+esiRNA[3]+"-5\t"+esiRNA[3]+"-3"
			outText = ""+header
			for length in range(dsP_RNADegrade_max,dsP_RNADegrade_min-1,-1):
				outText+="\n"+str(length)
				for strand in [0,1]:
					for esiRNA in bundleTarget.annotation[strand]:
						if esiRNA[4] == "Guide" or esiRNA[4] == "Passenger":
							try:
								count5p = countData.getReadCount(libID,strand,length,esiRNA[0]-strand*(length-1))
								count3p = countData.getReadCount(libID,strand,length,esiRNA[0]+(1-strand)*(esiRNA[1]-length)-strand*(esiRNA[1]-1))
								outText+="\t"+str(count5p)+"\t"+str(count3p)
							except:
								print("error with esiRNA annotation: "+str(esiRNA))
			if dsP_RNADegradeGUI:main.writeTextOutput(outText)
			if dsP_RNADegradeFile:
				with open(os.path.join(resultDir,libID+"_esiRNA_degrade.tsv"),"w") as esiWriter:
					esiWriter.write(outText)
		print("done.")

def getGrouping(main,selectedLibIDs):
	grouping = dict()
	for libID in selectedLibIDs:
		try:
			for target in main.IM.getLib(libID).getCountfiles():	#target = (bundleID,psname)
				if not target[1] == main.IM.getLib(libID).ppt:continue	#only draw the currently selected Parameterset
				if not target[0] == main.IM.getLib(libID).getSelectedTarget():continue	#only draw the currently selected target
				if not target in grouping:grouping[target] = list()
				grouping[target].append(libID)
		except:
			print(f"Error, problem with finding targets for {libID}: {main.IM.getLib(libID).getCountfiles()}")
	return grouping

def loadDataIntoGUI(main,wantedgraphs,selectedLibIDs,highlightStyles=None,tableParams=None):
	grouping = getGrouping(main,selectedLibIDs)
		
	#print(f"\n[dsP eval] Groups: \n"+"\n".join([f"{key}:\t{value}" for key,value in sorted(grouping.items())])+"\n")
	for (bundleID,psname),libIDs in sorted(grouping.items()):
		resultDir = os.path.join(main.PM.get("projectPath"),"Graphics",bundleID,psname)
		Path(resultDir).mkdir(parents=True, exist_ok=True)
		#print(f"[Debug][dsP] Group: {bundleID}-{psname}, {libIDs}
		countDir = os.path.join(main.PM.get("projectPath"),"Counts",bundleID,psname)
		countFile = os.path.join(countDir,"$libID_readcounts.tsv")
		#print(f"[dsP eval] Countfile: {countFile}")
		bundleTarget = main.IM.getTarget(bundleID)
		if bundleTarget.mainSeqID is None or bundleTarget.mainSequence is None:	#None if bundle is invalid (because of missing file)
			main.writeWarning(f"Target {bundleID} is invalid, skipping libraries {libIDs}",terminalPrefix="[dsP]")	#skip if target is None (invalid)
			continue
		countData = loadCounts(main,countFile,libIDs,bundleTarget.mainLength)
		if countData is None or countData is False: 
			print("Error, data is None!")
			main.writeError("Error while reading counts from file! {countFile}")
			continue
		
		#---------------------- Prepare graphs -------------------
		siRNAPos = [dict(),dict()]	#TODO this is somewhat redundant with annotation
		if not bundleTarget.annotation is None:
			for strand,entrylist in enumerate(bundleTarget.annotation):
				for feature in entrylist:
					#start,length,class,id,ps/gs,label
					#if "gs" in feature[2] or "ps" in feature[2]:
					if feature[4] == "Guide" or feature[4] == "Passenger":
						siRNAPos[strand][feature[0]]=feature[1]
					else:
						#print(feature[1])
						pass
		for dic in wantedgraphs:
			dic["mainTargetSeqID"] = bundleTarget.mainSeqID	#mainTarget
			dic["bundleID"] = bundleID
			dic["psname"] = psname
		#TODO fix highlightStyles, do we still need that?	highlightStyles is used to colour the bars, cols from graphdef is used for the legend. ????
		if len(wantedgraphs)>0:
			loadGraphs(main,countData,libIDs,wantedgraphs,siRNAPos,annotation=bundleTarget.annotation,highlightStyles=highlightStyles)
		
		#---------------------- Create tabular output -------------------
		if not tableParams is None:
			writeRNAExpressionStats(main,resultDir,countData,libIDs,bundleTarget,
				dsP_RNAExpressionGUI = tableParams["dsP-RNAExpressionGUI"],
				dsP_RNAExpressionFile = tableParams["dsP-RNAExpressionFile"])
			
			writeRNADegradeStats(main,resultDir,countData,libIDs,bundleTarget,
				dsP_RNADegradeGUI = tableParams["dsP-RNADegradeGUI"],
				dsP_RNADegradeFile = tableParams["dsP-RNADegradeFile"],
				dsP_RNADegrade_min = tableParams["dsP-RNADegrade_min"],
				dsP_RNADegrade_max = tableParams["dsP-RNADegrade_max"])
	return True
