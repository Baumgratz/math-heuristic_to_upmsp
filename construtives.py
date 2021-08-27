from util import shuffle
from problem import Problem
from solution import Solution


def construtive(problem: Problem) -> Solution:
    # print("Entrei aqui")

    M = problem.M
    N = problem.N
    # N0 = problem.N0
    m = 0
    complete_time = 0

    solution = [[0, 0, []] for _ in M]

    for j in N:
        # print_s(s)
        m = 0
        complete_time = solution[m][0]
        processing_j = problem.processing[m][j]

        for i in M[1:]:

            if solution[i][0] < solution[m][0]:
                m = i
                complete_time = solution[i][0]
                processing_j = problem.processing[m][j]

            elif solution[i][0] == solution[m][0] and \
                    processing_j > problem.processing[i][j]:
                m = i
                complete_time = solution[i][0]
                processing_j = problem.processing[m][j]

        if complete_time == 0:
            solution[m][0] = problem.setup[m][0][j]
            solution[m][2].append(j)

        elif solution[m][1] == 1:
            k = solution[m][2][0]
            if problem.setup[m][0][j] + problem.setup[m][j][k] < \
                    problem.setup[m][0][k] + problem.setup[m][k][j]:
                solution[m][0] += problem.setup[m][0][j]
                solution[m][0] += problem.setup[m][j][k]
                solution[m][0] -= problem.setup[m][0][k]
                solution[m][2].insert(0, j)

            else:
                solution[m][0] += problem.setup[m][k][j]
                solution[m][2].append(j)

        else:
            p = -10
            pa = 0
            pd = solution[m][2][0]
            for k in range(solution[m][1]):
                pd = solution[m][2][k]
                if problem.setup[m][pa][j] + problem.setup[m][j][pd] < problem.setup[m][pa][pd]:
                    p = k-1

                pa = solution[m][2][k]

            if p == -10:
                ul = solution[m][2][-1]
                solution[m][0] += problem.setup[m][ul][j]
                solution[m][2].append(j)

            elif p >= 10:
                pa = solution[m][2][p]
                pd = solution[m][2][p+1]
                solution[m][0] += problem.setup[m][pa][j] + \
                    problem.setup[m][j][pd]
                solution[m][0] -= problem.setup[m][pa][pd]
                solution[m][2].insert(p+1, j)

            else:
                fj = solution[m][2][0]
                solution[m][0] += problem.setup[m][0][j] + \
                    problem.setup[m][j][fj]
                solution[m][0] -= problem.setup[m][0][fj]
                solution[m][2].insert(0, j)

        solution[m][0] += processing_j
        solution[m][1] += 1
    class_solution = Solution(problem)
    class_solution.new_solution(solution)
    return class_solution


def construtive_random(problem: Problem) -> Solution:
    # print("Entrei aqui")

    M = problem.M
    N = problem.N
    # N0 = problem.N0
    m = 0
    complete_time = 0

    solution = [[0, 0, []] for _ in M]

    shuffle(N)

    for j in N:
        m = 0
        complete_time = solution[m][0]
        processing_j = problem.processing[m][j]

        for i in M[1:]:

            if solution[i][0] < solution[m][0]:
                m = i
                complete_time = solution[i][0]
                processing_j = problem.processing[m][j]

            elif solution[i][0] == solution[m][0] and \
                    processing_j > problem.processing[i][j]:
                m = i
                complete_time = solution[i][0]
                processing_j = problem.processing[m][j]

        if complete_time == 0:
            solution[m][0] = problem.setup[m][0][j]
            solution[m][2].append(j)

        elif solution[m][1] == 1:
            k = solution[m][2][0]
            if problem.setup[m][0][j] + problem.setup[m][j][k] < problem.setup[m][0][k] + problem.setup[m][k][j]:
                solution[m][0] += problem.setup[m][0][j] + \
                    problem.setup[m][j][k]
                solution[m][0] -= problem.setup[m][0][k]
                solution[m][2].insert(0, j)

            else:
                solution[m][0] += problem.setup[m][k][j]
                solution[m][2].append(j)

        else:
            p = -10
            pa = 0
            pd = solution[m][2][0]
            for k in range(solution[m][1]):
                pd = solution[m][2][k]
                if problem.setup[m][pa][j] + problem.setup[m][j][pd] < problem.setup[m][pa][pd]:
                    p = k-1

                pa = solution[m][2][k]

            if p == -10:
                ul = solution[m][2][-1]
                solution[m][0] += problem.setup[m][ul][j]
                solution[m][2].append(j)

            elif p >= 10:
                pa = solution[m][2][p]
                pd = solution[m][2][p+1]
                solution[m][0] += problem.setup[m][pa][j] + \
                    problem.setup[m][j][pd]
                solution[m][0] -= problem.setup[m][pa][pd]
                solution[m][2].insert(p+1, j)

            else:
                fj = solution[m][2][0]
                solution[m][0] += problem.setup[m][0][j] + \
                    problem.setup[m][j][fj]
                solution[m][0] -= problem.setup[m][0][fj]
                solution[m][2].insert(0, j)

        solution[m][0] += processing_j
        solution[m][1] += 1
    class_solution = Solution(problem)
    class_solution.new_solution(solution)
    return class_solution
