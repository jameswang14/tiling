import sys
import re
import itertools
import copy
def pretty_print(piece):
    for line in piece:
        print(line)
    print()

def rotate(piece):
    return [ [i for i in row] for row in zip(*piece[::-1])]

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
    solutions = []
    for i, row in enumerate(curr):
        for j, char in enumerate(row):
            for p in pieces:
                curr_copy = _try_placing(board, curr, p, i,j)
                print(curr_copy)
    # _backtrack(board, curr, pieces, solutions)
    return solutions

def _backtrack(board, curr, pieces, solutions):
    if _check_complete(board, curr):
        solutions.add(curr)
        return
    if len(pieces) == 0:
        return
    for i, row in enumerate(curr):
        for j, char in enumerate(row):
            if char == ' ' and board[i][j] != ' ': # first empty spot that shouldn't be empty
                for p in pieces:
                    curr_copy = _try_placing(board, curr, p, i, j)
                    print(curr_copy)
                    if curr_copy:
                        pieces_copy = copy.deepcopy(pieces)
                        pieces_copy.remove(p)
                        print(pieces_copy)
                        for p in pieces: pretty_print(p)
                        for p in pieces: pretty_print(pieces_copy)
                        _backtrack(board, curr_copy, pieces_copy, solutions)

def _check_complete(board, curr):
    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char != curr[i][j]:
                return False
    return True

def _try_placing(board, curr, piece, i, j):
    curr_copy = copy.deepcopy(curr)
    for k, row in enumerate(piece):
        for l, char in enumerate(row):
            if (    
                    i >= len(board) or j >= len(board[i]) or 
                    (char != ' ' and curr_copy[i][j] != ' ') or 
                    (char != ' ' and char != board[i][j])
                ):
                return None
            curr[i][j] = piece[k][l]
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
pretty_print(pieces)
# solutions = solve(pieces, board)
# print (solutions)