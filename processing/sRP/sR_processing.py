
import os.path
from pathlib import Path
from threading import Thread

from functions.baseFunctions import getSpacedParams

from .static import moduleID

bowtieversion = 1	# Bowtie (1) is used for mapping these short reads

# ----------------------------- sR processing steps -----------------------------------------------

def prepareInput(main,psname,libIDs,paired=False,force=False):	#cat sequencing repeats into single files in project directory
	if main.isStepRunning():return False
	libraries = dict()
	for libID in libIDs:
		lib = main.IM.getLib(libID)
		libraries[libID] = [lib.r1, lib.r2]
	
	print(f"{'-'*30} sRP {'-'*30}")
	print(f"Processing parameter set {psname}, {"paired-end" if paired else "single-end"}")
	print(f"[sRP prep] Selected input libraries and files:")
	print("\n".join([libID+":"+"".join([f"\n\t{s}" for s in R1repeats])+"".join([f"\n\t{s}" for s in R2repeats]) for libID,(R1repeats,R2repeats) in libraries.items()]))
	main.writeLog(f"{'-'*30} sRP {'-'*30}")
	main.writeLog(f"Processing parameter set {psname},{"paired-end" if paired else "single-end"}")
	main.writeLog("Selected input libraries and files:")
	main.writeLog("\n".join([libID+":"+"".join([f"\n\t{s}" for s in R1repeats])+"".join([f"\n\t{s}" for s in R2repeats]) for libID,(R1repeats,R2repeats) in libraries.items()]))
	
	readDir = os.path.join(main.PM.get("projectPath"),"Reads",moduleID,psname,"0_reads")
	Path(readDir).mkdir(parents=True, exist_ok=True)
	
	genFiles = {"$outR1":os.path.join(readDir,"$libID_R1.fastq.gz")}
	commands = ["cat \"$inRepeatsR1\" > \"$outR1\""]
	if paired:
		genFiles["$outR2"]=os.path.join(readDir,"$libID_R2.fastq.gz")
		commands.append("cat \"$inRepeatsR2\" > \"$outR2\"")
	
	thread = Thread(target=main.runCommand,args=["CAT",commands,None,genFiles,list(sorted(libraries.keys()))],kwargs={"libraries":libraries,"force":force})
	thread.start()
	main.runningThreads.append((thread,"CAT"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True	# this true is only for successfully generating the command and starting the thread

def runCutadapt(main,psname,libIDs,paired=False,force=False):
	if main.isStepRunning():return False
	parameters = main.PM.getDict(tags=["general","project"])
	parameters.update(main.PM.getParameterSet(psname))
	parameters["paired"] = paired
	parameters["libIDs"] = libIDs
	#print(f"[sRP Cut] Params:\n"+"\n".join([f"{k}: {v}" for k,v in parameters.items()]))
	return runCutadaptPipe(main,parameters,force=force)
	
def runCutadaptPipe(main,parameters,force=False):	#required parameters in parameters dictionary
	readDir = os.path.join(parameters["projectPath"],"Reads",moduleID,parameters[".name"],"0_reads")
	adaptDir = os.path.join(parameters["projectPath"],"Reads",moduleID,parameters[".name"],"1_cutadapt")
	Path(adaptDir).mkdir(parents=True, exist_ok=True)
	
	reqFiles = dict()
	genFiles = dict()
	
	extraBuffer = getSpacedParams(parameters["sRP-cut-extraParams"])
	if parameters["paired"]:
		command = f"cutadapt {extraBuffer}-j {parameters["threadsVar"]} -e {parameters["sRP-cut-errorRate"]}"
		command += f" -m {parameters["sRP-cut-minReadLength"]} -O {parameters["sRP-cut-minAdapterLength"]}"
		command += ("" if parameters["sRP-cut-allowAdapterInDel"] else " --no-indels")+" --discard-untrimmed -q 20,20"
		command += f" -a {parameters["sRP-cut-adapter1"]} -A {parameters["sRP-cut-adapter2"]} -o \"$outR1\" -p \"$outR2\" \"$inR1\" \"$inR2\""
		reqFiles = {"$inR1":os.path.join(readDir,"$libID_R1.fastq.gz"),"$inR2":os.path.join(readDir,"$libID_R2.fastq.gz")}
		genFiles = {	"$outR1":os.path.join(adaptDir,"$libID_R1.fastq.gz"),
				"$outR2":os.path.join(adaptDir,"$libID_R2.fastq.gz"),
				"$report":os.path.join(adaptDir,"$libID_report.txt")}
	else:
		command = f"cutadapt {extraBuffer}-j {parameters["threadsVar"]} -e {parameters["sRP-cut-errorRate"]}"
		command += f" -m {parameters["sRP-cut-minReadLength"]} -O {parameters["sRP-cut-minAdapterLength"]}"
		command += ("" if parameters["sRP-cut-allowAdapterInDel"] else " --no-indels")+" --discard-untrimmed -q 20,20"
		command += f" -a {parameters["sRP-cut-adapter1"]} -o \"$outR1\" \"$inR1\""
		reqFiles = {"$inR1":os.path.join(readDir,"$libID_R1.fastq.gz")}
		genFiles = {"$outR1":os.path.join(adaptDir,"$libID_R1.fastq.gz"),"$report":os.path.join(adaptDir,"$libID_report.txt")}
	
	commands = [command]
	outfiles=["$report"]
	
	#------------- for removing extra nucleotides from the ends of reads AFTER the adapter has been clipped ----------------
	if parameters["sRP-cut-cut5pnucs"] > 0 and parameters["sRP-cut-cut3pnucs"] > 0:
		genFiles["$outR1"]=os.path.join(adaptDir,"$libID_R1_adapt.fastq.gz")
		genFiles["$outcut5p"]=os.path.join(adaptDir,"$libID_R1_cut5p.fastq.gz")
		genFiles["$outcut3p"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append(f"cutadapt -j {parameters["threadsVar"]}"
			+f" -m {parameters["sRP-cut-minReadLength"]} --cut {parameters["sRP-cut-cut5pnucs"]} -o \"$outcut5p\" \"$outR1\"")
		commands.append(f"cutadapt -j {parameters["threadsVar"]}"
			+f" -m {parameters["sRP-cut-minReadLength"]} --cut -{parameters["sRP-cut-cut3pnucs"]} -o \"$outcut3p\" \"$outcut5p\"")
		outfiles.append("$report_cut5p")
		outfiles.append("$report_cut3p")
	elif parameters["sRP-cut-cut5pnucs"] > 0:
		genFiles["$outR1"]=os.path.join(adaptDir,"$libID_R1_adapt.fastq.gz")
		genFiles["$outcut5p"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append(f"cutadapt -j {parameters["threadsVar"]}"
			+" -m "+str(parameters["sRP-cut-minReadLength"])+" --cut "+str(parameters["sRP-cut-cut5pnucs"])+" -o \"$outcut5p\" \"$outR1\"")
		outfiles.append("$report_cut5p")
	elif parameters["sRP-cut-cut3pnucs"] > 0:
		genFiles["$outR1"]=os.path.join(adaptDir,"$libID_R1_adapt.fastq.gz")
		genFiles["$outcut3p"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append(f"cutadapt -j {parameters["threadsVar"]}"
			+f" -m {parameters["sRP-cut-minReadLength"]} --cut -{parameters["sRP-cut-cut3pnucs"]} -o \"$outcut3p\" \"$outR1\"")
		outfiles.append("$report_cut3p")
	
	#,"grepRequireOr":["(6","(7","(8","(9"]	#to enforce adapter found in a certain fraction of reads and throw error otherwise
	thread = Thread(target=main.runCommand,args=["CUT",commands,reqFiles,genFiles,parameters["libIDs"]],
		kwargs={"stdoutFiles":outfiles,"grep":["with adapter"],"force":force})
	
	thread.start()
	main.runningThreads.append((thread,"CUT"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def runNGmerge(main,psname,libIDs,force=False):
	if main.isStepRunning():return False
	parameters = main.PM.getDict(tags=["general","project"])
	parameters.update(main.PM.getParameterSet(psname))
	parameters["libIDs"] = libIDs
	return runNGmergePipe(main,parameters,force=force)

def runNGmergePipe(main,parameters,force=False):
	adaptDir = os.path.join(parameters["projectPath"],"Reads",moduleID,parameters[".name"],"1_cutadapt")
	mergeDir = os.path.join(parameters["projectPath"],"Reads",moduleID,parameters[".name"],"2_NGmerge")
	Path(mergeDir).mkdir(parents=True, exist_ok=True)
	
	#NGmerge only uses <=2 cores
	#"-n "+str(parameters["threadsVar"])+	#NGmerge with 16 cores caused an error
	#since it only uses few anyway, just always run it on one
	extraBuffer = getSpacedParams(parameters["sRP-merge-extraParams"])
	command = f"NGmerge {extraBuffer} -m {parameters["sRP-merge-minPairedOverlap"]}"
	command += (" -s" if parameters["sRP-merge-produceShortestRead"] else "")		
	command += " -1 \"$inR1\" -2 \"$inR2\" -o \"$out\""
	reqFiles = {"$inR1":os.path.join(adaptDir,"$libID_R1.fastq.gz"),"$inR2":os.path.join(adaptDir,"$libID_R2.fastq.gz")}
	genFiles = {"$out":os.path.join(mergeDir,"$libID.fastq.gz")}
	
	commands = [command]
	thread = Thread(target=main.runCommand,args=["NGMERGE",commands,reqFiles,genFiles,parameters["libIDs"]],kwargs={"force":force})
	
	thread.start()
	main.runningThreads.append((thread,"NGMERGE"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def deleteIntermediateSeqfiles(main,psname,libIDs,paired=False):
	pp = main.PM.get("projectPath")
	readDir = os.path.join(pp,"Reads",moduleID,psname,"0_reads")
	adaptDir = os.path.join(pp,"Reads",moduleID,psname,"1_cutadapt")
	
	delFiles = {"$out0R1":os.path.join(readDir,"$libID_R1.fastq.gz")}
	commands = [" > \"$out0R1\""]
	if paired:
		delFiles["$out1R1"]=os.path.join(adaptDir,"$libID_R1.fastq.gz")
		commands.append(" > \"$out1R1\"")
		delFiles["$out0R2"]=os.path.join(readDir,"$libID_R2.fastq.gz")
		delFiles["$out1R2"]=os.path.join(adaptDir,"$libID_R2.fastq.gz")
		commands.append(" > \"$out0R2\"")
		commands.append(" > \"$out1R2\"")
	thread = Thread(target=main.runCommand,args=["DEL",commands,delFiles,{"gen":"DONOTDELETE"},libIDs])
	thread.start()
	main.runningThreads.append((thread,"DEL"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def createIndex(main,psname,libIDs,force=False):
	if main.isStepRunning():return False
	parameters = main.PM.getDict(tags=["general","project"])
	parameters.update(main.PM.getParameterSet(psname))
	grouping = dict()
	for libID in libIDs:
		try:
			target = main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).bundleID
		except:
			print(f"Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; {main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}")
		if not target in grouping:grouping[target] = list()
		grouping[target].append(libID)
	print(f"[sRP Index] Groups: \n\t"+"\n\t".join([f"{key}:\t{value}" for key,value in grouping.items()]))
	parameters["targets"] = list(grouping.keys())
	return createIndexPipe(main,parameters,force=force)

def createIndexPipe(main,parameters,force=False):
	reqFiles = dict()
	genFiles = dict()
	indexDir = os.path.join(parameters["projectPath"],"Index")
	Path(indexDir).mkdir(parents=True, exist_ok=True)
	
	extraBuffer = getSpacedParams(parameters["sRP-index-extraParams"])
	genFiles=dict()
	commands = list()
	for target in parameters["targets"]:
		indexID = str(main.IM.getTarget(target).bundleID)
		print(f"[sRP index] Target: {target}, ID: {indexID}")
		Path(os.path.join(indexDir,indexID)).mkdir(parents=True, exist_ok=True)
		targetList = list()
		for i,target in enumerate(main.IM.getTarget(target).fastaList):
			reqFiles[f"$target-{indexID}-{i}"] = f"{target}"
			targetList.append(f"$target-{indexID}-{i}")
		
		#needs the --quiet option or the massive stdout clogs up the pipe
		#Bowtie needs the index prefix
		if bowtieversion==2:	#Bowtie2
			indexFile = f"{indexID}.1.bt2"
			command = f"bowtie2-build {extraBuffer}--quiet --threads {parameters["threadsVar"]}"
			command += " \"$targetSeq"+"\" \"{os.path.join(indexDir,indexID,indexID)}\""
		elif bowtieversion==1:	#bowtie1
			indexFile = f"{indexID}.1.ebwt"
			command = f"bowtie-build {extraBuffer}--quiet --threads {parameters["threadsVar"]}"
			command += " \""+"\",\"".join(targetList)+f"\" \"{os.path.join(indexDir,indexID,indexID)}\""
		
		genFiles[f"$index-{indexID}"]=os.path.join(indexDir,indexID,indexFile)
		
		commands.append(command)
	thread = Thread(target=main.runCommand,args=["INDEX",commands,reqFiles,genFiles,["None"]],kwargs={"force":force})
	thread.start()
	main.runningThreads.append((thread,"INDEX"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

def mapReads(main,psname,libIDs,force=False):
	if main.isStepRunning():return False
	
	if len(main.mapTmp) == 0:	#collect params and store as tmp var
		parameters = main.PM.getDict(tags=["general","project"])
		parameters.update(main.PM.getParameterSet(psname))
		main.mapTmpParams = parameters
		grouping = dict()
		for libID in libIDs:
			try:
				target = main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).bundleID
				isPaired = main.IM.getLib(libID).isPairedEnd()
			except:
				print(f"""[sRP Map] Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; 
					{main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}""")
			key = (target,isPaired)
			if not key in grouping:grouping[key] = list()
			grouping[key].append(libID)
		print(f"[sRP Map] Groups: \n\t"+"\n\t".join([f"{key}:\t{value}" for key,value in grouping.items()]))
		main.mapTmp = [[main.IM.getTarget(target).bundleID,main.IM.getTarget(target).mainSeqID,main.IM.getTarget(target).mainLength,libIDs,isPaired] 
				for (target,isPaired),libIDs in grouping.items()]
		#run for each target
		#queue all map runs and only put "DONE" into coms-queue when the last one finishes
		return True,True	#Setup successful, repeat to start processing the groups
	else:
		group = main.mapTmp[0]
		del main.mapTmp[0]
		repeat = len(main.mapTmp)>0	#repeat this step until all map runs have been completed
		print(f"[sRP Map] Group: {group}, Repeat: {repeat}")
		return mapReadsPipe(main,main.mapTmpParams,group,force=force),repeat
	
def mapReadsPipe(main,parameters,group,force=False):
	indexID = group[0]
	mainTarget = group[1]
	mainlength = group[2]
	libIDs = group[3]
	isPaired = group[4]
	
	indexDir = os.path.join(parameters["projectPath"],"Index",indexID)
	if isPaired:
		readDir = os.path.join(parameters["projectPath"],"Reads",moduleID,parameters[".name"],"2_NGmerge")
	else:
		readDir = os.path.join(parameters["projectPath"],"Reads",moduleID,parameters[".name"],"1_cutadapt")
	mapDir = os.path.join(parameters["projectPath"],"Alignments",indexID,parameters[".name"])
	Path(mapDir).mkdir(parents=True, exist_ok=True)
	
	reqFiles = dict()
	genFiles = dict()
	commands = list()
	
	extraBuffer = getSpacedParams(parameters["sRP-map-extraParams"])
	
	if bowtieversion==2:	#Bowtie2
		indexFile = f"{indexID}.1.bt2"
		command = f"bowtie2 {extraBuffer}--threads {int(int(parameters["threadsVar"])/2)} -x \""
		command += os.path.join(indexDir,str(indexID))+"\" -U \"$inFastq\" --no-unal --very-sensitive"
		#command += " --score-min C,0,0"	#prevents mismatches and gaps
		command += f" | samtools view -@ {int(int(parameters["threadsVar"])/4)} -bS -"
		command += f" | samtools sort -@ {int(int(parameters["threadsVar"])/2)} -o \"$outBam\""
		commands.append(command)
	elif bowtieversion==1:	#bowtie1
		indexFile = f"{indexID}.1.ebwt"
		command = f"bowtie {extraBuffer} -p {int(int(parameters["threadsVar"])/2)} -x \""
		command += os.path.join(indexDir,str(indexID))+"\" -q \"$inFastq\" --no-unal --best --tryhard -n 3 --chunkmbs 512 -S"
		command += f" | samtools view -@ {int(int(parameters["threadsVar"])/4)} -bS -"
		command += f" | samtools sort -@ {int(int(parameters["threadsVar"])/2)} -o \"$outBam\""
		commands.append(command)
	
	commands.append("samtools idxstats \"$outBam\" > \"$idxfile\"")
	commands.append(f"samtools index -@ {int(int(parameters["threadsVar"])/2)} \"$outBam\"")
	commands.append(f"samtools view -@ {int(int(parameters["threadsVar"])/2)} -b -o \"$outRegion\" \"$outBam\" \"{mainTarget}:1-{mainlength}\"")
	
	if main.IM.getLib(libIDs[0]).isPairedEnd():
		reqFiles = {"$inFastq":os.path.join(readDir,"$libID.fastq.gz"),"$index":os.path.join(indexDir,indexFile)}
		genFiles = {"$outBam":os.path.join(mapDir,"$libID.sorted.bam"),"$err":os.path.join(mapDir,"$libID.bam.err"),
				"$outRegion":os.path.join(mapDir,"$libID.construct.bam"),"$idxfile":os.path.join(mapDir,"$libID.bam.idx")}
	else:
		reqFiles = {"$inFastq":os.path.join(readDir,"$libID_R1.fastq.gz"),"$index":os.path.join(indexDir,indexFile)}
		genFiles = {"$outBam":os.path.join(mapDir,"$libID.bam"),"$err":os.path.join(mapDir,"$libID.bam.err"),
				"$outRegion":os.path.join(mapDir,"$libID.construct.bam"),"$idxfile":os.path.join(mapDir,"$libID.bam.idx")}
	
	stderrFilesList = [""]*len(commands)
	stderrFilesList[0]="$err"
	thread = Thread(target=main.runCommand,args=["MAP",commands,reqFiles,genFiles,libIDs],kwargs={"stderrFiles":stderrFilesList,"grep":["reads","%"],"force":force})
	thread.start()
	main.runningThreads.append((thread,"MAP"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True


def countReads(main,psname,libIDs,force=False):
	if main.isStepRunning():return False
	
	if len(main.countTmp) == 0:	#Same system as for mapping
		parameters = main.PM.getDict(tags=["general","project"])
		parameters.update(main.PM.getParameterSet(psname))
		main.countTmpParams = parameters
		grouping = dict()
		for libID in libIDs:
			try:
				target = main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).bundleID
			except:
				print(f"""[sRP Count] Error, problem with finding targets for {libID}: {main.IM.getLib(libID).mapTargets}; 
					{main.IM.getTarget(main.IM.getLib(libID).mapTargets[0]).mainSeqID}""")
			if not target in grouping:grouping[target] = list()
			grouping[target].append(libID)
		print(f"[sRP Count] Groups: \n\t"+"\n\t".join([f"{key}:\t{value}" for key,value in grouping.items()]))
		
		main.countTmp = [[main.IM.getTarget(target).bundleID,main.IM.getTarget(target).mainSeqID,main.IM.getTarget(target).mainLength,libIDs]
					 for target,libIDs in grouping.items()]
		return True,True
	else:
		group = main.countTmp[0]
		del main.countTmp[0]
		repeat = len(main.countTmp)>0
		print(f"[sRP Count] Group: {group}, Repeat: {repeat}")
		return countReadsPipe(main,main.countTmpParams,group,force=force),repeat

def countReadsPipe(main,parameters,group,force=False):
	indexID = group[0]
	mainTarget = group[1]
	mainlength = group[2]
	libIDs = group[3]
	
	mapDir = os.path.join(parameters["projectPath"],"Alignments",indexID,parameters[".name"])
	countDir = os.path.join(parameters["projectPath"],"Counts",indexID,parameters[".name"])
	Path(countDir).mkdir(parents=True, exist_ok=True)
	
	for libID in libIDs:
		main.IM.getLib(libID).addCountfile(indexID,parameters[".name"])	#tell the Library Object what files exist. Use later for selection for graphic gen
		#doesnt exist *yet*..., but should soon if weve made it this far
		#so the settings need to be saved or at least the libraries updated
	
	command = f"python3 {os.path.join(parameters["execPath"],"processing/sRP/countReads.py")} '$in' '$outfile' '{mainTarget}:1-{mainlength}'"
	command += f" --minLength {parameters["sRP-count-minLen"]} --maxLength {parameters["sRP-count-maxLen"]}"
	commands = [command]
	
	reqFiles = {"$in":os.path.join(mapDir,"$libID.construct.bam")}
	genFiles = {"$outfile":os.path.join(countDir,"$libID_readcounts.tsv")}
	
	thread = Thread(target=main.runCommand,args=["COUNT",commands,reqFiles,genFiles,libIDs],kwargs={"grep":["[Log]"],"force":force})
	
	thread.start()
	main.runningThreads.append((thread,"COUNT"))
	main.getMain().after(100,main.checkForLogUpdates)
	return True

# ----------------------------- sR processing pipeline -----------------------------------------------
def runPipeline(main):
	main.mainNotebook.select(main.logTabIndex)
	if main.isStepRunning():return False
	main.writeLog("Running sRP pipeline")
	main.writeLog("Project Path: "+main.PM.get("projectPath"))
	main.pipelineError = False
				
	usedParameterSets = set()
	for libID,lib in main.IM.getLibraries().items():
		#print(f"[sRP] {libID} {lib.psnames}")
		for psname in lib.psnames:
			ps = main.PM.getParameterSet(psname)
			if ps is None:
				main.writeError(f"Error, could not find parameterset \"{psname}\" for library \"{libID}\"!")
				continue
			if ps[".moduleID"] == moduleID:
				usedParameterSets.add(psname)
	
	main.tmp_run_psList_sRP = sorted(usedParameterSets)
	print(f"[sRP run] Found PSs: {main.tmp_run_psList_sRP}")
	main.tmp_run_psList_sRP_Index = 0
	runPipelineWithParameterSetIndex(main)
	return True
	
def runPipelineWithParameterSetIndex(main):
	if main.tmp_run_psList_sRP is None or main.tmp_run_psList_sRP_Index is None:return False
	if main.tmp_run_psList_sRP_Index >= len(main.tmp_run_psList_sRP):	#ran all parametersets, now return to main
		main.tmp_run_psList_sRP = None
		main.tmp_run_psList_sRP_Index = None
		main.nextPPTModule()
	else:
		psname = main.tmp_run_psList_sRP[main.tmp_run_psList_sRP_Index]
		main.tmp_run_psList_sRP_Index+=1
		runPipelineStep(main,"PREPRO",psname)

def runPipelineStep(main,stepID,psname,paired=False,selectedEndLibIDs=None):
	if main.killSignal[0]: return
	if main.pipelineError: return	#quit when error in steps
	if len(main.runningThreads)>0:	#delay the next step until the previous one has finished running
		main.getMain().after(200,lambda sid = stepID: runPipelineStep(main,sid,psname,paired=paired,selectedEndLibIDs=selectedEndLibIDs))
		return "wait"
	print(f"[sRP] Running pipelinestep {stepID}, with PS {psname} - {"paired-end" if paired else "single-end"} for libraries: {selectedEndLibIDs}")
	
	
	if stepID == "PREPRO":	# ---------------------------- prep ----------------------------
		#group libraries into single-end and paired-end, then run CAT,CUT,DEL and/or CAT,CUT,MERGE,DEL
		#then continue with INDEX and MAP
		if selectedEndLibIDs is None:
			singleEndLibIDs = list()
			pairedEndLibIDs = list()
			for libID,lib in main.IM.getLibraries().items():
				if not psname == lib.ppt:continue	#only process the currently selected Parameterset
				#if not psname in lib.psnames:continue	#process all/only libraries that have this psname
				if lib.isPairedEnd():pairedEndLibIDs.append(libID)
				else: singleEndLibIDs.append(libID)
			selectedEndLibIDs = [singleEndLibIDs,pairedEndLibIDs]
			print(f"[sRP prep] {stepID} {psname}: se: {singleEndLibIDs}, pe: {pairedEndLibIDs}")
		
		if len(selectedEndLibIDs[0])==0 and len(selectedEndLibIDs[1])==0:
			main.writeError("ERROR, no libraries selected!")
			return "Done"
		if not paired and len(selectedEndLibIDs[0])>0:	#Start with single-end processing, if such libraries exist
			main.getMain().after(200,lambda main=main,sid = "CAT": runPipelineStep(main,sid,psname,paired=False,selectedEndLibIDs=selectedEndLibIDs))
		else:
			if len(selectedEndLibIDs[1])>0:		#If paired-end libraries exist, process those
				main.getMain().after(200,lambda main=main,sid = "CAT": runPipelineStep(main,sid,psname,paired=True,selectedEndLibIDs=selectedEndLibIDs))
			else:				#otherwise skip paired-end processing and go to indexing
				main.getMain().after(200,lambda main=main,sid = "INDEX": runPipelineStep(main,sid,psname,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "CAT":	# ---------------------------- cat ----------------------------
		if not prepareInput(main,psname,selectedEndLibIDs[paired],paired=paired):
			main.writeError("ERROR with the input")	#error with setting up the command, not the actuall step!
			return "ERROR"
		main.getMain().after(200,lambda main=main,sid = "CUT": runPipelineStep(main,sid,psname,paired=paired,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "CUT":	# ---------------------------- cut ----------------------------
		if not runCutadapt(main,psname,selectedEndLibIDs[paired],paired=paired):
			main.writeError("ERROR with removing the adapters")
			return "ERROR"
		if paired: stepID = "MERGE"
		else: stepID = "DEL"		#single-end skips the merge step
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid,psname,paired=paired,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "MERGE":	# ---------------------------- ngmerge ----------------------------
		if not runNGmerge(main,psname,selectedEndLibIDs[1]):
			main.writeError("ERROR with merging the paired-end reads")
			return "ERROR"
		main.getMain().after(200,lambda main=main,sid = "DEL": runPipelineStep(main,sid,psname,paired=paired,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "DEL":	# ---------------------------- delete intermediates ----------------------------
		if not deleteIntermediateSeqfiles(main,psname,selectedEndLibIDs[paired],paired=paired):
			main.writeError("ERROR with merging the paired-end reads")
			return "ERROR"
		if not paired: stepID = "PREPRO"	#loop back to paired round before starting indexing
		else: stepID = "INDEX"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid,psname,paired=True,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "INDEX":	#index	#builds indices for each target belonging to the selected libraries
		if not createIndex(main,psname,selectedEndLibIDs[0]+selectedEndLibIDs[1]):
			main.writeError("ERROR while creating the index")
			return "ERROR"
		main.getMain().after(200,lambda main=main,sid = "MAP": runPipelineStep(main,sid,psname,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "MAP":	# ---------------------------- map ----------------------------
		#needs to run for each target with the corresponding libIDs
		#mapReads stores the order of targets and libraries in main temporarily
		#then next call takes next group from that until none remains, only then set sid=COUNT
		success,repeat = mapReads(main,psname,selectedEndLibIDs[0]+selectedEndLibIDs[1])
		if not success:
			main.writeError("ERROR while mapping the reads")
			return "ERROR"
		if repeat: stepID = "MAP"	#Repeat until btgui.mapReads(main) has processed all groups and returns repeat=false
		else: stepID = "COUNT"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid,psname,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "COUNT":	# ---------------------------- count ----------------------------
		success,repeat = countReads(main,psname,selectedEndLibIDs[0]+selectedEndLibIDs[1])
		if not success:
			main.writeError("ERROR while mapping the reads")
			return "ERROR"
		if repeat: stepID = "COUNT"	#Repeat until countgui.countReads(main) has processed all groups and returns repeat=false
		else: stepID = "DONE"
		main.getMain().after(200,lambda main=main,sid = stepID: runPipelineStep(main,sid,psname,selectedEndLibIDs=selectedEndLibIDs))
		
	elif stepID == "DONE":
		main.writeLog("[sRP] Pipeline finished.")
		runPipelineWithParameterSetIndex(main)
		return "Done"
