
from graphs.Combograph import Combograph
from .static import moduleID

def addGraph_LenDist(main,graphDef,libIDs,db,highlightStyles=None):
	doPercent=graphDef["percent"]
	graphList = list()
	highlighting = [dict(),dict()]
	minL=graphDef["minL"]
	maxL=graphDef["maxL"]
	for length in range(minL,maxL+1):	#Highlighting queries the xvalue, not index!
		highlighting[0][length]="colour_primary_guide"
		highlighting[1][length]="colour_primary_passenger"
	
	for libID in libIDs:
		countList = list()
		#print((maxL+1-minL))
		totalReads=0
		for length in range(minL,maxL+1):
			senseSum = db.getLengthCount(libID,0,length)
			asenseSum = db.getLengthCount(libID,1,length)
			countList.append([length,senseSum,asenseSum])
			totalReads+=senseSum+asenseSum
			
		if doPercent:
			totalReads=max(1,totalReads)
			for point in countList:
				point[1] = point[1]/totalReads*100.0
				point[2] = point[2]/totalReads*100.0
		graphList.append((libID,countList))
	
	if "hideLegend" in graphDef:
		legend=None
	else:
		legendLabels = ["forward","reverse"]
		cols = graphDef["cols"]
		legend=("Strand:",[(cols[i],label) for i,label in enumerate(legendLabels)])
	
	graphKey = f"Length-Distribution"+("_percent" if doPercent else "")		#Used for dictionary key and filename
	graphTitle = f"Length-Distribution"								#used as GUI and SVG graph title
	tabName = f"Length-Distribution"+(" (percent)" if doPercent else "")		#Used as tab name
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="BAR2",
		legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"],
		fileName=graphKey,tabName=tabName)
	graph.addData(graphList,globalYScale=graphDef["globalYScale"])
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def readAnnotation(annotation):	#TODO what if anntoation not "nice" or even correct?
	highlighting = [dict(),dict()]	#dict of position -> style; for both strands
	xLabels = dict()	#pos -> string #pseudo1_gs, si297_gs, si350_ps
	if not annotation is None:
		for strand,entrylist in enumerate(annotation):
			i=1
			#start,length,class,id,ps/gs,label
			for feature in sorted(entrylist):
				if "pseudo" in feature[3]:
					if feature[4] == "Guide":
						highlighting[strand][i]="colour_secondary_guide"
						xLabels[i]=feature[3]
					elif feature[4] == "Passenger":
						highlighting[strand][i]="colour_secondary_passenger"
					i+=1
				else:
					if feature[4] == "Guide":
						highlighting[strand][i]="colour_primary_guide"
						xLabels[i]=feature[3]
						i+=1
					elif feature[4] == "Passenger":
						highlighting[strand][i]="colour_primary_passenger"
						i+=1
	#print(highlighting)
	return highlighting,xLabels

