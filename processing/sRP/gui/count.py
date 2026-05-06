
from tkinter import StringVar
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Button as ThemedButton

from gui.functions import addInputVar

from .cutadapt import addThemedEntry

def resetCount(main):
	main.PM.reset(tag="sRP-count")

def add_sRP_count_GUI(main,parent):
	#Step4: Counting -------------------------------------------------------------------------------------------------------------------
	countBaseFrame = ThemedFrame(parent)
	ThemedLabel(countBaseFrame,text="Step 4: Count reads",anchor="w",style="Medium.TLabel").pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	countSettingsFrame = ThemedFrame(countBaseFrame)
	countSettingsFrame.pack(fill="x",expand=False,anchor="nw",padx=main.frameBorderSize,pady=main.frameBorderSize)
	ThemedLabel(countSettingsFrame,text="Minimum read length",anchor="w").grid(column=0,row=0,sticky="w")
	addThemedEntry(main,countSettingsFrame,textvariable=addInputVar(main,"sRP-count-minLen",StringVar(),"int",15,
		"Minimum length needs to be an integer!","Minimum length of reads to count",tag="sRP-count")).grid(column=1,row=0,sticky="e",padx=main.frameBorderSize)
	ThemedLabel(countSettingsFrame,text="Maximum read length",anchor="w").grid(column=0,row=1,sticky="w")
	addThemedEntry(main,countSettingsFrame,textvariable=addInputVar(main,"sRP-count-maxLen",StringVar(),"int",30,
		"Maximum length needs to be an integer!","Maximum length of reads to count",tag="sRP-count")).grid(column=1,row=1,sticky="e",padx=main.frameBorderSize)
	ThemedButton(countSettingsFrame,text="Reset to defaults",command=lambda main=main: resetCount(main)).grid(column=0,row=2,columnspan=3,sticky="ew")
	
	main.countTmp=list()	#needed for runnung this step
	
	countSettingsFrame.columnconfigure(0,weight=0,uniform="fred")
	countSettingsFrame.columnconfigure(1,weight=1,uniform="fred")
	
	countSettingsFrame.rowconfigure(0,weight=1,uniform="fred")
	countSettingsFrame.rowconfigure(1,weight=1,uniform="fred")
	countSettingsFrame.rowconfigure(2,weight=1,uniform="fred")
	
	return countBaseFrame
