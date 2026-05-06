
import os.path
from pathlib import Path
from math import log2
from itertools import chain

import evaluation.loadGraphs as lg
from graphs.Combograph import Combograph
from functions.baseFunctions import getReverseSeq
from graphs.drawGraphics import interpolateColoursFraction

libdash = "-"

# execution related functions ---------------------------------------------------------------

def loadDataIntoGUI(main,libPairs,gui=True,export=True):	#TODO this needs a stronger rework for the new system
	
	if not main.PM.validateTags(["graphics"]):return False
	
	if gui:main.writeLog("\n-------------------------------------------------------\nLoading siI data into GUI")
	else:main.writeLog("\n-------------------------------------------------------\nLoading siI data")
	
	print("[siI eval] Loading graphics")
	for i,pair in enumerate(libPairs):	#[([libPos],[libNeg])]	#TODO this should be LibID-Target-PS	#or even better: Select Target+PS, then from all libs that have this
		if pair is None:continue	#shouldnt happen anymore !
		print(f"\n[siI eval] LibPair: {pair}")
		
		#plot the bar diagram and volcano-like plot
		targetDict = dict()
		for side in pair[:-1]:
			for libID in side:
				for target in main.IM.getLib(libID).getCountfiles():
					if not target[1] == main.IM.getLib(libID).ppt:continue	#only draw the currently selected Parameterset
					if target not in targetDict: targetDict[target] = 0
					targetDict[target]+=1
		
		pairLabel = pair[-1]
		libIDs = list(chain(*pair[:-1]))
		for (bundleID,psname),value in targetDict.items():	#for each target+PS that was found for all libs of the pair (should only be one, but *could* be more)
			if value<len(libIDs):continue			#only process parametersets that were used for all libraries of this pair
			#print(f"[siI eval] bundleID: {bundleID}, PS: {psname}, LibIDs: {libIDs}")
			for index in range(len(main.IM.getLib(libIDs[0]).mapTargets)):
				graphList = list()
				
				targetBundle = main.IM.getTarget(bundleID)
				countDir = os.path.join(main.PM.get("projectPath"),"Counts",bundleID,psname)
				countFile = os.path.join(countDir,"$libID_readcounts.tsv")
				#print(f"[siI eval] Countfiles: {countFile}")
				
				resultDir = os.path.join(main.PM.get("projectPath"),"Graphics",bundleID,psname)
				Path(resultDir).mkdir(parents=True, exist_ok=True)
				
				countData = lg.loadCounts(main,countFile,libIDs,targetBundle.mainLength)
				if countData is None or countData is False: 
					print("[siI eval] Error, data is None!")
					main.writeError("Error while reading counts from file!")
					continue
				#countData.printStats()
				strand=1	#we only want siRNAs that map to the complement of the mRNA
				length=21	#only anti-viral active siRNAs	#TODO this could be a setting if someone is interested in reads of a different length
				
				axisLabelTemplate = [("5' Position","Abundance (enriched)"),("5' Position","Abundance (control)")]
				axisLabels = list()
				for isControl in [0,1]:
					nlibs = len(pair[isControl])
					if nlibs==0:continue
					
					#TODO [regionStart-1:regionEnd] for region stuff ! ~~
					data = [None]*targetBundle.mainLength
					for position in range(1,len(data)+1):
						data[position-1] = (position,int(sum([countData.getReadCount(libID,strand,length,position) for libID in pair[isControl]])/nlibs))
					
					graphList.append(("+".join(pair[isControl]),data))
					#print(f"[siI eval] Pairgraphload: {graphList[-1][0]} {len(graphList)}")
					axisLabels.append(axisLabelTemplate[isControl])
				
				graphNameA = "Abundance "+pairLabel
				#TODO maybe make this a BAR2 instead with control on negative
				graph = Combograph(main,graphNameA,targetBundle.mainSeqID+"_"+psname,graphType="BAR")	#TODO bundleID use bundleLabel instead!!
				graph.bundleID=bundleID
				graph.psname=psname
				graph.addData(graphList,globalYScale=True,axislabels=axisLabels)
				main.comboGraphs[graphNameA+"_"+psname] = graph
				print(f"[siI eval] Added {graphNameA} to comboGraphs.") # {main.comboGraphs[graphNameA+"_"+psname]}")
				if len(graphList) ==1:continue
				
				pointHeatValues = [log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(len(graphList[0][1]))]
				maxHeat = max(max(pointHeatValues),1)
				col1 = "#000000"
				col2 = "#00ff00"
				pointColours = [interpolateColoursFraction(val/maxHeat, col1, col2) for val in pointHeatValues]
				graphNameV = "Foldchange "+pairLabel
				graph = Combograph(main,graphNameV,targetBundle.mainSeqID+"_"+psname,graphType="SCATTER")
				graph.bundleID=bundleID
				graph.psname=psname
				points = [(graphList[0][1][i][0],log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
					 for i in range(len(graphList[0][1]))]
				logPoolCounts = [(graphList[0][1][i][0],graphList[0][1][i][0],log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
							 for i in range(len(graphList[0][1]))]
				logPoolGraph = (graphList[0][0]+"_log",logPoolCounts)
				
				graph.addData([(graphList[0][0]+"_Volcano",points),logPoolGraph],colouroverride=[None,pointColours],
					axislabels=[("Log2 Foldchange","Log2 Difference"),("Position","Log2 Difference")])
				#graph.addData([(graphList[0][0]+"_Volcano",points)],	#Only show volcano
				#	axislabels=[("Log2 Foldchange","Log2 Difference")])
				
				main.comboGraphs[graphNameV+"_"+psname] = graph
				
				graph.addConnectedGraph(main.comboGraphs[graphNameA+"_"+psname])
				main.comboGraphs[graphNameA+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameV+"_"+psname])
			
				descriptorFields = ["ID    ","cutPos","seq                  ","countAGO","countDCL","foldChange","log2FC","diff","log2Diff"]
				pointDescriptor = [("siRNA-"+str(graphList[0][1][i][0]+10),	#ID
							graphList[0][1][i][0],	#cutpos
							getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-11:graphList[0][1][i][0]+10],main=main),
							graphList[0][1][i][1],	#ago
							graphList[1][1][i][1],	#dcl
							round((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1),3),	#FC
							round(log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),3),	#logFC
							graphList[0][1][i][1]-graphList[1][1][i][1],	#diff
							round(log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1),3))	#logDiff
							 for i in range(len(points))]
				
				graph.addPointDescriptor(descriptorFields,pointDescriptor)
			
		
	#if gui:displayGraphs(main)	#TODO check this
	#if export:exportGraphs(main)	#TODO auto export is disabled (?)
	main.writeLog("done.\n")
	#print(f"[siI eval] Number of comboGraphs: {len(main.comboGraphs.keys())}")
	return True

