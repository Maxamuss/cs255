"""
Methods used in task 3. This is used for testing of methods and ideas. My final 
working solution will be added to the scheduler.py file.
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
    time_table = timetable.Timetable(2)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print(file_name + ': ' + str(time_table.scheduleChecker(tutors, modules)))
    print('Table cost: ' + str(time_table.cost))

"""
Core methods for the CSP backtracking.
"""
bound = 12000
min_cost_time_table = None

def solve_timetable():
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements("ExampleProblems/Problem7.txt")
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
                pairs.append(ModuleTutorPair(module, tutor, True))
    # sort the pairs by their number of least constraining values. If there is a
    # tie-break, lab sessions come before modules as they have less constraints.
    return sort_domain(pairs)

def can_solve_slot(time_table, pairs, slot, cost=0):
    """
    This is going to be my first attempt traversing the timetable vertically 
    starting on Monday, time slot 1. When time slot 5 is populated, move to the 
    next day, time slot 1.
    """
    global bound, min_cost_time_table
    # check if all slots have been filled and the cost is smallest possible.
    if slot == 25:
        if cost == 10050:
            return True
        bound = cost
        min_cost_time_table = time_table
        return False

    day, time_slot = minimum_remaining_value(slot)

    # pairs = sorted(pairs, key=lambda x: calc_path_cost(time_table, day, cost, x))
    # print([calc_path_cost(time_table, day, cost, x) for x in pairs][:10])
    pairs = sort_pairs(time_table, slot, day, cost, pairs)
    print([calc_path_cost(time_table, day, cost, x) for x in pairs][:10])

    for pair in pairs:
        if can_assign_pair(time_table, day, pair):
            path_cost = calc_path_cost(time_table, day, cost, pair)
            
            time_table.addSession(day, time_slot, pair.tutor, pair.module, pair.session_type)
            
            heuristic_cost = calc_heuristic_cost(time_table, slot, day, time_slot, pair)
            if path_cost + heuristic_cost >= bound:
                break
            
            print(str(slot) + ' Assigned ' + pair.module.name + ' : ' + pair.tutor.name + ' : ' + pair.session_type)
            print('cost: ' + str(path_cost + heuristic_cost) +' | ' + str(path_cost) +' | ' + str(bound))
            print('pairs: ' + str(len(pairs)))

            pruned_pairs = forward_checking(time_table, pair, pairs)

            if can_solve_slot(time_table, pruned_pairs, slot + 1, path_cost):
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
            credit = 1 if slot[2] == 'lab' else 2
            day_credits += credit

    if day_credits + pair.credit > 2:
        return False

    # check the tutor is not teaching more than 4 credits.
    total_credits = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair.tutor:
                credit = 1 if slot[2] == 'lab' else 2
                total_credits += credit

    if total_credits + pair.credit > 4:
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
    time_table_slots = {
        '1': ['Monday', 1],
        '2': ['Monday', 2],
        '3': ['Monday', 3],
        '4': ['Monday', 4],
        '5': ['Monday', 5],
        '6': ['Monday', 6],
        '7': ['Tuesday', 1],
        '8': ['Tuesday', 2],
        '9': ['Tuesday', 3],
        '10': ['Tuesday', 4],
        '11': ['Wednesday', 1],
        '12': ['Wednesday', 2],
        '13': ['Wednesday', 3],
        '14': ['Wednesday', 4],
        '15': ['Wednesday', 5],
        '16': ['Wednesday', 6],
        '17': ['Wednesday', 7],        
        '18': ['Wednesday', 8],
        '19': ['Thursday', 1],
        '20': ['Thursday', 2],
        '21': ['Friday', 1],
        '22': ['Friday', 2],
        '23': ['Friday', 3],
        '24': ['Friday', 4],
        '25': ['Monday', 7],
        '26': ['Monday', 8],
        '27': ['Monday', 9],
        '28': ['Monday', 10],
        '29': ['Tuesday', 5],
        '30': ['Tuesday', 6],
        '31': ['Tuesday', 7],
        '32': ['Tuesday', 8],
        '33': ['Tuesday', 9],
        '34': ['Tuesday', 10],
        '35': ['Wednesday', 9],
        '36': ['Wednesday', 10],      
        '37': ['Thursday', 5],
        '38': ['Thursday', 6],
        '39': ['Thursday', 7],
        '40': ['Thursday', 8],
        '41': ['Thursday', 9],
        '42': ['Thursday', 10],
        '43': ['Friday', 5],  
        '44': ['Friday', 6],
        '45': ['Friday', 7],
        '46': ['Friday', 8],
        '47': ['Friday', 9],
        '48': ['Friday', 10],
        '49': ['Thursday', 4],
        '50': ['Thursday', 3],
    }
    slot_meta = time_table_slots[str(slot)] 
    return slot_meta[0], slot_meta[1]

def calc_heuristic_cost(time_table, slot, day, time_slot, pair):
    """
    Calculate the lower bound estimate of the cost to the goal. This is going to 
    try to see what would be needed to create the optimal time table and work 
    out that cost.
    """
    return 50 * (50 - slot)

def calc_path_cost(time_table, day, cost, pair):
    """
    This method will calculate the cost of adding the given pair.
    """
    PREV_DAY = {
        'Tuesday': 'Monday',
        'Wednesday': 'Tuesday',
        'Thursday': 'Wednesday',
        'Friday': 'Thursday'
    }

    if pair.is_lab:
        # look in the and calc cost of adding this lab
        labs = 0
        lab_today = False
        for day_slots in time_table.schedule.items():
            for slot in day_slots[1].values():
                if slot[2] == 'lab' and slot[0] == pair.tutor:
                    labs += 1
                    if day_slots[0] == day:
                        lab_today = True

        discount = 0.5 * (250 - (50 * (labs - 1))) if lab_today else 0
        today_discount = 0.5 if lab_today else 1
        lab_cost = (250 - (50 * labs)) * today_discount

        return cost + lab_cost - discount
    else:
        first_day = None
        # check to see if the tutor is already teaching a module this week and if 
        # so, what day it is on
        for day_slots in time_table.schedule.items():
            for slot in day_slots[1].values():
                if slot[0] == pair.tutor and slot[2] == 'module':
                    first_day = day_slots[0]
        
        if first_day is not None and day != 'Monday':
            if first_day == PREV_DAY[day]:
                return cost + 100
            return cost + 300
        return cost + 500

def sort_pairs(time_table, slot, day, cost, pairs):
    """
    My first attempt is to first allocate all of the labs, then the modules.
    """
    def get_tutor_count():
        tutor_count = {}
        tutor_lab_count = {}
        tutor_module_count = {}
        module_count = {}

        tutor_lab = {}
        tutor_credits = {}
        
        for pair in pairs:
            # counting
            t_count = tutor_count.get(pair.tutor.name)
            if t_count is None:
                tutor_count[pair.tutor.name] = 1
            else:
                tutor_count[pair.tutor.name] += 1

            if pair.is_lab:
                l_count = tutor_lab_count.get(pair.tutor.name)
                if l_count is None:
                    tutor_lab_count[pair.tutor.name] = 1
                else:
                    tutor_lab_count[pair.tutor.name] += 1
            else:
                m_count = tutor_module_count.get(pair.tutor.name)
                if m_count is None:
                    tutor_module_count[pair.tutor.name] = 1
                else:
                    tutor_module_count[pair.tutor.name] += 1

            mod_count = module_count.get(pair.tutor.name)
            if mod_count is None:
                module_count[pair.tutor.name] = 1
            else:
                module_count[pair.tutor.name] += 1
            # credits
            total_credits = 0
            for day_slots in time_table.schedule.items():
                for slot in day_slots[1].values():
                    if slot[0] == pair.tutor:
                        if slot[2] == 'lab':
                            tutor_lab[pair.tutor.name] = True

                        credit = 1 if slot[2] == 'lab' else 2
                        total_credits += credit
            
            c_count = tutor_credits.get(pair.tutor.name)
            if c_count is None:
                tutor_credits[pair.tutor.name] = 1
            else:
                tutor_credits[pair.tutor.name] += 1

        return tutor_count, tutor_lab_count, tutor_module_count, module_count, tutor_lab, tutor_credits

    if slot < 25:
        # This will pick a random lab and then its tutor will get allocated 3 more
        # modules, 2 on 2 different days. This will happen 6 times. The reason 
        # why it didn't work before is because it didn't leave enough module tutors
        # left afterwards. Hence choosing the labs needs to have a better system. 
        # TODO: select by the lab tutor with the least modules
        tutor_count, tutor_lab_count, tutor_module_count, module_count, tutor_lab, tutor_credits = get_tutor_count()

        print(tutor_lab_count)

        pairs = sorted(pairs, key=lambda x: (
            calc_path_cost(time_table, day, cost, x),
            tutor_lab_count.get(x.tutor.name, 0) + tutor_credits.get(x.tutor.name, 0) <= 3, # make sure there is 4 labs
            tutor_lab_count.get(x.tutor.name, 0)
        ))
        return pairs
    # elif slot == 25:
    #     # This is for the "stray" lab that does not get a cost saving. This needs
    #     # to be choosen with the modules in mind.
    #     # TODO:
    #     pairs = sorted(pairs, key=lambda x: calc_path_cost(time_table, day, cost, x))
    #     print(pairs)
    #     return pairs
    else:
        # This is where the modules will be sorted. The idea is to prioritise
        # a tutor that can teach 2 modules on consecutive days.
        tutor_count, tutor_lab_count, tutor_module_count, module_count, tutor_lab, tutor_credits = get_tutor_count()
        print(tutor_count)
        print(tutor_lab)
        print(tutor_credits)

        pairs = sorted(pairs, key=lambda x: (
            tutor_lab.get(x.tutor.name, False), # make sure the tutor isnt teaching a lab
            calc_path_cost(time_table, day, cost, x),
            -tutor_count[x.tutor.name],

            x.tutor.name, # group by name
        ))#, tutor_count[x.tutor.name], x.tutor.name
        # print([calc_path_cost(time_table, day, cost, x) for x in pairs])
        print(pairs)
        return pairs

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

def forward_checking(time_table, pair, pairs):
    """
    Apply forward checking to the given pairs to reduce the domain. by removing 
    all domain elements with the same module that was just selected. 
    """
    total_credits = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair.tutor:
                credit = 1 if slot[2] == 'lab' else 2
                total_credits += credit

    if total_credits >= 4:
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
        print(day)
        for slot_name, slot_val in slots.items():
            print(str(slot_name) + ': ' + slot_val[1].name + ' ' + slot_val[2] + ': ' + slot_val[0].name)
    print('----------------------------')
    print('Table valid status: ' + str(time_table.scheduleChecker(tutors, modules)))
    print('Table cost: ' + str(time_table.cost))

solve_timetable()