def addGraph_annotCount(main,graphDef,libIDs,db,siRNAPos,annotation=None,highlightStyles=None):
	doPercent=graphDef["percent"]
	
	highlighting,xLabels = readAnnotation(annotation)
	
	graphList = list()
	for libID in libIDs:
		#[{3: 21, 24: 21, 45: 21, 66: 21, 89: 21, 110: 21, 131: 21, 152: 21}, {21: 21, 42: 21, 63: 21, 84: 21, 107: 21, 128: 21, 149: 21, 170: 21}]

		total21=0
		countList = [[0,0,0] for i in range(len(siRNAPos[0]))]
		#need to assign gs and ps and also differentiate them!; also pseudo, need full ID
		for i,((spos,slen),(apos,alen)) in enumerate(zip(sorted(siRNAPos[0].items()),sorted(siRNAPos[1].items()))):
			countList[i][0]=i+1
			countList[i][1]=db.getReadCount(libID,0,slen,spos)
			countList[i][2]=db.getReadCount(libID,1,alen,apos-alen+1)
		
		targetLen=21	#TODO add parameter
		for spos in range(1,db.seqLen+1):
			total21+=db.getReadCount(libID,0,targetLen,spos)+db.getReadCount(libID,1,targetLen,spos-targetLen+1)
		if doPercent:
			total21=max(1,total21)
			for point in countList:
				point[1] = point[1]/total21*100.0
				point[2] = point[2]/total21*100.0
		if len(countList)>0:
			graphList.append((libID,countList))
		else:
			print("ERROR, no counts ???")
		#print(countList)
	
	if "hideLegend" in graphDef:
		legend=None
	else:
		legendLabels = ["esiRNA guide strand","esiRNA passenger strand","pseudo guide strand","pseudo passenger strand"]	#TODO generalise these?
		cols = graphDef["cols"]
		legend=("RNA:",[(col,legendLabels[i]) for i,col in enumerate(cols)])
	
	graphKey = f"RNA-Counts"+("_percent" if doPercent else "")	#could also be generalised to "annotated counts"
	graphTitle = f"RNA Counts"
	tabName = f"RNA Counts"+(" (percent)" if doPercent else "")
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="BAR2",
		legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"],
		fileName=graphKey,tabName=tabName)
	if len(graphList)>0:graph.addData(graphList,globalYScale=graphDef["globalYScale"])
	
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	graph.setXLabels(xLabels,0)
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def addGraph_singleLengthCounts(main,graphDef,libIDs,db,annotation=None,highlightStyles=None):
	doPercent=graphDef["percent"]
	targetLen=graphDef["targetlen"]
	graphList = list()
	
	highlighting = [dict(),dict()]	#dict of position -> style
	if not annotation is None:
		for strand,entrylist in enumerate(annotation):
			#start,length,class,id,ps/gs,label
			for feature in entrylist:
				if feature[1]!=targetLen:continue
				if "pseudo" in feature[3]:
					if feature[4] == "Guide":
						highlighting[strand][feature[0]]="colour_secondary_guide"
					elif feature[4] == "Passenger":
						highlighting[strand][feature[0]]="colour_secondary_passenger"
				else:
					if feature[4] == "Guide":
						highlighting[strand][feature[0]]="colour_primary_guide"
					elif feature[4] == "Passenger":
						highlighting[strand][feature[0]]="colour_primary_passenger"
	
	for libID in libIDs:		
		total21=0
		countList = [[i,0,0] for i in range(1,db.seqLen+1)]
		for spos in range(1,db.seqLen+1):
			countList[spos-1][1]=db.getReadCount(libID,0,targetLen,spos)
			if spos>=targetLen:countList[spos-1][2]=db.getReadCount(libID,1,targetLen,spos-targetLen+1)
			total21+=db.getReadCount(libID,0,targetLen,spos)+db.getReadCount(libID,1,targetLen,spos-targetLen+1)
		if doPercent:
			total21=max(1,total21)
			for point in countList:
				point[1] = point[1]/total21*100.0
				point[2] = point[2]/total21*100.0
		graphList.append((libID,countList))
	
	if "hideLegend" in graphDef:
		legend=None
	else:
		if len(highlighting[0])+len(highlighting[0])>0:
			legendLabels = ["esiRNA guide strand","esiRNA passenger strand","pseudo guide strand","pseudo passenger strand"]
			cols = graphDef["cols"]
			legend=("Read start-position:",[(col,legendLabels[i]) for i,col in enumerate(cols)])
		else:
			legend=None
	
	graphKey = f"Read-Counts"+("_percent" if doPercent else "")
	graphTitle = f"Read Counts"
	tabName = f"Read Counts"+(" (percent)" if doPercent else "")
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="BAR2",
		legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"],
		fileName=graphKey,tabName=tabName)
	graph.addData(graphList,globalYScale=graphDef["globalYScale"])
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def addGraph_singleLengthCoverage(main,graphDef,libIDs,db,siRNAPos,annotation=None,highlightStyles=None):
	targetLen=graphDef["targetlen"]
	
	highlighting = [dict(),dict()]	#dict of position -> style
	if not annotation is None:
		strand=0
		entrylist=annotation[0]
		for feature in entrylist:
			if feature[1]!=targetLen:continue
			if "pseudo" in feature[3]:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="colour_secondary_guide"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="colour_secondary_passenger"
			else:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="colour_primary_guide"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="colour_primary_passenger"
		strand=1
		entrylist=annotation[1]
		for feature in entrylist:
			if feature[1]!=targetLen:continue
			if "pseudo" in feature[3]:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="colour_secondary_guide"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="colour_secondary_passenger"
			else:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="colour_primary_guide"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="colour_primary_passenger"
	
	graphList = list()
	for libID in libIDs:
		coverage = [[i,0,0,0,0] for i in range(1,db.seqLen+1)]	#per position
		for spos in range(1,db.seqLen+1):
			senseCount = db.getReadCount(libID,0,targetLen,spos)
			if senseCount>0:
				for cpos in range(spos,spos+targetLen):coverage[cpos-1][3]+=senseCount
				if spos in siRNAPos[0] and siRNAPos[0][spos]==targetLen:
					for cpos in range(spos,spos+targetLen):coverage[cpos-1][1]+=senseCount
			
			revCount = db.getReadCount(libID,1,targetLen,spos)
			if revCount>0:
				for cpos in range(spos,spos+targetLen): coverage[cpos-1][4]+=revCount
				if spos+targetLen-1 in siRNAPos[1] and siRNAPos[1][spos+targetLen-1]==targetLen:
					for cpos in range(spos,spos+targetLen): coverage[cpos-1][2]+=revCount
		graphList.append((libID,coverage))
	
	if "hideLegend" in graphDef:
		legend=None
	else:
		if len(highlighting[0])+len(highlighting[0])>0:
			legendLabels = ["esiRNA guide strand","esiRNA passenger strand","pseudo guide strand","pseudo passenger strand"]
			cols = graphDef["cols"]
			ledDesc = [("black",str(targetLen)+"nt reads")]
			ledDesc.extend([(col,legendLabels[i]) for i,col in enumerate(cols)])
			legend=("Coverage:",ledDesc)
		else:
			legend=("Coverage:",[("black",str(targetLen)+"nt reads")])
	
	graphKey = f"Coverage-{targetLen}"
	graphTitle = f"Coverage of {targetLen}-nt long reads"
	tabName = f"Coverage {targetLen}"
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="BAR2",
		legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"],
		fileName=graphKey,tabName=tabName)
	graph.addData(graphList,globalYScale=graphDef["globalYScale"])
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def addGraph_multiLengthCoverage(main,graphDef,libIDs,db):
	targetLengths=[int(p[0]) for p in graphDef["targets"]]
	graphList = list()
	for libID in libIDs:
		coverage = [[0]*(len(targetLengths)*2+1) for i in range(1,db.seqLen+1)]	#per position
		for i in range(1,db.seqLen+1):
			coverage[i-1][0] = i
		for i,targetLen in enumerate(targetLengths):
			for spos in range(1,db.seqLen+1):
				senseCount = db.getReadCount(libID,0,targetLen,spos)
				if senseCount>0:
					for cpos in range(spos,spos+targetLen):coverage[cpos-1][i*2+1]+=senseCount
				
				revCount = db.getReadCount(libID,1,targetLen,spos)
				if revCount>0:
					for cpos in range(spos,spos+targetLen): coverage[cpos-1][i*2+2]+=revCount
		graphList.append((libID,coverage))
	
	if "hideLegend" in graphDef:
		legend=None
	else:
		legend=("Coverage:",[(p[1],str(p[0])+"nt") for p in graphDef["targets"]])
	
	lineColours = [graphDef["targets"][int(i/2)][1] for i in range(len(targetLengths)*2)]
	graphKey = f"MultiCoverage_"+"".join(["l"+str(l) for l in targetLengths])
	graphTitle = f"Coverage of multiple lengths"
	tabName = f"MultiCoverage"
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="multiLine",
		legend=legend,xlab=graphDef["xlab"],ylab=graphDef["ylab"],lineColours=lineColours,
		fileName=graphKey,tabName=tabName)
	graph.addData(graphList,globalYScale=graphDef["globalYScale"])
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def addGraph_coverage(main,graphDef,libIDs,db):	#Unused
	graphList = list()
	for libID in libIDs:
		coverage = [[i,0,0,0,0] for i in range(1,db.seqLen+1)]	#per position
		for targetLen in range(15,30):	# use parameters for this # is not use anymore / right now
			for spos in range(1,db.seqLen+1):
				if db.getReadCount(libID,0,targetLen,spos)>0:
					for cpos in range(spos,spos+targetLen):
						coverage[cpos-1][3]+=db.getReadCount(libID,0,targetLen,spos)
				if db.getReadCount(libID,1,targetLen,spos)>0:
					for cpos in range(spos,spos+targetLen):
						coverage[cpos-1][4]+=db.getReadCount(libID,1,targetLen,spos)
				
		graphList.append((libID,coverage))
	
	graphKey = f"FullCoverage"
	graphTitle = f"Coverage over all lengths"
	tabName = f"Full Coverage"
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="BAR2",
		xlab=graphDef["xlab"],ylab=graphDef["ylab"],
		fileName=graphKey,tabName=tabName)
	graph.addData(graphList,globalYScale=graphDef["globalYScale"])
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def addGraph_heatmap(main,graphDef,libIDs,db,annotation=None,highlightStyles=None):
	graphList = list()
	highlightEsis=graphDef["highlightEsis"]
	highlightFrames=graphDef["highlightFrames"]
	minL=graphDef["minLen"]
	maxL=graphDef["maxLen"]
	midpointPercentile=graphDef["middlePercentile"]
	
	for libID in libIDs:
		heatmap = list()	#pos x [rev,-1,for]
		lengthList = list(range(minL,maxL+1))
		lengthList.append(-1)
		lengthList.extend(list(range(minL,maxL+1)))
		posList = list(range(1,db.seqLen+1))
		for spos in range(1,db.seqLen+1):
			posCounts = [db.getReadCount(libID,1,targetLen,spos+1-targetLen) for targetLen in range(minL,maxL+1)]
			posCounts.append(-1)
			posCounts.extend([db.getReadCount(libID,0,targetLen,spos) for targetLen in range(minL,maxL+1)])
			heatmap.append(posCounts)
		heatGraph = [heatmap,lengthList,posList]
		graphList.append((libID,heatGraph))
	
	#set of (pos,len)
	highlighting = set()
	if not annotation is None:
		for strand,entrylist in enumerate(annotation):
			for feature in entrylist:
				if strand==0:
					highlighting.add((feature[0]-1,feature[1]+maxL+1-minL-minL+1))
				else:
					highlighting.add((feature[0]-1,feature[1]-minL))
	
	for length in highlightFrames:
		for i in range(0,db.seqLen,length):
			highlighting.add((i+2,length+maxL+1-minL-minL+1))
			highlighting.add((db.seqLen-i-3,length-minL))
	
	if "hideLegend" in graphDef:
		legend=None
	else:
		legend=("Count:",[("#000000","0"),("#000064",">0"),("#00ffff","95th percentile"),("#ff0000","max")])	#TODO overwritten, but used to check for stuff..
	
	colourscale_define = [(("abs",0),(0,0,0)), (("abs",1),(0,0,100)), (("rel","percentile",midpointPercentile),(0,255,255)), (("rel","max"),(255,0,0))]
	
	graphKey = f"Heatmap"
	graphTitle = f"Heatmap over all lengths and positions"
	tabName = f"Heatmap"
	graph = Combograph(main,graphTitle,graphDef["mainTargetSeqID"]+"_"+graphDef["psname"]+"_"+moduleID,graphType="HEAT",
		legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"],
		fileName=graphKey,tabName=tabName)
	graph.bundleID=graphDef["bundleID"]
	graph.psname=graphDef["psname"]
	graph.addData(graphList,colourscale_define=colourscale_define)
	main.comboGraphs[graphKey+graphDef["bundleID"]+graphDef["psname"]] = graph

