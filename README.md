
# GaFEM
GaFEM is a software, which aims at coupling genetic algorithm with FEM simulations for automated parameter optimization in the design processes. However, it is also suitable for many other optimization tasks, where the quality of a design can be evaluated by various computational approaches. 

## Features
 - The user can use the graphic user interface of GaFEM (see **usage** section) to perform both single- and multi-objective optimizations. For single-objective optimization, the user will get the optimum or at least the sub-optimum designs with the highest fitness values. For multi-objective optimization, the user will get the so-called Pareto front, which is a set of designs that show the best compromise between conflicting design objectives. 
 - The user can choose to perform the computation either on the local computer or on a remote cluster.
 - In case of large optimization problems, parallelization of computation can be performed to accelerate the optimization process.
 - The user can save frequently applied optimization scenarios as .opt files, which can 
 - When the optimization is interupted unexpectedly, it is possible to resume the optimizaton process at the broken point.

## Getting started
1. Make sure python 2.7 is installed in the computer.
2. The following python libraries must be installed: tkinter, mttkinter, matplotlib, numpy, pandas, Pmw, paramiko, PIL.
3. Copy all the files in this repository to your working directory.
4. Enter your working directory through a command prompt in Window system or a terminal in Linux system and type `python GAGUI.py` to start the software.
