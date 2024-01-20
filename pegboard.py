import copy
import random
import time
import sys
import heapq
class State:
    def __init__(self, value, path = []):
        self.value = value
        self.path = path

    def __str__(self):
        binary = format(self.value, '016b')
        chars = ['X' if c == '1' else 'O' for c in binary]
        return "\n".join([" ".join(chars[i*4:i*4+4]) for i in range(4)])

    def get_parity(self):
        return bin(self.value).count("1") % 2


class Action:
    def __init__(self, jumper, goner, newpos):
        self.jumper = jumper
        self.goner = goner
        self.newpos = newpos

    def __str__(self):
        return f"The peg in slot {self.jumper} jumps over the peg in slot {self.goner} and lands in slot {self.newpos}"

    def applyState(self, state):
        new_state_val = state.value
        new_state_val |= (1 << self.newpos)
        new_state_val &= ~(1 << self.jumper)
        new_state_val &= ~(1 << self.goner)
        return State(new_state_val)

    def precondition(self, state):
        jumper_has_peg = (state.value & (1 << self.jumper)) != 0
        goner_has_peg = (state.value & (1 << self.goner)) != 0
        newpos_has_no_peg = (state.value & (1 << self.newpos)) == 0
        return jumper_has_peg and goner_has_peg and newpos_has_no_peg

def applicableActions(state):
    actions = []

    def get_position(pos, dx, dy, step):
        x, y = pos // 4, pos % 4  # convert to 2D
        new_x, new_y = x + dx*step, y + dy*step
        if 0 <= new_x < 4 and 0 <= new_y < 4:
            return new_x * 4 + new_y
        return None

    for pos in range(16):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            jumper = pos
            goner = get_position(pos, dx, dy, 1)
            newpos = get_position(pos, dx, dy, 2)
            if None not in [jumper, goner, newpos]:
                action = Action(jumper, goner, newpos)
                if action.precondition(state):
                    actions.append(action)


    return actions


def goal(state):
    return state.value == int('0000001000000000', 2)

def flailWildly(state):
    state = State(state)
    current_state = copy.deepcopy(state)
    while not goal(current_state):
        actions = applicableActions(current_state)
        if not actions:
            print("No further actions!")
            break
        action = random.choice(actions)
        print(current_state)
        print(action)
        current_state = action.applyState(current_state)
    print(current_state)


# Testing code
# initialState = State(45759)
# flailWildly(45759)




# 1.) DFS IMPLEMENTATION
class DFS:
    def __init__(self, initial_state):
        self.stack = [(initial_state, None)]
        self.visited = set()
        self.path = []
        self.expanded_nodes = 0

    def search(self):
        while self.stack:
            current_state, chosen_action = self.stack.pop()

            # 2.) OPTIMIZING DFS BY RECOGNIZING STATES FROM WHICH THE GOAL CANNOT BE REACHED

            # TO SEE THE PROOF THAT THE OPTIMIZATION WORKS, COMMENT THESE TWO LINES AND YOU WILL NOTICE AN INCREASE IN THE NUMBER OF EXPANDED NODES AND SEARCH TIME WILL INCREASE TOO
            # This is based on the observation that if the parities are different we can never reach the goal state from the current state, so there's no point in exploring this branch further.

            if current_state.get_parity() != (len(self.path) + 1) % 2: # DFS optimization
                continue # DFS optimization

            self.expanded_nodes +=1

            if goal(current_state):
                self.path.append((current_state, chosen_action))
                return True, self.path

            self.visited.add(current_state.value)

            actions = applicableActions(current_state)

            for action in actions:
                new_state = action.applyState(current_state)

                if new_state.value not in self.visited:
                    self.stack.append((new_state, action))

            self.path.append((current_state, chosen_action))

        return False, []


