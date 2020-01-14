"""
Methods used in task 2. This is used for testing of methods and ideas. My final 
working solution will be added to the scheduler.py file. This is a version of 
task2.py that has logging (via print statements) to the console when the program
is running.
"""
import module
import tutor
import ReaderWriter
import timetable
import random
import math

import sys
from time import time
"""
Methods for testing.
"""
def solve_timetable_test(file_name):
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements(file_name)
    time_table = timetable.Timetable(3)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print(file_name + ': ' + str(time_table.task1Checker(tutors, modules)))
    simulated_annealing(time_table)

"""
Core methods for the CSP backtracking.
"""
TIME_TABLE_SLOTS = {}

def solve_timetable():
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements("ExampleProblems/Problem4.txt")
    print(len(modules))
    time_table = timetable.Timetable(2)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    generate_time_table_slot()
    # attempt to solve the task
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print_timetable(time_table, tutors, modules)
    t = simulated_annealing(time_table, tutors, modules)
    print(t.cost)

def generate_module_tutor_pairs(time_table, modules, tutors):
    """
    Generate a valid list of module-tutor pairs. For a pair to be valid, the 
    topics of a module must all be in a tutors expertise. This is the as doing it
    in the can_assign_pair method but I do here to reduce the domain before we 
    start the backtracking.
    """
    pairs = []
    for module in modules:
        for tutor in tutors:
            if time_table.canTeach(tutor, module, False):
                pairs.append(ModuleTutorPair(module, tutor, False))
            if time_table.canTeach(tutor, module, True):
                pairs.append(ModuleTutorPair(module, tutor, True))

    return sort_domain(pairs)

def generate_time_table_slot():
    global TIME_TABLE_SLOTS
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    counter = 1
    for day in days:
        for i in range(1, 11):
            TIME_TABLE_SLOTS[str(counter)] = [day, i]
            counter += 1

def can_solve_slot(time_table, pairs, slot):
    """
    This is going to be my first attempt traversing the timetable vertically 
    starting on Monday, time slot 1. When time slot 5 is populated, move to the 
    next day, time slot 1.
    """
    print('\nslot: ' + str(slot))
    # check if all slots have been filled.
    if slot == 51:
        return True

    day, time_slot = minimum_remaining_value(slot)

    for pair in pairs:
        if can_assign_pair(time_table, day, pair):
            time_table.addSession(day, time_slot, pair.tutor, pair.module, pair.session_type)
            print(time_slot)
            print('Assigned ' + pair.module.name + ' : ' + pair.tutor.name + ' : ' + pair.session_type)
            
            pruned_pairs = forward_checking(time_table, pair, pairs)

            a = []
            for mod in pruned_pairs:
                a.append(mod.module)
            print('modules left: ' +  str(len(set(a))))
            print('pairs left: ' + str(len(pruned_pairs)))


            if can_solve_slot(time_table, pruned_pairs, slot + 1):
                return True
            else:
                print('\nslot: ' + str(slot))

            print('Deleteing ' + pair.module.name)
            del time_table.schedule[day][time_slot]
    # no solution.
    print('No solution')
    return False

def can_assign_pair(time_table, day, pair):
    """
    Check that the module-tutor pair given does not violate any of the 
    constraints. The constraints are:
    1) A tutor cannot teach more than 2 credits a day,
    2) A tutor can teach a maximum of 4 credits,
    """
    # check that the tutor is not already teaching more than 2 credits that day.
    day_credits = 0
    for slot in time_table.schedule[day].values():
        if slot[0] == pair.tutor:
            credit = 1 if slot[2] == 'lab' else 2
            day_credits += credit

    if day_credits + pair.credit > 2:
        print('over daily credits')
        return False

    # check the tutor is not teaching more than 4 credits.
    total_credits = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair.tutor:
                credit = 1 if slot[2] == 'lab' else 2
                total_credits += credit

    if total_credits + pair.credit > 4:
        print('over weekyly credits')
        return False

    # passed all tests, pair is valid.
    print('pair valid')
    return True

def minimum_remaining_value(slot):
    """
    This method chooses the variable with the fewest remaining values. It is 
    effectively starting a Monday slot 1 then slot 2 ... slot 10 then going to 
    Tuesday slot 1 and repeating until Friday slot 10. It does this as the way to
    reduce the domain is by selecting a slot in the same day as the one just 
    selected as we can remove tutors and modules.
    """
    time_table_slots = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    counter = 1
    for day in days:
        for i in range(1, 11):
            time_table_slots[str(counter)] = [day, i]
            counter += 1
    
    slot_meta = time_table_slots[str(slot)] 
    return slot_meta[0], slot_meta[1]

