import os.path

def loadFasta(path,main=None):
	print(f"[SeqIO] Loading fasta: {path}")
	if not os.path.isfile(path):
		print(f"[SeqIO] Error, fasta file doesnt exist! {path}")
		if not main is None:
			main.writeError("Error, fasta file doesnt exist! ")
			main.writeError(str(path))
			main.writeError("Re-select the file!")
		return None,None
	seqID=""
	seq=""
	with open(path,"r") as fastareader:
		for line in fastareader:
			if line.startswith(">"):
				if seqID != "":
					print("[SeqIO] Error, fasta contains multiple sequences!")
					if not main is None:
						main.writeError("Error, fasta contains multiple sequences!")
					break
				else:
					seqID=line.strip().split()[0].removeprefix(">")
			else: seq+=line.strip()
	return seqID,seq

def loadEMBL(path,main=None):	# path -> data (+optional error reporting in GUI)
	print(f"[SeqIO] Loading embl: {path}")
	if not os.path.isfile(path):
		print(f"[SeqIO] Error, embl file doesnt exist! {path}")
		if not main is None:
			main.writeError("Error, embl file doesnt exist! ")
			main.writeError(str(path))
			main.writeError("Re-select the file!")
		return None,None,None
	sequence=""
	annotation = [list(),list()]	#forward, reverse
	seqID = os.path.basename(path).removesuffix(".embl")
	lastft=""
	
	with open(path,"r") as emblreader:
		readingSeq=False
		current_ncRNA = None
		current_label = None
		current_ncRNAclass = None
		for line in emblreader:
			if line.startswith("FT"):	#Feature
				if "ncRNA " in line and ".." in line:
					try:
						ft,featureType,coords=line.strip().split()
						#assert ft=="FT"	#Asserts not good in try/catch and certainly not in GUI
						#assert featureType=="ncRNA"
						if not featureType=="ncRNA":
							print(f"[SeqIO] Featuretype not recognised: {line.strip()}")
							if not main is None:
								main.writeWarning(f"Featuretype not recognised: {line.strip()}")
						#assert current_ncRNA is None
						#print("coords: "+str(current_ncRNA))
						strand=0	# 0=sense, 1=antisense
						if "complement" in coords:
							coords = coords.removeprefix("complement(").removesuffix(")")
							strand=1
						start,end = coords.split("..")
						current_ncRNA = [int(start),int(end),strand]
					except Exception as e:
						print(e)
						print("[SeqIO] Error with line (ncRNA):")
						print(line)
						if not main is None:
							main.writeError(f"Error with line: {line.strip()}")
							main.writeLog("")
							main.writeWarning("Please ensure that the embl-file follows the convention for siRNA annotation.")
				elif "/label" in line:
					if current_ncRNA is None:
						print(f"[SeqIO] Featuretype not recognised: {line.strip()}")
						if not main is None:
							main.writeWarning(f"Label belongs to an unknown feature: {line.strip()}")
							continue
					try:
						ft,label=line.strip().split("/label=")
						#assert ft.strip()=="FT"
						#assert current_label is None
						#print("labels: "+str(current_label))
						text = label.split()
						featureID = text[0]
						featureStrandType = "None"
						if featureID.endswith("_gs"):
							featureStrandType = "Guide"
							featureID = featureID.removesuffix("_gs")
						elif featureID.endswith("_ps"):
							featureStrandType = "Passenger"
							featureID = featureID.removesuffix("_ps")
						else:
							main.writeError("Could not identify guide/passegner for siRNA "+featureID)
						featureLabel = " ".join(text[1:])
						current_label = (featureID,featureStrandType,featureLabel)
					except Exception as e:
						print(e)
						print("[SeqIO] Error with line (label):")
						print(line)
						if not main is None:
							main.writeError(f"Error with line: {line.strip()}")
							main.writeWarning("Please ensure that the embl-file follows the convention for siRNA annotation.")
				elif "/ncRNA_class" in line:
					try:
						ft,ncRNAclass=line.strip().split("/ncRNA_class=")
						#assert ft.strip()=="FT"
						#assert current_ncRNAclass is None
						#print("class: "+str(current_ncRNAclass))
						current_ncRNAclass = ncRNAclass.removeprefix("\"").removesuffix("\"")
					except Exception as e:
						print(e)
						print("[SeqIO] Error with line (ncRNA_class):")
						print(line)
						if not main is None:
							main.writeError(f"Error with line: {line.strip()}")
							main.writeWarning("Please ensure that the embl-file follows the convention for siRNA annotation.")
				else:
					print(f"[SeqIO] Unknown feature description: {line.strip()}")
					if not main is None:
						main.writeWarning(f"Unknown feature description: {line.strip()}")
				
				if not current_ncRNA is None and not current_label is None and not current_ncRNAclass is None:
					
					strand = current_ncRNA[2]
					#start,length,class,id,ps/gs,label
					annotation[strand].append((current_ncRNA[strand],current_ncRNA[1]-current_ncRNA[0]+1,current_ncRNAclass,
							current_label[0],current_label[1],current_label[2]))
					current_ncRNA = None
					current_label = None
					current_ncRNAclass = None
				
			elif line.startswith("SQ"):
				readingSeq=True
			elif line.startswith("     ") and readingSeq:
				lsp =line.strip().split()
				sequence+="".join(lsp[:-1])
				length = int(lsp[-1])
				if len(sequence)!=length:	# warn if length doesnt match description !
					print("[SeqIO] Sequencelength doesnt match descriptor! {line.strip()}")
					if not main is None:
						main.writeWarning("Sequencelength doesnt match descriptor! "+line.strip())
	return seqID,sequence,annotation
