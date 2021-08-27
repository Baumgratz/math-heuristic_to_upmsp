# Math-Heuristic to UPMSP

The algorithm to find the solution the **UPMSP** (*Unrelated Parallel Machine Scheduling Problem with Sequence Dependent and Setup Times*) when it is use a **math-heuristic**.

***In progress***

## Install

The project **required** install:

 - [Python](https://www.python.org/) >= 3.6
 - [Pip](https://pypi.org/project/pip/) >= 20.1.1
 - [MIP](https://python-mip.readthedocs.io/) >= 1.8.1

It is **recommend** use:

 - [Pypy](https://www.pypy.org/) >= 7.3.1
 - [Gurobi](https://www.gurobi.com/) >= 9.0

## Execute

To execute the project the command is:

```bash
pypy3 main.py $DIR_INSTANCE $PARAMETERS
```

The **$DIR_INSTANCE** put the directory of instance and it is **required**.

### Parameters

The **$PARAMETERS** ins't required.

The parameters is:

 * *mip_max_it_time* : the maximum time (in seconds) to MIP solver execute.
 * *max_jobs* : the number of the initial jobs to work in algorithm;
    * If *max_jobs* is low then amount of jobs on two machines, the algorithm get all jobs in this two machines. (Ignored the initial value of *max_jobs*)
 * *total_time* : Maximum time (in seconds) to algorithm execute.
 * *output*: path when will save the solution of the execution (if exists the path, will write in the end of file)
 * *save_result*: dir that will generate a csv file with results

If doesn't pass a values to parameters, the default values each parameter is:

 - *mip_max_it_time* = 16
 - *max_jobs* = 106
 - *total_time* = 3600 (1 hour)
 - *output* = solutions/**$INSTANCE_NAME**
 - *save_result* = results/**$INSTANCE_NAME**

### Example

```bash
pypy3 main_nw.py instances/I_50_20_S_1-9_1.txt -max_time 600 -mip_max_it_time 30
```

In this example, don't have the parameters *max_jobs*  and they receveid the default value.
Don't matter the order of the parameters, only the name.

## Results

The result's file have the information like in the table below:

| A | B | C | D | E | F |
| :---: | :---: | :---: | :---: | :---: | :---: | 
| objective_initial |  construtive_time | objetive_heuristic | heuristic_time | heuristic.cont | total_time | 

### Instances

The instances used on this projects is on the [link](http://soa.iti.es/files/RSDST.7z)
