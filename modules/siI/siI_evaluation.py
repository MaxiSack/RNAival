
import os.path
from pathlib import Path
from math import log2
from itertools import chain

from iostuff.loadCounts import loadCounts
from graphs.Combograph import Combograph
from functions.baseFunctions import getReverseSeq
from graphs.drawGraphics import interpolateColoursFraction

from .static import moduleID

def loadDataIntoGUI(main,libPairs,params,gui=True,export=True):
	
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
	hideLabels = main.PM.get("RNAival-hide_Labels_Legends")
	for pair in libPairs:	#[(libPos,libNeg,label,TPS,start,end)]	#TPS = (bundleID,psname)
		libIDs = pair[0]+pair[1]
		pairLabel = pair[2]
		bundleID,psname = pair[3]
		regionStart = pair[4]
		regionEnd = pair[5]
		regionlength = regionEnd-regionStart+1
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
		
		axisLabelTemplate = [("5' Position on target","Abundance (enriched)"),("5' Position on target","Abundance (control)")]
		axisLabels = list()
		graphList = list()
		for isControl in [0,1]:
			nlibs = len(pair[isControl])
			if nlibs==0:continue
			data = [None]*regionlength
			for position in range(regionStart,regionEnd+1):
				data[position-regionStart] = (position,int(sum([countData.getReadCount(libID,strand,length,position) for libID in pair[isControl]])/nlibs))
			
			graphList.append(("+".join(pair[isControl]),data))
			axisLabels.append(axisLabelTemplate[isControl])
		
		
		
		descriptorFields = ["Source","ID    ","3\' Pos","Cut Pos","5\' Pos","siRNA seq            ","binding seq          ","count enriched"]
		if strand==0:	#incase all reads are of interest, or just the one fitting against the target
			pointDescriptor = [[pairLabel,
					"siRNA-"+str(graphList[0][1][i][0]),	#ID = 5' Position on target
					graphList[0][1][i][0]+length-1,			#3' pos on target
					str(graphList[0][1][i][0]+10)+"-"+str(graphList[0][1][i][0]+11),	#cut position on target
					graphList[0][1][i][0],				#5' pos on target
					targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],
					getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],main=main),
					graphList[0][1][i][1]]				#enrichment count
					 for i in range(regionlength)]
		elif strand==1:
			pointDescriptor = [[pairLabel,
					"siRNA-"+str(graphList[0][1][i][0]+length-1),	#ID = 5' Position on target
					graphList[0][1][i][0],				#3' pos on target
					str(graphList[0][1][i][0]+length-11)+"-"+str(graphList[0][1][i][0]+length-10),	#cut position on target
					graphList[0][1][i][0]+length-1,			#5' pos on target
					getReverseSeq(targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],main=main),
					targetBundle.mainSequence[graphList[0][1][i][0]-1:graphList[0][1][i][0]+length-1],
					graphList[0][1][i][1]]				#enrichment count
					 for i in range(regionlength)]
		
		if len(graphList) ==1:
			# ------------- Abundance Bar graph -------------------
			graphKeyA = f"Abundance_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
			graphA = Combograph(main,graphKeyA,targetBundle.mainSeqID+"_"+psname+"_"+moduleID,graphType="BAR2",isScrollGraph=False)
			graphA.bundleID=bundleID
			graphA.psname=psname
			graphA.addData(graphList,globalYScale=True,axislabels=axisLabels if not hideLabels else None)
			main.comboGraphs[graphKeyA+"_"+psname] = graphA
			#print(f"[siI eval] Added {graphKeyA} to comboGraphs.")
			
			maxCount = max([graphList[0][1][i][1] for i in range(regionlength)])
			for i in range(regionlength):
				pointDescriptor[i][-1] = round(graphList[0][1][i][1]/maxCount,3)
			graphA.addPointDescriptor(descriptorFields,pointDescriptor)	#so that textoutput appears when a bar is selected
		elif len(graphList) ==2:
			# ------------- Abundance Bar2 graph -------------------
			graphKeyA = f"Abundance_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"		#Used for dictionary key and filename
			graphTitleA = f"{pairLabel} - Abundance: l{length}, s{strand}, {regionStart}-{regionEnd}"	#used as GUI and SVG graph title
			tabNameA = f"{pairLabel} - Abundance"											#Used as tab name
			graphA = Combograph(main,graphTitleA,targetBundle.mainSeqID+"_"+psname+"_"+moduleID,graphType="BAR2",isScrollGraph=False,fileName=graphKeyA,tabName=tabNameA)
			graphA.bundleID=bundleID
			graphA.psname=psname
			counts2 = [(graphList[0][1][i][0],graphList[0][1][i][1],graphList[1][1][i][1])
						 for i in range(regionlength)]
			counts2Graph = ("",counts2)	#single graph gets no extra title
			graphA.addData([counts2Graph],axislabels=[("5' Position on target","Abundance (enriched: +, control: -)")] if not hideLabels else None)
			main.comboGraphs[graphKeyA+"_"+psname] = graphA
			
			# ------------- Volcano-like scatter graph -------------------
			graphKeyV = f"Foldchange_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
			graphTitleV = f"{pairLabel} - Foldchange: l{length}, s{strand}, {regionStart}-{regionEnd}"
			tabNameV = f"{pairLabel} - Foldchange"
			graphV = Combograph(main,graphTitleV,targetBundle.mainSeqID+"_"+psname+"_"+moduleID,graphType="SCATTER",isScrollGraph=False,fileName=graphKeyV,tabName=tabNameV)
			graphV.bundleID=bundleID
			graphV.psname=psname
			points = [(graphList[0][1][i][0],log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
					for i in range(regionlength)]
			
			# ------------- diff Bar graph -------------------
			#pointHeatValues = [log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(regionlength)]
			#maxHeat = max(max(pointHeatValues),1)
			#col1 = "#000000"
			#col2 = "#00ff00"
			#pointColours = [interpolateColoursFraction(val/maxHeat, col1, col2) for val in pointHeatValues]
			#logPoolCounts = [(graphList[0][1][i][0],graphList[0][1][i][0],log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1))
			#			 for i in range(regionlength)]
			#logPoolGraph = (graphList[0][0]+"_log",logPoolCounts)
			#graphV.addData([(graphList[0][0]+"_Volcano",points),logPoolGraph],
			#	axislabels=[("Log2 Foldchange","Log2 Difference"),("Position","Log2 Difference")])
			graphV.addData([("",points)],	#Only show volcano
				axislabels=[("Log2 Foldchange","Log2 Difference")] if not hideLabels else None)
			
			main.comboGraphs[graphKeyV+"_"+psname] = graphV
			
			# ------------- fill out remaining fields -------------------
			for i in range(len(points)):
				descriptorFields.extend(["count control","foldchange","log2FC","diff","log2Diff"])
				pointDescriptor[i].extend([
					graphList[1][1][i][1],							#control count
					round((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1),3),		#FC
					round(log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)),3),	#logFC
					graphList[0][1][i][1]-graphList[1][1][i][1],				#diff
					round(log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1),3)])	#logDiff
			
			maxLog2FC = max([log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1)) for i in range(len(points))])
			maxLog2Diff = max([log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1) for i in range(len(points))])
			distScalar = 2**0.5	#sqrt(2) to bring the normed diagonal into [0,1]
			if maxLog2FC>0 and maxLog2Diff>0:
				for i in range(len(points)):
					descriptorFields.extend(["FCnorm","diffNorm","distNorm","revDist","score"])
					fcnorm = log2((graphList[0][1][i][1]+1)/(graphList[1][1][i][1]+1))/maxLog2FC
					diffnorm = log2(abs(graphList[0][1][i][1]-graphList[1][1][i][1])+1)/maxLog2Diff
					pointDescriptor[i].extend([
						round(fcnorm,3),									#FC normed
						round(diffnorm,3),									#Diff normed
						round(((fcnorm)**2 + (diffnorm)**2)**0.5 /distScalar * (1 if fcnorm>0 else -1),3),	#Dist-to-(0,0)
						round(((1-fcnorm)**2 + (1-diffnorm)**2)**0.5 /distScalar + (1 if fcnorm<0 else 0),3)])	#Dist-to-(max,max)
					pointDescriptor[i].append(round(1-pointDescriptor[i][-1],3))					#score is always last
			
			descriptorFieldsShort = descriptorFields[0:10]+[descriptorFields[-1]]
			pointDescriptorShort = [None]*len(points)
			for i in range(len(points)):
				pointDescriptorShort[i] = pointDescriptor[i][0:10]+[pointDescriptor[i][-1]]
			graphV.addPointDescriptor(descriptorFieldsShort,pointDescriptorShort)
			
			if False:
				# ------------- Score graph -------------------
				graphNameS = f"Score_{pairLabel}_l{length}-s{strand}_{regionStart}-{regionEnd}"
				graphS = Combograph(main,graphNameS,targetBundle.mainSeqID+"_"+psname+"_"+moduleID,graphType="BAR2",isScrollGraph=False)
				graphS.bundleID=bundleID
				graphS.psname=psname
				scoreCounts = [(
						graphList[0][1][i][0],
						pointDescriptor[i][-1]  if pointDescriptor[i][-1]>0 else 0,
						-pointDescriptor[i][-1] if pointDescriptor[i][-1]<0 else 0
						) for i in range(regionlength)]
				scoreGraph = ("",scoreCounts)
				graphS.addData([scoreGraph],axislabels=[("5' Position","Score")])
				main.comboGraphs[graphNameS+"_"+psname] = graphS
				
				# ---- connect graphs for interactivity -----
				#main.comboGraphs[graphKeyA+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameS+"_"+psname])
				#main.comboGraphs[graphKeyV+"_"+psname].addConnectedGraph(main.comboGraphs[graphNameS+"_"+psname])
				#main.comboGraphs[graphNameS+"_"+psname].addConnectedGraph(main.comboGraphs[graphKeyA+"_"+psname])
				#main.comboGraphs[graphNameS+"_"+psname].addConnectedGraph(main.comboGraphs[graphKeyV+"_"+psname])
			
			# ---- connect graphs for interactivity -----
			main.comboGraphs[graphKeyA+"_"+psname].addConnectedGraph(main.comboGraphs[graphKeyV+"_"+psname])
			main.comboGraphs[graphKeyV+"_"+psname].addConnectedGraph(main.comboGraphs[graphKeyA+"_"+psname])
		
		bestSiRNAsRev = sorted(pointDescriptor, key = lambda x:x[-1],reverse=True)
		filename = os.path.join(countDir,pairLabel+f"_siRNA-candidates_l{length}-s{strand}_{regionStart}-{regionEnd}.tsv")
		with open (filename,"w") as fr:
			fr.write("\t".join(descriptorFields)+"\n")
			for point in bestSiRNAsRev:
				fr.write("\t".join([str(v) for v in point])+"\n")
		
	
	main.writeLog("done.\n")
	return True

