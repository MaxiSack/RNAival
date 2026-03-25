
import os.path

from graphs.Combograph import Combograph
from iostuff.readCountDB import ReadCountsDatabase

def showGraphs(basegui,resultDir,fontmultiplier=1.0):
	if basegui.comboGraphs is None:
		basegui.writeError("\tERROR Data not loaded!")
		print("[LoadGraphs] ERROR Data not loaded!")
		return False
	#print("[LoadGraphs][Debug] "+str(basegui.comboGraphs.items()))
	for graph in basegui.comboGraphs.values():
		#print("[Debug] displaying "+str(graph.title))
		graph.generateIGs(basegui,resultDir)
		graph.drawOntoGui(fontmultiplier=fontmultiplier)
	return True

def exportGraphs(basegui,resultsPath,exportW,exportH,exportFontsize):
	if basegui.comboGraphs is None:
		basegui.writeError("\tERROR Data not loaded!")
		print("[LoadGraphs] ERROR Data not loaded!")
		return False
	for graph in basegui.comboGraphs.values():
		graph.exportAsSVG(resultsPath,exportW,exportH,exportFontsize)
	return True

def setStyles(basegui,highlightStyles):
	if basegui.comboGraphs is None:
		basegui.writeError("\tERROR Data not loaded!")
		print("[LoadGraphs] ERROR Data not loaded!")
		return False
	for graph in basegui.comboGraphs.values():
		graph.setStyles(highlightStyles)
	return True

def addGraph_LenDist(basegui,graphDef,libIDs,db,highlightStyles=None):
	doPercent=graphDef["percent"]
	graphtype="lengths"+("_percent" if doPercent else "")
	graphList = list()
	highlighting = [dict(),dict()]
	minL=graphDef["minL"]
	maxL=graphDef["maxL"]
	for length in range(minL,maxL+1):	#Highlighting queries the xvalue, not index!
		highlighting[0][length]="esiGS"
		highlighting[1][length]="esiPS"
	#print("LendistHighlights")
	#print(highlighting)
	#print(graphDef)
	for libID in libIDs:
		countList = list()
		print((maxL+1-minL))
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
		#print(countList)
	#print("")
	legendLabels = ["positive","negative"]
	cols = graphDef["cols"]
	legend=("Strand:",[(cols[i],label) for i,label in enumerate(legendLabels)])
	if "hideLegend" in graphDef:legend=None
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="BAR2",legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"])
	graph.addData(graphList)
	#graph.cutOuterXLabs()
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph

def readAnnotation(annotation):	#TODO what if anntoation not "nice" or even?
	highlighting = [dict(),dict()]	#dict of position -> style; for both strands
	xLabels = dict()	#pos -> string #pseudo1_gs, si297_gs, si350_ps
	if not annotation is None:
		for strand,entrylist in enumerate(annotation):
			i=1
			#start,length,class,id,ps/gs,label
			for feature in sorted(entrylist):
				if "pseudo" in feature[3]:
					if feature[4] == "Guide":
						highlighting[strand][i]="pseudoGS"
						xLabels[i]=feature[3]
					elif feature[4] == "Passenger":
						highlighting[strand][i]="pseudoPS"
					i+=1
				else:
					if feature[4] == "Guide":
						highlighting[strand][i]="esiGS"
						xLabels[i]=feature[3]
						i+=1
					elif feature[4] == "Passenger":
						highlighting[strand][i]="esiPS"
						i+=1
	#print(highlighting)
	return highlighting,xLabels

def addGraph_esiCounts(basegui,graphDef,libIDs,db,siRNAPos,annotation=None,highlightStyles=None):
	doPercent=graphDef["percent"]
	
	highlighting,xLabels = readAnnotation(annotation)
	
	graphtype="esiCounts"+("_percent" if doPercent else "")
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
		
		targetLen=21
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
	
	legendLabels = ["esiRNA guide strand","esiRNA passenger strand","pseudo guide strand","pseudo passenger strand"]
	cols = graphDef["cols"]
	legend=("esiRNA:",[(col,legendLabels[i]) for i,col in enumerate(cols)])
	#print("")
	if "hideLegend" in graphDef:legend=None
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="BAR2",legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"])
	if len(graphList)>0:graph.addData(graphList)
	#print("\nXlabels:")
	#print(xLabels)
	graph.setXLabels(xLabels,graphDef["xlabSpace"])
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph

