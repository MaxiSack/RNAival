
from tkinter import BooleanVar
from tkinter import StringVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Radiobutton as ThemedRadioButton
from tkinter.ttk import Entry as ThemedEntry

from gui.functions import addInputVar

from .cutadapt import addThemedEntry,addThemedRadioButton

def resetNGmerge(main):
	main.PM.reset(tag="sRP-ngmerge")
	
def add_sRP_ngmerge_GUI(main,parent):
	#Step2: NGmerge -------------------------------------------------------------------------------------------------------------------
	ngmergeBaseFrame = ThemedFrame(parent)
	ThemedLabel(ngmergeBaseFrame,text="Step 2: Merge paired-end reads",anchor="w",style="Medium.TLabel"
		).pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ngmergeSettingsFrame = ThemedFrame(ngmergeBaseFrame)
	ngmergeSettingsFrame.pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(ngmergeSettingsFrame,text="Parameters for NGmerge: ",anchor="w").grid(column=0,row=0,columnspan=1,sticky="ew")
	ThemedLabel(ngmergeSettingsFrame,text="Minimum read overlap:",anchor="w").grid(column=0,row=1,sticky="ew")
	addThemedEntry(main,ngmergeSettingsFrame,width=main.numberEntryWidth,textvariable=addInputVar(main,"sRP-merge-minPairedOverlap",StringVar(),"int",10,
		"Minimum overlap of pairs needs to be an integer","Minimum overlap of pairs to merge",tag="sRP-ngmerge")).grid(column=2,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(ngmergeSettingsFrame,text="Produce shortest read when merging:",anchor="w").grid(column=0,row=2,sticky="ew")
	produceShortestReadsVar = addInputVar(main,"sRP-merge-produceShortestRead",BooleanVar(),"bool",True,"Bool","Produce the shortest read when merging (yes/no).",tag="sRP-ngmerge")
	addThemedRadioButton(main,ngmergeSettingsFrame,text=" Yes      ",variable=produceShortestReadsVar,value=True).grid(column=1,row=2,sticky="e")
	addThemedRadioButton(main,ngmergeSettingsFrame,text=" No       ",variable=produceShortestReadsVar,value=False).grid(column=2,row=2,sticky="w")
	ThemedLabel(ngmergeSettingsFrame,text="Extra parameters:",anchor="w").grid(column=0,row=3,sticky="ew")
	addThemedEntry(main,ngmergeSettingsFrame,textvariable=addInputVar(main,"sRP-merge-extraParams",StringVar(),"text","",
		"Free text ?","Extra parameters for NGmerge.",tag="sRP-ngmerge")).grid(column=1,row=3,columnspan=2,sticky="ew",padx=main.frameBorderSize)
	
	ThemedButton(ngmergeSettingsFrame,text="Reset to defaults",command=lambda main=main: srp.resetNGmerge(main)).grid(column=0,row=4,columnspan=3,sticky="ew")
	
	for row in range(5): ngmergeSettingsFrame.rowconfigure(row,weight=1,uniform="fred")
	
	ngmergeSettingsFrame.columnconfigure(0,weight=0)
	ngmergeSettingsFrame.columnconfigure(1,weight=1,uniform="fred")
	ngmergeSettingsFrame.columnconfigure(2,weight=1,uniform="fred")
	
	return ngmergeBaseFrame
