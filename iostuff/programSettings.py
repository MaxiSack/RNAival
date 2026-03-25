
import os.path
def getLastProjects(ptype,execPath=None):
	if ptype =="":projectListFile = ".lastProjects"
	else:projectListFile = "."+ptype+"_lastProjects"
	if not execPath is None:projectListFile=os.path.join(execPath,projectListFile)
	print("Loading list "+str(projectListFile))
	lastProjects = list()
	if os.path.isfile(projectListFile):
		try:
			with open(projectListFile,"r") as lpr:
				for line in lpr:
					path = line.strip()
					name = os.path.basename(path)
					lastProjects.append((name,path))
		except:
			pass
	else: 
		print("ERROR, could not find file!")
		pass
	print()
	return lastProjects
