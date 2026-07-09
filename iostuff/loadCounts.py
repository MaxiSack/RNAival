
import os.path

from iostuff.readCountDB import ReadCountsDatabase

def loadCounts(main,countFile,libIDs,seqLen):
	reqNeeded=0
	reqFound=0
	for libID in libIDs:
		reqNeeded+=1
		reqFile = countFile.replace("$libID",libID)
		if not os.path.isfile(reqFile):
			main.writeError("\tERROR "+reqFile+" not found")
		else:
			reqFound+=1
	if reqFound!=reqNeeded:
		main.writeError("\tCould not find all input files ("+str(reqFound)+"/"+str(reqNeeded)+"), skipping")
		return False
	
	#print("[loadCounts] Loading counts")
	db = ReadCountsDatabase(libIDs,seqLen)
	for libID in libIDs:
		if not db.loadFile(libID,countFile.replace("$libID",libID)):
			main.writeError("Count table "+str(countFile.replace("$libID",libID))+" has too many errors, aborting!")
			return None
	#db.printStats()
	return db
