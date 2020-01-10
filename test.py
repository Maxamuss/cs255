from task1 import solve_timetable_test

for i in range(1, 9):
    file_name = 'ExampleProblems/Problem'+ str(i) +'.txt'
    solve_timetable_test(file_name)

for j in range(9, 61):
    file_name = 'ExampleProblems2/Problem'+ str(j) +'.txt'
    solve_timetable_test(file_name)