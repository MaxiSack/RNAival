
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

def loadDataIntoGUI(main,libPairs,gui=True,export=True):
	
	if main.isStepRunning():return False
	if not main.checkInputParams():return False
	countDir = os.path.join(main.projectPath,"4_results")
	resultDir = os.path.join(main.projectPath,"5_graphics")
	Path(resultDir).mkdir(parents=True, exist_ok=True)
	
	if gui:main.writeLog("\n-------------------------------------------------------\nLoading siI data into GUI")
	else:main.writeLog("\n-------------------------------------------------------\nLoading siI data")
	
	#main.resetGraphicsOutput()
	#main.showTextOutputTab()
	#main.resetTextOutput()
	
	suffixes = {"counts":"_counts.tsv"}
	reqFiles = {"$in":os.path.join(countDir,"$libID")}
	print("[siI eval] Loading graphics")
	#main.comboGraphs = dict()
	for i,pair in enumerate(libPairs):	#[([libPos],[libNeg])]	
		if pair is None:continue	#shouldnt happen anymore !
		print(f"[siI eval] LibPair: {pair}")
		#[siI eval] LibPair: (['TG_MK4_Ago1_S4', 'TG_MK6_Ago1_S6'], ['TG_MK1_DCL_S1', 'TG_MK2_DCL_S2', 'TG_MK3_DCL_S3'])
		#[siI eval] LibPair: (['TG_MK7_Ago2_S7', 'TG_MK8_Ago2_S8', 'TG_MK9_Ago2_S9'], ['TG_MK1_DCL_S1', 'TG_MK2_DCL_S2', 'TG_MK3_DCL_S3'])
		
		#plot the bar diagram and volcano-like plot
		
		pairLabel = pair[-1]
		libIDs = list(chain(*pair[:-1]))
		for index in range(len(main.IM.getLib(libIDs[0]).mapTargets)):
			graphList = list()
			
			#load all libPos countfiles, extract 21nt reads on reverse and average them
			#same for libNeg
			print(f"[siI eval] LibIDs: {libIDs}")
			pairTargetID = main.IM.getLib(libIDs[0]).mapTargets[index]
			print(f"[siI eval] PairTargetID: {pairTargetID}")
			countFile = os.path.join(countDir,pairTargetID+"_$libID_readcounts.tsv")
			print(f"[siI eval] Countfiles: {countFile}")
			countData = lg.loadCounts(main,countFile,libIDs,main.IM.getTarget(pairTargetID).mainLength)
			if countData is None or countData is False: 
				print("[siI eval] Error, data is None!")
				main.writeError("Error while reading counts from file!")
				continue
			#countData.printStats()
			strand=1	#we only want siRNAs that map to the complement of the mRNA
			length=21	#only anti-viral active siRNAs	#TODO this could be a setting if someone is interested in reads of a different length
			
			data = [None,None]	#TODO start and end positions !
			for isControl in [0,1]:
				nlibs = len(pair[isControl])
				data[isControl] = [0]*main.IM.getTarget(pairTargetID).mainLength
				for position in range(1,len(data[isControl])+1):
					data[isControl][position-1] = (position,int(sum([countData.getReadCount(libID,strand,length,position) for libID in pair[isControl]])/nlibs))
				#data[isControl][regionStart-1:regionEnd] for region stuff !
				graphList.append(("+".join(pair[isControl]),data[isControl]))
				print("[siI eval] Pairgraphload: "+graphList[-1][0]+" "+str(len(graphList)))
			
			graphNameA = "Abundance "+pairLabel+" - "+pairTargetID
			#TODO maybe make this a BAR2 instead with control on negative
			graph = Combograph(main,graphNameA,main.IM.getTarget(pairTargetID).mainSeqID,graphType="BAR")
			graph.addData(graphList,globalYScale=True,axislabels=[("5' Position","Abundance (enriched)"),("5' Position","Abundance (control)")])
			main.comboGraphs[graphNameA] = graph
			print("[siI eval] Added "+str(graphNameA)+" to comboGraphs: "+str(main.comboGraphs[graphNameA]))
			
			pointHeatValues = [log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(len(graphList[0][1]))]
			maxHeat = max(max(pointHeatValues),1)
			col1 = "#000000"
			col2 = "#00ff00"
			pointColours = [interpolateColoursFraction(val/maxHeat, col1, col2) for val in pointHeatValues]
			#TODO scatter/Volcano plot
			graphNameV = "Foldchange "+pairLabel+" - "+pairTargetID
			graph = Combograph(main,graphNameV,main.IM.getTarget(pairTargetID).mainSeqID,graphType="SCATTER")
			points = [(graphList[0][1][i][0],log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
				 for i in range(len(graphList[0][1]))]
			logPoolCounts = [(graphList[0][1][i][0],graphList[0][1][i][0],log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1)) for i in range(len(graphList[0][1]))]
			logPoolGraph = (graphList[0][0]+"_log",logPoolCounts)
			#graph.addData([(graphList[0][0]+"_Volcano",points),logPoolGraph],colouroverride=[None,pointColours],
			#	axislabels=[("Log2 Foldchange","Log2 Difference"),("Position","Log2 Difference")])
			
			graph.addData([(graphList[0][0]+"_Volcano",points)],	#Only show volcano
				axislabels=[("Log2 Foldchange","Log2 Difference")])
			main.comboGraphs[graphNameV] = graph
			
			graph.addConnectedGraph(main.comboGraphs[graphNameA])
			main.comboGraphs[graphNameA].addConnectedGraph(main.comboGraphs[graphNameV])
		
			descriptorFields = ["ID    ","cutPos","seq                  ","countAGO","countDCL","foldChange","log2FC","diff","log2Diff"]
			#pointDescriptor = [None]*len(points)	#fields per point that are relevant
			pointDescriptor = [("siRNA-"+str(graphList[0][1][i][0]+10),	#ID
						graphList[0][1][i][0],	#cutpos
						getReverseSeq(main.IM.getTarget(pairTargetID).mainSequence[graphList[0][1][i][0]-11:graphList[0][1][i][0]+10],main=main),
						graphList[0][1][i][1],	#ago
						graphList[1][1][i][1],	#dcl
						round((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1),3),	#FC
						round(log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),3),	#logFC
						graphList[0][1][i][1]-graphList[1][1][i][1],	#diff
						round(log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1),3))	#logDiff
						 for i in range(len(points))]
			
			graph.addPointDescriptor(descriptorFields,pointDescriptor)
			
		
	#if gui:displayGraphs(main)	#TODO check this
	if export:exportGraphs(main)	#TODO auto export is disabled (?)
	main.writeLog("done.\n")
	print("[siI eval] main.comboGraphs: "+str(main.comboGraphs.items()))
	return True

