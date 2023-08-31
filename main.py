from os import system
import sys
import timeit
# from pathlib import Path
import os

from problem import Problem
from solution import Solution
from heuristic import Heuristic
from construtives import construtive_random
import read_init_sol as ris
from util import thebest

import logging


def initial_solution(
    parameter: str,
    file_instance: str,
    problem: Problem,
    parameters: str,
    seed: int,
    time: int
) -> Solution:
    if parameter == 'SLS':
        job = problem.jobs
        machine = problem.machines
        num = problem.num
        instance = problem.instance
        name = "SLS_%d_%d_%d_%d_%s.txt" % (
            job, machine, num, instance, parameters
        )
        destiny = 'init_solution/%s' % (name)
        command = 'java -jar upmsp.jar %s %s -time %d -seed %d' % (
            file_instance, destiny, time, seed)
        system(command)
        return ris.init_solution(destiny, problem)
    if parameter == 'Greedy':
        return construtive_random(problem)
    else:
        raise NameError('Variável Instanciada errada')


def func(argv):
    # -max_jobs 33 -exec_time 22
    file_instance = argv[1]
    mip_max_it_time = 16
    sls_time = 0
    max_free_jobs = 106
    max_opt_execs = 1
    total_time = 3600
    seed = -1
    file_inst = file_instance.split('/')[-1]
    output = "solutions_2021/" + file_inst
    init_sol = 'Greedy'
    i = 2
    save_result = 'resultados_2021'
    while i < len(argv):
        if '-mip_max_it_time' == argv[i]:
            i += 1
            mip_max_it_time = float(argv[i])
        if '-max_jobs' == argv[i]:
            i += 1
            max_free_jobs = int(argv[i])
        if '-total_time' == argv[i]:
            i += 1
            total_time = float(argv[i])
        if '-init_sol' == argv[i]:
            i += 1
            init_sol = argv[i]
        if '-seed' == argv[i]:
            i += 1
            seed = int(argv[i])
        if '-output' == argv[i]:
            i += 1
            output = argv[i]
        if '-sls_time' == argv[i]:
            i += 1
            sls_time = int(argv[i])
        if '-save_result' == argv[i]:
            i += 1
            save_result = argv[i]
        i += 1

    parameters = '%.2f_%d' % (mip_max_it_time, max_free_jobs)
    time_start = timeit.default_timer()
    problem = Problem(directory=file_instance)
    solution = initial_solution(
        parameter=init_sol,
        file_instance=file_instance,
        problem=problem,
        parameters=parameters,
        seed=seed,
        time=sls_time
    )
    objetive_solution = solution.makespan
    heuristic = Heuristic(problem, solution)
    time_end = timeit.default_timer()

    job = problem.jobs
    machine = problem.machines
    num = problem.num
    instance = problem.instance
    name = "I_%d_%d_S_1-%d_%d"
    inst = name % (job, machine, num, instance)

    elapsed_time = time_end - time_start
    mip_max_time = total_time - elapsed_time

    print('Começo a execução')
    time_start = timeit.default_timer()
    heuristic.run(
        mip_max_time=mip_max_time,
        max_free_jobs=max_free_jobs,
        mip_max_it_time=mip_max_it_time,
        max_opt_execs=max_opt_execs,
        random_seed=seed
    )
    time_end = timeit.default_timer()
    heuristic_time = time_end - time_start
    print('Terminou a execução')

    obj = heuristic.solution.makespan
    B = thebest()
    gap = (obj - B[inst])/obj*100
    # print(gap)

    #Save Solution
    #Path(output).mkdir(parents=True, exist_ok=True)
    #Gets and creates the output path (if needed)
    create_path = False
    output_path = ""
    for i in range(len(output) - 1, 0, -1):
        if output[i] == '/':
            output_path = output[0:i + 1]
            path = True
            break
    if create_path:
        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    heuristic.solution.write(output)

    # Save Results
    total_time = heuristic_time + elapsed_time

    try:
        file = open(
            '%s/%d_%d_%d_%d.csv' % (save_result, job, machine, num, instance),
            'a+'
        )
    except FileNotFoundError:
        file = open(
            '%s/%d_%d_%d_%d.csv' % (save_result, job, machine, num, instance),
            'w+'
        )
    file.write(
        '%d;%.2f;%d;%.2f;%d;%.2f\n' %
        (
            objetive_solution,  # A
            elapsed_time,  # B
            obj,  # C
            heuristic_time,  # D
            heuristic.cont,  # E
            total_time  # F
        )
    )
    file.close()


if __name__ == '__main__':
    logging.disable(sys.maxsize) 
    func(sys.argv)