def addGraph_singleLengthCounts(basegui,graphDef,libIDs,db,annotation=None,highlightStyles=None):
	doPercent=graphDef["percent"]#False
	targetLen=graphDef["targetlen"]
	graphtype="Counts_l"+str(targetLen)+("_percent" if doPercent else "")
	graphList = list()
	
	highlighting = [dict(),dict()]	#dict of position -> style
	if not annotation is None:
		for strand,entrylist in enumerate(annotation):
			#start,length,class,id,ps/gs,label
			for feature in entrylist:
				if feature[1]!=targetLen:continue
				if "pseudo" in feature[3]:
					if feature[4] == "Guide":
						highlighting[strand][feature[0]]="pseudoGS"
					elif feature[4] == "Passenger":
						highlighting[strand][feature[0]]="pseudoPS"
				else:
					if feature[4] == "Guide":
						highlighting[strand][feature[0]]="esiGS"
					elif feature[4] == "Passenger":
						highlighting[strand][feature[0]]="esiPS"
	
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
	
	if len(highlighting[0])+len(highlighting[0])>0:
		legendLabels = ["esiRNA guide strand","esiRNA passenger strand","pseudo guide strand","pseudo passenger strand"]
		cols = graphDef["cols"]
		legend=("Read start-position:",[(col,legendLabels[i]) for i,col in enumerate(cols)])
	else:
		legend=None
	if "hideLegend" in graphDef:legend=None
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="BAR2",legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"])
	graph.addData(graphList)
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph

def addGraph_singleLengthCoverage(basegui,graphDef,libIDs,db,siRNAPos,annotation=None,highlightStyles=None):
	targetLen=graphDef["targetlen"]
	graphtype="Coverage_l"+str(targetLen)
	
	highlighting = [dict(),dict()]	#dict of position -> style
	if not annotation is None:
		#for strand,entrylist in enumerate(annotation):
		strand=0
		entrylist=annotation[0]
		for feature in entrylist:
			if feature[1]!=targetLen:continue
			if "pseudo" in feature[3]:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="pseudoGS"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="pseudoPS"
			else:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="esiGS"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]+c]="esiPS"
		strand=1
		entrylist=annotation[1]
		for feature in entrylist:
			if feature[1]!=targetLen:continue
			if "pseudo" in feature[3]:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="pseudoGS"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="pseudoPS"
			else:
				if feature[4] == "Guide":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="esiGS"
				elif feature[4] == "Passenger":
					for c in range(feature[1]):highlighting[strand][feature[0]-c]="esiPS"
	#print(graphtype)
	#print(siRNAPos)
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
		#print(coverage)
	if len(highlighting[0])+len(highlighting[0])>0:
		legendLabels = ["esiRNA guide strand","esiRNA passenger strand","pseudo guide strand","pseudo passenger strand"]
		cols = graphDef["cols"]
		ledDesc = [("black",str(targetLen)+"nt reads")]
		ledDesc.extend([(col,legendLabels[i]) for i,col in enumerate(cols)])
		legend=("Coverage:",ledDesc)
	else:
		legend=("Coverage:",[("black",str(targetLen)+"nt reads")])
	if "hideLegend" in graphDef:legend=None
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="BAR2",legend=legend,positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"])
	graph.addData(graphList)
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph

def addGraph_multiLengthCoverage(basegui,graphDef,libIDs,db):
	targetLengths=[int(p[0]) for p in graphDef["targets"]]
	graphtype="MultiCoverage_"+"".join(["l"+str(l) for l in targetLengths])
	
	#print(graphtype)
	#print(siRNAPos)
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
		#print(coverage)
	legend=("Coverage:",[(p[1],str(p[0])+"nt") for p in graphDef["targets"]])
	
	lineColours = [graphDef["targets"][int(i/2)][1] for i in range(len(targetLengths)*2)]
	if "hideLegend" in graphDef:legend=None
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="multiLine",legend=legend,xlab=graphDef["xlab"],ylab=graphDef["ylab"],lineColours=lineColours)
	graph.addData(graphList)
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph
	#print("")

