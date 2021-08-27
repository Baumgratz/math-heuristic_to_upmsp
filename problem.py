from copy import copy, deepcopy


def print2D(matrix):
    for j in range(len(matrix)):
        s = 'M_'+str(j)+' : '
        for k in range(len(matrix[j])):
            s += str(matrix[j][k]) + ' '
        print(s)


def print3D(matrix):
    for i in range(len(matrix)):
        print('M_'+str(i)+' : ')
        for j in range(len(matrix[i])):
            s = ''
            for k in range(len(matrix[i][j])):
                s += str(matrix[i][j][k]) + ' '
            print(s)


class Problem:
    def __init__(self, job=0, machine=0, num=0, instance=0, directory=None, type_dominance=False, typ=None):
        file = None
        if type_dominance:
            # balanced : 0
            # p-domin : 1
            # s-domin : -1
            if directory is None:
                self.read_rabadi(
                    '../Rabadi_Instance/%s/%don%dRp50Rs50_%dAmeer.dat' % (typ, job, machine, instance))
                self.instance = instance
                self.typ = self.set_typ(typ)
                self.num = self.typ
            else:
                self.read_rabadi(directory)
                end_file = directory.split('_')[-1]
                file = directory.split('/')
                i = 1
                while file[i-1] != 'Rabadi_Instance':
                    i += 1
                instance = int(end_file.split('.')[0])
                self.typ = self.set_typ(file[i])
                self.instance = instance
                self.num = self.typ
        else:
            if directory is None:
                job = str(job)
                machine = str(machine)
                num = str(num)
                instance = str(instance)
                file = open('../instancia/I_'+job+'_'+machine +
                            '_S_1-'+num+'_'+instance+'.txt')
            else:
                file = open(directory)
                d = directory.split('/')[-1].split('_')
                job = int(d[1])
                machine = int(d[2])
                num = int(d[4].split('-')[-1])
                instance = int(d[5].split('.txt')[0])

            lines = file.readlines()
            file.close()
            line = []
            job = int(job)
            machine = int(machine)
            num = int(num)
            instance = int(instance)
            for l in lines:
                aux = l.split('\n')
                aux = aux[0].split(' ')
                nums = self.splitSpace(aux)
                line.append(nums)
            auxp = line[2:job+2]
            cont = job+4
            p = []
            for m in range(machine):
                p.append([0])
                for j in range(job):
                    n = 2*m
                    p[auxp[j][n]].append(auxp[j][n+1])
            auxs = line[cont:]
            # print2D(p)
            while(True):
                try:
                    auxs.remove([])
                except ValueError:
                    break
            s = []
            for m in range(machine):
                s.append([])
                s[m].append([0]*(job+1))
                for j in range(job):
                    s[m].append([0])
                    for k in range(job):
                        nj = job*m + j
                        s[m][j+1].append(auxs[nj][k])
                        #s[m][j+1][k+1] = deepcopy(auxs[nj][k])
            # print3D(s)
            for i in range(machine):
                #p[i][0] = 0
                for k in range(1, job+1):
                    a = s[i][k][k]
                    s[i][0][k] = s[i][k][k]
            self.setup = s
            self.processing = p
            self.M = list(range(machine))
            self.N0 = list(range(job+1))
            self.N = self.N0[1:]
            self.jobs = job
            self.machines = machine
            self.num = num
            self.instance = instance

    def splitSpace(self, strings):
        r = []
        aux = ''
        # print(strings)
        for string in strings:
            for s in string:
                # print(s)
                if(s != '\t'):
                    aux += s
                else:
                    if(aux != ''):
                        if(aux != 'SSD' and aux[0] != 'M'):
                            r.append(int(aux))
                            aux = ''
            if(aux != '' and aux != 'SSD' and aux[0] != 'M'):
                r.append(int(aux))
                aux = ''
        return r

    def read_rabadi(self, arq: str):
        file = open(arq, 'r')
        lines = [l[:-1] for l in file.readlines()]
        file.close()
        machine = int(lines[1])
        job = int(lines[2])
        N = list(range(job))
        N0 = list(range(job+1))
        M = list(range(machine))
        i = 2
        while lines[i] != '':
            i += 1
        i += 1
        lines = [l.split(' ')[:-1] for l in lines[i:]]
        str_processing = lines[:job]
        processing = [[0 for _ in N0] for _ in M]
        for j in N:
            for i in M:
                processing[i][j+1] = int(str_processing[j][i])
        str_setup = lines[job+1:]
        while(True):
            try:
                str_setup.remove([])
            except ValueError:
                break
        setup = [[[0 for _ in N0] for _ in N0] for _ in M]
        for i in M:
            for j in N:
                for k in N:
                    nj = job*i + j
                    setup[i][j+1][k+1] = int(str_setup[nj][k])
        for i in M:
            for k in N0[1:]:
                setup[i][0][k] = setup[i][k][k]

        self.setup = setup
        self.processing = processing
        self.M = machine
        self.N = job
        self.N0 = job+1
        self.jobs = N0
        self.machines = M

    def who_instance(self):
        return "%d_%d_%d_%s" % (self.jobs, self.machines, self.num, self.instance)

    def set_typ(self, string_type):
        if 'Balanced' in string_type:
            return 0
        if 'ProcDomin' in string_type:
            return 1
        if 'SetupDomin' in string_type:
            return -1
