
# coding: utf-8

# In[27]:

from sunfish import *
import random
import pandas as pd


# In[28]:


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


# In[29]:

#testing fen2sunfish function to see if sunfish likes it 
pos = Position(sunfish_board_sample, 0, (True,True), (True,True), 0, 0)
#if to_move == 'b' : pos = pos.rotate()
print(pos)

#moves generator
# for move in pos.gen_moves():
#     print(move)

# print_pos(pos)
#looks good


# In[30]:

iboard_sample


# In[31]:


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


# In[32]:

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

# In[33]:

len(k)


# In[34]:

# apply_move(iboard_sample, move)


# In[114]:

# rotate iboard so that we can generate moves for the correct side (this has to be done for black)
def rotate_iboard(iboard):
    return [" " + row[1:9][::-1].swapcase() + "\n" for row in iboard[::-1]]
assert iboard_sample == rotate_iboard(rotate_iboard(iboard_sample))


# In[143]:

#legal move keras generation

#returns list of legal moves, using generator from sunfish
def get_legal_moves(iboard):
    (sunfish_board, to_move) = iboard2sunfish(iboard)
    pos = Position(sunfish_board, 0, (True,True), (True,True), 0, 0)
    moves = []
    for m in pos.gen_moves():
        moves.append(m)
    random.shuffle(moves)
    return moves

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

def prettify_1halfkeras(keras_input):
    return [["p k  q  n  b  r  P  K  Q  N  B  R"]] + [keras_input[i:i+12] for i in range(0,768, 12)]

def prettify_2halfkeras(keras_input):
    return [["p k  q  n  b  r  P  K  Q  N  B  R"]] + [keras_input[i:i+12] for i in range(768,1538, 12)]

# print(len(legal_moves))
# print(get_legal_moves(iboard_sample))
#print(get_random_legal_move(get_legal_moves(iboard_sample)))
k = move2keras(iboard_sample, get_legal_moves(iboard_sample)[0])
#prettify_keras(k)
get_legal_moves(iboard_sample)[0]


# In[48]:

#generating illegal moves

# takes in intermediate board 
# returns the sunfish style piece locations as array
def get_piece_positions(i_board):
    #print(i_board)
    assert len(i_board) == 8 and len(i_board[0]) == 10, "how? {}".format(i_board)
    return [20 + x * 10 + y for x in range(0,8) for y in range(1,9) if i_board[x][y] in "PKQNBRpkqnbr"]

#given a position (intermediate board) and legal moves generator (see get_legal_move_generatr, 
# generate illegal moves (generator, use next() to get next value)
def gen_illegal_moves(i_board, legal_moves):
    #need to convert sunfish board 
    # get all piece locations (yours and opponents)
    start_options = get_piece_positions(i_board)
    # randomly grab a piece
    chosen_start = random.choice(start_options)
    # pick from all possible move locations + disappear
    target_options = sum([range(i, i+8) for i in range(21, 92, 10)], []) + [None]
    chosen_target = random.choice(target_options)
    # check if legal or not
    if (chosen_start, chosen_target) in legal_moves:
        #print("already legal!")
        #call again (recursively until illegal move found)
        yield(gen_illegal_moves(i_board, legal_moves))
    else :
        yield((chosen_start, chosen_target))
    #print(chosen_start, chosen_target)   
    #check if already legal; if so, return a different one
    # categorize (piece captured? side moved? etc.)
#print(get_piece_positions(iboard))
#print(pos.gen_moves())
for i in range(0,2) :
    print(gen_illegal_moves(iboard_sample, get_legal_moves(iboard_sample)).next())


# In[38]:

