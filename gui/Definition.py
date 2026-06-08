
from tkinter import Tk
from tkinter import Text
from tkinter import Menu

from tkinter.ttk import Notebook
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton

from gui.functions import *
from gui.inputSelection import add_inputGUI

from gui.siI_eval import add_siI_eval_GUI
from gui.dsP_eval import add_dsP_eval_GUI

from iostuff.programSettings import getLastProjects

#ONLY gui definitions here!
def defineGUI(main):
	mainWindow = main.mainWindow
	
	#---------------- Menu -------------------
	mainWindow.option_add('*tearOff', False)	#prevents "tearing off" dropdowns
	menubar = Menu(mainWindow)
	main.menubar = menubar
	mainWindow.config(menu=menubar)
	menubar.config(font=main.buttonTextFont,fg=main.styleman.textColour,bg=main.styleman.backgroundColour,
			activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	main.styleman.registredMenus.append(menubar)
	menubar.add_command(label=" New ",command=lambda main=main:createNewProjectMenu(main))	#padding?
	openRecentMenu = Menu(menubar)
	menubar.add_cascade(menu=openRecentMenu,label=" Recent ")
	openRecentMenu.config(font=main.textFont,fg=main.styleman.textColour,bg=main.styleman.backgroundColour,
			activeforeground=main.styleman.textColour,activebackground=main.styleman.textBackgroundColour)
	main.styleman.registredMenus.append(openRecentMenu)
	lastProjects = getLastProjects("",execPath=main.execPath)
	for name,path in lastProjects:
		openRecentMenu.add_command(label=name,command=lambda main=main,pp=path:loadProject(main,pp))
	
	#menubar.add_command(label="Open",command=openProjectList)	#not implemented
	main.settingsMenu = None
	menubar.add_command(label=" Settings ",command=lambda main=main:openSettingsMenu(main))
	#menubar.add_command(label="About",command=openAboutMenu)
	#menubar.add_command(label="        ",command=openAboutMenu)
	#menubar.add_command(label="Project ",command=openAboutMenu)
	menubar.add_command(label=" Darkmode ",command=lambda main=main:switchTheme(main))
	
	mainWindow.bind_all("<Control-d>",lambda event,main=main:switchTheme(main))
	
	#---------------- Tabs -------------------
	main.mainNotebook = Notebook(mainWindow)
	main.mainNotebook.pack(fill="both",expand=True,anchor="nw")
	
	add_inputGUI(main)
	
	main.outputTextLog = getStyledText(main,main.mainNotebook)	#Log is now second tab 
	main.mainNotebook.add(main.outputTextLog,	text="Program log")
	main.outputTextLog.tag_configure("error",foreground="#ff0000",font=main.errorLogFont)
	main.outputTextLog.tag_configure("warn",foreground="#dd8800",font=main.errorLogFont)
	main.logTabIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding LOG at {main.logTabIndex}")
	main.mainNotebooktabs[main.logTabIndex] = main.outputTextLog
	
	# -------------------- loading modules and applying their GUI --------------- 
	main.moduleDict = loadModules(main)
	for key,value in main.moduleDict.items():
		value.add_GUI(main)
	
	# -------------------- GUI for evaluation types --------------- 
	add_siI_eval_GUI(main)
	
	add_dsP_eval_GUI(main)
	
	
	main.graphicsTabIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding Graphics at {main.graphicsTabIndex}")
	
	graphicsPadding = ThemedFrame(main.mainNotebook,style="gBorder.TFrame")
	main.mainNotebook.add(graphicsPadding,text="Graphical output")
	main.mainNotebooktabs[main.graphicsTabIndex] = graphicsPadding
	
	main.outputGraphicsNotebook = Notebook(graphicsPadding)
	main.outputGraphicsNotebook.pack(fill="both",expand=True,padx=main.frameBorderSize*2,pady=main.frameBorderSize*2)
	#main.mainNotebook.add(main.outputGraphicsNotebook,text="Graphical output")
	main.outputGroups = dict()	#target-key -> notebook
	
	
	textNotebookIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding Text at {textNotebookIndex}")
	main.outputTextField = getStyledText(main,main.mainNotebook)
	main.outputTextField.config(tabs = "6c")
	main.mainNotebook.add(main.outputTextField,text="Textual output")
	main.mainNotebooktabs[textNotebookIndex] = main.outputTextField
	
	for i in range(len(main.mainNotebook.tabs())):	#hiding all tabs until a new project has been generated or an existing one was loaded
		main.mainNotebook.hide(i)
	
	if main.PM.get("loadLastProjectOnStartup") and len(lastProjects)>0:loadProject(main,lastProjects[0][1])

