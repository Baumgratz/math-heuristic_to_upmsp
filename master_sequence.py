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
    
    def model_sequence(self):
        model = Model(solver_name=GUROBI)
        const = 0
        u = []
        #Variables
        # model_cmax = model.add_var(var_type=CONTINUOUS,name='Makespan')
        for j in self.problem.N0:
            u.append(model.add_var(var_type=INTEGER,name='U_'+str(j)))
        x = []
        for i in self.problem.M:
            x.append([])
            for j in self.problem.N0:
                x[i].append([])
                for k in self.problem.N0:
                    x[i][j].append(model.add_var(var_type=BINARY,name='x_'+str(i)+'_'+str(j)+'_'+str(k)))
                    if j==k and j != 0:
                        x[i][j][k].ub = 0

        # Constraint 3
        for i in self.problem.M:
            const+=1
            model.add_constr(
                xsum(x[i][0][k] for k in self.problem.N0) <= 1,
                name = 'start_'+str(i)
            )

        # Constraint 5
        for i in self.problem.M:
            for j in self.problem.N:
                const+=1
                model.add_constr(
                    round(self.y[i][j].x) == xsum(x[i][j][k] for k in self.problem.N0 if j!=k),
                    name = 'yf_'+str(i)+'_'+str(j)
                )

        # Constraint 6
        for i in self.problem.M:
            for k in self.problem.N:
                const+=1
                model.add_constr(
                    round(self.y[i][k].x) == xsum(x[i][j][k] for j in self.problem.N0 if j!=k),
                    name = 'yb_'+str(i)+'_'+str(k)
                )

        # n = len(self.problem.N)
        num_jobs = []
        for i in self.problem.M:
            total_y = sum(round(self.y[i][j].x) for j in self.problem.N)
            num_jobs.append(total_y)

        n = [0]
        for j in self.problem.N:
            for i in self.problem.M:
                if self.y[i][j].x > 0.5:
                    n.append(num_jobs[i])
                    break

        # Constraint 10
        for j in self.problem.N:
            for k in self.problem.N:
                if j != k:
                    model.add_constr(
                        u[j] - u[k] + n[j] * xsum(x[i][j][k] for i in self.problem.M) <= n[j] - 1,
                        name=f'cycle_u_{j}_{k}'
                    )

        # Constraint 14
        for j in self.problem.N:
            model.add_constr(
                u[j] + (n[j] - 1) * xsum(x[i][0][j] for i in self.problem.M) <= n[j] - 1,
                name=f'big_m_{j}'
            )

        # Constraint 13
        for j in self.problem.N:
            model.add_constr(
                u[j] + xsum(x[i][0][j] for i in self.problem.M) >= 1,
                name=f'small_m_{j}'
            )

        model.objective = xsum(
            xsum(self.problem.setup[i][j][k]*x[i][j][k] for j in self.problem.N0 for k in self.problem.N) +
            xsum(self.problem.processing[i][j]*round(self.y[i][j].x) for j in self.problem.N)
            for i in self.problem.M
        )

        model.sense = MINIMIZE
        self.model = model
        self.x = x

    def optimize_sequence(self, time=10) -> Solution:
        self.model.verbose = 0
        self.model.threads = 1
        status = self.model.optimize(max_seconds = time)

        solution_ = Solution(self.problem)
        # print("*******************************************")
        # print(f"Status sequence: {self.model.status}")
        # print(f"Num of solutions: {self.sequence.num_solutions}")
        # print("*******************************************")
        if status != OptimizationStatus.NO_SOLUTION_FOUND:
            for i in self.problem.M:
                j = 0
                while True:
                    for k in self.problem.N0:
                        if self.x[i][j][k].x > 0.5:
                            if k != 0:
                                solution_.allocate(i,k)
                            j = k
                            break
                    if j == 0:
                        break
        else:
            solution_.makespan = float('inf')
        return solution_

    def set_solution_sequence(self):
        start = []
        for i in self.problem.M:
            j = 0
            for k in self.problem.N:
                if self.y[i][k].x > 0.5:
                    start.append((self.x[i][j][k], 1.0))
                    j = k
                start.append((self.x[i][j][0], 1.0))
        self.model.start = start

    def generate_constrs(self, model: Model):
        self.cmax = model.translate(self.master.cmax)
        if self.master.solution and self.cmax.x > self.master.solution.makespan + 1e-4 :
            return
        self.y = model.translate(self.master.y)

        self.model_sequence()
        self.set_solution_sequence()
        solution = self.optimize_sequence()

        if not self.master.solution or solution.makespan < self.master.solution.makespan:
            self.master.solution = solution
            model.add_constr(self.cmax <= solution.makespan)

        # print(f'Master Makespan : {self.cmax.x}')
        # print(f'Makespan: {solution.makespan}')

        if self.cmax.x < solution.makespan:
            for i in self.problem.M:
                N_i = solution.machine[i]
                model.add_constr(
                    self.master.cmax >= solution.cost[i] - 
                    xsum(
                        (1 - self.y[i][j]) * 
                        (self.problem.processing[i][j] + max([self.problem.setup[i][k][j] for k in self.problem.N if k != j])) 
                        for j in N_i
                    ), 
                    name=f'CUT_{self.count}_{i}'
                )
        self.count += 1


