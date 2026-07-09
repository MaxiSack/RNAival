
import json
import os.path

from .static import moduleID,moduleType,guiOrder,moduleTags
from .gui.main_gui import add_dsP_eval_GUI,loadData,setMultiCovPairs

def add_GUI(main):	#Called to create GUI elements and other things on Program startup
	add_dsP_eval_GUI(main)	#Add GUI elements with parameters to the main GUI

def init_project(main):	#called when a new project is created or an existing one is loaded
	main.PM.deleteTags(["dsP-multiCoverage-tmp"])	#Delete tmp tags from PM so that they can be properly re-added next
	setMultiCovPairs(main)	#load default values for multiCov

def after_project_load(main):	#called after project has been loaded, can be used to load custom stuff
	dsPStoragePath = os.path.join(main.PM.get("projectPath"),"Parameters","dsP.json")
	multiCoverageList = None
	if os.path.isfile(dsPStoragePath):
		print(f"[dsP module] Loading settings from {dsPStoragePath}")
		try:
			with open(dsPStoragePath,"r") as jr:
				jsonstr = jr.read()
				saveConstruct = json.loads(jsonstr)
				parameters = saveConstruct["Parameters"]
				main.PM.setAll(parameters)
				multiCoverageList = saveConstruct["MultiCoverage"]
		except Exception as e:
			main.writeError(f"[dsP module] Error loading settings from \"{dsPStoragePath}\".")
			main.writeError(str(e))
			return False
	else:
		print("[dsP module] Could not find settings, using defaults instead")
	setMultiCovPairs(main,multiCoverageList=multiCoverageList)

def save_data(main):	#store all GUI based data from this module that is not in a Parameterset (which is all for this module)
	dsPStoragePath = os.path.join(main.PM.get("projectPath"),"Parameters","dsP.json")
	print(f"[dsP module] Saving settings to {dsPStoragePath}")
	
	parameters = main.PM.getDict(tags=moduleTags)
	multiCoverageList = [(int(pair[1].get()),pair[2].get()) for pair in main.dsP_multiCovPairListWidgets if not pair is None]
	saveConstruct = {"Parameters":parameters,"MultiCoverage":multiCoverageList}
	try:
		with open(dsPStoragePath,"w") as jw:
			json.dump(saveConstruct,jw,indent="\t")
	except Exception as e:
		main.writeError(f"[dsP module] Error saving project settings to \"{dsPStoragePath}\".")
		main.writeError(str(e))
		return False

def process(main):
	pass

def evaluate(main):	#evaluate all libraries that use this module for evaluation
	print(f"[dsP module] Loading graphics")
	loadData(main,export=False,gui=False)
