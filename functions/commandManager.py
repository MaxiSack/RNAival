import sys
import os
import os.path
import time
import subprocess
import signal

def handleOutput(commsQueue,out,error,stdout="",stderr="",grep=[],grepRequireOr=[],force=False):
	allGood=True
	if out!="":
		if stdout!="":
			with open(stdout,"w") as ow:
				ow.write("TEST!")
				ow.write(out)
		if len(grep)>0:
			for line in out.split("\n"):
				for pat in grep:
					if pat in line:
						commsQueue.put(("LOG",line))
						if not force:
							if not hasRequriedGrep(grepRequireOr,line):
								commsQueue.put(("pipeERROR","Likely wrong adapters used, aborting the pipeline!"))
								allGood=False
	if error!="":
		if stderr!="":
			with open(stderr,"w") as ew:
				ew.write(error)
		if len(grep)>0:
			for line in error.split("\n"):
				for pat in grep:
					if pat in line:
						commsQueue.put(("ERROR",line))
	return allGood

def hasRequriedGrep(grepRequireOr,line):
	if len(grepRequireOr)==0:return True
	for pat in grepRequireOr:
		if pat in line:
			return True
	return False

#runs the provided command
#catches the stdout and stderr
#writes to Log if error occures or "grep=[]" is provided
#writes to file if files are provided for stdout= and stderr=
def runCommand(commsQueue,stepID,commands,reqFiles,genFiles,libIDs,killSignal=[False],stdoutFiles=None,stderrFiles=None,grep=[],grepRequireOr=[],force=False,libraries=None):
	#commsQueue is a queue that is used to communicate with the generalGUI in a thread-safe manner
	#stepID is used for debug
	#commands is a list of strings: commands with placeholders that get replaced with the correcponding liIDs and files
	#reqFiles	dict of "$inR1":os.path.join(readDir,"$libID_R1.fastq.gz")
	#genFiles	dict of "$outR1":os.path.join(adaptDir,"$libID_R1.fastq.gz")
	#libIDs		list of libIDs
	#killSignal=[False]	for termination
	#stdout=None	write stdout to this file
	#stderr=None	write stderr to this file
	#grep=None	write matching lines from stdout or stderr to the log
	#libraries=None	used for catInput
	
	print(f"[Command] Running step {stepID}")
	if commsQueue is None:return False	#finished with error
	commsQueue.put(("LOG",f"\n-------------------------------------------------------\nRunning step {stepID}:"))
	commsQueue.put(("LOG","\tcommand:\n\t"+"\n\t".join(commands)))	#if not commsQueue is None: commsQueue.put(...)	#for use with the pipeline..?	#no, required for stopping
	startTime = time.time()						#TODO make an output function/manager(object) that deals with this
									#also does the update managing and so on for GUI, IF provided with the references
	
	#print(f"[Command] {libIDs}")
	
	nsucessfullLibs = 0
	#for each library, test files and execute commands
	for libID in libIDs:
		commsQueue.put(("LOG",f"\tProcessing {libID}:"))
		#check for generated files	[genFiles]	replace $libID with libID
		genFound=0
		for genPattern in genFiles.values():
			genFile = genPattern.replace("$libID",libID)
			if os.path.isfile(genFile):
				commsQueue.put(("WARN",f"\t{genFile} already exists"))
				genFound+=1
			else:
				#commsQueue.put(("WARN",f"\tDEBUG {genFile} not found"))
				pass
		if force:
			commsQueue.put(("WARN","\tRunning step by force"))
		elif genFound==len(genFiles.values()):
			commsQueue.put(("WARN","\tFound all output files, skipping"))
			nsucessfullLibs+=1
			continue
		if genFound>0:
			commsQueue.put(("WARN",f"\tFound some output files ({genFound}/{len(genFiles.values())}), recalculating"))
		
		
		if libraries is not None:	# for CAT input	#TODO should be independent!
			R1repeats,R2repeats = libraries[libID]
			reqFiles = dict()
			for i,fp in enumerate(R1repeats):
				reqFiles["R1-"+str(i)]=fp
			for i,fp in enumerate(R2repeats):
				reqFiles["R2-"+str(i)]=fp
		
		if stepID=="DEL":
			#delFiles["$out0R2"]=os.path.join(readDir,"$libID_R2.fastq.gz")
			nFailed=0
			for reqPattern in reqFiles.values():
				reqFile = reqPattern.replace("$libID",libID)
				if not os.path.isfile(reqFile):
					nFailed+=1
				elif os.path.getsize(reqFile)==0:
					nFailed+=1
			if nFailed==len(reqFiles.values()):
				nsucessfullLibs+=1
				continue
		
		#check for input files	[reqFiles]
		reqFound=0
		for reqPattern in reqFiles.values():
			reqFile = reqPattern.replace("$libID",libID)
			if not os.path.isfile(reqFile):
				commsQueue.put(("ERROR",f"\tERROR {reqFile} not found"))
			else:
				reqFound+=1
				#commsQueue.put(("WARN",f"\tDEBUG {reqFile} found"))
		if reqFound!=len(reqFiles.values()):
			commsQueue.put(("ERROR",f"\tCould not find all input files ({reqFound}/{len(reqFiles.values())}), skipping"))
			continue
		#if True:
		#	commsQueue.put(("WARN",f"\tDEBUG returning"))
		#	nsucessfullLibs+=1
		#	continue	#TODO debuging
		if killSignal[0]:break
		for i,command in enumerate(commands):
			libCommand = command
			
			
			if not stdoutFiles is None:stdoutfile = stdoutFiles[i]
			else:stdoutfile=""
			if not stderrFiles is None:stderrfile = stderrFiles[i]
			else:stderrfile=""
			#replace command placeholders with files	[libCommand]
			
			if libraries is not None:	# for CAT input
				R1repeats,R2repeats = libraries[libID]
				libCommand = libCommand.replace("$inRepeatsR1","\" \"".join(R1repeats))
				libCommand = libCommand.replace("$inRepeatsR2","\" \"".join(R2repeats))
			else:
				for (pattern,replaceString) in reqFiles.items():
					libCommand = libCommand.replace(pattern,replaceString)
			
			for (pattern,replaceString) in genFiles.items():
				libCommand = libCommand.replace(pattern,replaceString)
				stdoutfile = stdoutfile.replace(pattern,replaceString)
				stderrfile = stderrfile.replace(pattern,replaceString)
			libCommand = libCommand.replace("$libID",libID)
			stdoutfile = stdoutfile.replace("$libID",libID)
			stderrfile = stderrfile.replace("$libID",libID)
			
			#print(f"Output params: {stdoutfile} {stderrfile} {grep}")
			
			#commsQueue.put(("WARN",f"\t[DEBUG] Running command for {libID}:"))
			#commsQueue.put(("WARN",f"\t[DEBUG] {libCommand}"))
			#print(libCommand)
			try:
				process=subprocess.Popen(libCommand,shell=True,preexec_fn=os.setsid,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				
				while process.poll() is None:
					time.sleep(0.2)	#check for killsignal every 0.2 seconds, then kill process
					if killSignal[0]:
						os.killpg(os.getpgid(process.pid),signal.SIGTERM)
						process.terminate()	#this is nicer
						commsQueue.put(("ERROR","Process killed"))
						out,error = process.communicate()
						handleOutput(commsQueue,out.decode(),error.decode(),stdout=stdoutfile,stderr=stderrfile,grep=grep,grepRequireOr=grepRequireOr,force=force)
						
				if killSignal[0]:break
				
				if process.returncode == 0:
					#print("\n\nDONE\n\n")
					out,error = process.communicate()
					if handleOutput(commsQueue,out.decode(),error.decode(),stdout=stdoutfile,stderr=stderrfile,grep=grep,grepRequireOr=grepRequireOr,force=force):
						nsucessfullLibs+=1
					else:
						killSignal[0]=True
				else:
					out,error = process.communicate()
					errormsg = error.decode().strip()
					commsQueue.put(("ERROR","An Error occured during command execution:"))
					commsQueue.put(("ERROR",libCommand))
					for line in errormsg.split("\n"):
						commsQueue.put(("ERROR",line))
					print("ERROR during execution:")
					print("ERR: "+errormsg+" :RRE")
					handleOutput(commsQueue,out.decode(),errormsg,stdout=stdoutfile,stderr=stderrfile,grep=grep,grepRequireOr=grepRequireOr,force=force)
			except subprocess.CalledProcessError as e:
				print(f"\nError {e.returncode}\n{e.cmd}\n{e.stdout.decode()}\n{e.stderr.decode()}")
			except:
				print(f"\n{sys.exc_info()[0]}\n{sys.exc_info()[1]}\n{sys.exc_info()[2]}\n")
			#commsQueue.put(("LOG","done."))
			if killSignal[0]:break
		if killSignal[0]:break
	
	if nsucessfullLibs ==0:
		commsQueue.put(("pipeERROR","No command finished sucessfully, aborting the pipeline!"))
		#commsQueue.put(("WARN","[DEBUG] No command finished sucessfully, [not] aborting the pipeline!"))

	
	print("[Command] Done in "+str(time.time()-startTime)+" seconds")
	commsQueue.put(("FINISHED",stepID))
	commsQueue.put(("LOG",f"\nFinished {stepID} in {round(time.time()-startTime,2)} seconds"))

	