# Function to test the DFS
def solve_pegboard_using_DFS(initial_state):
    start_time = time.time()
    dfs = DFS(initial_state)
    solution_found, path = dfs.search()
    end_time = time.time()
    time_elapsed = end_time-start_time
    if solution_found:
        print("Solution found using DFS!!!!!!!!!!!!!!!!!!!!")

        for state, action in path:
            if action:  # If action exists (i.e., not for the initial state)
                print("After taking action:", action, "and the resulting state is: ")
            print(state)
            print("------")
        print("Number of expanded nodes: ", dfs.expanded_nodes)
        print("Search time: ", time_elapsed, "seconds")

    else:
        print("No solution found.")

#A STAR IMPLEMENTATION USING THE TWO GIVEN HEURISTICS

# 3.a)
def heuristic1(state):
    return len(applicableActions(state))

def manhattan_distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)

# 3.b)
def heuristic2(state):
    target = (2, 1)
    total_distance = 0
    for i in range(16):
        if (state.value >> i) & 1:
            total_distance += manhattan_distance((i // 4, i % 4), target)
    return total_distance



# 3) A Star Search
class AStarSearch:

    def __init__(self, initial_state, heuristic, path = []):
        self.counter = 0  # To ensure unique comparison for states with same priority
        self.initial_state = initial_state
        self.heuristic = heuristic
        self.visited = set()
        self.priority_queue = [self.calculate_priority(self.initial_state)]
        self.path = path

    def calculate_priority(self, state):
        h_value = self.heuristic(state)
        self.counter += 1
        return (h_value + len(state.path), self.counter, state)

    def search(self):
        expanded_nodes = 0
        start_time = time.time()

        iterations = 0
        while self.priority_queue:
            iterations += 1
            print(f"Iteration {iterations}, Priority Queue Size: {len(self.priority_queue)}")

            total_priority, counter, current_state = heapq.heappop(self.priority_queue)

            print("Current State:\n")
            print(current_state)

            if goal(current_state):
                print("Found Goal!")
                print(f"Number of expanded nodes: {expanded_nodes}")
                end_time = time.time()
                print(f"Running time: {end_time - start_time:.4f} seconds")
                return current_state.path

            if current_state in self.visited:
                continue

            self.visited.add(current_state)
            print("Available Actions: ")
            # Explore neighboring states
            for action in applicableActions(current_state):
                if action.precondition(current_state):

                    successor = action.applyState(current_state)
                    if successor not in self.visited:
                        print(f" {action}")
                        # successor.path = current_state.path + [(current_state, action)]
                        heapq.heappush(self.priority_queue, self.calculate_priority(successor))
            expanded_nodes += 1



        return None

initialState = State(int('1101011011011110',2))
# initialState = State(45759)


def action1():
    print("Solution using DFS: ")
    solve_pegboard_using_DFS(initialState)

def action2():
    print("A Star with heuristic 1: Number of available moves: ")
    searcher = AStarSearch(initialState, heuristic1)
    result = searcher.search()
    print("As you can see, the solution is not optimal as the heuristic is not admissible")


def action3():
    print("A Star with heuristic 2: Manhattan Distance: ")
    searcher = AStarSearch(initialState, heuristic2)
    result = searcher.search()
    print("As you can see, the solution optimal as the heuristic is admissible")

actions = {
    '1': action1,
    '2': action2,
    '3': action3
}

while True:
    print("\n")
    print("-----------------------------------------------------------------------------------")
    print("Starting state of the problem: \n")
    print(initialState)
    print("\n")
    print("Choose an option:")
    print("Press 1 for solution using DFS")
    print("Press 2 for solution using A Star with heuristic 1: Number of available moves ")
    print("Press 3 for solution using A Star with heuristic 2: Manhattan Distance ")
    print("0. Exit")
    print("-----------------------------------------------------------------------------------")
    #print("\n")

    user_input = input("Enter your choice: ")

    if user_input == '0':
        print("Exiting program...")
        break
    else:
        action = actions.get(user_input)
        if action:
            action()
        else:
            print("Invalid option!")
