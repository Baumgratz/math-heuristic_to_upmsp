import sys
import timeit
import os

from problem import Problem
from solution import Solution
from heuristic import Heuristic
from construtives import construtive_random

import logging


def func(argv):
    file_instance = argv[1]
    mip_max_it_time = 16
    max_free_jobs = 106
    max_opt_execs = 1
    total_time = 3600
    seed = -1
    file_inst = file_instance.split('/')[-1]
    output = "solutions/" + file_inst
    i = 2
    save_result = 'results'
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
        if '-seed' == argv[i]:
            i += 1
            seed = int(argv[i])
        if '-output' == argv[i]:
            i += 1
            output = argv[i]
        if '-save_result' == argv[i]:
            i += 1
            save_result = argv[i]
        i += 1

    time_start = timeit.default_timer()
    problem = Problem(directory=file_instance)
    solution = construtive_random(problem)
    objetive_initial = solution.makespan
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
    
    objective_final = heuristic.solution.makespan
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

    results_file_name = '%s/I_%d_%d_S_1-%d_%d.csv' % (save_result, job, machine, num, instance)
    try:
        file = open(results_file_name, 'a+')
    except FileNotFoundError:
        file = open(results_file_name, 'w+')
    file.write(
        '%d;%.2f;%d;%.2f;%d;%.2f\n' %
        (
            objective_initial,  # A
            elapsed_time,  # B
            objective_final,  # C
            heuristic_time,  # D
            heuristic.cont,  # E
            total_time  # F
        )
    )
    file.close()


if __name__ == '__main__':
    logging.disable(sys.maxsize) 
    func(sys.argv)