def addGraph_coverage(basegui,graphDef,libIDs,db):	#Unused
	graphtype="Coverage_all"
	graphList = list()
	for libID in libIDs:
		coverage = [[i,0,0,0,0] for i in range(1,db.seqLen+1)]	#per position
		for targetLen in range(15,30):	#TODO use parameters
			for spos in range(1,db.seqLen+1):
				if db.getReadCount(libID,0,targetLen,spos)>0:
					for cpos in range(spos,spos+targetLen):
						coverage[cpos-1][3]+=db.getReadCount(libID,0,targetLen,spos)
				if db.getReadCount(libID,1,targetLen,spos)>0:
					for cpos in range(spos,spos+targetLen):
						coverage[cpos-1][4]+=db.getReadCount(libID,1,targetLen,spos)
				
		graphList.append((libID,coverage))
		#print(coverage)
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="BAR2",xlab=graphDef["xlab"],ylab=graphDef["ylab"])
	graph.addData(graphList)
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph

def addGraph_heatmap(basegui,graphDef,libIDs,db,annotation=None,highlightStyles=None):
	graphtype = "Heatmap"
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
		#print("\tlengths: "+str(lengthList))
		#print("\tpos: "+str(posList))
		heatGraph = [heatmap,lengthList,posList]
		graphList.append((libID,heatGraph))
	
	#set of (pos,len)
	highlighting = set()
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
	#print("\n[Debug] "+str(highlighting))
	
	legend=("Count:",[("#000000","0"),("#000064",">0"),("#00ffff","95th percentile"),("#ff0000","max")])	#TODO overwritten, but used to check for stuff..
	colourscale_define = [(("abs",0),(0,0,0)), (("abs",1),(0,0,100)), (("rel","percentile",midpointPercentile),(0,255,255)), (("rel","max"),(255,0,0))]
	
	if "hideLegend" in graphDef:legend=None
	graph = Combograph(basegui,graphtype+" - "+graphDef["bundleID"],graphDef["mainTargetSeqID"],graphType="HEAT",legend=legend,
		positionalColouring=highlighting,styles=highlightStyles,xlab=graphDef["xlab"],ylab=graphDef["ylab"])
	graph.addData(graphList,colourscale=colourscale_define,globalYScale=True)
	basegui.comboGraphs[graphtype+graphDef["bundleID"]] = graph

def loadCounts(basegui,countFile,libIDs,seqLen):
	#check for input files	[reqFiles]
	reqNeeded=0
	reqFound=0
	for libID in libIDs:
		reqNeeded+=1
		reqFile = countFile.replace("$libID",libID)
		if not os.path.isfile(reqFile):
			basegui.writeError("\tERROR "+reqFile+" not found")
		else:
			reqFound+=1
			#basegui.writeLog("\t"+reqFile+" was found")
	if reqFound!=reqNeeded:
		basegui.writeError("\tCould not find all input files ("+str(reqFound)+"/"+str(reqNeeded)+"), skipping")
		return False
	
	print("[LoadGraphs] Loading counts")
	db = ReadCountsDatabase(libIDs,seqLen)
	for libID in libIDs:
		if not db.loadFile(libID,countFile.replace("$libID",libID)):
			basegui.writeError("Count table "+str(countFile.replace("$libID",libID))+" has too many errors, aborting!")
			return None
	#db.printStats()
	return db

def loadGraphs(basegui,db,libIDs,wantedgraphs,siRNAPos,annotation=None,highlightStyles=None):
	
	print("[LoadGraphs] Defining/generating graphics")
	#basegui.comboGraphs = dict()
	for graphDef in wantedgraphs:	#create grpahs based on the data
		if graphDef[0]=="lendist":
			addGraph_LenDist(basegui,graphDef,libIDs,db,highlightStyles=highlightStyles)
		elif graphDef[0]=="esiCounts":
			addGraph_esiCounts(basegui,graphDef,libIDs,db,siRNAPos,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="countsSingle":
			addGraph_singleLengthCounts(basegui,graphDef,libIDs,db,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="coverageSingleEsi":
			addGraph_singleLengthCoverage(basegui,graphDef,libIDs,db,siRNAPos,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="coverageMulti":
			addGraph_multiLengthCoverage(basegui,graphDef,libIDs,db)
		elif graphDef[0]=="heapmapEsi":
			addGraph_heatmap(basegui,graphDef,libIDs,db,annotation=annotation,highlightStyles=highlightStyles)
		elif graphDef[0]=="coverageAll":
			addGraph_coverage(basegui,graphDef,libIDs,db)
	
	basegui.writeLog("done.\n")
