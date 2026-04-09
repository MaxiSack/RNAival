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


