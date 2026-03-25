from gui.Main import launch
import sys
execPath = ""
if len(sys.argv)>1:
	execPath=sys.argv[1]
launch(execPath)
