
# GaFEM
GaFEM is a software, which initially aims at coupling genetic algorithm with FEM simulations for automated parameter optimization in the design processes. It is also suitable for many other optimization tasks, where the quality of a design can be evaluated by various computational approaches. 

## Features
 - The user can use the graphic user interface of GaFEM (see **Using the graphic user interface** section) to perform both single- and multi-objective optimizations. For single-objective optimization, the user will get the optimum or at least the sub-optimum designs with the highest fitness values. For multi-objective optimization, the user will get the so-called Pareto front, which is a set of designs that show the best compromise between conflicting design objectives. 
 - The user can choose to perform the computation either on the local computer or on a remote cluster.
 - In case of large optimization problems, parallelization of computation can be performed to accelerate the optimization process.
 - The user can save frequently applied optimization scenarios as .opt files for the convenience of repeated usage. 
 - When the optimization is interupted unexpectedly, it is possible to resume the optimizaton process at the broken point.

## Getting started
1. Make sure python 3 is installed in the computer.
2. The following python libraries must be installed: tkinter, matplotlib, numpy, pandas, Pmw, paramiko, PIL, deap.
3. Copy all the files in this repository to your working directory.
4. Enter your working directory through a command prompt in Window system or a terminal in Linux system and type `python GAGUI.py` to start the software.

## Using the graphic user interface
1. The primary user interface

   <img src="images/main_interface.png" width="1200"> 
   
2. Monitoring the optimization process

   <img src="images/monitoring_optimization.png" width="1200"> 
   
3. Viewing the optimization results in tabular form

   <img src="images/print_results.png" width="500"> 
   
## Preparations for starting an optimization case
   to be continued
