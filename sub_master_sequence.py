from mip import *
from random import choice
from problem import Problem
from solution import Solution

from time import time
import math


class SequenceOptimizer(ConstrsGenerator):
    """Class to generate cutting planes for the TSP"""
    def __init__(self, problem, master):
        self.problem = problem
        self.master = master
        self.y = None
        self.cmax = None
        self.count = 0
        self.count_nc = 0
    
    def model_sequence(self):
        model = Model(solver_name=GUROBI)
        const = 0
        u = []

        #Sets
        M = list(range(len(self.master.machines)))
        N = list(range(len(self.master.jobs[:-1])))
        # jobs.append(0)
        N0 = list(range(len(self.master.jobs)))

        jobs = self.master.jobs
        machines = self.master.machines

        pos0 = len(self.master.jobs) - 1

        #Variables
        for j in N0:
            u.append(model.add_var(var_type=INTEGER,name='U_'+str(jobs[j])))
        x = []
        for i in M:
            x.append([])
            for j in N0:
                x[i].append([])
                for k in N0:
                    x[i][j].append(model.add_var(var_type=BINARY,name='x_'+str(machines[i])+'_'+str(jobs[j])+'_'+str(jobs[k])))
                    if j == k and jobs[j] != 0:
                        x[i][j][k].ub = 0

        # Constraint 3
        for i in M:
            const+=1
            model.add_constr(
                xsum(x[i][pos0][k] for k in N0) <= 1,
                name = 'start_'+str(machines[i])
            )

        # Constraint 5
        for i in M:
            for j in N:
                const+=1
                model.add_constr(
                    round(self.y[i][j].x) == xsum(x[i][j][k] for k in N0 if j!=k),
                    name = 'yf_'+str(machines[i])+'_'+str(jobs[j])
                )

        # Constraint 6
        for i in M:
            for k in N:
                const+=1
                model.add_constr(
                    round(self.y[i][k].x) == xsum(x[i][j][k] for j in N0 if j!=k),
                    name = 'yb_'+str(machines[i])+'_'+str(jobs[k])
                )

        # n = len(self.problem.N)
        num_jobs = []
        for i in M:
            total_y = sum(round(self.y[i][j].x) for j in N)
            num_jobs.append(total_y)

        n = []
        for j in N:
            for i in M:
                if self.y[i][j].x > 0.5:
                    n.append(num_jobs[i])
                    break

        # Constraint 10
        for j in N:
            for k in N:
                if j != k:
                    model.add_constr(
                        u[j] - u[k] + n[j] * xsum(x[i][j][k] for i in M) <= n[j] - 1,
                        name=f'cycle_u_{jobs[j]}_{jobs[k]}'
                    )

        # Constraint 14
        for j in N:
            model.add_constr(
                u[j] + (n[j] - 1) * xsum(x[i][pos0][j] for i in M) <= n[j] - 1,
                name=f'big_m_{jobs[j]}'
            )

        # Constraint 13
        for j in N:
            model.add_constr(
                u[j] + xsum(x[i][pos0][j] for i in M) >= 1,
                name=f'small_m_{jobs[j]}'
            )

        model.objective = xsum(
            xsum(self.problem.setup[machines[i]][jobs[j]][jobs[k]]*x[i][j][k] for j in N0 for k in N) +
            xsum(self.problem.processing[machines[i]][jobs[j]]*round(self.y[i][j].x) for j in N)
            for i in M
        )

        model.sense = MINIMIZE
        self.model = model
        self.x = x

    def optimize_sequence(self, time=10) -> Solution:
        self.model.verbose = 0
        self.model.threads = 1
        status = self.model.optimize(max_seconds = time)

        solution_ = Solution(self.problem)
        # if status == OptimizationStatus.INFEASIBLE:
        #     jobs = self.master.problem.jobs
        #     machine = self.master.problem.machines
        #     num = self.master.problem.num
        #     instance = self.master.problem.instance
        #     name = f'{jobs}_{machine}_{num}_{instance}_{self.count}_{self.count_nc}'
        #     self.model.write(f'MODELO_INVIAVEL_{name}.lp')
        #     self.master.solution.write(f'solution_modelo_inviavel_{name}.txt')
        #     print(f'Status: {status}')
        #     raise Exception
        if status != OptimizationStatus.NO_SOLUTION_FOUND:
            for i in self.problem.M:
                if i in self.master.machines:
                    m = self.master.machines.index(i)
                    j = self.master.jobs[-1]
                    n1 = self.master.jobs.index(j)
                    while True:
                        for k in self.master.jobs:
                            n2 = self.master.jobs.index(k)
                            if self.x[m][n1][n2].x > 0.5:
                                if k != 0:
                                    solution_.allocate(i, k)
                                j = k
                                n1 = n2
                                break
                        if j == 0:
                            break
            solution_.makespan = max(solution_.cost)
        else:
            solution_.makespan = float('inf')
        return solution_

    def set_solution_sequence(self):
        solution = self.master.solution
        start = []
        for i in self.master.machines:
            m = self.master.machines.index(i)
            if solution.machine[i] != []:
                n1 = self.master.jobs.index(0)
                for k in solution.machine[i]:
                    n2 = self.master.jobs.index(k)
                    start.append((self.x[m][n1][n2], 1.0))
                    n1 = n2
                n2 = self.master.jobs.index(0)
                start.append((self.x[m][n1][n2], 1.0))
        self.model.start = start

    def _set_solution_master(self, solution: Solution):
        for j in range(1, self.master.problem.jobs+1):
            if solution.jobs[j]:
                self.master.solution.jobs[j] = False
                self.master.solution.njobs -= 1
        for i in self.master.machines:
            self.master.solution.cost[i] = 0
            self.master.solution.machine[i][:] = []
            self.master.solution.tam_machine[i] = 0
            for j in solution.machine[i]:
                self.master.solution.allocate(i, j)
        self.master.solution.makespan = max(self.master.solution.cost)
            

    def generate_constrs(self, model: Model):
        self.cmax = model.translate(self.master.cmax)
        if self.master.solution and self.cmax.x > self.master.solution.makespan + 1e-4 :
            return
        self.y = model.translate(self.master.y)

        self.model_sequence()
        self.set_solution_sequence()
        solution = self.optimize_sequence()

        if not self.master.solution or solution.makespan < self.master.solution.makespan:
            self._set_solution_master(solution)
            model.add_constr(self.cmax <= solution.makespan)

        if self.cmax.x < solution.makespan:
            # print(f'Add Cut : {self.counter}')
            for i in self.master.machines:
                self.count_nc += 1
                m = self.master.machines.index(i)
                list_job = solution.machine[i]
                N_i = [self.master.jobs.index(j) for j in list_job if j in self.master.jobs]

                if len(N_i) == 1:
                    j = N_i[0]
                    model.add_constr(
                        self.master.cmax >= solution.cost[i] - ((1 - self.y[m][j]) * (self.problem.processing[i][self.master.jobs[j]])),
                        name=f'CUT_{self.count}_{i}'
                    )
                elif len(N_i) > 1:
                    model.add_constr(
                        self.master.cmax >= solution.cost[i] -
                        xsum(
                            (1 - self.y[m][j]) *
                            (
                                self.problem.processing[i][self.master.jobs[j]] +
                                max([
                                    self.problem.setup[i][self.master.jobs[k]][self.master.jobs[j]]
                                    for k in N_i if k != j
                                ])
                            )
                            for j in N_i
                        ),
                        name=f'CUT_{self.count}_{i}'
                    )
        self.count += 1