#store information about the type of move
class MoveInfo:
    move = None;
    #one of pkqnbrPKQNBR from board, should not be None after init
    piece_moved = None
    #piece captured can be None if it disappeared
    #can be "." if no piece captured
    piece_captured = None
    
    #move is in sunfish form, ie. (26, 36)
    # iboard is board before move in intermediate form
    def __init__(self, iboard, move):
        self.move = move
        move_start, move_end = move
        start_x, start_y = (move_start / 10 - 2, move_start - move_start / 10 * 10)
        self.piece_moved = iboard[start_x][start_y]
        if (move_end is None) :
            #disappear
            self.piece_captured = None;
            return
        end_x, end_y = (move_end / 10 - 2, move_end - move_end / 10 * 10)
        self.piece_captured = iboard[end_x][end_y]
    
    def is_disappear(self):
        return piece_captured is None
    
    def is_capture(self):
        return piece_captured is not None and piece_captured != "."
    
    def __str__(self):
        return "{}, {}->{}".format(self.move, self.piece_moved, self.piece_captured)
        
print(MoveInfo(iboard_sample, get_legal_moves(iboard_sample)[2]))


# In[39]:

# NUM_LEGAL = 5
# NUM_ILLEGAL = 5
# with open("../data/2015-12-01-fen_sample") as f:
#     content = [" ".join(line.split(" ")[:2]) for line in f.readlines()]


# In[154]:

#converts list of fens to dataframe of the form:
# 'move info': MoveInfo Object, 'board': intermediate board rep, 'x': single keras/pybrain input, 
#'y': label, 1 for legal, 0 for illegal
#given a list of size n, output is m * (num_legal_per_board + num_illegal_per_board)
def fen2mlinput(fen_list, num_legal_per_board=5, num_illegal_per_board=5):

    df = pd.DataFrame([], columns=['move', 'piece_moved', 'piece_captured', 'preboard', 'postboard', 'x', 'y'])
    for fen in fen_list:
        try :
            iboard, to_move = fen2iboard(fen)
            #rotate if necessary
            iboard = rotate_iboard(iboard) if to_move == 'b' else iboard
            #generate n legal moves
            legal_moves = get_legal_moves(iboard)
            iboard = [a.swapcase() for a in iboard] if to_move == 'b' else iboard
            for i in range(0, num_legal_per_board) :
                if not (i < len(legal_moves) - 1):
                    break
                post_board = apply_move(iboard, legal_moves[i])
                new_legal = move2keras(iboard, legal_moves[i]) 
                moveinfo = MoveInfo(iboard, legal_moves[i])
                df = df.append(pd.DataFrame([[moveinfo.move, moveinfo.piece_moved, moveinfo.piece_captured, iboard, post_board, new_legal, 1]],                                            columns=['move', 'piece_moved', 'piece_captured', 'preboard', 'postboard', 'x', 'y']))
            #generate m illegal moves
            for i in range(0, num_illegal_per_board):
                next_move = gen_illegal_moves(iboard, legal_moves).next()
                if (type(next_move) is tuple): # will be none when it is out of legal moves
                    post_board = apply_move(iboard, next_move)
                    new_illegal = move2keras(iboard, next_move)
                    moveinfo = MoveInfo(iboard, legal_moves[i])
                    df = df.append(pd.DataFrame([[moveinfo.move, moveinfo.piece_moved, moveinfo.piece_captured, iboard, post_board, new_illegal, 0]],                                                columns=['move', 'piece_moved', 'piece_captured', 'preboard', 'postboard', 'x', 'y']))
        except IndexError:
            #print("index error")
            pass
            #dear coding gods: forgive me
    return df

#df = fen2mlinput(content[:5])#, num_legal_per_board=5, num_illegal_per_board=5)


# In[155]:

# with open("../data/2015-12-01-fen_sample") as f:
#     content = [" ".join(line.split(" ")[:2]) for line in f.readlines()]


# In[156]:

#df = fen2mlinput(content[:250])


# In[157]:

# df.head()


# In[133]:

#is_black[is_black['y'] == 1].head()


# In[134]:

#iboard_black = is_black.iloc[0,1]
#iboard_black


# In[135]:

#is_black.iloc[0,2]

