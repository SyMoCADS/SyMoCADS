<img src="idc_bvt_logo.png" alt="IDC Logo" width="65" height="40"/>

# Media Modulation Testbed: Code Package 

This repository contains the experiments and the associated code used to evaluate those experiments from the "Media Modulation: Experimental Paper" ($\color{red}Louis:\ requires\ revision\ if\ new\ title\ is\ decided$).

`Note`: For reasons of package size and download speed, this package only contains data from 3 example experiments. To access data from all experiments, download the extended *mmtb.db* database from zenodo ($\color{red}Louis:\ add\ link$) and move it into your project folder. As long as the extended database is present in the current working directory or its subdirectories, the experiments it contains will be available.

## Installation
The *mmtb* package can easily be installed via the pip package manager by entering:

```pip install git+https://github.com/SyMoCADS/SyMoCADS.git```

## Module Structure
* mmtb
    * [evaluation](./docs/evaluation.md)
      * [synchronization](./docs/evaluation/synchronization.md)
      * [detection](./docs/evaluation/detection.md)
      * [filters](./docs/evaluation/filters.md)
    * [experiments](./docs/experiments.md)
    * ([dtypes](./docs/dtypes.md))

## Examples
We have provided some [code examples](./examples) to serve as a brief tutorial on the functionality and use of this package.

## Contact 
If you have any question or suggestions for improvents, feel free to open up issues or contact us directly.

($\color{red}Louis:\ feel\ free\ to\ add\ your\ contact\ informations$)

**Louis Wolf**:

- Email: louis.wolf@fau.de




