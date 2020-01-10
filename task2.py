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
Methods for testing.
"""
def solve_timetable_test(file_name):
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements(file_name)
    time_table = timetable.Timetable(2)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print(file_name + ': ' + str(time_table.task1Checker(tutors, modules)))

"""
Core methods for the CSP backtracking.
"""
def solve_timetable():
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements("ExampleProblems/Problem2.txt")
    time_table = timetable.Timetable(2)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    # attempt to solve the task
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print_timetable(time_table, tutors, modules)

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
                pairs.append(ModuleTutorPair(module, tutor, True) )

    return pairs

def can_solve_slot(time_table, pairs, slot):
    """
    This is going to be my first attempt traversing the timetable vertically 
    starting on Monday, time slot 1. When time slot 5 is populated, move to the 
    next day, time slot 1.
    """
    # check if all slots have been filled.
    if slot == 2:
        return True

    day, time_slot = minimum_remaining_value(slot)
    # sort the pairs by their number of least constraining values. If there is a
    # tie-break, lab sessions come before modules as they have less constraint.
    pairs = sorted(pairs, key=lambda x: (constraining_values(x, pairs), x.is_lab), reverse=True)

    for pair in pairs:
        if can_assign_pair(time_table, day, pair):
            time_table.addSession(day, time_slot, pair.tutor, pair.module, pair.session_type())
            pruned_pairs = forward_checking(pair, pairs)

            if can_solve_slot(time_table, pruned_pairs, slot + 1):
                return True

            del time_table.schedule[day][time_slot]
    # no solution.
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
            credit = 1 if slot.is_lab else 2
            day_credits += credit
    
    if day_credits >= 2:
        return False

    # check the tutor is not teaching more than 4 credits.
    total_credits = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair.tutor:
                credit = 1 if slot.is_lab else 2
                total_credits += credit

    if total_credits >= 4:
        return False

    # passed all tests, pair is valid.
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
        for slot in range(1, 11):
            time_table_slots[str(counter)] = [day, slot]
            counter += 1
    
    slot_meta = time_table_slots[str(slot)] 
    return slot_meta[0], slot_meta[1]

def constraining_values(pair, pairs):
    """
    This method returns the number of values left in the domain if the given
    pair was choosen.
    """
    remaining_domain_size = len(forward_checking(pair, pairs))
    return remaining_domain_size

def forward_checking(pair, pairs):
    """
    Apply forward checking to the given pairs to reduce the domain. by removing 
    all domain elements with the same module that was just selected. 
    """
    if pair.is_lab:
        pruned_pairs = [x for x in pairs if not (x.is_lab and x.module == pair[0])]
    else:
        pruned_pairs = [x for x in pairs if not (not x.is_lab and x.module == pair[0])]
        
    return pruned_pairs

class ModuleTutorPair:

    def __init__(self, module, tutor, is_lab):
        self.module = module
        self.tutor = tutor,
        self.is_lab = is_lab

    def session_type(self):
        if self.is_lab:
            return 'lab'
        return 'module'
    
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