# Matheuristic to UPMSP

This repo contains the source-code, instances, and data related to the paper **A Fix-and-Optimize Heuristic for the Unrelated Parallel Machine Scheduling Problem**, that is under consideration for publication in Computers & OR.

The paper proposes a fix-and-optimize approach that addresses, at each iteration, a subset of the machines to be scheduled and tries to minimize its largest completion time (makespan). The model that solves each subproblem is based on the exact decomposition approach proposed by [Fanjul Peyro et al. (2019)](https://www.sciencedirect.com/science/article/abs/pii/S0305054818301916?via%3Dihub), that takes advantage of solving non-trivial ordering subproblems separately.
## Installing dependencies

The following packages are required:

- [Python](https://www.python.org/) >= 3.6
- [Pip](https://pypi.org/project/pip/) >= 20.1.1
- [PythonMIP](https://python-mip.readthedocs.io/) >= 1.8.1

To obtain the best performance, the application should be executed with:

- [Pypy](https://www.pypy.org/) >= 7.3.1

and as a MIP solver:

- [Gurobi](https://www.gurobi.com/) >= 9.0

## Run the project

The following command line runs the algorithm:

```bash
pypy3 main.py $INSTANCE $PARAMETERS
```

where `$INSTANCE` is required and stands for the instance file name (and directory).

### CLI parameters

Several optional parameters can be passed to the algorithm:

- `_mip_max_it_time_` (default `16`): runtime limit (secs) for each iteration of the fix-and-optimize algorithm.
- `_max_jobs_` (default `100`): the initial number of jobs to be released in the first iteration of the algorithm;
- `_total_time_` (default `3600`): overall runtime limit (secs) of the algorithm;
- `_output_` (default `solutions/$INSTANCE`): path in which the solution will be written;
- `_save_result_` (default `results/$INSTANCE`): path in which a csv file with the summary of the execution will be written.

### Example

```bash
pypy3 main_nw.py instances/I_50_20_S_1-9_1.txt -max_time 600 -mip_max_it_time 30
```

In this example, the overall runtime limit is 600 seconds and the timelimit for each fix-and-optimize iteration is 30 seconds.

## Results file

The .csv result file has the following structure:

|         A         |        B         |         C          |       D        |       E        |     F      |
| :---------------: | :--------------: | :----------------: | :------------: | :------------: | :--------: |
| objective_initial | construtive_time | objetive_heuristic | heuristic_time | heuristic.cont | total_time |

## Instances

The instances used in this projects are available at [link](http://soa.iti.es/files/RSDST.7z).
