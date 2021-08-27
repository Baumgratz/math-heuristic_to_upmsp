from problem import Problem
from copy import deepcopy
from random import randint, seed


class Solution:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.machine = [[] for _ in self.problem.M]
        self.cost = [0]*self.problem.machines
        self.tam_machine = [0]*self.problem.machines
        self.makespan = 0
        self.jobs = [False]*(self.problem.jobs+1)
        self.njobs = 0

    @property
    def num_jobs(self):
        num = 0
        for m in self.machine:
            for _ in m:
                num += 1
        return num

    def write(self, directory):
        string = '%d\n' % (self.problem.machines)
        for i in self.problem.M:
            string += '%d ' % len(self.machine[i])
            if len(self.machine[i]) > 0:
                k = self.machine[i][0]
                string += str(k-1)
                for k in self.machine[i][1:]:
                    string += ' ' + str(k-1)
            string += '\n'
        string += '\nTotal makespan: %d\n\n' % (self.makespan)
        try:
            file = open(directory, 'a+')
        except FileNotFoundError:
            file = open(directory, 'w+')
        file.write(string)
        file.close()


    def copy(self) -> "Solution":
        solution = Solution(self.problem)
        solution.machine = deepcopy(self.machine)
        solution.cost = deepcopy(self.cost)
        solution.jobs = deepcopy(self.jobs)
        solution.tam_machine = deepcopy(self.tam_machine)
        solution.makespan = self.makespan
        solution.njobs = self.njobs
        return solution

    def allocate(self, machine: int, job: int, position=None):
        if position is None:
            position = len(self.machine[machine])
        if not self.jobs[job]:
            self.tam_machine[machine] += 1
            self.machine[machine].insert(position, job)
            self.jobs[job] = True
            self.njobs += 1
            # calculo de custo
            self.new_cost(machine, job, position)

    def new_cost(self, machine: int, job: int, position: int):
        # custo
        j = self.machine[machine][position-1]
        self.cost[machine] += self.problem.processing[machine][job]

        self.cost[machine] += self.problem.setup[machine][j][job]
        if position+1 < len(self.machine[machine]):
            k = self.machine[machine][position+1]
            self.cost[machine] += self.problem.setup[machine][job][k]
            self.cost[machine] -= self.problem.setup[machine][j][k]

        self.makespan = max(self.cost[machine], self.makespan)

    def print(self):
        print(self.to_string())

    def to_string(self):
        string = '\n'
        for i in self.problem.M:
            string += (str(i+1) + ' : ' + str(self.machine[i]) + ' = ' + str(self.cost[i]) + '\n')
        string += str(self.makespan) + '\n'
        for j in self.problem.N0:
            if not self.jobs[j]:
                string += str(j) + ' '
        string += '\n'
        # print(self.jobs)
        # print(self.njobs)
        return string

    def new_solution(self, solution: list):
        for i in self.problem.M:
            self.cost[i] = solution[i][0]
            self.tam_machine[i] = solution[i][1]
            if solution[i][0] > self.makespan:
                self.makespan = solution[i][0]
            for j in solution[i][2]:
                self.machine[i].append(j)
                self.jobs[j] = True
                self.njobs += 1

    def is_all_jobs_set(self) -> bool:
        for job in self.jobs:
            if not job:
                return False
        return True
