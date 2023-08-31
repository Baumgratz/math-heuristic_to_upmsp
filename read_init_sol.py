from problem import Problem
from solution import Solution


def init_solution(arq: str, problem: Problem) -> Solution:
    file = open(arq)
    file.seek(0)
    lines = file.readlines()
    file.close()
    lines = [l[:-1] for l in lines]
    machines = int(lines[0])
    solution = Solution(problem)
    for i in range(1, machines+1):
        jobs = [int(n)+1 for n in lines[i].split(' ')][1:]
        for j in jobs:
            solution.allocate(i-1, j)
    return solution
