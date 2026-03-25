
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
		self.parameterDict = dict()
		self.parametertags = dict()
	
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
	
	def validateParameter(self,name):
		vardesc = self.parameterDict[name]
		tmp = vardesc[0].get()

		if len(vardesc)>1:
			error=False
			if vardesc[1]=="int":
				try:
					int(float(tmp))
				except:
					error=True
			elif vardesc[1]=="intList":
				tmp = str(tmp).removeprefix("(").removesuffix(")")
				for char in tmp.lower():
					if not char in intListset:
						error=True
						break
			elif vardesc[1]=="float":
				try:
					float(tmp)
				except:
					error=True
			elif vardesc[1]=="bool":
				if not (tmp.lower() in trueList or tmp.lower() in falseList):
					error=True
			elif vardesc[1]=="nuc":
				for char in tmp.upper():
					if not char in nucset:
						error=True
						break
			elif vardesc[1]=="id":	#idstring for idstrings that are not allowed to countain weird characters or spaces
				for char in tmp.lower():
					if not char in idset:
						error=True
						break
			elif vardesc[1]=="text":
				pass
			elif vardesc[1]=="path":
				pass
			elif vardesc[1]=="colour":
				if len(tmp)!=7:
					error=True	#not correct format
					self.main.writeError("ERROR, not correct format!")	#TODO maybe use regex istead
				if not tmp.startswith("#"):
					error=True	#not correct format
					self.main.writeError("ERROR, not correct format #!")
				for char in tmp.lower()[1:]:
					if not char in hexset:
						error=True	#other chars in hex-colour
						self.main.writeError("ERROR, other chars in hex-colour! "+str(char))
						break
			elif vardesc[1]=="unknown":
				print("[PM] Warning, Unknown parameter cannot be validated, "+vardesc[4])
				self.main.writeWarning("Unknown parameter cannot be validated, "+vardesc[4])
				pass
			else:
				self.main.writeError("ERROR, unidentified parameter description! Please report this!")
				print("[PM] ERROR, unidentified parameter!")
				print("[PM] "+str(vardesc))
			
			#self.main.writeLog(key+": "+str(vardesc[0].get())+", type: "+str(vardesc[1])+", default: "+str(vardesc[2])+"; "+vardesc[4])
			if error:
				self.main.writeError(vardesc[3])
				#self.main.writeWarning(vardesc[4])
				return False
		return True
	
	def checkInputParams(self, inputDict=None):
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
	
