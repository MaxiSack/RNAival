
import json
import os.path

from .static import moduleID,moduleType,guiOrder,moduleTags
from .gui.main_gui import add_siIGUI,loadData,addPair,getLibraryPairsFromGUI,resetPairs

def add_GUI(main):	#Called to create GUI elements and other things on Program startup
	add_siIGUI(main)	#Add GUI elements with parameters to the main GUI

def init_project(main):	#called when a new project is created or an existing one is loaded
	main.PM.deleteTags(["siI-pairs-tmp"])	#Delete temporary parameters from PM
	resetPairs(main)

def after_project_load(main):	#called after project has been loaded
	siIStoragePath = os.path.join(main.PM.get("projectPath"),"Parameters","siI.json")
	
	if os.path.isfile(siIStoragePath):
		print(f"[siI module] Loading settings from {siIStoragePath}")
		try:
			with open(siIStoragePath,"r") as jr:
				jsonstr = jr.read()
				saveConstruct = json.loads(jsonstr)
				parameters = saveConstruct["Parameters"]
				main.PM.setAll(parameters)
				libPairs = saveConstruct["Pairs"]
		except Exception as e:
			main.writeError(f"Error loading siI-Pairs from \"{siIStoragePath}\".")
			main.writeError(str(e))
			return False
	else:
		print("[siI module] Trying old system instead")
		try:
			if hasattr(main.IM,"siiPairs"):	#For backwards compatibility
				print(f"[siI module] main.IM.siiPairs exists!")
				libPairs = main.IM.siiPairs
				del main.IM.siiPairs		#delete from IM so that it doesnt also store the siIPairs
			else:
				print("[siI module] siI-Pairs not found, starting at nothing instead.")
				libPairs = list()
		except:
			print("[siI module] Inputmanager did not load siI-Pairs, starting at nothing instead.")
			libPairs = list()
	#print(f"[siI module][Debug] LibPairs: {libPairs}")
	for pair in libPairs:
		addPair(main,pairLoad=pair)	#Add GUI elements based on loaded data

def save_data(main):	#store all GUI based data from this module that is not in a Parameterset
	siIStoragePath = os.path.join(main.PM.get("projectPath"),"Parameters","siI.json")
	print(f"[siI module] Saving settings to {siIStoragePath}")
	
	parameters = main.PM.getDict(tags=moduleTags)
	libPairs = getLibraryPairsFromGUI(main)
	saveConstruct = {"Parameters":parameters,"Pairs":libPairs}
	try:
		with open(siIStoragePath,"w") as jw:
			json.dump(saveConstruct,jw,indent="\t")
	except Exception as e:
		main.writeError(f"[siI module] Error saving project settings to \"{siIStoragePath}\".")
		main.writeError(str(e))
		return False

def process(main):
	pass

def evaluate(main):	#evaluate all libraries that use this module for evaluation
	print(f"[siI module] Loading graphics")
	loadData(main,export=False,gui=False)
