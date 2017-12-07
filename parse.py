import sys
import re
import copy
import timeit
import numpy as np
# todo - convert everything to numpy matricies
count = 0
def pretty_print(piece):
    for line in piece:
        print(line)

def rotate(piece):
    return [ [i for i in row] for row in zip(*piece[::-1])]

def _deepcopy_matrix(m):
    return [ [j for j in i] for i in m] 

def _deepcopy_3d(m):
    return [ [ [k for k in j] for j in i] for i in m]

def _flood(input_matrix, i, j, k, l, points):
    if (
            i < 0 or j < 0 or 
            i >= len(input_matrix) or j >= len(input_matrix[i]) or 
            re.match(r'\s\s*', input_matrix[i][j])
        ):
        return
    points.append((i, j, input_matrix[i][j]))
    input_matrix[i][j] = ' '
    combinations = [(1,0), (0,1), (-1, 0), (0,-1)]
    for t in combinations:
        _flood(input_matrix, i+t[0], j+t[1], k+t[0], l+t[1], points) 
    return points


def process_input(input_matrix):
    pieces = []
    for i, row in enumerate(input_matrix):
        for j, char in enumerate(row):
            if not re.match(r'\s\s*', input_matrix[i][j]):
                points = []
                _flood(input_matrix, i, j, 0, 0, points)
                piece = _reconstruct_piece(points)
                pieces.append(_reconstruct_piece(points))

    board = max(pieces, key=lambda p: len(p) * len(p[0]))
    pieces.remove(board)
    return pieces, board


def _reconstruct_piece(points):
    x = min(points, key=lambda t: t[0])[0]
    y = min(points, key=lambda t: t[1])[1]
    width = max(points, key=lambda t: t[0])[0] - x + 1
    length = max(points, key=lambda t: t[1])[1] - y + 1
    piece = [ [ ' ' for i in range(length)] for j in range(width) ]
    
    for (i, j, c) in points:
        piece[(i-x)][(j-y)] = c

    return piece

def solve(pieces, board):
    curr = [ [' ' for i in range(len(board[j]))] for j in range(len(board))]
    curr_unique = [ [' ' for i in range(len(board[j]))] for j in range(len(board))]
    num_pieces = [ i for i in range(len(pieces))]
    solutions = []
    _backtrack(board, curr, curr_unique, pieces, num_pieces, solutions)
    return solutions

def _backtrack(board, curr, curr_unique, pieces, num_pieces, solutions):
    if _check_complete(board, curr):
        if curr_unique not in solutions:
            solutions.append(curr_unique)
        return
    if len(num_pieces) == 0:
        return
    for i, row in enumerate(curr):
        for j, char in enumerate(row):
            if char == ' ' and board[i][j] != ' ': # first empty spot that shouldn't be empty
                for n in num_pieces:
                    rp = pieces[n]
                    for x in range(0,4):
                        rp = rotate(rp)
                        curr_copy = _try_placing(board, curr, rp, i, j)
                        if curr_copy:
                            num_pieces.remove(n)
                            curr_unique_copy = _place_unique(curr_unique, rp, i, j, n)
                            _backtrack(board, curr_copy, curr_unique_copy, pieces, num_pieces, solutions)
                            num_pieces.append(n)

def _check_complete(board, curr):
    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char != curr[i][j]:
                return False
    return True

def _place_unique(curr_unique, piece, i, j, num):
    curr_unique_copy = _deepcopy_matrix(curr_unique)
    for row in piece:
        for char in row:
            if char != ' ':
                curr_unique_copy[i][j] = num
            j+=1
        j-=len(row)
        i+=1
    return curr_unique_copy

def _try_placing(board, curr, piece, i, j):
    curr_copy = _deepcopy_matrix(curr)
    for k, row in enumerate(piece):
        for l, char in enumerate(row):
            if (    
                    i >= len(board) or j >= len(board[i]) or 
                    (char != ' ' and curr_copy[i][j] != ' ') or 
                    (char != ' ' and char != board[i][j])
                ): 
                return None
            
            if char != ' ':
                curr_copy[i][j] = piece[k][l]
            j+=1
        j-=len(row)
        i+=1
    return curr_copy


filename = './input/'+sys.argv[1]
f = open(filename, 'r')
input_matrix = [ 
    [char for char in line] for line in f
]

pieces, board = process_input(input_matrix)
solutions = solve(pieces, board)
for sol in solutions: 
    pretty_print(sol)
    print()
