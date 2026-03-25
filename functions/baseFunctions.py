import os.path
from threading import Thread
from pathlib import Path
	
readFileType = ".fastq.gz"
read1_suffix = "_R1"
read2_suffix = "_R2"
	
def getSpacedParams(params):
	if params.strip()=="": return ""
	return params.strip()+" "

def getLibName(readFile):	#extract the name of the library from the file	#TG_AGB25sR1_S57_L004_R1_001.fastq.gz	#TG_AGB25sR1_S57_R1.fastq.gz	-> TG_AGB25sR1_S57
	filename = os.path.basename(readFile)
	#print("[DEBUG] "+str(readFile))
	#print("[DEBUG] "+str(filename))
	if read1_suffix in filename and read2_suffix in filename:	#if both for some reason, se which is later and use that...
		r1base = read1_suffix.join(filename.split(read1_suffix)[:-1])
		r2base = read2_suffix.join(filename.split(read2_suffix)[:-1])
		if len(r1base)>len(r2base): return r1base
		elif len(r1base)<len(r2base): return r2base
		else:
			print(f"ERROR with file {readFile}\n _R1 and _R2 appear at the same place")
			return None
	elif read1_suffix in filename:
		return read1_suffix.join(filename.split(read1_suffix)[:-1])	#just incase an _R1 appears somwhere before the real one...
	elif read2_suffix in filename:
		return read2_suffix.join(filename.split(read2_suffix)[:-1])
	else:
		return filename.removesuffix(readFileType)

reverseDict = {"A":"T","T":"A","G":"C","C":"G","N":"N","U":"A"}
def getReverseSeq(sequence,main=None):
	try:
		return "".join([reverseDict[base] for base in reversed(sequence.upper())])
	except:
		print("ERROR, could not reverse the sequence!")
		print(sequence)
		if not main is None:
			main.writeError("ERROR, could not reverse the sequence!")
			main.writeError(sequence)
		return None

def getLocalMaxima(counts,windowRadius=5,groupPeaks=True,onlyPeaks=True):
	#for windows of size, find the highest count
	#then if groupPeaks sum all local values as extra info and remove
	#	if onlypeaks, only do so with locally lesser counts
	#		meaning other local maxima can be found in same frame
	#	else take entire window around the maximum
	
	highestCounts = sorted(counts, key = lambda x: x[1],reverse=True)
	
	#print(counts)
	#print(highestCounts)
	
	removedPos = [0]*(len(counts)+1)	#These are positions, 0 is unused; instead of -1 everywhere else
	offset= counts[0][0]-1
	
	localMaxima = list()	#([maxPosCountTuple, other positionsCountTuple that belong to this peak])
	
	largestCount = highestCounts[0][1]
	countThreshold = max(10,int(largestCount / 50))	#atleast 2% of highest peak or atleast 10
	
	for i in range(len(highestCounts)):	#here we could choose to ignore a certain percentile
		try:
			if removedPos[highestCounts[i][0]-offset]==1:continue
		except:
			print("Error removeHighest")
			print(len(removedPos))
			print(len(highestCounts))
			print(i)
			print(highestCounts[i][0])
		if highestCounts[i][1] <= countThreshold:break
		try:
			localMaxPos = highestCounts[i][0]
			
			removedPos[localMaxPos-offset]=1
		except:
			print("Error localMaxPos")
			print(localMaxPos)
			print(len(removedPos))
			
		
		peakPositions = list()
		peakPositions.append(localMaxPos-offset)
		
		if localMaxPos>0:
			lastCount = counts[localMaxPos-offset-1][1]
			curPos = localMaxPos-1
			curCount = counts[localMaxPos-offset-1-1][1]
			while curCount <= lastCount:
				if removedPos[curPos-offset]==1:break
				if curPos-offset==0:break
				peakPositions.append(curPos-offset)
				removedPos[curPos-offset]=1
				
				curPos -=1
				if curPos-offset<0:break
				if removedPos[curPos-offset]==1:break
				lastCount = curCount
				curCount=counts[curPos-offset-1][1]
				if curCount<=0:break
		
		if localMaxPos<len(counts)-1:
			lastCount = counts[localMaxPos-offset-1][1]
			curPos = localMaxPos+1
			curCount = counts[localMaxPos-offset+1-1][1]
			while curCount <= lastCount:
				if removedPos[curPos-offset]==1:break
				if curPos-offset==0:break
				peakPositions.append(curPos-offset)
				removedPos[curPos-offset]=1
				
				curPos +=1
				if curPos-offset>=len(counts):break
				if removedPos[curPos-offset]==1:break
				lastCount = curCount
				curCount=counts[curPos-offset-1][1]
				if curCount-offset<=0:break
		
		if len(peakPositions)>2 and localMaxPos-offset<len(counts)-10:
			localMaxima.append(peakPositions)
	
	#print(localMaxima)
	return localMaxima