def getGraphKey(graphDef):
	if graphDef[0]=="startPos":
		doPercent=graphDef["percent"]
		targetLen=graphDef["targetlen"]
		graphKey = f"Read-Counts"+("_percent" if doPercent else "")
	elif graphDef[0]=="singleCov":
		targetLen=graphDef["targetlen"]
		graphKey = f"Coverage-{targetLen}"
	elif graphDef[0]=="multiCov":
		targetLengths=[int(p[0]) for p in graphDef["targets"]]
		graphKey = f"MultiCoverage_"+"".join(["l"+str(l) for l in targetLengths])
	return graphKey

def loadGraphs(main,db,libIDs,wantedgraphs,siRNAPos,annotation=None,highlightStyles=None):
	for graphDef in wantedgraphs:	#create grpahs based on the data
		if graphDef[0]=="lendist":
			addGraph_LenDist(main,graphDef,libIDs,db,highlightStyles=highlightStyles)
		elif graphDef[0]=="annotCount":
			if not annotation is None:
				addGraph_annotCount(main,graphDef,libIDs,db,siRNAPos,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="startPos":
			addGraph_singleLengthCounts(main,graphDef,libIDs,db,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="singleCov":
			addGraph_singleLengthCoverage(main,graphDef,libIDs,db,siRNAPos,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="multiCov":
			addGraph_multiLengthCoverage(main,graphDef,libIDs,db)
		elif graphDef[0]=="heapmap":
			addGraph_heatmap(main,graphDef,libIDs,db,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="coverageAll":
			addGraph_coverage(main,graphDef,libIDs,db)
		else:
			main.writeError(f"Unknown graph type: {graphDef[0]}",terminalPrefix="[dsP module]")
	
	connectGraphs = {"startPos","singleCov","multiCov"}
	for graphDef in [g for g in wantedgraphs if g[0] in connectGraphs]:		#connecting all of these grphs afterwards
		for graphDef2 in [g for g in wantedgraphs if g[0] in connectGraphs]:	#doesnt care about different lengths between single-length coverage
			main.comboGraphs[getGraphKey(graphDef)+graphDef["bundleID"]+graphDef["psname"]].addConnectedGraph(
				main.comboGraphs[getGraphKey(graphDef2)+graphDef2["bundleID"]+graphDef2["psname"]])

