# Neuro trace utils

some utils for tracing neurons

# Instalation
This is a python package that can be installed with pip or conda. Pip is faster and simpler, but conda is less likely to fail.

## instalation with pip
Install the package and dependencies with:

```
pip install "git+https://github.com/pnewstein/neurotraceutils.git@master"
```

## instalation with conda
First, use git clone, or simpy download the file ```environment.yml```. Next, cd into the directory containing ```environment.yml``` and 

the following will create a conda environment named ```ntu``` with neurotraceutils installed

```
conda env create -f environment.yml
```

Next activate the environment:
```
conda activate ntu
```

Now to run neurotraceutils, you must make sure that the ntu conda environment is active

# Updating
Regradless of how you installed the package. The following will upgrade neurotraceutils:
```
pip install --upgrade "git+https://github.com/pnewstein/neurotraceutils.git@master"
```

# Usage
use ```python -m neurotraceutils --help``` for detailed help

## imaris to swc
The following code will convert the filaments within the imaris file ```image.ims``` to swc files. These
files will be in the folder ```image```.
```
python -m traceutils ims2swc image.ims
```
