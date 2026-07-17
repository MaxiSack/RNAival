
import webbrowser

from tkinter import Tk
from tkinter import Text
from tkinter import Menu

from tkinter.ttk import Notebook
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton

from gui.functions import loadModules,loadProject,loadProjectSelect,createNewProjectMenu,openSettingsMenu,setTheme,switchThemeDarkLight,openAboutMenu
from gui.inputSelection import add_inputGUI

from iostuff.programSettings import getLastProjects

#ONLY gui definitions here!
def defineGUI(main):
	mainWindow = main.mainWindow
	
	#---------------- Menubar -------------------
	mainWindow.option_add('*tearOff', False)	#prevents "tearing off" dropdowns
	menubar = main.styleman.getStyledMenu(mainWindow)
	mainWindow.config(menu=menubar)
	
	#------------- File -------------
	fileMenu = main.styleman.getStyledMenu(menubar)
	menubar.add_cascade(menu=fileMenu,label=" File ")
	fileMenu.add_command(label="New",command=lambda main=main:createNewProjectMenu(main))
	fileMenu.add_command(label="Open",command=lambda main=main:loadProjectSelect(main))
	
	openRecentMenu = main.styleman.getStyledMenu(menubar)
	fileMenu.add_cascade(menu=openRecentMenu,label="Open Recent")
	lastProjects = getLastProjects("",execPath=main.execPath)
	for name,path in lastProjects:
		openRecentMenu.add_command(label=name,command=lambda main=main,pp=path:loadProject(main,pp))
	fileMenu.add_separator()
	fileMenu.add_command(label="Save",command=main.saveSettings)
	fileMenu.add_separator()
	fileMenu.add_command(label="Quit",command=main.closeWindow)
	
	#------------- Edit -------------
	editMenu = main.styleman.getStyledMenu(menubar)
	menubar.add_cascade(menu=editMenu,label=" Edit ")
	main.settingsMenu = None
	editMenu.add_command(label="Settings",command=lambda main=main:openSettingsMenu(main))
	
	themeSelectMenu = main.styleman.getStyledMenu(menubar)
	editMenu.add_cascade(menu=themeSelectMenu,label="Theme")
	for theme in main.styleman.availableThemes:
		themeSelectMenu.add_command(label=theme,command=lambda main=main,theme=theme:setTheme(main,theme))
	main.lastTheme = "light"
	mainWindow.bind_all("<Control-d>",lambda event,main=main:switchThemeDarkLight(main))
	
	#------------- Actions -------------
	actionsMenu = main.styleman.getStyledMenu(menubar)
	menubar.add_cascade(menu=actionsMenu,label=" Actions ")
	actionsMenu.add_command(label="Run pipeline",command=main.runPipeline)
	actionsMenu.add_command(label="Stop pipeline",command=main.terminateThreads)
	actionsMenu.add_separator()
	actionsMenu.add_command(label="Reload graphics",command=main.loadDataIntoGUI)
	actionsMenu.add_command(label="Export graphics",command=main.exportGraphs)
	
	#------------- Help -------------
	helpMenu = main.styleman.getStyledMenu(menubar)
	menubar.add_cascade(menu=helpMenu,label=" Help ")
	main.aboutMenu = None
	helpMenu.add_command(label="About",command=lambda main=main:openAboutMenu(main))
	helpMenu.add_command(label="Manual",command=main.openManual)
	helpMenu.add_command(label="Github",command=lambda url = "https://github.com/MaxiSack/RNAival": webbrowser.open(url,new=0,autoraise=True))
	helpMenu.add_command(label="Contact",command=lambda url = "https://www.informatik.uni-halle.de/arbeitsgruppen/bioinformatik/mitarbeiterinnen/sack/?lang=en": webbrowser.open(url,new=0,autoraise=True))
	
	#---------------- Menubar end -------------------
	
	
	#---------------- Tabs -------------------
	main.mainNotebook = Notebook(mainWindow)
	main.mainNotebook.pack(fill="both",expand=True,anchor="nw")
	
	add_inputGUI(main)
	
	main.outputTextLog = main.styleman.getStyledText(main.mainNotebook)	#Log is now second tab 
	main.mainNotebook.add(main.outputTextLog,	text="Program log")
	main.outputTextLog.tag_configure("error",foreground="#ff0000",font=main.errorLogFont)
	main.outputTextLog.tag_configure("warn",foreground="#dd8800",font=main.errorLogFont)
	main.logTabIndex = len(main.mainNotebooktabs.keys())
	print(f"[GUI def] adding LOG at {main.logTabIndex}")
	main.mainNotebooktabs[main.logTabIndex] = main.outputTextLog
	
	# -------------------- loading modules and applying their GUI --------------- 
	main.moduleDict = loadModules(main)
	for _,value in sorted([(value.guiOrder,value) for key,value in main.moduleDict.items()], key = lambda x:x[0]):
		value.add_GUI(main)
	
	# --------------------Output --------------- 
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
	main.outputTextField = main.styleman.getStyledText(main.mainNotebook)
	main.outputTextField.config(tabs = "6c")
	main.mainNotebook.add(main.outputTextField,text="Textual output")
	main.mainNotebooktabs[textNotebookIndex] = main.outputTextField
	
	for i in range(len(main.mainNotebook.tabs())):	#hiding all tabs until a new project has been generated or an existing one was loaded
		main.mainNotebook.hide(i)
	
	if main.PM.get("RNAival-load_last_project_on_startup") and len(lastProjects)>0:loadProject(main,lastProjects[0][1])

