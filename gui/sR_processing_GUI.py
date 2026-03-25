
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton

from gui.sRP_cutadapt_GUI import add_sRP_cutadapt_GUI
from gui.sRP_ngmerge_GUI import add_sRP_ngmerge_GUI
from gui.sRP_bowtie_GUI import add_sRP_bowtie_GUI
from gui.sRP_count_GUI import add_sRP_count_GUI
import processing.sR_processing as srp
from gui.functions import addLibIDSelectionMenu

def add_sRGUI(main):	#creates one page for sRP parameters
	#Register self with the input as a read-library processing option
	# this system allows other people to add other methods of processing reads into the length,start/5'pos,forwardCount,reverseCount tables
	if not "sRP" in main.pptList:main.pptList.append("sRP")
	notebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[sRP] adding GUI at {notebookIndex}")
	processingFrame = ThemedFrame(main.mainNotebook)
	main.mainNotebook.add(processingFrame,	text="sR-processing")
	main.mainNotebooktabs[notebookIndex] = processingFrame
	
	
	ThemedLabel(processingFrame,text="Parameters for short-read pre-processing",anchor="nw",style="Medium.TLabel").pack(fill="x",expand=True,anchor="nw")
	processingFrame_parameters = ThemedFrame(processingFrame)
	processingFrame_parameters.pack(fill="both",expand=True,anchor="nw")
	
	libSelectionFrame,main.sRPLibIDSelection = addLibIDSelectionMenu(main,processingFrame_parameters,ppt="sRP")	#currently selected LibIDs are synced across all stepps
	libSelectionFrame.grid(row=0,column=0,rowspan=2,sticky="new")
	
	#Parameters for indiidual steps are out-sourced to other files
	add_sRP_cutadapt_GUI(main,processingFrame_parameters).grid(row=0,column=1,sticky="news")
	add_sRP_ngmerge_GUI(main,processingFrame_parameters).grid(row=1,column=1,sticky="news")
	add_sRP_bowtie_GUI(main,processingFrame_parameters).grid(row=0,column=2,sticky="news")
	add_sRP_count_GUI(main,processingFrame_parameters).grid(row=1,column=2,sticky="news")
	
	processingFrame_parameters.rowconfigure(0,weight=1,uniform="fred")
	processingFrame_parameters.rowconfigure(1,weight=1,uniform="fred")
	processingFrame_parameters.columnconfigure(0,weight=1)
	processingFrame_parameters.columnconfigure(1,weight=1,uniform="fred")
	processingFrame_parameters.columnconfigure(2,weight=1,uniform="fred")
	ThemedButton(processingFrame,text="Run entire pipeline",command=lambda main=main:srp.runPipeline(main)).pack(fill="x",expand=True,anchor="sw")













