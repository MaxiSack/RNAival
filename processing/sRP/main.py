
from .gui.main_gui import add_sRGUI,add_parametersetList,loadParameterSetValues
from .sR_processing import runPipeline
from .static import moduleID,pptTags

def add_GUI(main):	#Called to create GUI elements and other things on Program startup
	add_sRGUI(main)	#Add GUI elements with parameters to the main GUI

def run(main):		#Process all libraries that use this module
	runPipeline(main)

def init_project(main):	#called when a new project is created or an existing one is loaded
	main.PM.addParameterSet(pptTags,moduleID,setname="sRP",virtual=True)	#save default parameter set for this module
	main.PM.saveParameterSet("sRP",existsOkay=True)

def after_project_load(main):	#called after project has been loaded
	add_parametersetList(main)
	loadParameterSetValues(main,"sRP")
	
