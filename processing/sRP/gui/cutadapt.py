
from tkinter import BooleanVar
from tkinter import StringVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry

from gui.functions import addInputVar

def addThemedEntry(main,cutadaptSettingsFrame,width=None,textvariable=None):
	if width is None: tmp = ThemedEntry(cutadaptSettingsFrame,textvariable=textvariable)
	else: tmp = ThemedEntry(cutadaptSettingsFrame,width=width,textvariable=textvariable)
	main.sRP_entryList.append(tmp)
	return tmp

def addThemedRadioButton(main,cutadaptSettingsFrame,text=None,variable=None,value=None):
	tmp = ThemedRadioButton(cutadaptSettingsFrame,text=text,variable=variable,value=value)
	main.sRP_radioList.append(tmp)
	return tmp

def resetCutadapt(main):
	main.PM.reset(tag="sRP-cutadapt")

def add_sRP_cutadapt_GUI(main,parent):
	#Step1: cutadapt -------------------------------------------------------------------------------------------------------------------
	cutadaptBaseFrame = ThemedFrame(parent)
	ThemedLabel(cutadaptBaseFrame,text="Step 1: Cut adapters from reads",anchor="w",style="Medium.TLabel"
		).pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	cutadaptSettingsFrame = ThemedFrame(cutadaptBaseFrame)
	cutadaptSettingsFrame.pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="Parameters for cutadapt:",anchor="w").grid(column=0,row=0,columnspan=3,sticky="ew")
	ThemedLabel(cutadaptSettingsFrame,text="3' Adapter for forward reads:",anchor="w").grid(column=0,row=1,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,textvariable=addInputVar(main,"sRP-cut-adapter1",StringVar(),"nuc","TGGAATTCTCGGGTGCCAAGGAACTCCAGTCAC",
		"Adapter needs to be a string with only ACGT characters!","3' Adapter used for sequencing of the forward read",tag="sRP-cutadapt")
			).grid(column=1,row=1,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="3' Adapter for reverse reads:",anchor="w").grid(column=0,row=2,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,textvariable=addInputVar(main,"sRP-cut-adapter2",StringVar(),"nuc","AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT",
		"Adapter needs to be a string with only ACGT characters!","3' Adapter used for sequencing of the reverse read",tag="sRP-cutadapt")
			).grid(column=1,row=2,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="Minimum Adapter length:",anchor="w").grid(column=0,row=3,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"sRP-cut-minAdapterLength",StringVar(),"int",5,
		"Minimum adapter length needs to be an integer","Minimum length required to find the adpaters",tag="sRP-cutadapt")).grid(
			column=2,row=3,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="Allow insertions or deletions:",anchor="w").grid(column=0,row=4,sticky="ew")
	allowAdapterInDelVar = addInputVar(main,"sRP-cut-allowAdapterInDel",BooleanVar(),"bool",True,"Bool","Allow inserts and deletions in the adapters (yes/no).",tag="sRP-cutadapt")
	addThemedRadioButton(main,cutadaptSettingsFrame,text="Yes      ",variable=allowAdapterInDelVar,value=True).grid(column=1,row=4,sticky="e")
	addThemedRadioButton(main,cutadaptSettingsFrame,text="No       ",variable=allowAdapterInDelVar,value=False).grid(column=2,row=4,sticky="w")
	ThemedLabel(cutadaptSettingsFrame,text="Error rate:",anchor="w").grid(column=0,row=5,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"sRP-cut-errorRate",StringVar(),"float",0.2,
		"Cutadapt error rate needs to be a double.","Error rate for cutadapt to identify the adapters",tag="sRP-cutadapt")).grid(
			column=2,row=5,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="Minimum Read length:",anchor="w").grid(column=0,row=6,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"sRP-cut-minReadLength",StringVar(),"int",15,
		"Minimum read length needs to be an integer","Minimum length to keep reads",tag="sRP-cutadapt")).grid(column=2,row=6,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="Discard reads without adapter:",anchor="w").grid(column=0,row=7,columnspan=1,sticky="ew")
	ThemedLabel(cutadaptSettingsFrame,text="Yes",anchor="w").grid(column=2,row=7,sticky="ew")
	
	ThemedLabel(cutadaptSettingsFrame,text="Cut 5' nucleotides after adapter clipping:",anchor="w").grid(column=0,row=8,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"sRP-cut-cut5pnucs",StringVar(),"int",0,
		"5' cut needs to be an integer","Cut 5' nucleotides after adapter clipping",tag="sRP-cutadapt")).grid(
			column=2,row=8,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(cutadaptSettingsFrame,text="Cut 3' nucleotides after adapter clipping:",anchor="w").grid(column=0,row=9,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"sRP-cut-cut3pnucs",StringVar(),"int",0,
		"3' cut needs to be an integer","Cut 3' nucleotides after adapter clipping",tag="sRP-cutadapt")).grid(
			column=2,row=9,sticky="e",padx=main.frameBorderSize)
	
	ThemedLabel(cutadaptSettingsFrame,text="Extra parameters:",anchor="w").grid(column=0,row=10,sticky="ew")
	addThemedEntry(main,cutadaptSettingsFrame,textvariable=addInputVar(main,"sRP-cut-extraParams",StringVar(),"text","",
		"Free text ?","Extra parameters for cutadapt.",tag="sRP-cutadapt")).grid(column=1,row=10,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	
	ThemedButton(cutadaptSettingsFrame,text="Reset to defaults",command=lambda main=main: resetCutadapt(main)).grid(column=0,row=11,columnspan=3,sticky="ew")
	
	for row in range(10): cutadaptSettingsFrame.rowconfigure(row,weight=1,uniform="fred")
	
	cutadaptSettingsFrame.columnconfigure(0,weight=0)
	cutadaptSettingsFrame.columnconfigure(1,weight=1,uniform="fred")
	cutadaptSettingsFrame.columnconfigure(2,weight=1,uniform="fred")
	
	return cutadaptBaseFrame
