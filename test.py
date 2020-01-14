from time import time

from task2 import solve_timetable_test


for i in range(1, 9):
    t0 = time()
    file_name = 'ExampleProblems/Problem'+ str(i) +'.txt'
    solve_timetable_test(file_name)
    t1 = time()
    print(t1-t0)

for j in range(9, 61):
    if j in [28, 29, 38,39, 58,]: #35, 38, 39, 44, 58
        continue

    t0 = time()
    file_name = 'ExampleProblems2/Problem'+ str(j) +'.txt'
    solve_timetable_test(file_name)
    t1 = time()
    print(t1-t0)