
import os.path
from pathlib import Path
import iostuff.seqFiles as seqIO
from functions.baseFunctions import getLibName

class Library():
	def __init__(self,libID,r1,r2=[],ppt="",label="",comment=""):
		self.libID = libID
		self.r1=r1 if isinstance(r1,list) else [r1]
		self.r2=r2 if isinstance(r2,list) else ([] if r2 is None else [r2])
		if len(self.r2)==1 and self.r2[0] is None: self.r2 = []
		#TODO list of preprocessed files (ready for mapping), independent of single-end or paired-end
		self.ppt=ppt	#ppt = pre-processing Type (Parameter set that cointains this)
		self.label=label
		self.comment=comment
		self.mapTargets = list()
		self.evalTypes = list()
		self.psnames = set()
		self.countFiles = set()		#(psname,target)	#list of processed counts and where to find them
	def isPairedEnd(self):
		return len(self.r2)>0
	def addPS(self,psname):
		self.psnames.add(psname)
	def getPSs(self):
		return self.psnames
	def addCountfile(self,bundleID,psname):
		self.countFiles.add((bundleID,psname))
	def getCountfiles(self):
		return self.countFiles
	def toString(self):
		return f"{self.libID}:\t{self.r1}\t{self.r2}\t{self.ppt}\t{self.label}\t{self.comment}\t{self.mapTargets}\t{self.evalTypes}\t{self.psnames}\t{self.countFiles}"
	def serialize(self):
		return {"libID":self.libID,"r1":self.r1,"r2":self.r2,"ppt":self.ppt,"label":self.label,"comment":self.comment,
			"mapTargets":sorted(self.mapTargets),"evalTypes":sorted(self.evalTypes),"psnames":sorted(self.psnames),"countFiles":sorted(self.countFiles)}
def initLib(contentDict):
	lib = Library(contentDict["libID"],contentDict["r1"],r2=contentDict["r2"],ppt=contentDict["ppt"],label=contentDict["label"],comment=contentDict["comment"])
	lib.mapTargets = contentDict["mapTargets"]
	lib.evalTypes = contentDict["evalTypes"]
	lib.psnames = set(contentDict["psnames"])
	lib.countFiles = set()
	for (bundleID,psname) in contentDict["countFiles"]:
		lib.countFiles.add((bundleID,psname))
	#print(lib.toString())
	return lib

class TargetSequenceBundle():
	def __init__(self,bundleID):
		self.comment = ""
		self.bundleID = bundleID	#bundleID is set manually (but checked for ID-conformity)
		self.mainTarget = ""	#Path to main mapping target
		self.mainTargetFasta = ""
		self.offTargets = list()	#list of paths of genomes
		self.fastaList = list()		#list of paths of all targets as fasta (including generated fasta if maintarget is am embl)
		
		self.mainSeqID = None
		self.annotation = None
		self.mainLength = None
		self.mainSequence = None
	def loadAnnotation(self,main=None):	#load annotation from mainTarget
		if not self.mainTarget.endswith(".embl"):return
		print(f"[IM TB] Loading {self.mainTarget}")
		self.mainSeqID,self.mainSequence,self.annotation = seqIO.loadEMBL(self.mainTarget,main=main)
	def loadMainTarget(self,main=None):
		if self.mainTarget.endswith(".embl"):
			self.loadAnnotation(main=main)
		else:
			self.mainSeqID,self.mainSequence = seqIO.loadFasta(self.mainTarget,main=main)
			self.mainTargetFasta = self.mainTarget
		if not self.mainSequence is None:self.mainLength = len(self.mainSequence)
	def saveMainTargetLocally(self,projectPath):	#called when bundle is created
		fastaPath = os.path.join(projectPath,"fasta")
		Path(fastaPath).mkdir(parents=True, exist_ok=True)
		self.mainTargetFasta = os.path.join(fastaPath,self.mainSeqID+".fasta")
		if not os.path.isfile(self.mainTargetFasta):	#create fasta from embl for bowtie
			with open(self.mainTargetFasta,"w") as fastawriter:
				fastawriter.write(">"+self.mainSeqID+"\n"+self.mainSequence)
	def toString(self):
		return f"{self.bundleID}:\t{self.mainTarget}\t{self.offTargets}"
	def serialize(self):
		return {"comment":self.comment,"mainTarget":self.mainTarget,"offTargets":sorted(self.offTargets),"fastaList":sorted(self.fastaList)}
