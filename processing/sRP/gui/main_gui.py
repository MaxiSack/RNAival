
from tkinter import StringVar

from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry

from .cutadapt import add_sRP_cutadapt_GUI
from .ngmerge import add_sRP_ngmerge_GUI
from .bowtie import add_sRP_bowtie_GUI
from .count import add_sRP_count_GUI
from ..static import moduleID,pptTags

def loadParameterSetValues(main,psname):
	cancelNewPSCreationDialogue(main)
	main.PM.loadPSIntoMain(psname)
	for button in main.sRP_parameterSetButtonList:
		if button["text"] == psname: button.config(style="Selected.TButton")
		else: button.config(style="TButton")
	for entry in main.sRP_entryList:
		entry.config(state="readonly")
	for radiobutton in  main.sRP_radioList:
		radiobutton.config(state="disabled")

def add_parametersetList(main):
	for button in main.sRP_parameterSetButtonList:
		button.destroy()
	main.sRP_parameterSetButtonList = list()
	for psname in main.PM.getParameterSetKeys():
		if main.PM.getParameterSet(psname)[".moduleID"]==moduleID:
			addPSButton(main,psname)

def addPSButton(main,psname):
	tmp = ThemedButton(main.sRP_parameterSetListFrame,text=psname,command=lambda main=main,psname=psname: loadParameterSetValues(main,psname))
	tmp.pack(fill="x",expand=False,anchor="nw",pady=main.frameBorderSize)
	main.sRP_parameterSetButtonList.append(tmp)

def newPSCreationDialouge(main):
	main.sRP_parameterSetNewButton.pack_forget()
	
	main.sRP_parameterSetSaveVar.set("NewParameterSet")
	main.sRP_parameterSetSaveLabel.pack(fill="x",expand=False,anchor="nw",pady=main.frameBorderSize)
	main.sRP_parameterSetSaveEntry.pack(fill="x",expand=False,anchor="nw",pady=main.frameBorderSize)
	main.sRP_parameterSetSaveButton.pack(fill="x",expand=False,anchor="nw",pady=main.frameBorderSize)
	
	for button in main.sRP_parameterSetButtonList:
		button.config(style="TButton")
	for entry in main.sRP_entryList:
		entry.config(state="normal")
	for radiobutton in  main.sRP_radioList:
		radiobutton.config(state="normal")
	
def saveNewPSFromDialogue(main):
	try:
		psname = main.sRP_parameterSetSaveVar.get()
	except Exception as e:
		main.writeError("Error, Parameter set name has to be a string")
		print(f"[sRP gui] {e}")
		return
	existName = main.PM.addParameterSet(pptTags,moduleID,setname=psname)
	if existName != psname:
		print(f"[sRP gui] ERROR with PS creation! {existName} {psname}")
		return
	addPSButton(main,psname)
	loadParameterSetValues(main,psname)

def cancelNewPSCreationDialogue(main):
	main.sRP_parameterSetSaveLabel.pack_forget()
	main.sRP_parameterSetSaveEntry.pack_forget()
	main.sRP_parameterSetSaveButton.pack_forget()
	
	main.sRP_parameterSetNewButton.pack(fill="x",expand=False,anchor="nw",pady=main.frameBorderSize)

def add_sRGUI(main):	#creates one page for sRP parameters
	print(f"[sRP] adding GUI")
	#Register self with the input as a read-library processing option
	# this system allows other people to add other methods of processing reads into the length,start/5'pos,forwardCount,reverseCount tables
	notebookIndex = len(main.mainNotebooktabs.keys())
	processingFrame = ThemedFrame(main.mainNotebook,style="gBorder.TFrame")
	main.mainNotebook.add(processingFrame,	text="sR-processing")
	main.mainNotebooktabs[notebookIndex] = processingFrame
	
	ThemedLabel(processingFrame,text="Parameters for short-read processing",anchor="nw",style="Header.TLabel"
		).pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize*2,pady=(main.frameBorderSize*2,0))
	processingFrame_parameters = ThemedFrame(processingFrame,style="gBorder.TFrame")
	processingFrame_parameters.pack(fill="both",expand=True,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	parameterSetSelectionFrame = ThemedFrame(processingFrame_parameters)
	parameterSetSelectionFrame.grid(row=0,column=0,rowspan=2,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(parameterSetSelectionFrame,text="Parameter Sets",anchor="nw",style="Medium.TLabel").pack(fill="x",expand=False,anchor="nw")
	main.sRP_parameterSetListFrame = ThemedFrame(parameterSetSelectionFrame,style="Test.TFrame")
	main.sRP_parameterSetListFrame.pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	main.sRP_parameterSetButtonList = list()
	#later (after project load) add all PS that use this module here
	
	#Widgets for adding a new PS
	main.sRP_parameterSetNewFrame = ThemedFrame(parameterSetSelectionFrame,style="Test.TFrame")
	main.sRP_parameterSetNewFrame.pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	main.sRP_parameterSetNewButton = ThemedButton(main.sRP_parameterSetNewFrame,text="New",command=lambda main=main: newPSCreationDialouge(main))
	main.sRP_parameterSetNewButton.pack(fill="x",expand=False,anchor="nw",pady=main.frameBorderSize)
	main.sRP_parameterSetSaveLabel = ThemedLabel(main.sRP_parameterSetNewFrame,text="Name:",anchor="nw")
	main.sRP_parameterSetSaveVar = StringVar(value="NewParameterSet")
	main.sRP_parameterSetSaveEntry = ThemedEntry(main.sRP_parameterSetNewFrame,textvariable=main.sRP_parameterSetSaveVar)
	main.sRP_parameterSetSaveButton = ThemedButton(main.sRP_parameterSetNewFrame,text="Save",command=lambda main=main: saveNewPSFromDialogue(main))
	
	
	main.sRP_entryList = list()	#Stores all entries from this module for modification (readonly), to display existing PS
	main.sRP_radioList = list()
	#GUI for parameters for individual steps are outsourced to other files
	add_sRP_cutadapt_GUI(main,processingFrame_parameters).grid(row=0,column=1,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	add_sRP_ngmerge_GUI(main,processingFrame_parameters).grid(row=1,column=1,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	add_sRP_bowtie_GUI(main,processingFrame_parameters).grid(row=0,column=2,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	add_sRP_count_GUI(main,processingFrame_parameters).grid(row=1,column=2,sticky="news",padx=main.frameBorderSize,pady=main.frameBorderSize)
	
	processingFrame_parameters.rowconfigure(0,weight=1,uniform="fred")
	processingFrame_parameters.rowconfigure(1,weight=1,uniform="fred")
	processingFrame_parameters.columnconfigure(0,weight=1)
	processingFrame_parameters.columnconfigure(1,weight=1,uniform="fred")
	processingFrame_parameters.columnconfigure(2,weight=1,uniform="fred")

