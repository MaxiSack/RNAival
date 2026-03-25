
from tkinter import Tk
from tkinter import Text
from tkinter import Menu

from tkinter.ttk import Notebook
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton

from gui.functions import *
from gui.inputSelection import add_inputGUI
from gui.sR_processing_GUI import add_sRGUI
from gui.siI_eval import add_siI_eval_GUI
from gui.dsP_eval import add_dsP_eval_GUI

from iostuff.programSettings import getLastProjects


#ONLY gui definitions here!
#functions are in siRNAGUI.combinedFunctions !!
#makes it easier to switch GUI lib later... ?
#what about var.get() var.set and validation and such???

def defineGUI(main):
	mainWindow = main.mainWindow
	
	#---------------- Menu -------------------
	mainWindow.option_add('*tearOff', False)	#prevents "tearing off" dropdowns
	menubar = Menu(mainWindow)
	mainWindow.config(menu=menubar)
	menubar.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.textFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	
	
	menubar.add_command(label="New",command=lambda main=main:createNewProjectMenu(main))	#padding?
	openRecentMenu = Menu(menubar)
	menubar.add_cascade(menu=openRecentMenu,label="Open recent")
	openRecentMenu.config(bg=main.styleman.backgroundColour,fg=main.styleman.textColour,font=main.textFont,activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	
	lastProjects = getLastProjects("",execPath=main.execPath)
	for name,path in lastProjects:
		openRecentMenu.add_command(label=name,command=lambda main=main,pp=path:loadProject(main,pp))
	
	#menubar.add_command(label="Open",command=openProjectList)	#not implemented
	#menubar.add_command(label="Settings",command=openSettingsMenu)
	#menubar.add_command(label="About",command=openAboutMenu)
	#menubar.add_command(label="        ",command=openAboutMenu)
	#menubar.add_command(label="Project ",command=openAboutMenu)
	menubar.add_command(label="Darkmode",command=lambda main=main:switchTheme(main))
	
	mainWindow.bind_all("<Control-d>",lambda event,main=main:switchTheme(main))
	
	
	#---------------- Tabs -------------------
	main.mainNotebook = Notebook(mainWindow)
	main.mainNotebook.pack(fill="both",expand=True,anchor="nw")
	
	add_inputGUI(main)
	
	add_sRGUI(main)
	
	main.outputTextLog = getStyledText(main,main.mainNotebook)
	main.mainNotebook.add(main.outputTextLog,	text="Program log")
	main.outputTextLog.tag_configure("error",foreground="#ff0000",font=main.errorLogFont)
	main.outputTextLog.tag_configure("warn",foreground="#dd8800",font=main.errorLogFont)
	writeLog(main,"Here goes the log")
	main.logTabIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding LOG at {main.logTabIndex}")
	main.mainNotebooktabs[main.logTabIndex] = main.outputTextLog
	
	add_siI_eval_GUI(main)
	
	add_dsP_eval_GUI(main)
	
	
	main.graphicsTabIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding Graphics at {main.graphicsTabIndex}")
	main.outputGraphicsNotebook = Notebook(main.mainNotebook)
	main.mainNotebook.add(main.outputGraphicsNotebook,text="Graphical output")
	main.mainNotebooktabs[main.graphicsTabIndex] = main.outputGraphicsNotebook
	main.outputGroups = dict()	#target-key -> notebook
	
	
	textNotebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding Text at {textNotebookIndex}")
	main.outputTextField = getStyledText(main,main.mainNotebook)
	main.outputTextField.config(tabs = "6c")
	main.mainNotebook.add(main.outputTextField,text="Textual output")
	main.mainNotebooktabs[textNotebookIndex] = main.outputTextField
	
	
	
	#---------------- tmp -------------------
	ThemedButton(main.inputFrame,text="Check input [tmp]",command=lambda main=main:checkInputParams(main)).pack(fill="x",anchor="nw")
	ThemedButton(main.inputFrame,text="Save settings [tmp]",command=lambda main=main:saveSettings(main)).pack(fill="x",anchor="nw")
	ThemedButton(main.inputFrame,text="Load graphics [tmp]",command=main.loadDataIntoGUI).pack(fill="x",anchor="nw")
	
	
	
	#TODO make nicer! general parameters; sould be part of programsettings and/or projectsettings ~
	#ThemedLabel(inputFoldOutFrame,text="Threads to use").grid(column=2,row=9,columnspan=2,sticky="w")
	#ThemedEntry(inputFoldOutFrame,width=numberEntryWidth,textvariable=main.addInputVar("threadsVar",StringVar(),"int",16,
	#	"Number of threads needs to be an integer","Number of threads to be used by cutadapt, NGmerge and bowtie")).grid(column=3,row=9,sticky="e",padx=main.frameBorderSize)
	main.PM.add("threadsVar","int",16,"Threads error","Threads used of external tools",tag="general")
	main.PM.add("execPath","path","","Exec path error","Directory where the program runs in",tag="general")
	
	main.PM.add("projectPath","path","","Project path error","Directory where the project is stored",tag="project")
	main.PM.add("readDir","path","0_reads","Project path error","Directory where the project is stored",tag="project")
	main.PM.add("adaptDir","path","1_cutadapt","Project path error","Directory where the project is stored",tag="project")
	main.PM.add("mergeDir","path","2_NGmerge","Project path error","Directory where the project is stored",tag="project")
	main.PM.add("indexDir","path","","Project path error","Directory where the project is stored",tag="project")
	main.PM.add("mapDir","path","","Project path error","Directory where the project is stored",tag="project")
	
	for i in range(len(main.mainNotebook.tabs())):	#hiding all tabs until a new project has been generated or an existing one was loaded
		main.mainNotebook.hide(i)
		#print(f"Hiding notebook tab {i}")
	
	
		
	main.loadLast = True	#TODO programsetting!
	if main.loadLast and len(lastProjects)>0:loadProject(main,lastProjects[0][1])






















