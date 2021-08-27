from mip import *
from mip.model import *
from problem import Problem
from solution import Solution


class MIPModel:

    def __init__(self, problem: Problem, V, machines, jobs):

        model = Model(solver_name=GUROBI)
        self.problem = problem

        # Sets
        M = list(range(len(machines)))
        N = list(range(len(jobs)))
        jobs.append(0)
        N0 = list(range(len(jobs)))

        # Variables
        cmax = model.add_var(var_type=CONTINUOUS, name='Makespan')
        c = []
        for j in N0:
            # var +=1
            c.append(
                model.add_var(var_type=CONTINUOUS, name='CJ_' + str(jobs[j]))
            )
        y = []
        x = []
        for i in M:
            x.append([])
            y.append([])
            for j in N0:
                y[i].append(
                    model.add_var(
                        var_type=BINARY,
                        name='y_' + str(machines[i]) + '_' + str(jobs[j])
                    )
                )
                x[i].append([])
                for k in N0:
                    x[i][j].append(model.add_var(
                        var_type=BINARY, name='x_'+str(machines[i])+'_'+str(jobs[j])+'_'+str(jobs[k]))
                    )

        # Constraints

        const = 0

        # Constraint 10 (Avalos)
        for j in N:
            const += 1
            n = jobs[j]
            model.add_constr(
                xsum(y[i][j] for i in M) == 1,
                name='yj_' + str(n)
            )

        # Constraint 11 (Avalos)
        for i in M:
            m = machines[i]
            for k in N:
                const += 1
                n = jobs[k]
                model.add_constr(
                    y[i][k] == xsum(x[i][j][k] for j in N0 if j != k),
                    name='yf_'+str(m)+'_'+str(n)
                )

        # Constraint 12 (Avalos)
        for i in M:
            m = machines[i]
            for j in N:
                const += 1
                n = jobs[j]
                model.add_constr(
                    y[i][j] == xsum(x[i][j][k] for k in N0 if j != k),
                    name='yb_'+str(m)+'_'+str(n)
                )

        # Constraint 5 (Avalos)
        for i in M:
            const += 1
            m = machines[i]
            model.add_constr(
                xsum(x[i][-1][k] for k in N) <= 1,
                name='start_' + str(m)
            )

        # Constraint 6 (Avalos)
        self.big_m = []
        for i in M:
            m = machines[i]
            for j in N0:
                n1 = jobs[j]
                for k in N:
                    n2 = jobs[k]
                    if(j != k):
                        if(problem.setup[m][n1][n2] + problem.processing[m][n2] > V):
                            x[i][j][k].ub = 0
                        else:
                            const += 1
                            self.big_m.append(
                                model.add_constr(
                                    c[k] - c[j] + 2*V*(1-x[i][j][k]) >=
                                    problem.setup[m][n1][n2] +
                                    problem.processing[m][n2],
                                    name='cycle_%d_%d_%d' % (m, n1, n2)
                                )
                            )

        # Constraint 7 (Avalos)
        model.add_constr(c[-1] == 0, name='job_artificial')

        # Constraint 8 (Avalos)
        for j in N:
            model.add_constr(cmax >= c[j])

        # Constraint 14 (Avalos)
        for i in M:
            const += 1
            m = machines[i]
            model.add_constr(
                xsum(problem.setup[m][jobs[j]][jobs[k]]*x[i][j][k]
                     for j in N0 for k in N if k != j
                     ) +
                xsum(problem.processing[m][jobs[j]]*y[i][j]
                     for j in N
                     ) <= cmax,
                name='cmax_'+str(m)
            )

        model.objective = cmax
        model.sense = MINIMIZE

        self.model = model
        self.x = x
        self.y = y
        self.c = c
        self.cmax = cmax
        self.machines = machines
        self.jobs = jobs
        self.const = const

    def set_solution(self, solution: Solution):
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

    def optimize(self, solution: Solution, time=10) -> Solution:
        self.model.threads = 1
        self.model.verbose = 0
        self.status = self.model.optimize(max_seconds=time)

        if self.model.num_solutions > 0 and self.cmax.x < solution.makespan:
            # Updates solution object
            for j in self.jobs[:-1]:
                solution.jobs[j] = False
                solution.njobs -= 1
            for i in self.problem.M:
                if i in self.machines:
                    m = self.machines.index(i)
                    solution.cost[i] = 0
                    solution.machine[i][:] = []
                    solution.tam_machine[i] = 0
                    j = self.jobs[-1]
                    n1 = self.jobs.index(j)
                    while True:
                        for k in self.jobs:
                            if j != k:
                                n2 = self.jobs.index(k)
                                if self.x[m][n1][n2].x > 1e-4:
                                    if k != 0:
                                        solution.allocate(i, k)
                                    j = k
                                    n1 = n2
                                    break
                        if j == 0:
                            break
        solution.makespan = max(solution.cost)
        return solution

    def is_optimal(self):
        return self.model.status == OptimizationStatus.OPTIMAL

    def print(self):
        print('Machines %3d : %s' % (len(self.machines), self.machines))
        print('Jobs     %3d : %s' % (len(self.jobs), self.jobs))

    def print_var(self):
        M = list(range(len(self.machines)))
        N0 = list(range(len(self.jobs)))
        varx = [(self.x[i][j][k].name, self.x[i][j][k].x)
                for i in M for j in N0 for k in N0 if self.x[i][j][k].x > 1e-4]
        vary = [(self.y[i][j].name, self.y[i][j].x)
                for i in M for j in N0 if self.y[i][j].x > 1e-4]
        print('X : ')
        for (n, x) in varx:
            print('%s : %d' % (n, x))
        print('Y : ')
        for (n, x) in vary:
            print('%s : %d' % (n, x))
