import json
import os
import os.path
from pathlib import Path
from tkinter import StringVar

trueList = ["true","t","yes","y",1,"1"]	#lowercase inputs accepted for True
falseList = ["false","f","no","y",0,"0"]	#lowercase inputs accepted for False (used for validation)

nucset={"A","C","G","T","U","N"}
idset = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0","_","-"}
intListset = {"1","2","3","4","5","6","7","8","9","0"," ",","}
hexset = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0"}

class ParameterManager():
	def __init__(self,main):
		self.main = main
		self.parameterDict = dict()	#used for parameters added by the GUI
		self.parametertags = dict()
		self.parameterSetDict = dict()
		
	def getPSName(self):
		initialID = len(self.parameterSetDict)
		while f"PS-{initialID}" in self.parameterSetDict:
			initialID+=1
		return f"PS-{initialID}"
	def addParameterSet(self,tags,moduleID,setname=None,virtual=False):
		if not self.validateTags(tags):
			self.main.writeError("Error, cannot create Parameter set, fix errors with with parameters!")
			return False
		if not setname is None:
			if setname in self.parameterSetDict:
				if self.doesPSExist(parameterSet):
					return True
				else:
					self.main.writeError("Error, selected name \"{setname}\" for parameter set already exists.")
					return False
			psname = setname
		else:
			psname = self.getPSName()
			self.main.writeLog(f"No name for parameter set provided, using \"{psname}\".")
		parameterSet = self.getDict(tags=tags)
		parameterSet[".moduleID"] = moduleID	#this can then directly be passed to sRP or other modules
		parameterSet[".type"] = "PS"
		parameterSet[".name"] = psname
		exists,existName = self.doesPSExist(parameterSet)
		if exists:
			if not setname is None:	#if the user specified a different name for the same set of parameters
				self.main.writeError(f"Error, parameter set \"{setname}\" already exists under name \"{existName}\", please select that parameter set.")
			print(f"[PM] PS \"{psname}\" already exists under name \"{existName}\", skipping.")
			self.main.writeLog(f"Parameter set \"{psname}\" already exists under name \"{existName}\", using that instead.")
			return existName
		
		if not virtual:	#Virtual Parametersets exist only in memory, not in filesystem
			if not self.saveParameterSetDict(psname,parameterSet):return False
		self.parameterSetDict[psname] = parameterSet
		return psname
	def saveParameterSet(self,psname,existsOkay=False):
		if not psname in self.parameterSetDict:
			print(f"[PM] Error, {psname} does not exist")
			return False
		parameterSet = self.parameterSetDict[psname]
		self.saveParameterSetDict(psname,parameterSet,existsOkay=existsOkay)
	def saveParameterSetDict(self,psname,parameterSet,existsOkay=False):
		#print("\n".join([f"\t{key}:\t{value}" for key,value in parameterSet.items()]))
		if not self.hasKey("projectPath"):
			print("[PM] Error, PM has no projectpath, leaving parameter set virtual")
			return True	#if no PP set, just make virtual
		#parameterSets are immutable and cant be changed later
		psPath = os.path.join(self.get("projectPath"),f"Parameters/{psname}.ps.json")
		if os.path.isfile(psPath):
			if existsOkay:
				return True
			else:
				self.main.writeError(f"Error, parameter set \"{psname}\" already exists at {psPath}.")
				return False
		try:
			Path(os.path.join(self.get("projectPath"),"Parameters")).mkdir(parents=True, exist_ok=True)
			with open(psPath,"w") as jw:
				json.dump(parameterSet,jw,indent="\t",sort_keys=True)
		except Exception as e:
			self.main.writeError(f"Error writing parameter set \"{psname}\" as {psPath}.")
			self.main.writeError(str(e))
			return False
		return True
	def loadParameterSets(self):
		self.parameterSetDict = dict()
		psDir = os.path.join(self.get("projectPath"),"Parameters")
		files = os.listdir(psDir)
		for psfile in files:
			if not psfile.endswith(".ps.json"): continue
			psfile = os.path.join(psDir,psfile)
			print(f"[PM] loading PS {psfile}")
			try:
				with open(psfile,"r") as jr:
					jsonstr = jr.read()
					parameterSet = json.loads(jsonstr)
					if not parameterSet[".type"] == "PS":
						print(f"[PM] Error, PS {psfile} is not tagges as PS")
						continue
					name = parameterSet[".name"]
					self.parameterSetDict[name] = parameterSet
			except Exception as e:
				self.main.writeError(f"ERROR! Problem loading Parameter set {psfile}")
				self.main.writeError(str(e))
	def loadPSIntoMain(self,psname):
		for key,value in self.parameterSetDict[psname].items():
			if self.hasKey(key):
				self.set(key,value)
	def getParameterSet(self,psname):
		#print(self.parameterSetDict.keys())
		if not psname in self.parameterSetDict:return None
		return self.parameterSetDict[psname]
	def getParameterSetKeys(self):
		return list(self.parameterSetDict.keys())
	def doesPSExist(self,newPS):	#check if these parameters already exist in a set!
		for name,PS in self.parameterSetDict.items():
			if arePMEqual(PS,newPS):
				return True,name
		return False,None #set parameters THEN save. PS cant be changed after creation!
	def clearPS(self):
		self.parameterSetDict = dict()
	
	def add(self,name,vartype,default,errormessage,desc,tags=None,tag=None):
		if name in self.parameterDict:return self.parameterDict[name][0]
		self.parameterDict[name]=[StringVar(value=default),vartype,default,errormessage,desc]
		if tags is None and not tag is None:
			tags = [tag]
		if not tags is None:
			for ttag in tags:
				if ttag not in self.parametertags:
					self.parametertags[ttag] = list()
				self.parametertags[ttag].append(name)
		return self.parameterDict[name][0]
	
	def set(self,name,value):
		self.parameterDict[name][0].set(value)
	
	def hasKey(self,name):
		return name in self.parameterDict
	def setAll(self,settingsDict):
		for key,value in settingsDict.items():
			if self.hasKey(key):
				self.set(key,value)
			else:
				print(f"[PM] Warning: Added {key}-{value} from settings to GUIVars because it was not declared by GUI")
				self.add(key,"unknown",value,"Added automatically","Added automatically from settings")
	
	def get(self,name):
		vardesc = self.parameterDict[name]
		value = vardesc[0].get()
		if vardesc[1]=="int":return int(float(value))
		elif vardesc[1]=="float":return float(value)
		elif vardesc[1]=="intList":
			value = str(value).removeprefix("(").removesuffix(")")
			if value=="":return list()
			else:
				try:
					return [int(v.strip()) for v in value.split(",") if v!=""]
				except:
					return list()
		elif vardesc[1]=="bool": 
			return value.lower() in trueList
		
		return value
	
	def reset(self,tags=None,tag=None):
		if tags is None and not tag is None:
			tags = [tag]
		print("[PM] Reseting "+str(tags) if not tags is None else "everything")
		if tags is None:
			for key in self.parameterDict.keys():
				self.parameterDict[key][0].set(self.parameterDict[key][2])
		else:
			for ttag in tags:
				for key in self.parametertags[ttag]:
					self.parameterDict[key][0].set(self.parameterDict[key][2])
	
	def getDict(self,tags=None,tag=None):
		valueDict = dict()
		if tags is None and not tag is None:
			tags = [tag]
		if tags is None:
			for key in self.parameterDict.keys():
				valueDict[key] = self.get(key)
		else:
			for ttag in tags:
				for key in self.parametertags[ttag]:
					valueDict[key] = self.get(key)
		return valueDict
	
	def validateTags(self,tags):
		#print(f"\n\n[PM] Checking parameters for tags {tags}!\n\n")
		allGood = True
		for ttag in tags:
			for key in self.parametertags[ttag]:
				if not self.validateParameter(key):allGood = False
		return allGood
	
	def validateParameter(self,name):
		vardesc = self.parameterDict[name]
		tmp = vardesc[0].get()

		if len(vardesc)>1:
			
			error = self.checkVar(vardesc[1],tmp)
			#self.main.writeLog(key+": "+str(vardesc[0].get())+", type: "+str(vardesc[1])+", default: "+str(vardesc[2])+"; "+vardesc[4])
			if error:
				self.main.writeError(vardesc[3])
				#self.main.writeWarning(vardesc[4])
				return False
		return True
	
	def checkVar(self,vartype,value):
		error=False
		if vartype=="int":
			try:
				int(float(value))
			except:
				error=True
		elif vartype=="intList":
			value = str(value).removeprefix("(").removesuffix(")")
			for char in value.lower():
				if not char in intListset:
					error=True
					break
		elif vartype=="float":
			try:
				float(value)
			except:
				error=True
		elif vartype=="bool":
			if not (value.lower() in trueList or value.lower() in falseList):
				error=True
		elif vartype=="nuc":
			for char in value.upper():
				if not char in nucset:
					error=True
					break
		elif vartype=="id":	#idstring for idstrings that are not allowed to countain weird characters or spaces
			for char in value.lower():
				if not char in idset:
					error=True
					self.main.writeError(f"ERROR, character {char} from {value} is not allowed (letters, numbers, \"_\" and \"-\" are allowed)!")
					break
		elif vartype=="text":
			pass
		elif vartype=="path":
			pass
		elif vartype=="colour":
			if len(value)!=7:
				error=True	#not correct format
				self.main.writeError("ERROR, not correct format!")	#TODO maybe use regex istead
			if not value.startswith("#"):
				error=True	#not correct format
				self.main.writeError("ERROR, not correct format #!")
			for char in value.lower()[1:]:
				if not char in hexset:
					error=True	#other chars in hex-colour
					self.main.writeError("ERROR, other chars in hex-colour! "+str(char))
					break
		elif vartype=="unknown":
			print(f"[PM] Warning, Unknown parameter \"{name}\" cannot be validated, {vardesc[4]}")
			self.main.writeWarning(f"Unknown parameter \"{name}\" cannot be validated, {vardesc[4]}")
			pass
		else:
			self.main.writeError("ERROR, unidentified parameter description! Please report this!")
			print("[PM] ERROR, unidentified parameter!")
			print("[PM] "+str(vardesc))
		return error
	
	def checkInputParams(self, inputDict=None):	#validate all GUI parameters; unused right now / replaced by main.PM.validateTags()
		#print("\n\n[PM] Checking parameters!\ndont do this all the time!\nnew PS system should cover most uses!\nmake use to use before creatin PS!\n\n")
		allGood = True
		if inputDict is None:
			inputDict = self.parameterDict
		for key,vardesc in inputDict.items():
			try:
				valid = self.validateParameter(key)
				if not valid:allGood = False
			except Exception as e:
				self.main.writeError("ERROR! unidentified problem with inputvariable "+str(key))
				self.main.writeError(str(e))
				allGood = False
				#expand with more details and checks using vardesc[1] and vardesc[2], if available
				if len(vardesc)>1:
					self.main.writeError(vardesc[3])
					self.main.writeError("Current value "+str(vardesc[0].get())+" does not conform to the requirements")
					self.main.writeError(key+":\ntype: "+str(vardesc[1])+", default: "+str(vardesc[2])+"\n"+vardesc[4])
				else:
					self.main.writeError(key+": "+str(vardesc[0].get()))
				continue
			#if len(vardesc)>1:self.main.writeLog(key+": "+str(vardesc[0].get())+", type: "+str(vardesc[1])+", default: "+str(vardesc[2])+", "+vardesc[4])
			#else:self.main.writeLog(key+": "+str(vardesc[0].get()))
		return allGood
	
	def toString(self):
		text = "\nParameters:\n"
		for key, value in self.parameterDict.items():
			text+=key+":\t"+str(self.get(key))+"\t"+"\t".join([str(v) for v in value[1:]])+"\n"
		return text
	
def arePMEqual(PM1,PM2):
	if len(PM1)!=len(PM2):return False
	for (key1,value1),(key2,value2) in zip(sorted(PM1.items()),sorted(PM2.items())):
		if key1!=key2:return False
		if key1 == ".name":continue
		if value1!=value2:return False
	print(f"[PM] PS \"{PM1[".name"]}\" is equal to PS \"{PM2[".name"]}\"")
	return True
