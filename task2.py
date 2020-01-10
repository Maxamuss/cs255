"""
Methods used in task 2. This is used for testing of methods and ideas. My final 
working solution will be added to the scheduler.py file.
"""
import module
import tutor
import ReaderWriter
import timetable
import random
import math

"""
Core methods for the CSP backtracking.
"""
slot_def = {
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

def solve_timetable():
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements("ExampleProblems/Problem2.txt")
    time_table = timetable.Timetable(1)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    # attempt to solve the task
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print_timetable(time_table, tutors, modules)

def can_solve_slot(time_table, pairs, slot):
    """
    This is going to be my first attempt traversing the timetable vertically 
    starting on Monday, time slot 1. When time slot 5 is populated, move to the 
    next day, time slot 1.
    """
    # check if all slots have been filled.
    if slot == 26:
        return True

    # get this version of the backtrackings slot info.
    slot_meta = slot_def[str(slot)]
    day = slot_meta[0]
    time_slot = slot_meta[1]

    random.shuffle(pairs)
    # sorted(pairs, key=lambda x: calc_lcv(x))

    for pair in pairs:
        if can_assign_pair(time_table, day, pair):
            time_table.addSession(day, time_slot, pair[1], pair[0], 'module')
            # Remove module from the pairs list so it can't get chosen again.
            # pruned_pairs = forward_checking(pair, pairs, slot)
            pairs_removed = [x for x in pairs if x[0] != pair[0]]
            print(slot[1])
            next_slot = slot + 1
            # move onto the next slot, calling recursively.
            if can_solve_slot(time_table, pruned_pairs, next_slot):
                return True
            # may not be needed for this traversal method.
            del time_table.schedule[day][time_slot]

    # no solution.
    return False

def can_assign_pair(time_table, day, pair):
    """
    Check that the module-tutor pair given does not violate any of the 
    constraints.
    """       
    # check that the tutor is not already teaching a module on the given day.
    for slot in time_table.schedule[day].values():
        if slot[0] == pair[1]:
            return False

    # check the tutor is not teaching more than 2 modules.
    tutor_module_count = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair[1]:
                tutor_module_count += 1

    if tutor_module_count >= 2:
        return False

    # passed all tests, pair is valid.
    return True

def forward_checking(pair, pairs, slot):
    """
    Apply forward checking to the given pairs to reduce the domain. This is done 
    in two ways: the first is removing all domain elements with the module that
    was just selected. The second is to remove elements from the domain with the 
    tutor just selected UNLESS it is slot 5. This is because our MRV approach 
    means that we first start will slot 1 of a day and go down the slots to slot 
    5. A tutor cannot teach twice a day so if they have just been assigned, so 
    they are removed from the domain but only if it is not slot 5
    """
    # removing module from domain.
    pruned_pairs = [x for x in pairs if x[0] != pair[0]]
    # removing tutor from domain if slot 5 of day.
    if slot % 5 != 0:
        pruned_pairs = [x for x in pairs if x[1] != pair[1]]

    return pruned_pairs

def calc_lcv(pair):
    """
    Return the number of valid
    """
    return 1
    valid_slots = [x for x in range(1, 26)]
    print(valid_slots)
    # for day, slots in time_table.schedule.items():
    #     print(day)
    #     for slot_name, slot_val in slots.items():
    #         print(str(slot_name) + ': ' + slot_val[1].name)

"""
Utitlity methods
"""
def generate_module_tutor_pairs(time_table, modules, tutors):
    """
    Generate a valid list of module-tutor pairs. For a pair to be valid, the 
    topics of a module must all be in a tutors expertise. 
    """
    pairs = []
    for module in modules:
        for tutor in tutors:
            if set(module.topics).issubset(set(tutor.expertise)):
                pairs.append([module, tutor])

    return pairs

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