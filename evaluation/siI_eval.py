
import os.path
from pathlib import Path
from math import log2
from itertools import chain

import evaluation.loadGraphs as lg
from graphs.Combograph import Combograph
from functions.baseFunctions import getReverseSeq
from graphs.drawGraphics import interpolateColoursFraction

# execution related functions ---------------------------------------------------------------
#TODO can also be modularised, like ppt modules
def loadDataIntoGUI(main,libPairs,gui=True,export=True):
	projectPath = main.PM.get("projectPath")
	#if not main.PM.validateTags(["graphics"]):return False
	
	if gui:main.writeLog("\n-------------------------------------------------------\nLoading siI data into GUI")
	else:main.writeLog("\n-------------------------------------------------------\nLoading siI data")
	
	print("[siI eval] Loading graphics")
	for pair in libPairs:	#[(libPos,libNeg,label,TPS)]	#TPS = (bundleID,psname)
		#print(f"[siI eval][Debug] LibPair: {pair}")
		
		libIDs = pair[0]+pair[1]
		pairLabel = pair[2]
		bundleID,psname = pair[3]
		if len(libIDs)==0:
			main.writeError(f"No libraries selected for siI-pair {pairLabel}!")
			continue
		
		targetBundle = main.IM.getTarget(bundleID)
		countDir = os.path.join(projectPath,"Counts",bundleID,psname)
		countFile = os.path.join(countDir,"$libID_readcounts.tsv")
		resultDir = os.path.join(projectPath,"Graphics",bundleID,psname)
		Path(resultDir).mkdir(parents=True, exist_ok=True)
		#print(f"[siI eval] Countfiles: {countFile}")
		countData = lg.loadCounts(main,countFile,libIDs,targetBundle.mainLength)
		if countData is None or countData is False: 
			print("[siI eval] Error, data is None!")
			main.writeError("Error while reading counts from file!")
			continue
		#countData.printStats()
		
		strand=1	#we only want siRNAs that map to the complement of the mRNA
		length=21	#only anti-viral active siRNAs	#TODO this should be a setting if someone is interested in reads of a different length
		
		axisLabelTemplate = [("5' Position","Abundance (enriched)"),("5' Position","Abundance (control)")]
		axisLabels = list()
		graphList = list()
		for isControl in [0,1]:
			nlibs = len(pair[isControl])
			if nlibs==0:continue
			
			#TODO [regionStart-1:regionEnd] for region stuff ! ~~
			data = [None]*targetBundle.mainLength
			for position in range(1,len(data)+1):
				data[position-1] = (position,int(sum([countData.getReadCount(libID,strand,length,position) for libID in pair[isControl]])/nlibs))
			
			graphList.append(("+".join(pair[isControl]),data))
			axisLabels.append(axisLabelTemplate[isControl])
		
		graphNameA = "Abundance "+pairLabel
		#TODO maybe make this a BAR2 instead with control on negative
		graph = Combograph(main,graphNameA,targetBundle.mainSeqID+"_"+psname,graphType="BAR")
		graph.bundleID=bundleID
		graph.psname=psname
		graph.addData(graphList,globalYScale=True,axislabels=axisLabels)
		main.comboGraphs[graphNameA+"_"+psname] = graph
		print(f"[siI eval] Added {graphNameA} to comboGraphs.")
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
	
		descriptorFields = ["ID    ","3\' Pos","Cut Pos","5\' Pos","siRNA seq             ","binding seq           ",
					"count siRNA","count control","foldchange","log2FC","diff","log2Diff",
					"FCnorm","diffNorm","distNorm","revDist"]
		if strand==0:	#incase all reads are of interest, ot just the one fitting against the target
			pointDescriptor = [["siRNA-"+str(graphList[0][1][i][0]),	#ID = 5' Position on target
					graphList[0][1][i][0]+length-1,	#3' pos on target
					str(graphList[0][1][i][0]+10)+"-"+str(graphList[0][1][i][0]+11),	#cut position on target
					graphList[0][1][i][0],	#5' pos on target
					targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],
					getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],main=main),
					graphList[0][1][i][1],	#enrichment count
					graphList[1][1][i][1],	#control count
					round((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1),3),	#FC
					round(log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),3),	#logFC
					graphList[0][1][i][1]-graphList[1][1][i][1],	#diff
					round(log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1),3),	#logDiff
					0,0,0,0]
					 for i in range(len(points))]
		elif strand==1:
			pointDescriptor = [["siRNA-"+str(graphList[0][1][i][0]+length-1),	#ID = 5' Position on target
					graphList[0][1][i][0],	#3' pos on target
					str(graphList[0][1][i][0]+length-11)+"-"+str(graphList[0][1][i][0]+length-10),	#cut position on target
					graphList[0][1][i][0]+length-1,	#5' pos on target
					getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],main=main),
					targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],
					graphList[0][1][i][1],	#enrichment count
					graphList[1][1][i][1],	#control count
					round((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1),3),	#FC
					round(log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),3),	#logFC
					graphList[0][1][i][1]-graphList[1][1][i][1],	#diff
					round(log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1),3),	#logDiff
					0,0,0,0]
					 for i in range(len(points))]
		
		#New system of esiRNA candidates
		maxLog2FC = max([log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(len(points))])
		maxLog2Diff = max([log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1) for i in range(len(points))])
		distScalar = 2**0.5
		for i in range(len(points)):
			fcnorm = log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1))/maxLog2FC
			diffnorm = log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1)/maxLog2Diff
			pointDescriptor[i][-4] = round(fcnorm,3)
			pointDescriptor[i][-3] = round(diffnorm,3)
			pointDescriptor[i][-2] = round(((fcnorm)**2 + (diffnorm)**2)**0.5 /distScalar * (1 if fcnorm>0 else -1),3)
			pointDescriptor[i][-1] = round(((1-fcnorm)**2 + (1-diffnorm)**2)**0.5 /distScalar + (1 if fcnorm<0 else 0),3)
		
		graph.addPointDescriptor(descriptorFields,pointDescriptor)
		
		bestSiRNAsRev = sorted(pointDescriptor, key = lambda x:x[-1])
		filename = os.path.join(countDir,pairLabel+"_siRNA-candidates.tsv")
		with open (filename,"w") as fr:
			fr.write("\t".join(descriptorFields)+"\n")
			for point in bestSiRNAsRev:
				fr.write("\t".join([str(v) for v in point])+"\n")
	
	main.writeLog("done.\n")
	return True