def initTargetBundle(bundleID,contentDict,main=None):	#TODO check and make sure that everything is there! Or return an errormessage
	t = TargetSequenceBundle(bundleID)	#bundleIDs are not checked for collisions when loading settings, as settings are assumed to be correct
	if "comment" in contentDict:t.comment = contentDict["comment"]
	if "mainTarget" in contentDict:t.mainTarget = contentDict["mainTarget"]
	if "offTargets" in contentDict:t.offTargets = contentDict["offTargets"]
	if "fastaList" in contentDict:t.fastaList = contentDict["fastaList"]
	if "label" in contentDict:t.bundleID = contentDict["label"]
	t.loadMainTarget(main=main)
	return t

class InputManager():
	def __init__(self):
		self.libDict = dict()
		self.targetDict = dict()
		self.siiPairs = list()
	
	def addLib(self,path,path_r2=None,ppt="",label="",comment=""):
		#seqID = os.path.basename(path).removesuffix(".fasta.gz").removesuffix(".fasta").removesuffix(".fa")
		libID = getLibName(path)
		if label == "":label=libID
		if libID in self.libDict:	#update label and comment
			if self.libDict[libID].r2 is None and self.libDict[libID].r1 != path:
				self.libDict[libID].r2 = path
				self.libDict[libID].isPairedEnd = True
			self.libDict[libID].ppt=ppt
			self.libDict[libID].label=label
			self.libDict[libID].comment=comment
		else:
			self.libDict[libID] = Library(libID,path,r2=path_r2,ppt=ppt,label=label,comment=comment)
		print(f"[IM] Added lib {self.libDict[libID].toString()}")
	def updateLib(self,libID,ppt=None,label=None,comment=None,psname=None,mapTarget=None,evalType=None):
		if not libID in self.libDict: return False
		#if not ppt is None:self.libDict[libID].ppt=ppt
		if not label is None:self.libDict[libID].label=label
		if not comment is None:self.libDict[libID].comment=comment
		if not psname is None:
			self.libDict[libID].addPS(psname)
			self.libDict[libID].ppt=psname
		if not mapTarget is None:self.addMapTarget(libID,mapTarget)
		if not evalType is None:self.addEvalType(libID,evalType)
		
	def getLib(self,libID):		#user selects list of libIDs in GUI, then this is used to get the paths
		return self.libDict[libID]
	def getLibraries(self):
		return self.libDict
	def getLibIDs(self):
		return [lib.libID for lib in list(self.libDict.values())]
	def addSeqFiles(self,inputFileList):	#TODO improve this as stated
		sortedFiles = sorted(inputFileList)
		i=0
		while i<len(sortedFiles):
			#print(f"[IM] {i} {sortedFiles[i]}")
			#this doesnt account for _001 and _002, as only one path is stored each.... 
			# make lists instead...
			
			#make system to find all libIDs and then group by that instead of going through a sorted list!
			if i<len(sortedFiles)-1 and getLibName(sortedFiles[i]) == getLibName(sortedFiles[i+1]):
				self.addLib(sortedFiles[i],path_r2=sortedFiles[i+1])	# ensure r1 countains "R1" and r2 "R2"
				i+=2
			else:
				self.addLib(sortedFiles[i])
				i+=1
	def removeLib(self,libID):
		if libID in self.libDict:
			del self.libDict[libID]
		else:
			print(f"ERROR, wrong key used for removal: {libID} !")
	
	def addTargetBundle(self,main,bundleID,mainTarget,comment,offTargets=list()):
		if bundleID in self.targetDict:	#This shouldnt happen in the current implementation, but keeping it just in case
			main.writeError(f"ERROR! bundleID {bundlID} already exists!:{self.targetDict[bundleID].toString()} Overwriting old bundles is not allowed!")
			return False
		self.targetDict[bundleID] = TargetSequenceBundle(bundleID)
		self.targetDict[bundleID].comment = comment
		self.targetDict[bundleID].mainTarget = mainTarget
		self.targetDict[bundleID].offTargets = offTargets
		
		#convert maintarget to fasta if emble
		self.targetDict[bundleID].loadMainTarget(main=main)
		self.targetDict[bundleID].saveMainTargetLocally(main.PM.get("projectPath"))
		#and properly set the fastalist!
		fastaList = [self.targetDict[bundleID].mainTargetFasta]
		fastaList.extend(offTargets)
		self.targetDict[bundleID].fastaList = fastaList
	def getTarget(self,targetID):	#This should never be able to throw an error, because targetID is always selected from the list of keys
		return self.targetDict[targetID]
	def hasTarget(self,targetID):
		return targetID in self.targetDict
	def getTargets(self):
		return self.targetDict.values()
	def getTargetIDs(self):
		return sorted(self.targetDict.keys())
	
	def addMapTarget(self,libID,targetID):	#TargetID can also be a tuple (mainTarget, genome1,genome2,...)
		if targetID not in self.libDict[libID].mapTargets:
			self.libDict[libID].mapTargets.insert(0,targetID)
	def getMapTargets(self,libID):
		return sorted(self.libDict[libID].mapTargets)
	def removeMapTarget(self,libID,targetID):
		self.libDict[libID].mapTargets.remove(targetID)
	def addEvalType(self,libID,evalType):	#dsP, siI
		if evalType not in self.libDict[libID].evalTypes:
			self.libDict[libID].evalTypes.append(evalType)
			self.libDict[libID].evalTypes = [evalType]	#for now its just one!
	def getEvalTypes(self,libID):
		return sorted(self.libDict[libID].evalTypes)
	def removeEvalType(self,libID,evalType):
		self.libDict[libID].evalTypes.remove(evalType)
	
	def addSIIPair(self,libPos,libNeg,label=None):
		self.siiPairs.append((libPos,libNeg,label))
	def getSIIPairs(self):
		return self.siiPairs
	def removeSIIPair(self,index):
		self.siiPairs.remove(index)
	def resetLibPairs(self):
		self.siiPairs = list()
	
	def reset(self):
		print("[IM] Reseting input files")
		self.libDict = dict()
		self.targetDict = dict()
		self.siiPairs = list()
	
	def toString(self):
		text = "\nLibraries:\n"
		text += "\n".join(sorted([v.toString() for v in self.libDict.values()]))
		text += "\nTargets:\n"
		text += "\n".join(sorted([v.toString() for v in self.targetDict.values()]))
		text += "\nPairs:\n"
		text += "\n".join(sorted([f"{v[0]} - {v[1]}, {v[2]}" for v in self.siiPairs]))+"\n"
		return text
	
	def serializeLibs(self):
		serDict = dict()
		for key,value in self.libDict.items():
			serDict[key] = value.serialize()
		return serDict
	def serializeTargets(self):
		serDict = dict()
		for key,value in self.targetDict.items():
			serDict[key] = value.serialize()
		return serDict
	def serialize(self):
		return ["Libraries:",self.serializeLibs(),"Targets:",self.serializeTargets(),"siIPairs:",self.siiPairs]
	def setAll(self,varList,main=None):
		_,libDict,_,targetDict,_,self.siiPairs = varList	#TODO assert / ensure _ = key (see above)	# or use a dicttionary!
		for key,value in libDict.items():
			self.libDict[key] = initLib(value)
		for key,value in targetDict.items():
			self.targetDict[key] = initTargetBundle(key,value,main=main)
		
