# RNAival

Python based program for the identification of effective siRNAs and the evaluaiton of effective dsRNAs.

## Requirements
Linux, Mac or a WSL-capable Windows version

## Installation
```
bash install.sh
```
The installer will install miniforge into ~/RNAival_Dependencies and install dependencies through conda.
The installer tries to create a desktop entry in usr/share/applications, which requires root-user priviliges, but is not critical for usage.
On Windows/WSL, prefix the commands with "wsl" or switch to a WSL terminal beforehand.

## Run
```
bash run.sh
```

## Basic usage
- Create a new project
- Select sequencing libraries (fastq.gz)
- Select target sequences (embl,fasta,fna.gz)
- Select targets and evaluation types for libraries
- Run the pipeline
