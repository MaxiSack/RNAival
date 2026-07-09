
from .static import moduleID,moduleType,guiOrder,pptTags
from .gui.main_gui import add_sRGUI,add_parametersetList,loadParameterSetValues
from .sR_processing import runPipeline

def add_GUI(main):	#Called to create GUI elements and other things on Program startup
	add_sRGUI(main)	#Add GUI elements with parameters to the main GUI

def init_project(main):	#called when a new project is created or an existing one is loaded
	main.PM.addParameterSet(pptTags,moduleID,setname=moduleID,virtual=True)	#save default parameter set for this module
	main.PM.saveParameterSet(moduleID,existsOkay=True)

def after_project_load(main):	#called after project has been loaded
	add_parametersetList(main)
	loadParameterSetValues(main,moduleID)

def save_data(main):
	pass	#nothing to do here since all Parameters are stored in Parameter Sets and handled by the Parametermanager
	
def process(main):	#Process all libraries that use this module
	runPipeline(main)

def evaluate(main):	#evaluate all libraries that use this module for evaluation
	pass