# Based in the Fanjul-Peyro's article
class MasterSequence:

    def __init__(self, problem: Problem, machines, jobs):
        model = Model(solver_name=GUROBI)
        self.problem = problem

        #Sets
        M = list(range(len(machines)))
        N = list(range(len(jobs)))
        jobs.append(0)
        N0 = list(range(len(jobs)))

        #Variables
        cmax = model.add_var(var_type=CONTINUOUS,name='Makespan')
        y = []
        x = []
        for i in M:
            y.append([])
            x.append([])
            for j in N0:
                y[i].append(model.add_var(var_type=BINARY, name='y_'+str(machines[i])+'_'+str(jobs[j])))
                x[i].append([])
                for k in N0:
                    x[i][j].append(model.add_var(var_type=CONTINUOUS,name='x_'+str(machines[i])+'_'+str(jobs[j])+'_'+str(jobs[k]),ub=1))
                    if j == k and jobs[j] != 0:
                        x[i][j][k].ub = 0

        #Constraints
        const = 0

        # Constraint 2
        for i in M:
            const+=1
            model.add_constr(
                xsum(problem.setup[machines[i]][jobs[j]][jobs[k]]*x[i][j][k] for j in N0 for k in N if k!=j) +
                xsum(problem.processing[machines[i]][jobs[j]]*y[i][j] for j in N) <= cmax,
                name='cmax_'+str(machines[i])
            )

        # Constraint 3
        pos0 = len(N0)-1
        for i in M:
            const+=1
            model.add_constr(xsum(x[i][pos0][k] for k in N) <= 1, name = 'start_'+str(machines[i]))

        # Constraint 4
        for j in N:
            const+=1
            model.add_constr(xsum(y[i][j] for i in M) == 1, name = 'yj_'+str(jobs[j]))

        # Constraint 5
        for i in M:
            for j in N:
                const+=1
                model.add_constr(y[i][j] == xsum(x[i][j][k] for k in N0 if j!=k), name = 'yb_'+str(machines[i])+'_'+str(jobs[j]))

        # Constraint 6
        for i in M:
            for k in N:
                const+=1
                model.add_constr(y[i][k] == xsum(x[i][j][k] for j in N0 if j!=k), name = 'yf_'+str(machines[i])+'_'+str(jobs[k]))

        # new constraint
        for j in N:
            for k in N[j+1:]:
                model.add_constr(xsum(x[i][j][k] + x[i][k][j] for i in M) <= 1, name=f'cycle_{jobs[j]}_{jobs[k]}')

        model.objective = cmax
        model.sense = MINIMIZE

        # model.lazy_constrs_generator = SequenceOptimizer(problem, self)

        self.model = model
        self.x = x
        self.y = y
        self.cmax = cmax
        self.solution = None
        self.machines = machines
        self.jobs = jobs

    def set_solution(self, solution:Solution):
        start = [(self.cmax, solution.makespan)]
        for i in self.machines:
            m = self.machines.index(i)
            if solution.machine[i] != []:
                n1 = self.jobs.index(0)
                for k in solution.machine[i]:
                    n2 = self.jobs.index(k)
                    start.append((self.x[m][n1][n2], 1.0))
                    start.append((self.y[m][n2], 1.0))
                    n1 = n2
                n2 = self.jobs.index(0)
                start.append((self.x[m][n1][n2], 1.0))
        self.model.start = start

    def fix_vars(self, static_job: list, solution_list: list):
        dic_solution = [self.jobs.index(j) for j in solution_list]
        dic_static_job = [self.jobs.index(j) for j in static_job]
        j = 0
        for k in dic_solution:
            if k in dic_static_job:
                self.y[-1][k].lb = 1
                if j in dic_static_job:
                    self.x[-1][j][k].lb = 1
            j = k

    def optimize(self, time, solution: Solution):
        self.model.verbose = 0
        self.model.threads = 1

        self.model.optimize(max_seconds=time)
        return self.solution

    def is_optimal(self):
        return self.model.status == OptimizationStatus.OPTIMAL

    def run(self, max_time, solution) -> Solution:
        self.solution = solution
        self.lower_bound = float('inf')
        sequence_optimizer = SequenceOptimizer(self.problem, self)
        self.model.lazy_constrs_generator = sequence_optimizer
        solution = self.optimize(max_time, solution)
        return solution
