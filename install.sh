#!/bin/bash
execpath="$(pwd)"
echo "[install.sh] Installing ependencies for RNAival"
echo "[install.sh] Checking path...."

condaPath=$( realpath ~)
condaPath="$condaPath/RNAival_Dependencies"
if [ ! -e $condaPath ]; then
	space=" "
	echo $condaPath
	if ! [[ $condaPath =~ $space ]]; then
		mkdir $condaPath
	else
		echo "[install.sh] Error, space in linux home directory, exiting."
		exit 1
	fi
fi

if [[ $(uname) == "Linux" ]]; then	#use separate yml file for mac because the xft tk branch is not available!
	envFile="RNAival_environment.yml"
else
	envFile="RNAival_environment_mac.yml"	#yml with standard tk version
fi

cp $envFile $condaPath
cd $condaPath
echo "[install.sh] Selected path for dependencies: $(pwd)"

#Download miniforge installer
if [ ! -f Miniforge3-$(uname)-$(uname -m).sh ]; then
	if command -v wget >/dev/null; then
		echo "[install.sh] Downloading miniforge installer with wget."
		wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
	else
		echo "[install.sh] wget is not available, looking for curl instead."
		if command -v curl >/dev/null; then
			echo "[install.sh] Downloading miniforge installer with curl."
			curl -L -o "Miniforge3-$(uname)-$(uname -m).sh" "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
		else
			echo "[install.sh] curl is also not available, exiting."
			echo "[install.sh] You could manually download "
			echo "             https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
			echo "[install.sh] and place it into $(pwd) ."
			echo "[install.sh] Then start the installer again."
			exit 1
		fi
	fi
	
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
	conda env create -y -f $envFile
	
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
	conda env update --file $envFile --prune
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
cd ..

if [[ $(uname) == "Linux" ]]; then	#create desktop entry if on linux or WSL
	appdir=/usr/share/applications
	localappdir=~/.local/share/applications
	if [ ! -f "$appdir/RNAival.desktop" ] && [ ! -f "$localappdir/RNAival.desktop" ]; then
		echo "[install.sh] Creating .desktop file in $appdir"
		if [ ! -d $appdir ]; then
			echo "[install.sh] Creating $appdir"
			mkdir -p $appdir
		fi
		
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
		
		echo "[install.sh] This requires sudo privileges, use ctrl+C to cancel and create the entry locally instead"
		echo "$desktopFile" | sudo tee "$appdir/RNAival.desktop"	#requires entering password!
		#with WSLg, auto generated Windows link if in usr/share/applications
		
		lastCode=$?
		if [ $lastCode -eq 0 ]; then
			echo "[install.sh] Desktop entry created at $appdir/RNAival.desktop."
		else
			if [ ! -d $localappdir ]; then
				echo "[install.sh] Creating $localappdir"
				mkdir -p $localappdir
			fi
			echo "$desktopFile" | tee "$localappdir/RNAival.desktop"
			echo "[install.sh] Desktop entry created at $localappdir/RNAival.desktop."
		fi
	fi
fi

if [[ $(uname) == "Linux" ]]; then	#check if on WSl, then install extra packages with apt for the help functions
	if [[ ! $(command -v wslinfo) == "" ]]; then
		echo "[install.sh] On WSL, installing extra components so that the help functions work (requires sudo)."
		sudo add-apt-repository ppa:wslutilities/wslu
		sudo apt update
		sudo apt install wslu xdg-utils
	fi
fi

echo "[install.sh] Installation sucessful!"
