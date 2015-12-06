
# coding: utf-8

# In[3]:

from sunfish import *
import random


# In[5]:


#returns intermediate board type (used internally for convenience because it prints well)
def fen2iboard(fen):
    [fen_board, to_move] = fen.split(" ")
    #replace each number with corresponding number of spaces
    f = lambda x: "".join(["." * int(k) if (k in "12345678") else k for k in x])
    #split on /
    # end each line with \n and append space at beginning
    return ([f(" " + s + '\n') for s in fen_board.split("/")], to_move)

#returns sunfish input format from intermediate board in format (sunfish_board, to_move)
def iboard2sunfish(iboard):
    edge_buffer = "         \n"
    return (''.join([edge_buffer, edge_buffer, "".join(iboard), edge_buffer, edge_buffer[:-1]]), to_move)

#converts fen to sunfish format (just chains above two commands)
#returns:
#(sunfish_board, to_move )
def fen2sunfish(fen):
    iboard, to_move = fen2iboard(fen)
    return iboard2sunfish(iboard)
    

fen_sample = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b"
iboard_sample, to_move = fen2iboard(fen_sample)
(sunfish_board_sample, to_move) = fen2sunfish(fen_sample)
iboard_sample


# In[6]:

#testing fen2sunfish function to see if sunfish likes it 
pos = Position(sunfish_board_sample, 0, (True,True), (True,True), 0, 0)
#if to_move == 'b' : pos = pos.rotate()
print(pos)

#moves generator
for move in pos.gen_moves():
    print(move)

print_pos(pos)
#looks good


# In[7]:

iboard_sample


# In[8]:


#make all legal moves for a given board
#board: starting intermediate board (see output of fen2sunfish)
#(move_start, move_end): in output format of the moves generator from sunfish
#note that movestart/moveend are really confusing, ask for board diagram picture I took
#returns: (new_board, piece_moved, piece_taken)
#where new_board is the board after the move and piece moved is the letter of the piece moved
def apply_move(board, (move_start, move_end)):
    board_copy = [list(row) for row in board]
    start_x, start_y = (move_start / 10 - 2, move_start - move_start / 10 * 10)
    if (move_end is None) :
        #disappear
        start_piece = board[start_x][start_y]
        end_piece =  board[start_x][start_y]
        board_copy[start_x][start_y] = '.'
        return (["".join(row) for row in board_copy], start_piece, end_piece)
    end_x, end_y = (move_end / 10 - 2, move_end - move_end / 10 * 10)
    #print(start_x, start_y)
    #print(end_x, end_y)
    start_piece = board[start_x][start_y]
    #add . to original spot
    board_copy[start_x][start_y] = '.'
    #add piece to end
    #have to do funky stuff because strings are immutable: change to row array the nback
    end_piece = board_copy[end_x][end_y]
    board_copy[end_x][end_y] = start_piece
    return (["".join(row) for row in board_copy], start_piece, end_piece)

#move queen h6e3
apply_move(iboard_sample, (76,57))


# In[9]:

#convert intermediate board format (see above) to keras input format
#board: see above
#to_move: either 'b' or 'w'
#returns: "half" keras format, i.e. just one board position instead of 2
def intboard2halfkeras(iboard, to_move):
    return [1 if iboard[i][j] == p else 0 for i in range(0,8) for j in range (1,9) for p in "pkqnbrPKQNBR"]
len(intboard2halfkeras(iboard_sample, to_move))
k = intboard2halfkeras(iboard_sample, to_move)
[k[i:i+11] for i in range(0,148, 12)]


# Format: for each position, have which of the 12 pieces are there.|

# In[10]:

len(k)


# In[11]:

apply_move(iboard_sample, move)


# In[12]:

#store information about the type of move
class move_info:
    is_own_piece = False
    
    def __init__(self, is_own_piece):
        self.is_own_piece = is_own_piece


# In[13]:

# rotate iboard so that we can generate moves for the correct side (this has to be done for black)
def rotate_iboard(iboard):
    return [" " + row[1:9][::-1] + "\n" for row in iboard_sample[::-1]]


# In[21]:

#legal move keras generation

#generator to get a legal move in sunfish format (just wraps sunfish)
#NOTE: always generates moves for side that it is facing! i.e. if black to move, must be rotated
def get_legal_move_generator(iboard):
    (sunfish_board, to_move) = iboard2sunfish(iboard)
    pos = Position(sunfish_board, 0, (True,True), (True,True), 0, 0) 
    return pos.gen_moves()


#given a position and move, generate keras format for pre and postmove board
#returns: array of keras input formats, one for each legal move
def move2keras(pre_move_iboard, move):
    keras_half_pre = intboard2halfkeras(pre_move_iboard, to_move)
    assert type(move) == tuple, "move is not tuple: {}".format(move)
    post_move_iboard, piece_moved, piece_taken = apply_move(pre_move_iboard, move)
    keras_half_post = intboard2halfkeras(post_move_iboard, to_move)
    #combine, removing "to_move" bit from second half
    return keras_half_pre + keras_half_post

#prints keras format so that column is piece and row is board position (1 to 64, then 1 to 64 for oppoennt)
def prettify_keras(keras_input):
    return [["p k  q  n  b  r  P  K  Q  N  B  R"]] + [keras_input[i:i+12] for i in range(0,1538, 12)]

def prettify_kerasv2(keras_input):
    return [["p k  q  n  b  r  P  K  Q  N  B  R"]] + [keras_input[i:i+12] for i in range(0,1538, 12)]

# print(len(legal_moves))
# print(legal_moves[:5])
k = move2keras(iboard_sample, get_legal_move_generator(iboard_sample).next())
#prettify_keras(k)


# In[22]:

(76, 57) in get_legal_move_generator(iboard_sample)


# In[25]:

#generating illegal moves

# takes in intermediate board 
# returns the sunfish style piece locations as array
def get_piece_positions(i_board):
    #print(i_board)
    assert len(i_board) == 8 and len(i_board[0]) == 10, "how? {}".format(i_board)
    return [20 + x * 10 + y for x in range(0,8) for y in range(1,9) if i_board[x][y] in "PKQNBRpkqnbr"]

#given a position (intermediate board) and legal moves generator (see get_legal_move_generatr, 
# generate illegal moves (generator, use next() to get next value)
def gen_illegal_moves(i_board, legal_move_generator):
    #need to convert sunfish board 
    # get all piece locations (yours and opponents)
    start_options = get_piece_positions(i_board)
    # randomly grab a piece
    chosen_start = random.choice(start_options)
    # pick from all possible move locations + disappear
    target_options = sum([range(i, i+8) for i in range(21, 92, 10)], []) + [None]
    chosen_target = random.choice(target_options)
    # check if legal or not
    if (chosen_start, chosen_target) in legal_move_generator:
        #print("already legal!")
        #call again (recursively until illegal move found)
        yield(gen_illegal_moves(i_board, legal_move_generator))
    else :
        yield((chosen_start, chosen_target))
    #print(chosen_start, chosen_target)   
    #check if already legal; if so, return a different one
    # categorize (piece captured? side moved? etc.)


#print(pos.gen_moves())
for i in range(0,2) :
    print(gen_illegal_moves(iboard_sample, get_legal_move_generator(iboard_sample)).next())


