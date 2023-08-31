from problem import Problem
from solution import Solution
from subproblem import MIPModel
from sub_master_sequence import MasterSequence
from random import uniform, randint, seed
from copy import copy
from time import time


class Heuristic:

    def __init__(self, problem: Problem, solution: Solution, makespan=-1):
        self.problem = problem
        self.solution = solution
        makespan = int(makespan)
        if makespan == -1:
            makespan = solution.makespan
        self.cont = 0
        self.list_makespan = []
        self.list_max_jobs = []

    def run_fanjul(
        self,
        mip_max_time,
        max_free_jobs,
        mip_max_it_time,
        max_opt_execs,
        random_seed=-1
    ):
        if random_seed != -1:
            seed(random_seed)
        makespan = self.solution.makespan
        self.cont = 0
        opt_execs = 0
        start_time = time()
        print("    /-------------------------------------------------------------------------------\\")
        print("    |    Makespan   |   Free Jobs   | Free Machines |    It. Time   |   Total Time  | ")
        print("    |-------------------------------------------------------------------------------|")

        while time() - start_time < mip_max_time:
            self.cont += 1
            # Select free machines and jobs
            max_free_jobs = min(max_free_jobs, self.problem.jobs)

            # change num_jobs (int) to the list of jobs (list_jobs)
            (free_machines, list_jobs) = self.w_roullete(max_free_jobs)
            num_jobs = len(list_jobs)

            # Create a subproblem
            subproblem = MasterSequence(
                self.problem,
                free_machines,
                list_jobs
            )

            if len(self.solution.machine[free_machines[0]]) + 1 > max_free_jobs:
                max_free_jobs = len(self.solution.machine[free_machines[0]]) + 1

            # Choose free jobs on the last machine
            len_free_machines = len(free_machines)
            if num_jobs > max_free_jobs:
                i = free_machines[-1]
                tam = len(self.solution.machine[i])
                list_jobs = copy(self.solution.machine[i])
                fixed_jobs = []
                while num_jobs > max_free_jobs:
                    r = randint(0, tam - 1)
                    fixed_jobs.append(list_jobs.pop(r))
                    num_jobs -= 1
                    tam -= 1
                subproblem.fix_vars(fixed_jobs, self.solution.machine[i])

            subproblem.set_solution(self.solution)

            model_max_time = min(
                mip_max_it_time,
                mip_max_time - (time() - start_time)
            )
            model_max_time = max(model_max_time, 0)

            start_model_time = time()
            solution_ = subproblem.run(
                max_time=model_max_time,
                solution=self.solution
            )
            end_model_time = time()
            # solution_.print()
            model_time = end_model_time - start_model_time

            mark = "*" if makespan > solution_.makespan else ""
            print("    | %13d | %13d | %13d | %13.2f | %13.2f | %s" % (
                solution_.makespan,
                max_free_jobs,
                len_free_machines,
                model_time,
                time() - start_time,
                mark
            ))

            if makespan > solution_.makespan:  # Improved soln
                opt_execs = 0
            else:
                if subproblem.is_optimal():  # Optimal
                    opt_execs += 1
                    if opt_execs >= max_opt_execs:
                        # Increase free jobs in 20%
                        max_free_jobs = int(max_free_jobs * 1.2)
                        opt_execs = 0
                else:  # Time limit
                    # Decrease free jobs in 20%
                    max_free_jobs = int(max_free_jobs * 0.8)
                    opt_execs = 0

            self.solution = solution_
            makespan = self.solution.makespan
            opt_execs += 1
        print("    \\-------------------------------------------------------------------------------/")

    def run_avalara(
        self,
        mip_max_time,
        max_free_jobs,
        mip_max_it_time,
        max_opt_execs,
        random_seed=-1
    ):
        if random_seed != -1:
            seed(random_seed)
        makespan = self.solution.makespan
        self.cont = 0
        opt_execs = 0
        start_time = time()
        print("    /-------------------------------------------------------------------------------\\")
        print("    |    Makespan   |   Free Jobs   | Free Machines |    It. Time   |   Total Time  | ")
        print("    |-------------------------------------------------------------------------------|")

        while time() - start_time < mip_max_time:
            self.cont += 1
            # Select free machines and jobs
            max_free_jobs = min(max_free_jobs, self.problem.jobs)

            # change num_jobs (int) to the list of jobs (list_jobs)
            (free_machines, list_jobs) = self.w_roullete(max_free_jobs)
            num_jobs = len(list_jobs)

            # Create a subproblem
            subproblem = MIPModel(
                self.problem,
                makespan,
                free_machines,
                list_jobs
            )

            if len(self.solution.machine[free_machines[0]]) + 1 > max_free_jobs:
                max_free_jobs = len(self.solution.machine[free_machines[0]]) + 1

            # Choose free jobs on the last machine
            len_free_machines = len(free_machines)
            if num_jobs > max_free_jobs:
                i = free_machines[-1]
                tam = len(self.solution.machine[i])
                list_jobs = copy(self.solution.machine[i])
                fixed_jobs = []
                while num_jobs > max_free_jobs:
                    r = randint(0, tam - 1)
                    fixed_jobs.append(list_jobs.pop(r))
                    num_jobs -= 1
                    tam -= 1
                subproblem.fix_vars(fixed_jobs, self.solution.machine[i])

            subproblem.set_solution(self.solution)

            model_max_time = min(
                mip_max_it_time,
                mip_max_time - (time() - start_time)
            )
            model_max_time = max(model_max_time, 0)

            start_model_time = time()
            solution_ = subproblem.optimize(
                time=model_max_time,
                solution=self.solution
            )
            end_model_time = time()
            model_time = end_model_time - start_model_time

            mark = "*" if makespan > solution_.makespan else ""
            print("    | %13d | %13d | %13d | %13.2f | %13.2f | %s" % (
                solution_.makespan,
                max_free_jobs,
                len_free_machines,
                model_time,
                time() - start_time,
                mark
            ))

            if makespan > solution_.makespan:  # Improved soln
                opt_execs = 0
            else:
                if subproblem.is_optimal():  # Optimal
                    opt_execs += 1
                    if opt_execs >= max_opt_execs:
                        # Increase free jobs in 20%
                        max_free_jobs = int(max_free_jobs * 1.2)
                        opt_execs = 0
                else:  # Time limit
                    # Decrease free jobs in 20%
                    max_free_jobs = int(max_free_jobs * 0.8)
                    opt_execs = 0

            self.solution = solution_
            makespan = self.solution.makespan
            opt_execs += 1
        print("    \\-------------------------------------------------------------------------------/")

    def w_roullete(self, max_jobs: int) -> (list, list):
        list_machine = copy(self.problem.M)

        cost_min = min(self.solution.cost)
        cost_max = self.solution.makespan+1
        tg_alpha = 100/(cost_max - cost_min)

        select = self.solution.cost.index(self.solution.makespan)
        select_list = [select]
        list_jobs = copy(self.solution.machine[select])

        list_machine.remove(select)
        len_list_machine = len(list_machine)

        # Escolhendo a segunda máquina
        sum_ = 0
        fitness = [0 for _ in list_machine]
        fraction = [0 for _ in list_machine]
        scale = [0 for _ in list_machine]

        for i in range(len_list_machine):
            diff_medium = cost_max - self.solution.cost[list_machine[i]]
            fitness[i] = tg_alpha * diff_medium
            sum_ += fitness[i]

        for i in range(len_list_machine):
            fraction[i] = fitness[i]/sum_

        scale[0] = fraction[0]
        for i in range(1, len_list_machine):
            scale[i] = scale[i-1] + fraction[i]

        aux = uniform(0, 1)
        j = 0
        while scale[j] < aux:
            j += 1

        select = list_machine.pop(j)
        select_list.append(select)

        list_jobs += self.solution.machine[select]
        len_list_machine -= 1

        # termino da escolha
        while len(list_jobs) < max_jobs:
            sum_ = 0
            fitness = [0 for _ in list_machine]
            fraction = [0 for _ in list_machine]
            scale = [0 for _ in list_machine]

            for i in range(len_list_machine):
                diff_medium = cost_max - self.solution.cost[list_machine[i]]
                fitness[i] = tg_alpha * diff_medium
                sum_ += fitness[i]

            for i in range(len_list_machine):
                fraction[i] = fitness[i]/sum_

            scale[0] = fraction[0]

            for i in range(1, len_list_machine):
                scale[i] = scale[i-1] + fraction[i]

            aux = uniform(0, 1)
            j = 0
            while scale[j] < aux:
                j += 1

            select = list_machine.pop(j)
            select_list.append(select)

            list_jobs += self.solution.machine[select]
            len_list_machine -= 1
        return (select_list, list_jobs)

    def run(
        self,
        mip_max_time,
        max_free_jobs,
        mip_max_it_time,
        max_opt_execs,
        random_seed=-1,
        option='fanjul'
    ):
        if option.lower() == 'avalara':
            return self.run_avalara(mip_max_time, max_free_jobs, mip_max_it_time, max_opt_execs, random_seed)
        if option.lower() == 'fanjul':
            return self.run_fanjul(mip_max_time, max_free_jobs, mip_max_it_time, max_opt_execs, random_seed)
