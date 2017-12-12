import sys
import re
import copy
import timeit

#------- Utility Functions ---------#
# For convinence, debugging, or optimization

def pretty_print(piece):
    for line in piece:
        print(line)

def rotate(piece):
    return [ [i for i in row] for row in zip(*piece[::-1])]

def flip(piece):
    return [ row[::-1] for row in piece]

def _deepcopy_matrix(m):
    return [ i[:] for i in m] 

def _deepcopy_3d(m):
    return [ [ j[:] for j in i] for i in m]

#----------------------------------#

# Implementation of floodfill that stores points that have been flooded
# to be reconstructed later into a piece.
# returns: list[Tuple(int, int, char)]
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

# Reads ASCII file and pinds pieces/board
# Uses floodfill to generate pieces, which returns an encoding of points
# Board is found by finding the piece with the most non-whitespace characters
def process_input(input_matrix):
    pieces = []
    for i, row in enumerate(input_matrix):
        for j, char in enumerate(row):
            if not re.match(r'\s\s*', input_matrix[i][j]):
                points = []
                _flood(input_matrix, i, j, 0, 0, points)
                piece = _reconstruct_piece(points)
                pieces.append(_reconstruct_piece(points))
    if len(pieces) < 2:
        return None, None
    board = _find_board(pieces)
    pieces.remove(board)
    return pieces, board

# Helper function to find the board out of all the pieces
def _find_board(pieces):
    max_piece = max(pieces, key=lambda p: len(p) * len(p[0]))
    max_area = len(max_piece) * len(max_piece[0])
    largest = [p for p in pieces if len(p) * len(p[0]) == max_area]
    best_piece = None
    best_area = 0
    for p in largest:
        curr = 0
        for i, row in enumerate(p):
            for j, char in enumerate(row):
                if not char.isspace():
                    curr+=1
        if curr > best_area:
            best_area = curr
            best_piece = p
    return best_piece

# Reconstructs a piece based on encoding, where points 
# is a list[Tuple(x, y, c)] where x and y are the absolute coordiantes 
# (coordiantes on the original board). These are converted into relative 
# coordinates to construct the matrix representation of the piece
def _reconstruct_piece(points):
    x = min(points, key=lambda t: t[0])[0]
    y = min(points, key=lambda t: t[1])[1]
    width = max(points, key=lambda t: t[0])[0] - x + 1
    length = max(points, key=lambda t: t[1])[1] - y + 1
    piece = [ [ ' ' for i in range(length)] for j in range(width) ]
    
    for (i, j, c) in points:
        piece[(i-x)][(j-y)] = c

    return piece

# Finds and stores symmetries for each piece
def find_symmetries(pieces):
    symmetries = {}
    for i, p in enumerate(pieces):
        symmetries[i] = _check_symmetry(p)
    return symmetries

# Checks for rotational symmetry, recording answers with a string representation
def _check_symmetry(piece):
    l = []
    if piece == rotate(piece): # full rotational symmetry (e.g square)
        l.append('r0')
    elif piece == rotate(rotate(piece)) and rotate(piece) == rotate(rotate(rotate(piece))):
        l.append('r1')
    elif rotate(piece) == rotate(rotate(rotate(piece))):
        l.append('r12')
    elif piece == rotate(rotate(piece)): symmetries[i].append('r23')
    flipped_piece = flip(piece)
    if piece == flipped_piece:
        l.append('f')
        return l
    if flipped_piece == rotate(flipped_piece):
        l.append('fr0')
    elif flipped_piece == rotate(rotate(flipped_piece)) and rotate(flipped_piece) == rotate(rotate(rotate(flipped_piece))):
        l.append('fr1')
    elif rotate(flipped_piece) == rotate(rotate(rotate(flipped_piece))):
        l.append('fr12')
    elif flipped_piece == rotate(rotate(flipped_piece)):
        l.append('fr23')
    return l

# Generates data structures and calls recursive backtracking method
def solve(pieces, board):
    global board_symmetry
    curr = [ [' ' for i in range(len(board[j]))] for j in range(len(board))]
    curr_unique = [ [' ' for i in range(len(board[j]))] for j in range(len(board))]
    num_pieces = [ i for i in range(len(pieces))] # rather than store a copy of all the pieces, store the indicies for memory/speed optimization
    symmetries = find_symmetries(pieces)
    board_symmetry = _check_symmetry(board)
    # symmetries = {i:[] for i in range(len(pieces))}
    solutions = []
    _backtrack(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, 0, 0)
    return solutions

# Helper method to decide whether or not to prune
def _backtrack_branch(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, rp, i, j, n):
    curr_copy = _try_placing(board, curr, rp, i, j) # if returns None, prune
    if curr_copy:
        index = num_pieces.index(n)
        num_pieces.remove(n)
        curr_unique_copy = _place_unique(curr_unique, rp, i, j, n)
        _backtrack(board, curr_copy, curr_unique_copy, pieces, num_pieces, solutions, symmetries, i, j)
        num_pieces.insert(index, n)

# Checks if a completed board is unique
def _check_unique_solution(curr_unique, solutions):
    for s in solutions:
        for c in (curr_unique, flip(curr_unique)):
            if (
                c == s 
                or c == rotate(s)
                or c == rotate(rotate(s))
                or c == rotate(rotate(rotate(s)))
            ):
                return False
    return True

