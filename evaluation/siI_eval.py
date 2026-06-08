
import os.path
from pathlib import Path
from math import log2
from itertools import chain

from evaluation.loadGraphs import loadCounts
from graphs.Combograph import Combograph
from functions.baseFunctions import getReverseSeq
from graphs.drawGraphics import interpolateColoursFraction

#TODO can also be modularised, like ppt modules
def loadDataIntoGUI(main,libPairs,params,gui=True,export=True):
	#if not main.PM.validateTags(["graphics"]):return False
	
	if gui:main.writeLog("\n-------------------------------------------------------\nLoading siI data into GUI")
	else:main.writeLog("\n-------------------------------------------------------\nLoading siI data")
	
		
	length = params["siI-siRNAlength"]
	strandStr = params["siI-strand"]
	if strandStr=="reverse":strand=1
	elif strandStr=="forward":strand=0
	elif strandStr == "both":
		main.writeError("\"Both\" is currently not supported for siI.")
		return
	print("[siI eval] Loading graphics")
	for pair in libPairs:	#[(libPos,libNeg,label,TPS,start,end)]	#TPS = (bundleID,psname)
		libIDs = pair[0]+pair[1]
		pairLabel = pair[2]
		bundleID,psname = pair[3]
		regionStart = pair[4]
		regionEnd = pair[5]
		if len(libIDs)==0:
			main.writeError(f"No libraries selected for siI-pair {pairLabel}!")
			continue
		
		targetBundle = main.IM.getTarget(bundleID)
		countDir = os.path.join(main.PM.get("projectPath"),"Counts",bundleID,psname)
		countFile = os.path.join(countDir,"$libID_readcounts.tsv")
		resultDir = os.path.join(main.PM.get("projectPath"),"Graphics",bundleID,psname)
		Path(resultDir).mkdir(parents=True, exist_ok=True)
		#print(f"[Debug][siI eval] Countfiles: {countFile}")
		countData = loadCounts(main,countFile,libIDs,targetBundle.mainLength)
		if countData is None or countData is False: 
			print("[siI eval] Error, data is None!")
			main.writeError("Error while reading counts from file!")
			continue
		#countData.printStats()
		
		axisLabelTemplate = [("5' Position","Abundance (enriched)"),("5' Position","Abundance (control)")]
		axisLabels = list()
		graphList = list()
		for isControl in [0,1]:
			nlibs = len(pair[isControl])
			if nlibs==0:continue
			data = [None]*(regionEnd-regionStart+1)
			for position in range(regionStart,regionEnd+1):
				data[position-regionStart] = (position,int(sum([countData.getReadCount(libID,strand,length,position) for libID in pair[isControl]])/nlibs))
			
			graphList.append(("+".join(pair[isControl]),data))
			axisLabels.append(axisLabelTemplate[isControl])
		
		
		
		descriptorFields = ["ID    ","3\' Pos","Cut Pos","5\' Pos","siRNA seq             ","binding seq           ",
					"count siRNA","count control","foldchange","log2FC","diff","log2Diff",
					"FCnorm","diffNorm","distNorm","revDist","score"]
		if strand==0:	#incase all reads are of interest, or just the one fitting against the target
			pointDescriptor = [["siRNA-"+str(graphList[0][1][i][0]),	#ID = 5' Position on target
					graphList[0][1][i][0]+length-1,			#3' pos on target
					str(graphList[0][1][i][0]+10)+"-"+str(graphList[0][1][i][0]+11),	#cut position on target
					graphList[0][1][i][0],				#5' pos on target
					targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],
					getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],main=main),
					graphList[0][1][i][1],				#enrichment count
					"-","-","-","-","-","-","-","-","-","-"]
					 for i in range(len(graphList[0][1]))]
		elif strand==1:
			pointDescriptor = [["siRNA-"+str(graphList[0][1][i][0]+length-1),	#ID = 5' Position on target
					graphList[0][1][i][0],				#3' pos on target
					str(graphList[0][1][i][0]+length-11)+"-"+str(graphList[0][1][i][0]+length-10),	#cut position on target
					graphList[0][1][i][0]+length-1,			#5' pos on target
					getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],main=main),
					targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],
					graphList[0][1][i][1],				#enrichment count
					"-","-","-","-","-","-","-","-","-","-"]
					 for i in range(len(graphList[0][1]))]
		
		if len(graphList) ==1:
			# ------------- Abundance Bar graph -------------------
			graphNameA = f"Abundance_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
			graphA = Combograph(main,graphNameA,targetBundle.mainSeqID+"_"+psname,graphType="BAR")
			graphA.bundleID=bundleID
			graphA.psname=psname
			graphA.addData(graphList,globalYScale=True,axislabels=axisLabels)
			main.comboGraphs[graphNameA+"_"+psname] = graphA
			print(f"[siI eval] Added {graphNameA} to comboGraphs.")
			
			maxCount = max([graphList[0][1][i][1] for i in range(len(points))])
			for i in range(len(points)):
				pointDescriptor[i][-1] = round(graphList[0][1][i][1]/maxCount,3)
			graphA.addPointDescriptor(descriptorFields,pointDescriptor)	#so that textoutput appears when a bar is selected
		elif len(graphList) ==2:
			# ------------- Abundance Bar2 graph -------------------
			graphNameA = f"Abundance_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
			graphA = Combograph(main,graphNameA,targetBundle.mainSeqID+"_"+psname,graphType="BAR2")
			graphA.bundleID=bundleID
			graphA.psname=psname
			counts2 = [(graphList[0][1][i][0],graphList[0][1][i][1],graphList[1][1][i][1])
						 for i in range(len(graphList[0][1]))]
			counts2Graph = (graphList[0][0]+"_count2",counts2)
			graphA.addData([counts2Graph],axislabels=[("5' Position","Count")])
			main.comboGraphs[graphNameA+"_"+psname] = graphA
			
			# ------------- Volcano-like scatter graph -------------------
			graphNameV = f"Foldchange_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
			graphV = Combograph(main,graphNameV,targetBundle.mainSeqID+"_"+psname,graphType="SCATTER")
			graphV.bundleID=bundleID
			graphV.psname=psname
			points = [(graphList[0][1][i][0],log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
					for i in range(len(graphList[0][1]))]
			
			# ------------- diff Bar graph -------------------
			#pointHeatValues = [log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(len(graphList[0][1]))]
			#maxHeat = max(max(pointHeatValues),1)
			#col1 = "#000000"
			#col2 = "#00ff00"
			#pointColours = [interpolateColoursFraction(val/maxHeat, col1, col2) for val in pointHeatValues]
			#logPoolCounts = [(graphList[0][1][i][0],graphList[0][1][i][0],log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
			#			 for i in range(len(graphList[0][1]))]
			#logPoolGraph = (graphList[0][0]+"_log",logPoolCounts)
			#graphV.addData([(graphList[0][0]+"_Volcano",points),logPoolGraph],colouroverride=[None,pointColours],
			#	axislabels=[("Log2 Foldchange","Log2 Difference"),("Position","Log2 Difference")])
			graphV.addData([(graphList[0][0]+"_Volcano",points)],	#Only show volcano
				axislabels=[("Log2 Foldchange","Log2 Difference")])
			
			main.comboGraphs[graphNameV+"_"+psname] = graphV
			
			# ------------- fill out remaining fields -------------------
			for i in range(len(points)):
				pointDescriptor[i][7] = graphList[1][1][i][1]							#control count
				pointDescriptor[i][8] = round((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1),3)		#FC
				pointDescriptor[i][9] = round(log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),3)	#logFC
				pointDescriptor[i][10] = graphList[0][1][i][1]-graphList[1][1][i][1]				#diff
				pointDescriptor[i][11] = round(log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1),3)	#logDiff
			
			maxLog2FC = max([log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(len(points))])
			maxLog2Diff = max([log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1) for i in range(len(points))])
			distScalar = 2**0.5	#sqrt(2) to bring the normed diagonal into [0,1]
			if maxLog2FC>0 and maxLog2Diff>0:
				for i in range(len(points)):
					fcnorm = log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1))/maxLog2FC
					pointDescriptor[i][12] = round(fcnorm,3)						#FC normed
					diffnorm = log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1)/maxLog2Diff
					pointDescriptor[i][13] = round(diffnorm,3)						#Diff normed
					pointDescriptor[i][14] = round(((fcnorm)**2 + (diffnorm)**2)**0.5 /distScalar * (1 if fcnorm>0 else -1),3)	#Dist-to-(0,0)
					pointDescriptor[i][15] = round(((1-fcnorm)**2 + (1-diffnorm)**2)**0.5 /distScalar + (1 if fcnorm<0 else 0),3)	#Dist-to-(max,max)
					
					pointDescriptor[i][-1] = round(1-pointDescriptor[i][15],3)				#score is always last
			
			graphV.addPointDescriptor(descriptorFields,pointDescriptor)
			
			if False:
				# ------------- Score graph -------------------
				graphNameS = f"Score_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
				graphS = Combograph(main,graphNameS,targetBundle.mainSeqID+"_"+psname,graphType="BAR2")
				graphS.bundleID=bundleID
				graphS.psname=psname
				scoreCounts = [(
						graphList[0][1][i][0],
						pointDescriptor[i][-1]  if pointDescriptor[i][-1]>0 else 0,
						-pointDescriptor[i][-1] if pointDescriptor[i][-1]<0 else 0
						) for i in range(len(graphList[0][1]))]
				scoreGraph = (graphList[0][0]+"_score",scoreCounts)
				graphS.addData([scoreGraph],axislabels=[("5' Position","Score")])
				main.comboGraphs[graphNameS+"_"+psname] = graphS
				
				# ---- connect graphs for interactivity -----
				#main.comboGraphs[graphNameA+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameS+"_"+psname])
				#main.comboGraphs[graphNameV+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameS+"_"+psname])
				#main.comboGraphs[graphNameS+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameA+"_"+psname])
				#main.comboGraphs[graphNameS+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameV+"_"+psname])
			
			# ---- connect graphs for interactivity -----
			main.comboGraphs[graphNameA+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameV+"_"+psname])
			main.comboGraphs[graphNameV+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameA+"_"+psname])
		
		bestSiRNAsRev = sorted(pointDescriptor, key = lambda x:x[-1],reverse=True)
		filename = os.path.join(countDir,pairLabel+f"_siRNA-candidates_l{length}-s{strand}_{regionStart}-{regionEnd}.tsv")
		with open (filename,"w") as fr:
			fr.write("\t".join(descriptorFields)+"\n")
			for point in bestSiRNAsRev:
				fr.write("\t".join([str(v) for v in point])+"\n")
	
	main.writeLog("done.\n")
	return True

