"""
Methods used in task 1. This is used for testing of methods and ideas. My final 
working solution will be added to the scheduler.py file. This is a version of 
task1.py that has logging (via print statements) to the console when the program
is running.
"""
import module
import tutor
import ReaderWriter
import timetable
import random
import math

from time import time
"""
Methods for testing.
"""
def solve_timetable_test(file_name):
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements(file_name)
    time_table = timetable.Timetable(1)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print(file_name + ': ' + str(time_table.task1Checker(tutors, modules)))


"""
Core methods for the CSP backtracking.
"""
def solve_timetable():
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements("ExampleProblems/Problem1.txt")
    time_table = timetable.Timetable(1)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    # attempt to solve the task
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print_timetable(time_table, tutors, modules)

def generate_module_tutor_pairs(time_table, modules, tutors):
    """
    Generate a valid list of module-tutor pairs. For a pair to be valid, the 
    topics of a module must all be in a tutors expertise. 
    """
    pairs = []
    for module in modules:
        for tutor in tutors:
            if time_table.canTeach(tutor, module, False):
                pairs.append([module, tutor])

    return sort_domain(pairs)

def can_solve_slot(time_table, pairs, slot):
    """
    This is going to be my first attempt traversing the timetable vertically 
    starting on Monday, time slot 1. When time slot 5 is populated, move to the 
    next day, time slot 1.
    """
    print('\nslot: ' + str(slot))
    # check if all slots have been filled.
    if slot == 26:
        return True

    day, time_slot = minimum_remaining_value(slot)

    for pair in pairs:
        if can_assign_pair(time_table, day, pair):
            time_table.addSession(day, time_slot, pair[1], pair[0], 'module')
            print('Assigned ' + pair[0].name + ' : ' + pair[1].name)
            print(constraining_values(pair, pairs))
            
            pairs_pruned = forward_checking(pair, pairs)

            a = []
            for mod in pairs_pruned:
                a.append(mod[0])
            print('modules left: ' +  str(len(set(a))))
            print('pairs left: ' + str(len(pairs_pruned)))

            # move onto the next slot, calling recursively.
            if can_solve_slot(time_table, pairs_pruned, slot + 1):
                return True
            else:
                print('\nslot: ' + str(slot))
            print('Deleteing ' + pair[0].name)
            del time_table.schedule[day][time_slot]
        else:
            print('Failed to assign: ' + pair[0].name + ' : ' + pair[1].name)

    # No solution, return False
    print('FAILED')
    return False

def can_assign_pair(time_table, day, pair):
    """
    Check that the module-tutor pair given does not violate any of the 
    constraints.
    """
    # check the tutor is not teaching more than 2 modules.
    tutor_module_count = 0
    for day_slot in time_table.schedule.items():
        for slot in day_slot[1].values():
            # check that the tutor is not already teaching a module on the given day.
            if day_slot[0] == day and slot[0] == pair[1]:
                return False
            if slot[0] == pair[1]:
                tutor_module_count += 1

    if tutor_module_count >= 2:
        return False

    return True

def minimum_remaining_value(slot):
    """
    This method chooses the variable with the fewest remaining values. It is 
    effectively starting a Monday slot 1 then slot 2 ... slot 5 then going to 
    Tuesday slot 1 and repeating until Friday slot 5. It does this as the way to
    reduce the domain is by selecting a slot in the same day as the one just 
    selected as we can remove tutors and modules.
    """
    time_table_slots = {
        '1': ['Monday', 1],
        '2': ['Monday', 2],
        '3': ['Monday', 3],
        '4': ['Monday', 4],
        '5': ['Monday', 5],
        '6': ['Tuesday', 1],
        '7': ['Tuesday', 2],
        '8': ['Tuesday', 3],
        '9': ['Tuesday', 4],
        '10': ['Tuesday', 5],
        '11': ['Wednesday', 1],
        '12': ['Wednesday', 2],
        '13': ['Wednesday', 3],
        '14': ['Wednesday', 4],
        '15': ['Wednesday', 5],
        '16': ['Thursday', 1],
        '17': ['Thursday', 2],
        '18': ['Thursday', 3],
        '19': ['Thursday', 4],
        '20': ['Thursday', 5],
        '21': ['Friday', 1],
        '22': ['Friday', 2],
        '23': ['Friday', 3],
        '24': ['Friday', 4],
        '25': ['Friday', 5]
    }
    slot_meta = time_table_slots[str(slot)] 
    return slot_meta[0], slot_meta[1]

def sort_domain(pairs):
    """
    This method is going to sort and return the elements of the domain.
    """
    # for each module, count the number of elements with that module.
    module_count = {}
    for pair in pairs:
        module_name = pair[0].name
        count = module_count.get(module_name)
        if count is None:
            module_count[module_name] = 1
        else:
            module_count[module_name] += 1

    # sort by least common module count
    return sorted(pairs, key=lambda x: module_count[x[0].name])

def constraining_values(pair, pairs):
    """
    This method returns the number of values left in the domain if the given
    pair was choosen.
    """
    remaining_domain_size = len(forward_checking(pair, pairs))
    return remaining_domain_size

def forward_checking(pair, pairs):
    """
    Apply forward checking to the given pairs to reduce the domain. This is done 
    in two ways: the first is removing all domain elements with the module that
    was just selected. The second is to remove elements from the domain with the 
    tutor just selected UNLESS it is slot 5. This is because our MRV approach 
    means that we first start will slot 1 of a day and go down the slots to slot 
    5. A tutor cannot teach twice a day so if they have just been assigned, so 
    they are removed from the domain but only if it is not slot 5. 
    Finally, we check that the number of modules in the domain is equal to the 
    number of slots left since if it is not, then we cannot fill the time table
    with the given domain. Return None if this is the case.
    """
    pruned_pairs = [x for x in pairs if x[0] != pair[0]]
    return pruned_pairs

"""
Utitlity methods
"""
def print_timetable(time_table, tutors, modules):
    """
    Print the time table as well as showing if the solution found is valid.
    """
    for day, slots in time_table.schedule.items():
        for slot_name, slot_val in slots.items():
            print(str(slot_name) + ': ' + slot_val[1].name)
    print('----------------------------')
    print('Table valid status: ' + str(time_table.task1Checker(tutors, modules)))


solve_timetable()