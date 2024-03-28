import sys
import time
import functools
import heapq
from collections import deque

#Memoize function in utils.py from the AIMA Github
def memoize(fn, slot=None, maxsize=32):
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)

    return memoized_fn

#PriorityQueue class in utils.py from the AIMA Github
class PriorityQueue:
    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':
            self.f = lambda x: -f(x)
        else:
            raise ValueError("Order must be either 'min' or 'max'.")

    #Insert item into the priority queue
    def append(self, item):
        heapq.heappush(self.heap, (self.f(item), item))

    #Insert each item in items into the priority queue
    def extend(self, items):
        for item in items:
            self.append(item)

    #Return the item with the min or max value
    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    #Return the size of the priority queue
    def __len__(self):
        return len(self.heap)

    #Check if the priority queue contains the given key
    def __contains__(self, key):
        return any([item == key for _, item in self.heap])

    #Return the first value associated with the given key
    def __getitem__(self, key):
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")

    #Delete the first occurence of the given key
    def __delitem__(self, key):
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)

#Problem class based off the code given in search.py from the AIMA Github
class Problem:
    #Initialize the problem
    def __init__(self, initial):
        self.initial = initial
        self.goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.start_time = 0
        self.nodes_generated = 0

    #Check for valid actions depending on the given state
    def actions(self, state):
        actions = [(-3, "D"), (3, "U"), (1, "L"), (-1, "R")]
        blank_index = state.index(0)

        #Check if the resulting state is valid after moving the blank space
        if blank_index - 3 < 0:
            actions.remove((-3, "D"))
        if blank_index + 3 > 8:
            actions.remove((3, "U"))
        if (blank_index + 1) % 3 == 0:
            actions.remove((1, "L"))
        if (blank_index - 1) % 3 == 2:
            actions.remove((-1, "R"))
        
        return actions
    
    #The resulting state when perfoming the given action on the given state
    def result(self, state, action):
        blank_index = state.index(0)
        next_state = list(state)

        new_blank = blank_index + action[0]
        next_state[blank_index], next_state[new_blank] = next_state[new_blank], next_state[blank_index]
        return tuple(next_state)
    
    #Check if the given state matches the goal
    def goal_test(self, state):
        return state == self.goal
    
    #Heuristic for misplaced tiles given in search.py from the AIMA Github
    def h1(self, node):
        return sum(s != g for (s, g) in zip(node.state, self.goal))
    
    #Heuristic for the Manhattan Distance given in search.ipynb from the AIMA Github
    def h2(self, node):
        goal_indexes = {1:[0,0], 2:[0,1], 3:[0,2], 4:[1,0], 5:[1,1], 6:[1,2], 7:[2,0], 8:[2,1], 0:[2,2]}
        state_indexes = {}
        indexes = [[0,0], [0,1], [0,2], [1,0], [1,1], [1,2], [2,0], [2,1], [2,2]]
        for i in range(9):
            state_indexes[node.state[i]] = indexes[i]
        
        distance = 0
        for i in range(8):
            for j in range(2):
                distance = abs(goal_indexes[i][j] - state_indexes[i][j]) + distance
        
        return distance
    
    #Heuristic for the max of h1 and h2 given in search.ipynb from the AIMA Github
    def h3(self, node):
        misplaced = self.h1(node)
        manhattan = self.h2(node)
        return max(misplaced, manhattan)

#Node class based off the code in search.py from the AIMA Github
class Node:
    #Create a node based off the given state
    def __init__(self, state, path = "", parent = None):
        self.state = state
        self.path = path
        self.parent = parent
        self.time_taken = 0
        self.nodes_generated = 0

    #Get each child node from the current node
    def expand(self, problem):
        return [self.child_node(problem, action) for action in problem.actions(self.state)]
    
    #Get each state from the current state and turn them into nodes
    def child_node(self, problem, action):
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self.path + action[1], self)
        return next_node
    
    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state
    
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)
    
#Breadth First Search based off the graph version in search.py from the AIMA Github
def bfs(problem):
    frontier = deque([Node(problem.initial)])
    state_frontier = set()
    state_frontier.add(Node(problem.initial))
    visited = set()

    while frontier:
        #Check if the time exceeds 15 minutes (900 seconds) and cancel the search
        if time.time() - problem.start_time >= 900:
            node.state = "timeout"
            node.path = "Timeout"
            node.time_taken = 900
            node.nodes_generated = problem.nodes_generated
            return node
        
        node = frontier.popleft()
        #Frontier to keep track of the states to search for them faster
        state_frontier.remove(node)
        visited.add(node.state)

        #Check if the node's state matches the goal
        if problem.goal_test(node.state):
            node.nodes_generated = problem.nodes_generated
            node.time_taken = time.time() - problem.start_time
            return node

        #Generate the children for this node
        children = node.expand(problem)
        problem.nodes_generated += len(children)
        for child in children:
            #Check that each child has not been visited and that it is not in the state frontier
            if child.state not in visited and child not in state_frontier:
                frontier.append(child)
                state_frontier.add(child)

#Check for cycles when searching
def is_cycle(node):
    visited = set()
    while node:
        if node in visited:
            return True
        visited.add(node)
        node = node.parent
    return False