# Based in the Fanjul-Peyro's article
class MasterSequence:

    def __init__(self, problem: Problem):
        model = Model(solver_name=GUROBI)
        self.problem = problem

        #Sets
        M = problem.M
        N = problem.N
        N0 = problem.N0

        #Variables
        cmax = model.add_var(var_type=CONTINUOUS,name='Makespan')
        y = []
        x = []
        for i in M:
            y.append([])
            x.append([])
            for j in N0:
                y[i].append(model.add_var(var_type=BINARY, name='y_'+str(i)+'_'+str(j)))
                x[i].append([])
                for k in N0:
                    x[i][j].append(model.add_var(var_type=CONTINUOUS,name='x_'+str(i)+'_'+str(j)+'_'+str(k),ub=1))
                    if j == k and j != 0:
                        x[i][j][k].ub = 0

        #Constraints

        const = 0

        # Constraint 2
        for i in M:
            const+=1
            model.add_constr(
                xsum(problem.setup[i][j][k]*x[i][j][k] for j in N0 for k in N if k!=j) +
                xsum(problem.processing[i][j]*y[i][j] for j in N) <= cmax,
                name='cmax_'+str(i)
            )

        # Constraint 3
        for i in M:
            const+=1
            model.add_constr(xsum(x[i][0][k] for k in N) <= 1, name = 'start_'+str(i))

        # Constraint 4
        for j in N:
            const+=1
            model.add_constr(xsum(y[i][j] for i in M) == 1, name = 'yj_'+str(j))

        # Constraint 5
        for i in M:
            for j in N:
                const+=1
                model.add_constr(y[i][j] == xsum(x[i][j][k] for k in N0 if j!=k), name = 'yb_'+str(i)+'_'+str(j))

        # Constraint 6
        for i in M:
            for k in N:
                const+=1
                model.add_constr(y[i][k] == xsum(x[i][j][k] for j in N0 if j!=k), name = 'yf_'+str(i)+'_'+str(k))

        # new constraint
        # for j in N:
        #     for k in N:
        #         if j != k: 
        #             model.add_constr(xsum(x[i][j][k] + x[i][k][j] for i in M) <= 1, name=f'cycle_{j}_{k}')

        model.objective = cmax
        model.sense = MINIMIZE

        # model.lazy_constrs_generator = SequenceOptimizer(problem, self)

        self.model = model
        self.x = x
        self.y = y
        self.cmax = cmax
        self.solution = None

    def set_solution_master(self, solution:Solution):
        # start = []
        start = [(self.cmax, solution.makespan)]
        for i in self.problem.M:
            if solution.machine[i] != []:
                # j = solution.machine[i][0]
                # j = 0
                for k in solution.machine[i]:
                    # start.append((self.x[i][j][k], 1.0))
                    start.append((self.y[i][k], 1.0))
                    # j = k
        self.model.start = start

    def master_optimize(self, time, upper_bound=float('inf'), max_gap=1e-4, limited_solutions=False):

        # self.model.emphasis = SearchEmphasis(emphasis)
        # if not limited_solutions:
        #     self.model.max_solutions = 2
        # self.set_initial_solution()
        self.model.verbose = 0
        self.model.threads = 1
        self.model.max_mip_gap = max_gap

        self.model.optimize(max_seconds=time)
        # print("[Master] Valor de objetivo : {}".format(self.model.objective_value), flush=True)

        solution = Solution(self.problem)
        # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # print('Allocate master solution')
        for i in self.problem.M:
            # string = f'{i}: '
            for j in self.problem.N:
                print(f'({i}, {j})')
                if self.y[i][j].x > 0.5:
                    # string += f'{j} - '
                    solution.allocate(i, j)
            # print(string)
        # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        solution.makespan = self.model.objective_value
        return solution

    def set_initial_solution(self):
        start = []
        start.append((self.y[1][1], 1.0))
        start.append((self.y[0][2], 1.0))
        start.append((self.y[0][3], 1.0))
        start.append((self.y[0][4], 1.0))
        start.append((self.y[1][5], 1.0))
        start.append((self.y[0][6], 1.0))
        self.model.start = start

    def run(self, max_time):
        self.lower_bound = float('inf')
        sequence_optimizer = SequenceOptimizer(self.problem, self)
        # self.master_optimize(60, max_gap=2)
        # sequence_optimizer.generate_constrs(self.model)
        self.model.lazy_constrs_generator = sequence_optimizer
        # self.model.cuts_generator = SubTourCutGenerator(self.problem, self)
        self.model.write('out_model/model_master.lp')
        self.master_optimize(max_time)  #max_time*0.9, max_gap=2)
        self.cont = 1
        return self.solution