# Recursive backtracking method
def _backtrack(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, i, j):
    global rotate_flag, flip_flag
    if board == curr and _check_unique_solution(curr_unique, solutions):
        solutions.append(curr_unique)
        return
    if len(num_pieces) == 0:
        return
    if first_flag and len(solutions) > 0:
        return
    for i in range(len(curr)):
        row = curr[i]
        for j in range(len(row)):
            char = row[j]
            if char == ' ' and board[i][j] != ' ': # first empty spot that shouldn't be empty
                for n in num_pieces:
                    rp = pieces[n]
                    _backtrack_branch(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, rp, i, j, n)
                    if rotate_flag and 'r0' not in symmetries[n]:
                        x = 3
                        if 'r1' in symmetries[n]: x = 1
                        elif 'r12' in symmetries[n]: x = 2
                        elif 'r23' in symmetries[n]: # 2-way rotational symmetry, not necessary to check (e.g square)
                            rp = rotate(rp)
                            x = 2
                        for _ in range(0,x): # try all rotations 
                            rp = rotate(rp)
                            _backtrack_branch(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, rp, i, j, n)
                    if flip_flag and 'f' not in symmetries[n]: # flip flag and no flip symmetry
                        rp = flip(pieces[n])
                        _backtrack_branch(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, rp, i, j, n)
                        if rotate_flag and 'fr0' not in symmetries[n]:
                            x = 3
                            if 'fr0' in symmetries[n]: x = 0
                            if 'fr1' in symmetries[n]: x = 1
                            elif 'fr12' in symmetries[n]: x = 2
                            elif 'fr23' in symmetries[n]: # 2-way rotational symmetry, not necessary to check (e.g square)
                                rp = rotate(rp)
                                x = 2
                            for _ in range(0,x): # try all rotations 
                                rp = rotate(rp)
                                _backtrack_branch(board, curr, curr_unique, pieces, num_pieces, solutions, symmetries, rp, i, j, n)
                return

# Checks for isomorphic solutions - not used, implementation isn't
# optimized
def _check_partial_match(curr_unique, solutions):
    global board_symmetry, rotate_flag, flip_flag
    cr = _deepcopy_matrix(curr_unique)
    for s in solutions:
        if 'r0' or 'r1' or 'r12' or 'r23' in board_symmetry:
            for x in range(0,3):
                if _check_partial_equivalence(rotate(cr), s): return True
    return False

def _check_partial_equivalence(curr_unique, s):
    for i, row in enumerate(curr_unique):
        for j, c in enumerate(row):
            if c != ' ' and c != s[i][j]:
                return False
    pretty_print(curr_unique)
    pretty_print(s)
    return True

# Similar to placing a piece but places a fixed number num instead 
# of the character of the piece. This is to label which pieces are placed where
# for outputting to the GUI
def _place_unique(curr_unique, piece, i, j, num):
    offset = 0
    for char in piece[0]:
        if char != ' ':
            break
        offset+=1
    j -= offset
    curr_unique_copy = _deepcopy_matrix(curr_unique)
    for row in piece:
        for char in row:
            if char != ' ':
                curr_unique_copy[i][j] = num
            j+=1
        j-=len(row)
        i+=1
    return curr_unique_copy

# Attempts to place piece at given coordiates i, je
# Fails if piece goes out of bounds, doesn't match original board config, or
# another piece is in the way.m 
def _try_placing(board, curr, piece, i, j):
    offset = 0
    for char in piece[0]:
        if char != ' ':
            break
        offset+=1
    if (j-offset) < 0 or len(piece[0]) - offset > len(board[i]) - j or len(piece) > len(board) - i:
        return None
    j -= offset
    curr_copy = _deepcopy_matrix(curr)
    for k, row in enumerate(piece):
        for l, char in enumerate(row):
            if char == ' ':
                j+=1 
                continue
            if curr_copy[i][j] != ' ' or char != board[i][j]:
                return None
            
            curr_copy[i][j] = piece[k][l]
            j+=1
        j-=len(row)
        i+=1
    return curr_copy


count = 0
rotate_flag = False
flip_flag = False
first_flag = False
board_symmetry = []

def main(filename, rotates, flips, first):
    global rotate_flag, flip_flag, first_flag
    rotate_flag = True if rotates == "true" else False
    flip_flag = True if flips == "true" else False
    first_flag = True if first == "true" else False

    start = timeit.default_timer()
    f = open('./input/'+filename, 'r')
    input_matrix = [ [char for char in line] for line in f]
    pieces, board = process_input(input_matrix)
    if not pieces: # invalid input
        return None, None, None

    rotate_board = False

    # if board is longer than it is tall, rotate and solve
    # this is a large optimization because searching is top-down left-right
    if len(board[0]) > len(board) and rotate_flag: 
        rotate_board = True
        board = rotate(board)

    solutions = solve(pieces, board)
    # rotate solutions back if board was rotated
    if rotate_board:
        solutions = [rotate(rotate(rotate(s))) for s in solutions]
    end = timeit.default_timer()
    
    return solutions, (end-start), len(pieces)