#Depth limited Search based off the iterative version in the book
def depth_limited_search(problem, limit):
    frontier = [Node(problem.initial)]
    result = "failure"

    while frontier:
        #Check if the time exceeds 15 minutes (900 seconds) and cancel the search
        if time.time() - problem.start_time >= 900:
            node.state = "timeout"
            node.path = "Timeout"
            node.time_taken = 900
            node.nodes_generated = problem.nodes_generated
            return node
        
        node = frontier.pop()
        #Check if the node's state matches the goal state and return the node
        if problem.goal_test(node.state):
            node.nodes_generated = problem.nodes_generated
            node.time_taken = time.time() - problem.start_time
            return node
        
        #Check if the current node's depth is more than the limit
        if len(node.path) > limit:
            result = "cutoff"
        elif not is_cycle(node):
            children = node.expand(problem)
            problem.nodes_generated += len(children)
            for child in children:
                frontier.append(child)
    return result

#Iterative Deepening Search based off the the code given in search.py from the AIMA Github
def ids(problem):
    for depth in range(sys.maxsize):
        result = depth_limited_search(problem, depth)
        if result != "cutoff":
            return result
        
#Best First Search based off the code given in search.py from the AIMA Github
def best_first_search(problem, f):
    frontier = PriorityQueue('min', f)
    frontier.append(Node(problem.initial))

    #Frontier to keep track of the states to search for them faster
    state_frontier = set()
    state_frontier.add(Node(problem.initial))
    explored = set()

    while frontier:
        #Check if the time exceeds 15 minutes (900 seconds) and cancel the search
        if time.time() - problem.start_time >= 900:
            node.state = "timeout"
            node.path = "Timeout"
            node.time_taken = 900
            node.nodes_generated = problem.nodes_generated
            return node

        node = frontier.pop()
        state_frontier.remove(node)
        explored.add(node.state)

        #Check if the node's state matches the goal
        if problem.goal_test(node.state):
            node.nodes_generated = problem.nodes_generated
            node.time_taken = time.time() - problem.start_time
            return node
        
        #Generate the children for this node
        children = node.expand(problem)
        problem.nodes_generated += len(children)
        for child in children:
            #Check that each child has not been visited and that it is not in the state frontier
            if child.state not in explored and child not in state_frontier:
                frontier.append(child)
                state_frontier.add(child)
            #Check if the child is in the state frontier and that its f is less than its match
            elif child in state_frontier and f(child) < frontier[child]:
                del frontier[child]
                frontier.append(child)
    return None

#A* Search based off the code given in search.py from the AIMA Github
def astar(problem, h):
    h = memoize(h, "h")
    return best_first_search(problem, lambda n: len(n.path) + h(n))

#Code to check if the puzzle is solvable given in search.py from the AIMA Github
def check_solvability(state):
    inversion = 0
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if (state[i] > state[j]) and state[i] != 0 and state[j] != 0:
                inversion += 1

    return inversion % 2 == 0

def main():
    #Check users inputs
    if len(sys.argv) < 3:
        print("Please enter 2 arugments in the form <filepath> <algorithm>.")
        print("Algorithm options are BFS, IDS, h1, h2, or h3.")
        return
    file_path = sys.argv[1]
    algo = sys.argv[2].lower()

    #Secret input for Part 3
    print_format = "default"
    if len(sys.argv) > 3:
        print_format = sys.argv[3]

    #Make sure the file exists before opening
    try:
        #Read the file to get the starting game state
        file = open(file_path, "r")
        input_puzzle = []
        for line in file:
            split_line = line.strip().split()
            for char in split_line:
                if char == "_":
                    input_puzzle.append(0)
                elif char != "\n":
                    input_puzzle.append(int(char))
        eight_puzzle = Problem(tuple(input_puzzle))
        
        #Check if the puzzle is solvable
        if check_solvability(eight_puzzle.initial):
            eight_puzzle.start_time = time.time()
            #Run the chosen algorithm
            if algo == "bfs":
                solution = bfs(eight_puzzle)
            elif algo == "ids":
                solution = ids(eight_puzzle)
            elif algo == "h1":
                solution = astar(eight_puzzle, eight_puzzle.h1)
            elif algo == "h2":
                solution = astar(eight_puzzle, eight_puzzle.h2)
            elif algo == "h3":
                solution = astar(eight_puzzle, eight_puzzle.h3)
            else:
                print("Invalid algorithm.")
                return

            #Print the result of the search
            if isinstance(solution, Node):
                if print_format != "part3":
                    print("Path:", solution.path)
                    print("Path length:", len(solution.path) if solution.state != "timeout" else solution.path)
                    if solution.time_taken < 60:
                        print("Time taken: %.3f seconds" % solution.time_taken)
                    elif solution.state != "timeout":
                        print("Time taken: %d minutes and %.3f seconds" % (solution.time_taken // 60, solution.time_taken % 60))
                    else:
                        print("Time taken: %d minutes" % (solution.time_taken // 60))
                    print("Nodes Generated:", eight_puzzle.nodes_generated)
                #Print for Part 3
                else:
                    print(solution.time_taken)
                    print(solution.nodes_generated)
            else:
                print("No solution found")
        else:
            print("The given puzzle is not solvable")
        
        file.close()
    except FileNotFoundError:
        print("File not found.")
    except Exception as error:
        print(error)

main()