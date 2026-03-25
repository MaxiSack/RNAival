
import os.path
from pathlib import Path
from threading import Thread

from functions.baseFunctions import getSpacedParams

# ----------------------------- sR processing steps -----------------------------------------------

def prepareInput(main,force=False):	#cat sequencing repeats into single files in project directory	#also has benefit of locally storing input files
	
	# ------------------- Library Selection -----------------------
	libraries = dict()
	for libID,lib in main.IM.getLibraries().items():
		if not libID in main.sRPLibIDSelection:continue
		if not main.sRPLibIDSelection[libID].get():continue
		#TODO libraries in InputManager only store one path, making this step unnecessary / need to change InputManger....
		libraries[libID] = [[lib.r1],[] if lib.r2 is None else [lib.r2]]
	
	print(f"[sRP prep] Selected Libraries:\n{libraries}")
	main.saveSettings()
	main.writeLog("Selected input libraries and files:")
	main.writeLog("\n".join([libID+":\n\t"+"\n\t".join([str(s) for s in R1repeats])+"\n\t"+"\n\t".join([str(s) for s in R2repeats]) for libID,(R1repeats,R2repeats) in libraries.items()]))
	
	readDir = os.path.join(main.PM.get("projectPath"),"0_reads")
	Path(readDir).mkdir(parents=True, exist_ok=True)
	
	#reqFiles = dict()	#use libraries extra param
	genFiles = {"$outR1":os.path.join(readDir,"$libID_R1.fastq.gz")}
	commands = ["cat \"$inRepeatsR1\" > \"$outR1\""]
	#if main.isPairedEndReadsVar.get():	#TODO
	#	genFiles["$outR2"]=os.path.join(readDir,"$libID_R2.fastq.gz")
	#	commands.append("cat \"$inRepeatsR2\" > \"$outR2\"")
	
	thread = Thread(target=main.runCommand,args=["CAT",commands,None,genFiles,list(sorted(libraries.keys()))],kwargs={"libraries":libraries})
	thread.start()
	main.runningThreads.append((thread,"CAT"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True	# this true is only for sucressfully generated the command

def runCutadapt(parameters, main=None,force=False):	#required respective parameters in dict; optional main for GUI log output
	#new function that is just pipe?
	readDir = os.path.join(parameters["projectPath"],"0_reads")	#main.PM.get("readDir") / parameters["readDir"]
	adaptDir = os.path.join(parameters["projectPath"],"1_cutadapt")	#main.PM.get("adaptDir")
	Path(adaptDir).mkdir(parents=True, exist_ok=True)
	
	reqFiles = dict()
	genFiles = dict()
	
	
	#TODO have the pipe make two runs, one for unpaired, one for paired and process then after another (similar to map)
	#for ngmerge, just skip / filter out the libraries that are not paired end
	#for prep input ...?
	#for delete intermediates ??
	#
	
	extraBuffer = getSpacedParams(parameters["cutadaptExtraVar"])
	if False:	#main.isPairedEndReadsVar.get():	#TODO ~for each libID
		#cutadapt extra -j threads -a adapter1 -A adapter2 -o $outR1 -p §outR2 $inR1 $inR2 > $outReport
		command = "cutadapt "+extraBuffer+"-j "+str(parameters["threadsVar"])+" -e "+str(parameters["cutErrorRateVar"])
		command += " -m "+str(parameters["minReadLengthVar"])+" -O "+str(parameters["minAdapterLenVar"])
		command += ("" if parameters["allowAdapterInDelVar"] else " --no-indels")+" --discard-untrimmed -q 20,20"	#
		command += " -a "+parameters["adapt1Var"]+" -A "+parameters["adapt2Var"]+" -o \"$outR1\" -p \"$outR2\" \"$inR1\" \"$inR2\""
		reqFiles = {"$inR1":os.path.join(readDir,"$libID_R1.fastq.gz"),"$inR2":os.path.join(readDir,"$libID_R2.fastq.gz")}
		genFiles = {	"$outR1":os.path.join(adaptDir,"$libID_R1.fastq.gz"),
				"$outR2":os.path.join(adaptDir,"$libID_R2.fastq.gz"),
				"$report":os.path.join(adaptDir,"$libID_report.txt")}
	else:
		#cutadapt extra -j threads -a adapter1 -o $outR1 $inR1 > $outR12
		command = "cutadapt "+extraBuffer+"-j "+str(parameters["threadsVar"])+" -e "+str(parameters["cutErrorRateVar"])
		command += " -m "+str(parameters["minReadLengthVar"])+" -O "+str(parameters["minAdapterLenVar"])
		command += ("" if parameters["allowAdapterInDelVar"] else " --no-indels")+" --discard-untrimmed -q 20,20"
		command += " -a "+parameters["adapt1Var"]+" -o \"$outR1\" \"$inR1\""
		reqFiles = {"$inR1":os.path.join(readDir,"$libID_R1.fastq.gz")}
		genFiles = {"$outR1":os.path.join(adaptDir,"$libID_R1.fastq.gz"),"$report":os.path.join(adaptDir,"$libID_report.txt")}
	
	commands = [command]
	outfiles=["$report"]
	
	
	if parameters["cut5pnucs"] > 0 and parameters["cut3pnucs"] > 0:
		genFiles["$outR1"]=os.path.join(adaptDir,"$libID_R1_adapt.fastq.gz")
		genFiles["$outcut5p"]=os.path.join(adaptDir,"$libID_R1_cut5p.fastq.gz")
		genFiles["$outcut3p"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append("cutadapt -j "+str(parameters["threadsVar"])
			+" -m "+str(parameters["minReadLengthVar"])+" --cut "+str(parameters["cut5pnucs"])+" -o \"$outcut5p\" \"$outR1\"")
		commands.append("cutadapt -j "+str(parameters["threadsVar"])
			+" -m "+str(parameters["minReadLengthVar"])+" --cut -"+str(parameters["cut3pnucs"])+" -o \"$outcut3p\" \"$outcut5p\"")
		outfiles.append("$report_cut5p")
		outfiles.append("$report_cut3p")
	elif parameters["cut5pnucs"] > 0:
		genFiles["$outR1"]=os.path.join(adaptDir,"$libID_R1_adapt.fastq.gz")
		genFiles["$outcut5p"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append("cutadapt -j "+str(parameters["threadsVar"])
			+" -m "+str(parameters["minReadLengthVar"])+" --cut "+str(parameters["cut5pnucs"])+" -o \"$outcut5p\" \"$outR1\"")
		outfiles.append("$report_cut5p")
	elif parameters["cut3pnucs"] > 0:
		genFiles["$outR1"]=os.path.join(adaptDir,"$libID_R1_adapt.fastq.gz")
		genFiles["$outcut3p"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append("cutadapt -j "+str(parameters["threadsVar"])
			+" -m "+str(parameters["minReadLengthVar"])+" --cut -"+str(parameters["cut3pnucs"])+" -o \"$outcut3p\" \"$outR1\"")
		outfiles.append("$report_cut3p")
	
	#TODO replace main with a dedicated (GUI-less) commandRunner (that can optionally take main for GUI Log)
	libIDs = [key for key,value in main.sRPLibIDSelection.items() if value.get()]
	#print(libIDs)
	for key,value in main.sRPLibIDSelection.items():
		print(f"[sRP - cut] {key} {value.get()}")
	thread = Thread(target=main.runCommand,args=["CUT",commands,reqFiles,genFiles,libIDs],
		kwargs={"stdoutFiles":outfiles,"grep":["with adapter"],"force":force})	#,"grepRequireOr":["(6","(7","(8","(9"]	#to enforce adapter found in a certainf raction of reads
	
	thread.start()
	main.runningThreads.append((thread,"CUT"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def runNGmerge(parameters, main=None,force=False):
	adaptDir = os.path.join(parameters["projectPath"],"1_cutadapt")
	mergeDir = os.path.join(parameters["projectPath"],"2_NGmerge")	#TODO check NGmerge for stdout and if that cloggs up the pipe!
	Path(mergeDir).mkdir(parents=True, exist_ok=True)
	
	extraBuffer = getSpacedParams(parameters["ngmergeExtraVar"])	#TODO NGmerge only uses 2 cores? very CPU light...?
	command = "NGmerge "+extraBuffer+"-n "+str(parameters["threadsVar"])+" -m "+str(parameters["minPairedOverlapVar"])
	command += (" -s" if parameters["produceShortestReadsVar"] else "")
	command += " -1 \"$inR1\" -2 \"$inR2\" -o \"$out\""
	reqFiles = {"$inR1":os.path.join(adaptDir,"$libID_R1.fastq.gz"),"$inR2":os.path.join(adaptDir,"$libID_R2.fastq.gz")}
	genFiles = {"$out":os.path.join(mergeDir,"$libID.fastq.gz")}
	
	libIDs = [key for key,value in main.sRPLibIDSelection.items() if value.get()]
	commands = [command]
	thread = Thread(target=main.runCommand,args=["NGMERGE",commands,reqFiles,genFiles,libIDs],kwargs={"force":force})
	
	thread.start()
	main.runningThreads.append((thread,"NGMERGE"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def deleteIntermediateSeqfiles(main):
	if True:
		print("\n[sRP] +++++ Skipping deleting intermediate files +++++\n") #TODO re-enable this feature!
		return True
	readDir = os.path.join(parameters["projectPath"],"0_reads")
	adaptDir = os.path.join(parameters["projectPath"],"1_cutadapt")
	
	delFiles = {"$out0R1":os.path.join(readDir,"$libID_R1.fastq.gz")}#,"$out1R1":os.path.join(adaptDir,"$libID_R1.fastq.gz")}
	commands = [" > \"$out0R1\""]#," > \"$out1R1\""]	#cant delete cutadapt result if NGMerge isnt beeing run!
	if False:	#TODO needs to be done for each library individually!
		delFiles["$out1R1"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append(" > \"$out1R1\"")
		delFiles["$out0R2"]=os.path.join(readDir,"$libID_R2.fastq.gz")
		delFiles["$out1R2"]=os.path.join(adaptDir,"$libID_R2.fastq.gz")
		commands.append(" > \"$out0R2\"")
		commands.append(" > \"$out1R2\"")
	libIDs = list()	#TODO do for all
	thread = Thread(target=main.runCommand,args=["DEL",commands,delFiles,{"gen":"DONOTDELETE"},libIDs])
	thread.start()
	main.runningThreads.append((thread,"DEL"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def createIndex(parameters,main,force=False):
	
	reqFiles = dict()
	genFiles = dict()
	indexDir = os.path.join(parameters["projectPath"],"index")
	Path(indexDir).mkdir(parents=True, exist_ok=True)
	
	extraBuffer = getSpacedParams(parameters["indexExtraVar"])
	
	bowtieversion = 1	#TODO GUI option / discuss!	# Test bowtie vs bowtie2
	genFiles=dict()
	commands = list()
	for target in parameters["targets"]:
		indexID = main.IM.getTarget(target).bundleID	#TODO ID and label ~ label can have spaces, ID can be manually set (with restrictions)
		targetList = list()
		for i,target in enumerate(main.IM.getTarget(target).fastaList):
			reqFiles[f"$target-{indexID}-{i}"] = f"{target}"
			targetList.append(f"$target-{indexID}-{i}")
		if bowtieversion==2:	#Bowtie2	#TODO update, doesnt work right now
			indexFile = f"{indexID}.1.bt2"
			#needs the --quiet option or the massive stdout clogs up the pipe
			command = "bowtie2-build "+extraBuffer+"--quiet --threads "+str(parameters["threadsVar"])
			command += " \"$targetSeq"+"\" \""+os.path.join(indexDir,f"{indexID}\"")	# Bowtie needs the index prefix
		elif bowtieversion==1:	#bowtie1
			indexFile = f"{indexID}.1.ebwt"
			#needs the --quiet option or the massive stdout clogs up the pipe
			# Bowtie needs the index prefix
			#command = "bowtie2-build "+extraBuffer+"--quiet --threads "+str(parameters["threadsVar"])+" \"$targetSeq\"  \""+os.path.join(indexDir,"index\"")
			command = "bowtie-build "+extraBuffer+"--quiet --threads "+str(parameters["threadsVar"])
			command += " \""+"\",\"".join(targetList)+"\""+" \""+os.path.join(indexDir,f"{indexID}\"")
		
		genFiles[f"$index-{indexID}"]=os.path.join(indexDir,indexFile)
		
		commands.append(command)
	thread = Thread(target=main.runCommand,args=["INDEX",commands,reqFiles,genFiles,["None"]],kwargs={"force":force})
	
	thread.start()
	main.runningThreads.append((thread,"INDEX"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def mapReads(parameters,group,main,force=False):
	indexID = group[0]
	mainTarget = group[1]
	mainlength = group[2]
	libIDs = group[3]
	
	indexDir = os.path.join(parameters["projectPath"],"index")
	if main.IM.getLib(libIDs[0]).isPairedEnd:
		readDir = os.path.join(parameters["projectPath"],"2_NGmerge")
	else:
		readDir = os.path.join(parameters["projectPath"],"1_cutadapt")
	mapDir = os.path.join(parameters["projectPath"],"3_map")	# with multiple possible map target this needs to be split by targetbuldeID in directories or filenames..
	#and the project somehow needs to keep track of all the libs and maps and settings.... ~for selection in display
	#~then allows comparing different maps of same library
	Path(mapDir).mkdir(parents=True, exist_ok=True)
	
	reqFiles = dict()
	genFiles = dict()
	commands = list()
	
	extraBuffer = getSpacedParams(parameters["mapExtraVar"])
	
	bowtieversion = 1	#TODO GUI option / discuss!
	if bowtieversion==2:	#Bowtie2	#doesnt work right now
		indexFile = f"{indexID}.1.bt2"
		command = "bowtie2 "+extraBuffer+"--threads "+str(int(int(parameters["threadsVar"])/2))+" -x \""
		command += os.path.join(indexDir,f"{indexID}\"")+" -U \"$inFastq\" --no-unal --very-sensitive"
		#command += " --score-min C,0,0"	#prevents mismatches and gaps
		command += " | samtools view -@ "+str(int(int(parameters["threadsVar"])/4))+" -bS -"
		command += " | samtools sort -@ "+str(int(int(parameters["threadsVar"])/2))+" -o \"$outBam\""
		commands.append(command)
	elif bowtieversion==1:	#bowtie1
		indexFile = f"{indexID}.1.ebwt"
		command = "bowtie "+extraBuffer+" -p "+str(int(int(parameters["threadsVar"])/2))+" -x \""
		command += os.path.join(indexDir,f"{indexID}\"")+" -q \"$inFastq\" --no-unal --best --tryhard -n 3 --chunkmbs 512 -S"
		command += " | samtools view -@ "+str(int(int(parameters["threadsVar"])/4))+" -bS -"
		command += " | samtools sort -@ "+str(int(int(parameters["threadsVar"])/2))+" -o \"$outBam\""
		commands.append(command)
	
	commands.append("samtools idxstats \"$outBam\" > \"$idxfile\"")
	commands.append("samtools index -@ "+str(int(int(parameters["threadsVar"])/2))+" \"$outBam\"")
	commands.append("samtools view -@ "+str(int(int(parameters["threadsVar"])/2))+" -b -o \"$outRegion\" \"$outBam\" \""
			+mainTarget+":"+"1"+"-"+str(mainlength)+"\"")
	
	if main.IM.getLib(libIDs[0]).isPairedEnd:
		reqFiles = {"$inFastq":os.path.join(readDir,"$libID.fastq.gz"),"$index":os.path.join(indexDir,indexFile)}
		genFiles = {"$outBam":os.path.join(mapDir,indexID+"_$libID.sorted.bam"),"$err":os.path.join(mapDir,indexID+"_$libID.bam.err"),
				"$outRegion":os.path.join(mapDir,indexID+"_$libID.construct.bam"),"$idxfile":os.path.join(mapDir,indexID+"_$libID.bam.idx")}
	else:
		reqFiles = {"$inFastq":os.path.join(readDir,"$libID_R1.fastq.gz"),"$index":os.path.join(indexDir,indexFile)}
		genFiles = {"$outBam":os.path.join(mapDir,indexID+"_$libID.bam"),"$err":os.path.join(mapDir,indexID+"_$libID.bam.err"),
				"$outRegion":os.path.join(mapDir,indexID+"_$libID.construct.bam"),"$idxfile":os.path.join(mapDir,indexID+"_$libID.bam.idx")}
	
	stderrFilesList = [""]*len(commands)
	stderrFilesList[0]="$err"
	thread = Thread(target=main.runCommand,args=["MAP",commands,reqFiles,genFiles,libIDs],kwargs={"stderrFiles":stderrFilesList,"grep":["reads","%"],"force":force})
	thread.start()
	main.runningThreads.append((thread,"MAP"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def countReads(parameters,group,main,force=False):
	indexID = group[0]
	mainTarget = group[1]
	mainlength = group[2]
	libIDs = group[3]
	
	mapDir = os.path.join(parameters["projectPath"],"3_map")
	countDir = os.path.join(parameters["projectPath"],"4_results")
	Path(countDir).mkdir(parents=True, exist_ok=True)
	
	command = "python3 "+os.path.join(parameters["execPath"],"processing/countReads.py")+" '$in' '$outfile' '"
	command += mainTarget+":"+"1"+"-"+str(mainlength)
	command += "' --minLength "+str(parameters["countMinLen"])+" --maxLength "+str(parameters["countMaxLen"])
	commands = [command]
	
	reqFiles = {"$in":os.path.join(mapDir,indexID+"_$libID.construct.bam")}
	genFiles = {"$outfile":os.path.join(countDir,indexID+"_$libID_readcounts.tsv")}
	
	thread = Thread(target=main.runCommand,args=["COUNT",commands,reqFiles,genFiles,libIDs],kwargs={"grep":["[Log]"],"force":force})
	
	thread.start()
	main.runningThreads.append((thread,"COUNT"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

# ----------------------------- sR processing pipeline -----------------------------------------------
def runPipeline(main):
	main.mainNotebook.select(main.logTabIndex)
	if main.isStepRunning():return False
	if not main.checkInputParams():return False
	main.saveSettings()
	main.writeLog("Running entire pipeline")
	main.writeLog("Project Path: "+main.PM.get("projectPath"))
	main.pipelineError = False
	runPipelineStep(main,"CAT")
	return True

def runPipelineStep(main,stepID):
	if main.killSignal[0]: return
	if main.pipelineError: return	#quit when error in steps
	if len(main.runningThreads)>0:
		main.getMain().after(200,lambda sid = stepID: runPipelineStep(main,sid))
		return "wait"
	
	if stepID == "CAT":	#cat
		if not prepareInput(main):
			main.writeError("ERROR with the input")	#error with setting up the command, not the actuall step!
			return "ERROR"
		stepID = "CUT"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		#return "cut" #or give to loop
	elif stepID == "CUT":	#cut
		import gui.sRP_cutadapt_GUI as cutgui
		if not cutgui.runCutadapt(main):
			main.writeError("ERROR with removing the adapters")
			return "ERROR"
		stepID = "MERGE"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		
	elif stepID == "MERGE":	#ngmerge
		import gui.sRP_ngmerge_GUI as mergegui
		if not mergegui.runNGmerge(main):
			main.writeError("ERROR with merging the paired-end reads")
			return "ERROR"
		stepID = "DEL"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		
	elif stepID == "DEL":	#ngmerge
		if not deleteIntermediateSeqfiles(main):
			main.writeError("ERROR with merging the paired-end reads")
			return "ERROR"
		stepID = "INDEX"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		
	elif stepID == "INDEX":	#index	#builds indices for each target belonging to the selected libraries
		import gui.sRP_bowtie_GUI as btgui
		if not btgui.createIndex(main):
			main.writeError("ERROR while creating the index")
			return "ERROR"
		stepID = "MAP"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		
	elif stepID == "MAP":	#map	#needs to run for each target with the corresponding libIDs
		#mapReads stores the order of targets and libraries in main temporarily
		#then next call takes next group from that until none remains, only then set sid=COUNT
		import gui.sRP_bowtie_GUI as btgui
		success,repeat = btgui.mapReads(main)
		if not success:
			main.writeError("ERROR while mapping the reads")
			return "ERROR"
		if repeat:	#Repeat until btgui.mapReads(main) has processed all groups and returns repeat=false
			stepID = "MAP"
			main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		else:
			stepID = "COUNT"
			main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
	elif stepID == "COUNT":	#count
		import gui.sRP_count_GUI as countgui
		success,repeat = countgui.countReads(main)
		if not success:
			main.writeError("ERROR while mapping the reads")
			return "ERROR"
		if repeat:	#Repeat until countgui.countReads(main) has processed all groups and returns repeat=false
			stepID = "COUNT"
			main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
		else:
			stepID = "DRAW"
			#stepID = "DONE"
			main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
	elif stepID == "DRAW":	#draw
		if not main.loadDataIntoGUI():
			main.writeError("Unknown ERROR while while drawing")
			return "ERROR"
		stepID = "DONE"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid))
	elif stepID == "DONE":
		
		main.writeLog("Pipeline finished")
		return "Done"
