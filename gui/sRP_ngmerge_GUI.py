
from tkinter import BooleanVar
from tkinter import StringVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry
from gui.functions import addInputVar
import processing.sR_processing as srp

def resetNGmerge(main):
	main.PM.reset(tag="ngmerge")

def runNGmergeForce(main):
	runNGmergeMan(main,force=True)

def runNGmergeMan(main,force=False):
	main.saveSettings()
	runNGmerge(main,force=force)

def runNGmerge(main,force=False):
	if main.isStepRunning():return False
	if not main.checkInputParams():return False
	
	if True: return True	#TODO evaluate per library !!; paired-end reads are currently not supported
	
	parameters = main.PM.getDict(tags=["ngmerge","general","project"])
	print(f"Params:\n"+"\n".join([f"{k}: {v}" for k,v in parameters.items()]))
	return srp.runNGmerge(parameters, main=main,force=force)
	
def add_sRP_ngmerge_GUI(main,parent):
	ngmergeBaseFrame = ThemedFrame(parent)
	ThemedLabel(ngmergeBaseFrame,text="Step 2: Merge paired-end reads",anchor="w",style="Medium.TLabel").pack(fill="both",expand=True,anchor="nw")
	ngmergeFoldOutFrame = ThemedFrame(ngmergeBaseFrame)
	ngmergeFoldOutFrame.pack(fill="both",expand=True,anchor="nw")
	#Step2: NGmerge -------------------------------------------------------------------------------------------------------------------
	ThemedLabel(ngmergeFoldOutFrame,text="Parameters for NGmerge: ",anchor="w").grid(column=0,row=0,columnspan=1,sticky="ew")
	ThemedLabel(ngmergeFoldOutFrame,text="Minimum read overlap:",anchor="w").grid(column=0,row=1,sticky="ew")
	ThemedEntry(ngmergeFoldOutFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"minPairedOverlapVar",StringVar(),"int",10,
		"Minimum overlap of pairs needs to be an integer","Minimum overlap of pairs to merge",tag="ngmerge")).grid(column=2,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(ngmergeFoldOutFrame,text="Produce shortest read:",anchor="w").grid(column=0,row=2,sticky="ew")
	produceShortestReadsVar = addInputVar(main,"produceShortestReadsVar",BooleanVar(),"bool",True,"Bool","Produce the shortest read when merging (yes/no).",tag="ngmerge")
	ThemedRadioButton(ngmergeFoldOutFrame,text=" Yes      ",variable=produceShortestReadsVar,value=True).grid(column=1,row=2,sticky="e")
	ThemedRadioButton(ngmergeFoldOutFrame,text=" No       ",variable=produceShortestReadsVar,value=False).grid(column=2,row=2,sticky="w")
	ThemedLabel(ngmergeFoldOutFrame,text="Extra parameters:",anchor="w").grid(column=0,row=3,sticky="ew")
	ThemedEntry(ngmergeFoldOutFrame,textvariable=addInputVar(main,"ngmergeExtraVar",StringVar(),"text","",
		"Free text ?","Extra parameters for NGmerge.",tag="ngmerge")).grid(column=1,row=3,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	
	ThemedButton(ngmergeFoldOutFrame,text="Reset to defaults",command=lambda main=main: srp.resetNGmerge(main)).grid(column=0,row=4,sticky="ew")
	ThemedButton(ngmergeFoldOutFrame,text="Force run this step",command=lambda main=main: srp.runNGmergeForce(main)).grid(column=1,row=4,columnspan=2,sticky="ew")
	#ThemedButton(ngmergeFoldOutFrame,text="Run only this step",command=runLinkerMan).grid(column=2,row=5,sticky="ew")
	
	ngmergeFoldOutFrame.columnconfigure(0,weight=0)
	ngmergeFoldOutFrame.columnconfigure(1,weight=1,uniform="fred")
	ngmergeFoldOutFrame.columnconfigure(2,weight=1,uniform="fred")
	
	ngmergeFoldOutFrame.rowconfigure(0,weight=1,uniform="fred")
	ngmergeFoldOutFrame.rowconfigure(1,weight=1,uniform="fred")
	ngmergeFoldOutFrame.rowconfigure(2,weight=1,uniform="fred")
	ngmergeFoldOutFrame.rowconfigure(3,weight=1,uniform="fred")
	ngmergeFoldOutFrame.rowconfigure(4,weight=1,uniform="fred")
	
	return ngmergeBaseFrame
