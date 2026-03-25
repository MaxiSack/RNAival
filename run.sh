#!/bin/bash
#TODO check for env before and throw error!
condaPath=$( realpath ~)
condaPath="$condaPath/RNAival_Dependencies"
echo "[launcher.sh] Dependencies path: $condaPath"
#echo $condaPath/miniforge/envs/RNAival
#echo "[launcher.sh] Terminal location: $pwd"
echo "[launcher.sh] Exec path argument: $1"
execpath=$1
if [ -z "${execpath}" ]; then
	execpath="."
fi
echo "[launcher.sh] Execution path selected: $execpath"
#sleep 10
if [ -d $condaPath/miniforge/envs/RNAival ]; then
	if ! eval "$("$condaPath"/miniforge/bin/conda shell.bash hook)"; then
		echo "[launcher.sh] ERROR: could not start conda"
		echo "[launcher.sh] This terminal will close in 10 minutes"
		sleep 600
		exit 1
	fi
	if ! conda activate RNAival; then
		echo "[launcher.sh] ERROR: could not activate the program environment"
		echo "[launcher.sh] This terminal will close in 10 minutes"
		sleep 600
		exit 1
	fi
	#conda list
	echo "[launcher.sh] Activated conda, starting launcher"
	echo "[launcher.sh] running: python3 -u '$execpath/run.py' '$execpath' | tee '$execpath/terminal.log'"
	python3 -u "$execpath/run.py" "$execpath" | tee "$execpath/terminal.log"
	lastCode=$?
	if [ $lastCode -eq 0 ]; then
		echo "[launcher.sh] Program exited"
	else
		echo "[launcher.sh] Programm exited with error, exitcode $lastCode"
		echo "[launcher.sh] Please report this issue and provide the contents of this terminal"
		echo "[launcher.sh] This terminal will close in 10 minutes"
		sleep 600
		exit 1
	fi
else
	echo "[launcher.sh] ERROR: Conda environment not found, please run install.sh"
	echo "[launcher.sh] This terminal will close in 10 minutes"
	sleep 600
	exit 1
fi

#sleep 10
