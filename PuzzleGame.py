
import numpy as np
import argparse

class BoardState:
    def __init__ (self, board):
        self.board = board.copy()
        self.depth = 0
        self.h_val = float('inf')
        self.parent = None
        
    def f_val(self):
        return self.depth + self.h_val
    
    def __lt__(self, other):
        # less than
        # comparing class <-> comparing f value
        if self.__class__ != other.__class__:
            return False
        else:
            return self.f_val() < other.f_val()
        
    def __eq__(self, other):
        # equal 
        # compare board
        if self.__class__ != other.__class__:
            return False
        else:
            return np.array_equal(self.board, other.board)
        
    def copy(self):
        p = BoardState(self.board)
        p.depth = self.depth
        p.h_val = self.h_val
        p.parent = self.parent
        return p
    
    def __str__(self):
        s = ''
        for a in self.board:
            s += ' '.join([str(b) for b in a])
            s += '\n'
        return s
        
    def legal_moves(self):
        # returns index of legal moves from current
        
        r,c = self.find(0)
        N = len(self.board)

        moves = []
        # DRUL order since down and right is more in the general direction to the goal.
        if c < N - 1:
            moves.append((r, c + 1)) # move down
        if r < N - 1:
            moves.append((r + 1, c)) # move right
        if c > 0:
            moves.append((r, c - 1)) # move up
        if r > 0:
            moves.append((r - 1, c)) # move left
        
        return moves
    
    def new_boards(self):
        # generate all new boards from self
        moves = self.legal_moves()
        zero_idx = self.find(0)
        
        boards = [] 
        for m in moves:
            p = self.copy()
            p.swap(zero_idx, m)
            p.depth += 1
            p.parent = self
            boards.append(p)
        return boards
        
    def solution_path(self, path):
        if self.parent == None:
            return path
        else:
            path.append(self)
            return self.parent.solution_path(path)
        
    def find(self, value):
        # return index of value
        
        if value < 0 or value > np.max(self.board):
            raise ValueError('Value out of range')
        
        r,c = np.where(self.board == value)
        
        return r,c
    
    def swap(self, idx_a, idx_b):
        # swap values at idx_a with idx_b
        self.board[idx_a], self.board[idx_b] = self.board[idx_b], self.board[idx_a]

def index(i, seq):
    # return index if i in seq else return -1
    for k, s in enumerate(seq):
        if s == i:
            return k
    else:
        return -1


def manhatten(node, goal):
    total = 0
    for i in range(np.max(goal.board)):
        ra, ca = node.find(i)
        rb, cb = goal.find(i)
        total += abs(ra-rb) + abs(ca-cb)
    return total

def solver(startState, goalState, h_func = lambda t: 0, max_states = 10000):
    
    startState.h_val = 0
    openSet = [startState]
    closedSet = []
    
    states = 0
    
    while openSet:
        if states > max_states:
            break
        current = openSet.pop(0)
        if current ==  goalState:
            if len(closedSet) > 0:
                return list(reversed(current.solution_path([]))), states
            else:
                return [current], states
        
        moves = current.new_boards()
       
        for move in moves:
            o_idx = index(move, openSet)
            c_idx = index(move, closedSet)
            h_val = h_func(move, goalState)
            f_val = move.depth + h_val
            
            if o_idx == -1 and c_idx == -1:
                states += 1 # new state seen
                move.h_val = h_val
                openSet.append(move)
            elif o_idx > -1:
                # seen in openSet
                copy = openSet[o_idx]
                if f_val < copy.f_val():
                    copy.h_val = h_val
                    copy.parent = move.parent
                    copy.depth = move.depth
            elif c_idx > -1:
                # seen in closedSet
                copy = closedSet[c_idx]
                if f_val < copy.f_val():
                    move.h_val = h_val
                    closedSet.remove(copy)
                    openSet.append(move)
            
            closedSet.append(current)
            openSet = sorted(openSet, key = lambda p: p.f_val()) # sort moves based on f_val
    return [], states # no finish state found

def path_string(path):
    """
    return string of moves (left, right, up, down) given all visited nodes.
    """
    s = ''
    for i in range(0,len(path)-1):
        b1 = path[i]
        b2 = path[i+1]
        b1_row, b1_col = b1.find(0)
        b2_row, b2_col = b2.find(0)
        move = (b1_row - b2_row, b1_col - b2_col)
        if move == (0, 1):
            s += 'L'
        if move == (0, -1):
            s += 'R'
        if move == (1, 0):
            s += 'U'
        if move == (-1, 0):
            s += 'D'
    return s
   

def import_data(filename):
    """
    Reads file
    ex:
    3
    1 2 3
    4 0 5
    5 7 8
    """
    out = []
    with open(filename, 'r') as f:
        a = True
        for l in f:
            if a:
                N = l
                a = False
            else:
                for b in l.split():
                    out.append(int(b))
    N = int(N)
    return N, np.asarray(out).reshape((N,N))


def export_data(output_filename, solution):
    """
    Saves solution to file.
    ex: 
    1 2 3
    0 5 6
    4 7 8
    Solution: 1, DRR
    States seen: ?
    """
    full_path, states = solution
    s = path_string(full_path)
    with open(output_filename, 'w') as f:
        string = str(full_path[0])
        string += 'Solution: ' + str(len(s)) + ', '+ s + '\n'
        string += 'States seen: ' + str(states)
        
        f.write(string)

import time

def main(input_filename, output_filename, max_states = 10000):
    N, matrix = import_data(input_filename)
    GOAL = BoardState(np.append(np.arange(1, N**2), 0).reshape((N,N)))
    
    START = BoardState(matrix)
    full_path = [START]
    
    path, states = solver(START, GOAL, h_func = manhatten, max_states = max_states)
    
    full_path = full_path + path
    
    solution = (full_path, states)
    
    export_data(output_filename, solution)
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A* search solver for N-puzzle problem.')
    parser.add_argument('input_filename', help='Input filename')
    parser.add_argument('output_filename', help='Output filename')
    parser.add_argument('-max_states', type=int, help='Stop after max states seen', default=10000)
    args = parser.parse_args()
    main(args.input_filename, args.output_filename, args.max_states)
