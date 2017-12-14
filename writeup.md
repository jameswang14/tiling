James Wang (jjw6wz)
Tiling

#Implementation and Algorithms

##Parsing 
    
    To parse the ASCII files I implemented floodfill (BFS) to find the pieces and board. Scan the input files until a non-whitespace character is hit, then floodfill, storing the character and coordinates and replacing the original character in the input with whitespace. For each piece we'll then have a list of tuples in the form of (x, y, character) e.g [(3, 28, @), (4, 28, @)]. To reconstruct the piece, we find the smallest x and y coordinate and shift everything by those values - our piece earlier would become [(0, 0, @), (1, 0, @)]. Iterating through each point we place characters appropraitely and put whitespace everywhere else. To find the board, we pull out the piece with the largest area. 

##Tiling

    The backtracking algorithm works by find the first empty cell (from left-right, top-down order) that shouldn't be empty and trying to fit pieces into it (with or without rotation/flipping). When trying to place a piece, we check if it's valid: the piece doesn't go out of bounds, intersect with another piece, or mismatch with the target board configuration. If it's a valid placement, we also keep track 


#Optimizations

    A majority of the optimizations came from fine-tuning termination conditions, since the _backtrack() and methods inside of it make up 99%+ of the total run-time. The biggest optimization came from knowing when to prune the current branch. Because of the way we search for an empty spot, that is left-right and top-down, and the way we place tiles, that is the top-leftmost non-blank tile, if we ever can't fill a spot we can prune since all subsequent tilings will be unable to fill it.

    Within _try_placing(), we originally had bounds checking inside the loop i.e if the loop every iterated to be out of bounds then return.   Checking this before iteration however, saved a lot of time since it only requires inexpensive mathematical computations and no looping. 

    I noticed that without rotation or flipping, the algorithm ran orders of magnitude faster, which is unsurpising given that run time is factorial. If we can reduce the number of rotations/flips we need to search, we'd get huge performance gains. The only way we can really do this is checking for symmetry - if a piece is symmetrical, we cut down the number of flips and rotations we need to search down in half. 

    Some optimizations were python specific. For example, the built in copy.deepcopy() is extremely slow but was used in the initial implementation. I wrote a custom _deepcopy_matrix() and _deepcopy_3d() that improved speeds by about 100x, a significant improvement especially considering how many times deep copies are needed. I also different python implementations - python 2.7, python3.6, and pypy. Pypy ended up being the fastest, with a 5x speedup over the other two in some cases (2.7 appeared to be marginally faster than 3.6 surpisingly). 

#Optimizations that didn't work
    
     I'll describe some optimizations that didn't make significant gains, or perhaps any. First I tried getting rid of the curr_unique, that is the board that tells us exactly which piece is where, and instead encoding that information elsewhere and reconstructing only if it's a solution - there's no point keeping two running board states and doing tiling placement twice. The drawback is that this would require a custom equals comparator to check if the running board matches the target board, meaning we can't take advantage of python's == operator speed. Turns out this optimization, even without the custom equals() operator, made almost no difference in speed. 