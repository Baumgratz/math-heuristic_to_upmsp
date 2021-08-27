from random import randint


def shuffle(list_sort: list):
    length_list = len(list_sort)
    range_random = length_list - 1
    list_shuffle = list_sort
    times_num = randint(1, 10)
    for _ in range(times_num * length_list):
        first_pos = randint(0, range_random)
        second_pos = randint(0, range_random)
        auxiliar_num = list_shuffle[first_pos]
        list_shuffle[first_pos] = list_shuffle[second_pos]
        list_shuffle[second_pos] = auxiliar_num
