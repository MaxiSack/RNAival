
from tkinter import StringVar
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Button as ThemedButton

from gui.functions import addInputVar

from .cutadapt import addThemedEntry

def resetIndex(main):
	main.PM.reset(tag="sRP-index")

def resetMap(main):
	main.PM.reset(tag="sRP-bowtie")

def add_sRP_bowtie_GUI(main,parent):
	#Step3: Mapping -------------------------------------------------------------------------------------------------------------------
	bowtieBaseFrame = ThemedFrame(parent)
	ThemedLabel(bowtieBaseFrame,text="Step 3: Map reads to the target RNA",anchor="w",style="Medium.TLabel"
		).pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	mapSettingsFrame = ThemedFrame(bowtieBaseFrame)
	mapSettingsFrame.pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(mapSettingsFrame,text="Step 3.1: Create an index of the target RNA (using bowtielbuild)",anchor="w").grid(column=0,row=0,columnspan=3,sticky="ew")
	ThemedLabel(mapSettingsFrame,text="Extra parameters:",anchor="w").grid(column=0,row=1,sticky="ew")
	addThemedEntry(main,mapSettingsFrame,textvariable=addInputVar(main,"sRP-index-extraParams",StringVar(),"text","",
		"Free text ?","Extra parameters for bowtiebuild.",tag="sRP-index")).grid(column=1,row=1,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	ThemedButton(mapSettingsFrame,text="Reset to defaults",command=lambda main=main: resetIndex(main)).grid(column=0,row=2,columnspan=3,sticky="ew")
	
	ThemedLabel(mapSettingsFrame,text="Step 3.2: Map the reads onto the index (using bowtie)",anchor="w").grid(column=0,row=4,columnspan=3,sticky="ew")
	ThemedLabel(mapSettingsFrame,text="Align full reads:",anchor="w").grid(column=0,row=5,columnspan=2,sticky="ew")
	ThemedLabel(mapSettingsFrame,text="Yes",anchor="w").grid(column=2,row=5,sticky="ew")
	ThemedLabel(mapSettingsFrame,text="Extra parameters:",anchor="w").grid(column=0,row=6,sticky="ew")
	addThemedEntry(main,mapSettingsFrame,textvariable=addInputVar(main,"sRP-map-extraParams",StringVar(),"text","",
		"Free text ?","Extra parameters for bowtie.",tag="sRP-bowtie")).grid(column=1,row=6,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	main.mapTmp=list()	#needs to be added for mapping later
	ThemedButton(mapSettingsFrame,text="Reset to defaults",command=lambda main=main: resetMap(main)).grid(column=0,row=7,columnspan=3,sticky="ew")
	
	for row in range(8): mapSettingsFrame.rowconfigure(row,weight=1,uniform="fred")
	
	mapSettingsFrame.columnconfigure(0,weight=0)
	mapSettingsFrame.columnconfigure(1,weight=1,uniform="fred")
	mapSettingsFrame.columnconfigure(2,weight=1,uniform="fred")
	
	return bowtieBaseFrame