def sort_domain(pairs):
    """
    This method is going to sort and return the elements of the domain.
    """
   # for each module, count the number of elements with that module.
    module_count = {}
    tutor_count = {}
    for pair in pairs:
        m_count = module_count.get(pair.module_name)
        if m_count is None:
            module_count[pair.module_name] = 1
        else:
            module_count[pair.module_name] += 1
        t_count = tutor_count.get(pair.tutor.name)
        if t_count is None:
            tutor_count[pair.tutor.name] = 3 - pair.credit
        else:
            tutor_count[pair.tutor.name] += 3 - pair.credit
    # sort by least common module count
    return sorted(pairs, key=lambda x: (module_count[x.module_name], tutor_count[x.tutor.name], not x.is_lab))

def constraining_values(pair, pairs):
    """
    This method returns the number of values left in the domain if the given
    pair was choosen.
    """
    remaining_domain_size = len(forward_checking(pair, pairs))
    return remaining_domain_size

def forward_checking(time_table, pair, pairs):
    """
    Apply forward checking to the given pairs to reduce the domain. by removing 
    all domain elements with the same module that was just selected. Will also 
    check that the tutor of the pair given has not reached their weekly credit
    limit.
    """
    total_credits = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair.tutor:
                credit = 1 if slot[2] == 'lab' else 2
                total_credits += credit

    if total_credits >= 4:
        print('removing tutor')
        pruned_pairs = [
            x for x in pairs if x.tutor != pair.tutor and not (
                x.module == pair.module and x.is_lab == pair.is_lab
            )
        ]
    else:
        pruned_pairs = [
            x for x in pairs if not (x.module == pair.module and x.is_lab == pair.is_lab)
        ]
        
    return pruned_pairs

def simulated_annealing(time_table, tutors, modules, iterations=10000):
    """
    This method will do simulated_annealing to try find a better, or hopefully
    optimal solution. It will randomly swap two slots.
    """
    def sigmoid(gamma):
        if gamma < 0:
            return 1 - 1 / (1 + math.exp(gamma))
        return 1 / (1 + math.exp(-gamma))

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    initial = timetable.Timetable(3)
    for day_slots in time_table.schedule.items():
        for slot, value in day_slots[1].items():
            initial.schedule[day_slots[0]][slot] = time_table.schedule[day_slots[0]][slot]

    best_time_table = timetable.Timetable(3)
    lowest_cost = time_table.cost

    for k in range(1, iterations):
        T = iterations / k + 1

        if T == 0:
            break

        # randomly swap two slots
        day1 = days[random.randint(0, 4)]
        day2 = days[random.randint(0, 4)]
        slot1 = random.randint(1, 10)
        slot2 = random.randint(1, 10)
        module1 = time_table.getSession(day1, slot1)
        module2 = time_table.getSession(day2, slot2)
        time_table.addSession(day1, slot1, module2[0], module2[1], module2[2])
        time_table.addSession(day2, slot2, module1[0], module1[1], module1[2])

        if time_table.scheduleChecker(tutors, modules):
            if time_table.cost < lowest_cost:
                lowest_cost = time_table.cost
                for day_slots in time_table.schedule.items():
                    for slot, value in day_slots[1].items():
                        best_time_table.schedule[day_slots[0]][slot] = time_table.schedule[day_slots[0]][slot]
            elif sigmoid((time_table.cost - lowest_cost) / T) < random.random():
                time_table.addSession(day1, slot1, module1[0], module1[1], module1[2])
                time_table.addSession(day2, slot2, module2[0], module2[1], module2[2])

    if best_time_table.scheduleChecker(tutors, modules):
        return best_time_table
    initial.scheduleChecker(tutors, modules)
    return initial

class ModuleTutorPair:

    def __init__(self, module, tutor, is_lab):
        self.module = module
        self.tutor = tutor
        self.is_lab = is_lab

    def __str__(self):
        return '(' + self.module.name + ', ' + self.tutor.name + ', ' + self.session_type + ')' 

    def __repr__(self):
        return str(self)

    @property
    def session_type(self):
        if self.is_lab:
            return 'lab'
        return 'module'
    
    @property
    def credit(self):
        if self.is_lab:
            return 1
        return 2

    @property
    def module_name(self):
        module_name = self.module.name
        module_name = module_name + '_l' if self.is_lab else module_name
        return module_name

"""
Utitlity methods
"""
def print_timetable(time_table, tutors, modules):
    """
    Print the time table as well as showing if the solution found is valid.
    """
    print('----------------------------')
    for day, slots in time_table.schedule.items():
        for slot_name, slot_val in slots.items():
            print(str(slot_name) + ': ' + slot_val[1].name + ' ' + slot_val[2] + ': ' + slot_val[0].name)
    print('----------------------------')
    print('Table valid: ' + str(time_table.scheduleChecker(tutors, modules)))
    print('Table cost: ' + str(time_table.cost))

solve_timetable()