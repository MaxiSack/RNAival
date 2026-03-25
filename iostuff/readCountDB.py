class ReadCountsDatabase:
	def __init__(self,libIDs,seqLen):
		self.libIDs = libIDs
		self.seqLen = seqLen
		self.readCounts = dict()
		self.maxLength = 100
		for libID in libIDs:
			self.readCounts[libID] = [[None for i in range(self.maxLength)] for s in [1,-1]]
	
	def addReadCount(self,libID,strand,length,position,count):
		if self.readCounts[libID][strand][length] is None:
			self.readCounts[libID][strand][length] = [0]*self.seqLen
		self.readCounts[libID][strand][length][position-1] = count
	
	def getReadCount(self,libID,strand,length,position):
		if self.readCounts[libID][strand][length] is None: return 0
		return self.readCounts[libID][strand][length][position-1]
	
	def getLengthCount(self,libID,strand,length):
		return sum(self.readCounts[libID][strand][length])
	
	def getPosCount(self,libID,strand,position):
		if strand==0:
			return sum([self.readCounts[libID][strand][length][position-1] if not self.readCounts[libID][strand][length] is None else 0 for length in range(self.maxLength)])
		else:
			countSum=0
			for length in range(self.maxLength):
				if not self.readCounts[libID][strand][length] is None and position-length>=0:
					countSum += self.readCounts[libID][strand][length][position-length]
			return countSum
	
	def printStats(self):
		print("\n----- Database stats -----")
		print(", ".join(self.libIDs))
		for libID in self.libIDs:
			print(libID)
			print("\n".join([str(length)+":\t"+("0" if self.readCounts[libID][0][length] is None else str(sum(self.readCounts[libID][0][length])))
			+"\t"+("0" if self.readCounts[libID][1][length] is None else str(sum(self.readCounts[libID][1][length])))  for length in range(10,40)]))
		print("\n-----      End       -----\n")
	
	def loadFile(self,libID,countFile):
		maxerrors = 10
		errors = 0
		with open(countFile,"r") as countReader:
			for line in countReader:
				try:
					length,position,fcount,rcount = [int(v) for v in line.strip().split()]
				except Exception as e:	#only ints allowed, and empty lines are not caught! Do not modify these tables!
					print("\n <---------------- ERROR -------------->")
					print(e)
					print(line+" <---------------- ERROR -------------->\n")
					errors+=1
					if errors>maxerrors:
						print("\n <---------------- ERROR -------------->")
						print("Too many errors, aborting!")
						print(" <---------------- ERROR -------------->\n")
						return False
				self.addReadCount(libID,0,length,position,fcount)
				self.addReadCount(libID,1,length,position,rcount)
		return True
