from collections import namedtuple
import time

GameState = namedtuple('GameState', 'to_move, utility, board, moves')

#Gomoku class modified from games.py in the AIMA GitHub
class Gomoku:
    def __init__(self):
        self.h = 15
        self.v = 15
        self.k = 5
        moves = [(x, y) for x in range(1, self.h + 1) for y in range(1, self.v + 1)]
        self.initial = GameState(to_move='B', utility=0, board={}, moves=moves)
    
    #Get the list of moves
    def actions(self, state):
        return state.moves
    
    #Result after doing a move
    def result(self, state, move):
        if move not in state.moves:
            return state
        board = state.board.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return GameState(to_move=('W' if state.to_move == 'B' else 'B'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board, moves=moves)
    
    def utility(self, state, player):
        return state.utility if player == 'B' else -state.utility
    
    def terminal_test(self, state):
        return state.utility != 0 or len(state.moves) == 0
    
    #Print the game board
    def display(self, state):
        board = state.board
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

    def compute_utility(self, board, move, player):
        if (self.k_in_row(board, move, player, (0, 1)) or
            self.k_in_row(board, move, player, (1, 0)) or
            self.k_in_row(board, move, player, (1, -1)) or
            self.k_in_row(board, move, player, (1, 1))):
            return 1000 if player == 'B' else -1000
        else:
            return 0

    def k_in_row(self, board, move, player, delta_x_y):
        delta_x, delta_y = delta_x_y
        x, y = move
        n = 0  
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  
        return n >= self.k

    #First evaluation function, this one checks if the current state of the board has a win somewhere in it
    def eval_func_one(self, state):
        #Checks if the given state is terminal
        if self.terminal_test(state):
            return state.utility
        
        #Checking if there is a win for each direction (Row, Col, Diagonals)
        def check_chain(board, action):
            if (board.get((x, y), ".") == "B" 
                and board.get((x + action[0], y + action[1]), ".") == "B"
                and board.get((x + (action[0] * 2), y + (action[1] * 2)), ".") == "B"
                and board.get((x + (action[0] * 3), y + (action[1] * 3)), ".") == "B"
                and board.get((x + (action[0] * 4), y + (action[1] * 4)), ".") == "B"):
                return True
            return False
        
        score = 0
        actions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        board = state.board

        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                #Checking if each row has a win
                if x + 4 <= self.h and check_chain(board, actions[0]):
                    score += 1000
                #Checking if each col has a win
                if y + 4 <= self.v and check_chain(board, actions[1]):
                    score += 1000
                #Checking if each downward diagonal has a win
                if (x + 4 <= self.h and y + 4 <= self.v) and check_chain(board, actions[2]):
                    score += 1000
                #Checking if each upward diagonal has a win
                if (x + 4 <= self.h and y - 4 >= 1) and check_chain(board, actions[3]):
                    score += 1000
        return score

    #Sevond evaluation function, this one counts up how many B's are in a row
    def eval_func_two(self, state):
        #Checking if the given state is terminal
        if self.terminal_test(state):
            return state.utility
        
        #Checking how many B's in a row there are in each direction (Row, Col, Diagonals)
        def count_b(board, action):
            score = 0
            chain = False
            if board.get((x, y), ".") == "B":
                chain = True
                score += 10
            if board.get((x + action[0], y + action[1]), ".") == "B" and chain: 
                score += 20
            else: 
                chain = False
            if board.get((x + (action[0] * 2), y + (action[1] * 2)), ".") == "B" and chain: 
                score += 30
            else: 
                chain = False
            if board.get((x + (action[0] * 3), y + (action[1] * 3)), ".") == "B" and chain: 
                score += 40
            else: 
                chain = False
            if board.get((x + (action[0] * 4), y + (action[1] * 4)), ".") == "B" and chain: 
                score += 1000
            return score
                
        score = 0
        actions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        board = state.board

        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                #Checking how many B's in a row there are in each row
                if x + 4 <= self.h:
                    score += count_b(board, actions[0])
                #Checking how many B's in a row there are in each col
                if y + 4 <= self.v:
                    score += count_b(board, actions[1])
                #Checking how many B's in a row there are in each downwards diagonal
                if (x + 4 <= self.h and y + 4 <= self.v):
                    score += count_b(board, actions[2])
                #Checking how many B's in a row ther are in each upwards diagonal
                if (x + 4 <= self.h and y - 4 >= 1):
                    score += count_b(board, actions[3])
        return score
        
    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

#Alpha-Beta Search function from games.py in the AIMA GitHub
def alpha_beta_cutoff_search(state, game, eval_func, max_depth=2):
    #Max value function
    def max_value(state, alpha, beta, depth):
        if depth > max_depth or game.terminal_test(state):
            return game.eval_func_one(state) if eval_func == 1 else game.eval_func_two(state)
        v = float("-inf")
        for action in game.actions(state):
            v = max(v, min_value(game.result(state, action), alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    #Min value function
    def min_value(state, alpha, beta, depth):
        if depth > max_depth or game.terminal_test(state):
            return game.eval_func_one(state) if eval_func == 1 else game.eval_func_two(state)
        v = float("inf")
        for action in game.actions(state):
            v = min(v, max_value(game.result(state, action), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    #Getting the move
    alpha = float("-inf")
    beta = float("inf")
    move = None
    for action in game.actions(state):
        v = min_value(game.result(state, action), alpha, beta, 1)
        if v > alpha:
            alpha = v
            move = action
    return move

#Human player code modified from games.py in the AIMA GitHub
def human_player(game, state, preset=None, i=0):
    if preset:
        if preset[i] not in game.actions(state):
            print("Your move:", preset[i + 1])
            return preset[i + 1]
        print("Your move:", preset[i])
        return preset[i]
    
    print("Available Moves:")
    print(game.actions(state))
    move = None
    if game.actions(state):
        move_string = input("Your move: ")
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    else:
        print("No legal moves")
    return move

#Alpha-Beta player code modified from games.py in the AIMA GitHub
def alpha_beta_player(game, state, eval_func):
    ab_move = alpha_beta_cutoff_search(state, game, eval_func)
    print("Alpha-Beta's move:", ab_move)
    return ab_move

#Complete the first 3 moves of the game
def initialize_game(game, state, eval_func, preset=None):
    #Black's first move
    move = ((game.h // 2) + 1, (game.v // 2) + 1)
    print("Alpha-Beta's move:", move)
    state = game.result(state, move)
    game.display(state)
    print()

    #White's first move
    move = human_player(game, state, preset)
    state = game.result(state, move)
    game.display(state)
    print()

    #Black's second move
    #Get legal actions based on the rules of Gomoku
    actions = []
    for action in game.actions(state):
        if (action[0] <= 1 or action[0] >= 5) or (action[1] <= 1 or action[1] >= 5):
            actions.append(action)

    #Update the states legal moves while keeping track of the old legal moves to re-use after getting Alpha-Beta's move
    original_moves = state.moves
    state = state._replace(moves = actions)
    move = alpha_beta_player(game, state, eval_func)
    state = state._replace(moves = original_moves)
    state = game.result(state, move)
    game.display(state)
    return state

def main():
    if input("Are you using the preset (Yes or No)? ").lower() == "yes":
        use_preset = True
    else:
        use_preset = False
    eval_func = int(input("Which evaluation function do you want to use (1 or 2)? "))

    #Initialize the game
    start_time = time.time()
    state = Gomoku().initial
    Gomoku().display(state)
    print()
    if use_preset:
        #Predetermined moves for depth testing
        preset = [(1, 2), (2, 3), (3, 4), (4, 5), (1, 6), (2, 5), (4, 3), (5, 4), (2, 2), (2, 4), (2, 6), (7, 7), (10, 10), (9, 10), (10, 1), (9, 3), (8, 7), (7, 9)]
        state = initialize_game(Gomoku(), state, eval_func, preset)
        i = 1
    else:
        state = initialize_game(Gomoku(), state, eval_func)

    #Continue taking turns until the game is over
    while not Gomoku().terminal_test(state):
        print()
        player = state.to_move
        if player == "B":
            move = alpha_beta_player(Gomoku(), state, eval_func)
        else:
            if use_preset:
                move = human_player(Gomoku(), state, preset, i)
                i += 1
            else:
                move = human_player(Gomoku(), state)
        state = Gomoku().result(state, move)
        Gomoku().display(state)
    print()

    #Display who won
    if len(state.moves) != 0:
       print("Alpha-Beta wins!") if player == "B" else print("You won!")
    else:
        print("You guys tied!")
    
    #Display how long the game took
    if time.time() - start_time < 60:
        print("Time taken: %.3f seconds" % (time.time() - start_time))
    else:
        print("Time taken: %d mins and %.3f seconds" % ((time.time() - start_time) // 60, (time.time() - start_time) % 60))

main()