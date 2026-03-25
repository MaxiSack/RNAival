
from tkinter import BooleanVar
from tkinter import StringVar

from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry
from gui.functions import addInputVar
import processing.sR_processing as srp

def resetCutadapt(main):
	main.PM.reset(tag="cutadapt")

def runCutadaptForce(main):
	runCutadaptMan(main,force=True)

def runCutadaptMan(main,force=False):
	if not main.checkInputParams():return False
	main.saveSettings()
	runCutadapt(main,force=force)

def runCutadapt(main,force=False):
	if main.isStepRunning():return False
	if not main.checkInputParams():return False
	parameters = main.PM.getDict(tags=["cutadapt","general","project"])
	print(f"[sRP Cut] Params:\n"+"\n".join([f"{k}: {v}" for k,v in parameters.items()]))
	return srp.runCutadapt(parameters, main=main,force=force)

def add_sRP_cutadapt_GUI(main,parent):

	#Step1: cutadapt -------------------------------------------------------------------------------------------------------------------
	cutadaptBaseFrame = ThemedFrame(parent,style="wborder.TFrame")
	cutadaptBaseFrameInner = ThemedFrame(cutadaptBaseFrame)
	cutadaptBaseFrameInner.pack(fill="x",expand=True,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(cutadaptBaseFrameInner,text="Step 1: Cut adapters from reads",anchor="w",style="Medium.TLabel").pack(fill="x",expand=True,anchor="nw")
	cutadaptFoldOutFrame = ThemedFrame(cutadaptBaseFrameInner)
	cutadaptFoldOutFrame.pack(fill="x",expand=True,anchor="nw")
	ThemedLabel(cutadaptFoldOutFrame,text="Parameters for cutadapt:",anchor="w").grid(column=0,row=0,columnspan=3,sticky="ew")
	ThemedLabel(cutadaptFoldOutFrame,text="Adapter for forward reads:",anchor="w").grid(column=0,row=1,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,textvariable=addInputVar(main,"adapt1Var",StringVar(),"nuc","TGGAATTCTCGGGTGCCAAGGAACTCCAGTCAC",
		"Adapter needs to be a string with only ACGT characters!","Adapter used ???",tag="cutadapt")).grid(column=1,row=1,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(cutadaptFoldOutFrame,text="Adapter for reverse reads:",anchor="w").grid(column=0,row=2,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,textvariable=addInputVar(main,"adapt2Var",StringVar(),"nuc","AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT",
		"Adapter needs to be a string with only ACGT characters!","Adapter used ???",tag="cutadapt")).grid(column=1,row=2,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(cutadaptFoldOutFrame,text="Minimum Adapter length:",anchor="w").grid(column=0,row=3,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"minAdapterLenVar",StringVar(),"int",5,
		"Minimum adapter length needs to be an integer","minimum length required to find the adpaters",tag="cutadapt")).grid(
			column=2,row=3,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptFoldOutFrame,text="Allow insertions or deletions:",anchor="w").grid(column=0,row=4,sticky="ew")
	allowAdapterInDelVar = addInputVar(main,"allowAdapterInDelVar",BooleanVar(),"bool",True,"Bool","Allow inserts and deletions in the adapters (yes/no).",tag="cutadapt")
	ThemedRadioButton(cutadaptFoldOutFrame,text="Yes      ",variable=allowAdapterInDelVar,value=True).grid(column=1,row=4,sticky="e")
	ThemedRadioButton(cutadaptFoldOutFrame,text="No       ",variable=allowAdapterInDelVar,value=False).grid(column=2,row=4,sticky="w")
	ThemedLabel(cutadaptFoldOutFrame,text="Error rate:",anchor="w").grid(column=0,row=5,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"cutErrorRateVar",StringVar(),"float",0.2,
		"Cutadapt error rate needs to be a double.","Error rate for cutadapt to identify the adapters.",tag="cutadapt")).grid(
			column=2,row=5,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptFoldOutFrame,text="Minimum Read length:",anchor="w").grid(column=0,row=6,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"minReadLengthVar",StringVar(),"int",15,
		"Minimum read length needs to be an integer","Minimum length to keep reads",tag="cutadapt")).grid(column=2,row=6,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptFoldOutFrame,text="Discard reads without adapter:",anchor="w").grid(column=0,row=7,columnspan=1,sticky="ew")
	ThemedLabel(cutadaptFoldOutFrame,text="Yes",anchor="w").grid(column=2,row=7,sticky="ew")
	
	ThemedLabel(cutadaptFoldOutFrame,text="Cut 5' nucleotides after adapter clipping:",anchor="w").grid(column=0,row=8,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"cut5pnucs",StringVar(),"int",0,
		"5' cut needs to be an integer","Cut 5' nucleotides after adapter clipping",tag="cutadapt")).grid(
			column=2,row=8,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptFoldOutFrame,text="Cut 3' nucleotides after adapter clipping:",anchor="w").grid(column=0,row=9,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"cut3pnucs",StringVar(),"int",0,
		"3' cut needs to be an integer","Cut 3' nucleotides after adapter clipping",tag="cutadapt")).grid(
			column=2,row=9,sticky="e",padx=main.frameBorderSize)
	
	ThemedLabel(cutadaptFoldOutFrame,text="Extra parameters:",anchor="w").grid(column=0,row=10,sticky="ew")
	ThemedEntry(cutadaptFoldOutFrame,textvariable=addInputVar(main,"cutadaptExtraVar",StringVar(),"text","",
		"Free text ?","Extra parameters for cutadapt.",tag="cutadapt")).grid(column=1,row=10,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	
	ThemedButton(cutadaptFoldOutFrame,text="Reset to defaults",command=lambda main=main: resetCutadapt(main)).grid(column=0,row=11,sticky="ew")
	ThemedButton(cutadaptFoldOutFrame,text="Force run this step",command=lambda main=main: runCutadaptForce(main),style="Exit.TButton").grid(column=1,row=11,columnspan=2,sticky="ew")
	#ThemedButton(cutadaptFoldOutFrame,text="Run only this step",command=runCutadaptMan).grid(column=2,row=9,sticky="ew")
	
	cutadaptFoldOutFrame.rowconfigure(0,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(1,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(2,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(3,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(4,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(5,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(6,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(7,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(8,weight=1,uniform="fred")
	cutadaptFoldOutFrame.rowconfigure(9,weight=1,uniform="fred")
	
	cutadaptFoldOutFrame.columnconfigure(0,weight=0)
	cutadaptFoldOutFrame.columnconfigure(1,weight=1,uniform="fred")
	cutadaptFoldOutFrame.columnconfigure(2,weight=1,uniform="fred")
	
	return cutadaptBaseFrame
