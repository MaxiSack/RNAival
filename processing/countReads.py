import pysam

# count reads in inputFile (which was filtered by regionFile) with length between minLength and maxLength and write into outputFilePrefix_*.tsv
# import this file and use countReads directly, if you can
def countReads(inputFile, outputFile, region, minLength, maxLength, pattern=None, allow5pmm=False,report5pmm=None):
	bamfile = pysam.AlignmentFile(inputFile,"rb")
	
	regionDict = dict()	#Outdated, now its just always the entire dsRNA, no selection necessary / used samtools view region beforehand
	start,end = region.split(":")[1].split("-")
	regionDict[region.split(":")[0]] = (int(start),int(end))
	#with open(regionFile) as bed_reader:	#only one region in standard use-case
	#	for line in bed_reader:	#normally there is only one line per bed file
	#		lsp = line.strip().split("\t")	# [ReferenceSequence,regionStart,regionEnd]
	#		regionDict[lsp[0]] = (int(lsp[1]),int(lsp[2]))
	
	#Init data constructs for counting	[1]x[2]x[15]x[200]
	lengthCountDict = dict()	# ReferenceSequence -> [startposition[]]x[readlength[]x[forward,reverse]]	# [ref][strand][length][start-pos] -> count

	for targetRef,(regionStart,regionStop) in regionDict.items():
		regionLength = regionStop - regionStart + 1	#because both are inclusive!
		lengthCountDict[targetRef] = [[None]*(maxLength-minLength+1),[None]*(maxLength-minLength+1)]	#also inclusive!
		for strand in [0,1]:
			for i in range(maxLength-minLength+1):
				lengthCountDict[targetRef][strand][i] = [0]*regionLength
	
	totalReads=0
	totalCounted=0
	#count mismatches
	total1mm=0
	total2mm=0
	total3mm=0
	
	total1mmIn=0
	total1Tmm=0
	
	#Count reads
	missReffCount=0
	for read in bamfile:
		totalReads+=1
		if read.reference_name not in regionDict:	#if input is already filtered by the bed file, this shouldnt happen
			if missReffCount<10:
				print("[Log] Reference mismatch: "+read.reference_name)		#but if it does, give output
				missReffCount+=1
			elif missReffCount==10:
				print("[Log] Available references: "+str(regionDict.keys()))
				print("[Log] Please make sure that the current settings are in line with the mapping step or re-run the mapping.")
				missReffCount+=1
			continue
		
		if "T" in read.get_tag("MD"):
			total1Tmm+=1
			
		if "0T" in read.get_tag("MD"):
			total1mmIn+=1
		
		offset = - regionDict[read.reference_name][0]	#just in case different referenceSequences appear in the bed file
		#if the region starts at 1, then we get -1, which works for position -> array index !!!	HOWEVER, pysams reference_start and reference_end are 0-based!!!!
		
		#disregards any reads that isnt fully in the region
		if read.reference_start+1 >= regionDict[read.reference_name][0] and read.reference_end <= regionDict[read.reference_name][1]:
			#start and end are 0-based, but end ist 1 after the end, i.e. len = end - start
			
			strand = 0 if read.is_forward else 1
			
		
			#check for missmatches at start!	either with the MD or check seq[start+offset] == seq[0] ....
			#"MD:Z:0T0T20" -> mismatch,mismatch,20matches
			#	~ MD is in one of the tags at the end, no fixed column
			if read.get_tag("MD").startswith("0T"):
				if read.get_tag("MD").startswith("0T0T"):
					if read.get_tag("MD").startswith("0T0T0T"):	#there are also 1T reads, what does that mean?
						total3mm+=1
						continue
					else:
						total2mm+=1
						continue
				else:
					total1mm+=1
					continue
			#if read.get_tag("MD").endswith("0T"):
			#	n3pmm+=1
			#what about ANY mismatch in reads?
			#~discuss mapping parameters
			
			totalCounted+=1
			
			if read.reference_length >= minLength and read.reference_length <= maxLength:
				lengthCountDict[targetRef][strand][read.reference_length-minLength][read.reference_start+1+offset]+=1
		else:
			print("ERROR: Mapped read mapt to outside of region! shouldnt happen with only-construct-regions!")
			print(f"\t{read.reference_start+1} - {read.reference_end} @ {read.reference_name}")
	
	
	for (refName,lcounts) in lengthCountDict.items():
		print(f"Writing read counts of {refName} from \n{inputFile} into {outputFile}")
		offset = regionDict[refName][0]
		with open(outputFile,"w") as outWriter:
			#lcounts[ref][strand][length][start-pos]
			#len	pos	fcount	rcount)
			for i in range(maxLength-minLength+1):	#sorted by length, then position
				if i>0:outWriter.write("\n")
				outWriter.write("\n".join([f"{i+minLength}\t{p+offset}\t{lcounts[0][i][p]}\t{lcounts[1][i][p]}" for p in range(len(lcounts[0][i]))]))
		
	
	#Stats
	print("[Log] Total reads found: "+str(totalReads))
	print("[Log] Total reads counted: "+str(totalCounted))
	print("[Log] Reads starting with >=1 T-mismatch: "+str(total1Tmm))
	print("[Log] Reads starting with >=1 mismatch: "+str(total1mmIn+total1mm))
	print("[Log] Reads starting with 1 5'mismatch: "+str(total1mm))
	print("[Log] Reads starting with 2 5'mismatches: "+str(total2mm))
	print("[Log] Reads starting with 3 5'mismatches: "+str(total3mm))


if __name__ == '__main__':
	print("Start")
	import argparse
	parser = argparse.ArgumentParser(description="Count reads in file bam file")
	parser.add_argument('infile', type=str,help="Input reads (.bam)")
	parser.add_argument('outfilePrefix', type=str, help="Output file prefix for count tables")
	parser.add_argument('region', type=str, help="Region file to analyse reads in (regionID:start-end)")
	parser.add_argument('--minLength', type=int,default = 15, help="output table with counts (.tsv)")
	parser.add_argument('--maxLength', type=int,default = 30, help="output table with counts (.tsv)")
	args = parser.parse_args()
	countReads(args.infile,args.outfilePrefix,args.region, args.minLength, args.maxLength)
