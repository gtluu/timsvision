# Demo Branch

## This is a demo branch of TIMSvision using MALDI-TIMS-qTOF IMS data from MSV000088438

# TIMSvision: a tool to visualize multidimensional imaging mass spectrometry datasets

TIMSvision is a simple data visualization tool developed in Python 3.7 using Dash to be able to easily and quickly 
visualize matrix-assisted laser desorption/ionization-trapped ion mobility spectrometry-time-of-flight 
(MALDI-TIMS-TOF) imaging mass spectrometry (IMS) data acquired via the Bruker timsTOF fleX. Data is converted to 
the open imzML format using [TIMSCONVERT](https://github.com/gtluu/timsconvert) and then loaded into TIMSvision.

## Installation (Work in Progress)

#### Install Anaconda on Linux

1. Download and install Anaconda for [Linux](https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh). 
Follow the prompts to complete installation. Anaconda3-2021.11 for Linux is used as an example here.
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash /path/to/Anaconda3-2021.11-Linux-x86_64.sh
```
2. Add ```anaconda3/bin``` to PATH.
```
export PATH=$PATH:/path/to/anaconda3/bin
```

#### Install Anaconda on Windows.

1. Download and install Anaconda for [Windows](https://repo.anaconda.com/archive/Anaconda3-2021.11-Windows-x86_64.exe). 
Follow the prompts to complete installation.
2. Run ```Anaconda Prompt (R-MINI~1)``` as Administrator.

#### Set Up ```conda env```

3. Create a conda instance. You must be using Python 3.7.
```
conda create -n timsvision python=3.7
```
4. Activate conda environment.
```
conda activate timsvision
```

#### Install TIMSvision

5. Download TIMSvision by cloning the Github repo (you will need to have [Git](https://git-scm.com/downloads) and 
ensure that the option to enable symbolic links was checked during installation). It may be necessary to explicitly
allow for the use of symbolic links by adding the ```-c core.symlinks=true``` parameter on Windows.
```
git clone https://www.github.com/gtluu/timsvision
or
git clone -c core.symlinks=true https://www.github.com/gtluu/timsvision
```
6. Install dependencies.
```
# TIMSvision dependencies
pip install -r /path/to/timsvision/requirements.txt
```
7. You will also need to install a modified version of pyimzML. Currently, the necessary code is available on the
```mob_ion_image``` branch.
```
pip install git+https://github.com/gtluu/pyimzML.git@mob_ion_image
```

## Usage
Data is loaded into TIMSvision by loading the path for an imzML file. After loading, a contour plot is generated using 
binned m/z and 1/K0 values. An ion image can be obtained by manually specifying m/z and 1/K0 values and their absolute 
tolerances, or by viewing the contour plot and clicking on the heatmap peak of interest and clicking 
```Update Ion Image```.
