#!/bin/bash
execpath="$(pwd)"
echo "[install.sh] Installing ependencies for siRNATools"
echo "[install.sh] Checking path...."
#appdir=$( realpath ~)/.local/share/applications
condaPath=$( realpath ~)
condaPath="$condaPath/RNAival_Dependencies"
if [ ! -e $condaPath ]; then
	space=" "
	echo $condaPath
	if ! [[ $condaPath =~ $space ]]; then
		#echo "[install.sh] No space in home directory, proceding."
		mkdir $condaPath
	else
		echo "[install.sh] Error, space in linux home directory, exiting."
		exit 1
	fi
fi
cp RNAival_environment.yml $condaPath
cd $condaPath
echo "[install.sh] Selected path for dependencies: $(pwd)"

#DOwnload miniforge installer
if [ ! -f Miniforge3-$(uname)-$(uname -m).sh ]; then
	echo "[install.sh] Downloading miniforge installer"
	wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
	
	lastCode=$?
	if [ $lastCode -eq 0 ]; then
		echo "[install.sh] Download sucessfull"
	else
		echo "[install.sh] Error while downloading miniforge, exitcode $lastCode."
		echo "[install.sh] Please report this issue and provide the contents of this terminal."
		exit 1
	fi
else
	echo "[install.sh] Installer already present"
fi

#install miniforge
export HOME="./miniforge"
if [ ! -f ./miniforge/bin/conda ]; then
	echo "[install.sh] Installing miniforge"
	bash Miniforge3-$(uname)-$(uname -m).sh -p ./miniforge -b
	
	lastCode=$?
	if [ $lastCode -eq 0 ]; then
		echo "[install.sh] Miniforge installation sucessfull"
	else
		echo "[install.sh] Error while installing miniforge, exitcode $lastCode."
		echo "[install.sh] Please report this issue and provide the contents of this terminal."
		exit 1
	fi
else
	echo "[install.sh] Miniforge already installed"
fi
eval "$(miniforge/bin/conda shell.bash hook)"
lastCode=$?
if [ $lastCode -eq 0 ]; then
	echo "[install.sh] Sucessfully hooked conda to this shell"
else
	echo "[install.sh] Error while hoocking conda, exitcode $lastCode."
	echo "[install.sh] Please report this issue and provide the contents of this terminal."
	exit 1
fi

if [ ! -d ./miniforge/envs/RNAival ]; then
	echo "[install.sh] Creating environment"
	#conda config --add channels bioconda
	#conda config --add channels conda-forge
	#conda config --set channel_priority strict
	#conda update conda -y	#???
	#TODO conda update -n base -c conda-forge conda	#??
	conda env create -y -f RNAival_environment.yml	#TODO use separate yml file for mac if the xft tk branch is not available!
	
	lastCode=$?
	if [ $lastCode -eq 0 ]; then
		echo "[install.sh] Environment sucessfully created."
	else
		echo "[install.sh] Error while creating the program environment, exitcode $lastCode."
		echo "[install.sh] Please report this issue and provide the contents of this terminal."
		exit 1
	fi
else
	echo "[install.sh] Environment already present, updating"
	conda env update --file RNAival_environment.yml --prune
	lastCode=$?
	if [ $lastCode -eq 0 ]; then
		echo "[install.sh] Environment sucessfully updated."
	else
		echo "[install.sh] Error while updating the program environment, exitcode $lastCode."
		echo "[install.sh] Please report this issue and provide the contents of this terminal."
		exit 1
	fi
fi

echo "[install.sh] Activating environment"
conda activate RNAival
lastCode=$?
if [ $lastCode -eq 0 ]; then
	echo "[install.sh] Environment sucessfully activated."
else
	echo "[install.sh] Error while activating the program environment, exitcode $lastCode."
	echo "[install.sh] Please report this issue and provide the contents of this terminal."
	exit 1
fi
#conda list

cd ..

appdir=/usr/share/applications
if [ ! -d $appdir ]; then
	echo "[install.sh] Creating $appdir"
	mkdir -p $appdir
fi
if [ ! -f "$appdir/siRNATools.desktop" ]; then
	echo "[install.sh] Creating .desktop file in $appdir"
	#sudo touch $appdir/siRNATools.desktop
	read -r -d '' desktopFile <<- EOM
		[Desktop Entry]
		Version=1.0
		Type=Application
		Comment=RNAival software for evaluating siRNAs and dsRNAs for RNAi

		Name=RNAival
		Exec="$execpath/run.sh" "$execpath"
		Icon=$execpath/sprites/Icon.png

		Terminal=false
		Categories=Utility;
	EOM
	#echo "$desktopFile"
	echo "$desktopFile" | sudo tee "$appdir/RNAival.desktop"	#requires entering password!
	#doesnt work on WSL, because not isntalled
	#shouldnt be necessarly with WSLg, should auto gen Windows link if in usr/share/applications
	#update-desktop-database $homePath/.local/share/applications
fi

echo "[install.sh] Installation sucessful!"
