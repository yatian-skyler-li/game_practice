
"""
Chess Game
Assignment 1
Semester 2, 2021
CSSE1001/CSSE7030
"""

from typing import Optional, Tuple

from chess_support import *

__author__ = "Yatian Li, 46059145"
__email__ = "yatian.li@uqconnect.edu.au"

def initial_state() -> Board:
    """(Board) Returns the board state for a new game"""
    black_piece_line = ''.join(BLACK_PIECES[0:BOARD_SIZE])
    white_piece_line = ''.join(WHITE_PIECES[0:BOARD_SIZE])
    board = (black_piece_line, BLACK_PAWN*BOARD_SIZE, EMPTY*BOARD_SIZE,
             EMPTY*BOARD_SIZE, EMPTY*BOARD_SIZE, EMPTY*BOARD_SIZE,
             WHITE_PAWN*BOARD_SIZE, white_piece_line)
    return board

def print_board(board: Board) -> None:
    """Print a human-readable chess board.

    Parameters:
        board (Board): The current board state.
    """ 
    for i, piece in enumerate(board):
        print(piece, BOARD_SIZE - i, sep="  ")
        
    print("\nabcdefgh")  
    return None

def square_to_position(square: str) -> Position:
    """Convert chess notation to its position.

    Parameters:
        square (str): The chess notation of a piece

    Returns:
        (Position): The position of the chess piece.
    """
    for notation in square:
        if notation == 'a':
            col = 0
        elif notation == 'b':
            col = 1
        elif notation == 'c':
            col = 2
        elif notation == 'd':
            col = 3
        elif notation == 'e':
            col = 4
        elif notation == 'f':
            col = 5
        elif notation == 'g':
            col = 6
        elif notation == 'h':
            col = 7
        elif notation.isdigit():
            row = BOARD_SIZE - int(notation)
            
    position = (row, col)
    return position 

def process_move(user_input: str) -> Move:
    """Assume the user_input is valid and convert user input to a move
        based on position.

    Parameters:
        user_input (str): Origin chess notation and destination chess notation.
    
    Returns:
        (Move): A move based on (row, col): Position
    """
    origin_square, dest_square = user_input.split(' ')
    origin = square_to_position(origin_square)
    destination = square_to_position(dest_square)
    move = (origin, destination)
    return move

def change_position(board: Board, position: Position, piece: str) -> Board:
    """Return a copy of board with the character at position changed to
        character.
        
    Parameters:
        board (Board): The current board state.
        position (Position): The (row, col) position that will be changed.
        piece (str): The changed new character at position.

    Returns:
        (Board): The board state after changing character at position.     
    """
    row, col = position
    
    board_row = board[row]
    board_row_update = board_row[:col] + piece + board_row[col+1:]
    board = list(board)
    board[row] = board_row_update
    board = tuple(board)
    return board

def clear_position(board: Board, position: Position) -> Board:
    """Clear the piece at position (i.e. replace with an empty square) and
        return the resulting board. The board will remain unchanged when there
        is no piece at this position.
        
    Parameters:
        board (Board): The current board state.
        position (Position): The (row, col) position that will be cleared.

    Returns:
        (Board): The board state after clearing the piece at position.
    """
    if not piece_at_position(position, board):
        return board
    
    board = change_position(board, position, EMPTY)
    return board

def update_board(board: Board, move: Move) -> Board:
    """Assume the move is valid and return an updated version of the board
        with the move made.

    Parameters:
        board (Board): The current board state.
        move (Move): move the piece at origin position to the destination.

    Returns:
        (Board): The updated board state after the move.
    """
    origin, destination = move
    
    piece = piece_at_position(origin, board)
    board = change_position(board, destination, piece)
    board = clear_position(board, origin)
    
    return board
  
def is_current_players_piece(piece: str, whites_turn: bool) -> bool:
    """Returns true only when piece is belongs to the player whose turn it is.

    Parameters:
        piece (str): The character we are looking for.
        whites_turn (bool): True iff it's white's turn.

    Returns:
        (bool): True only when piece is belongs to the player whose turn it is.
    """
    if piece in WHITE_PIECES and whites_turn:
        return True
    elif piece in BLACK_PIECES and not whites_turn:
        return True
    
    return False

def is_move_valid(move: Move, board: Board, whites_turn: bool) -> bool:
    """Returns true only when the move is valid on the current board state for
        the player whose turn it is.

    Parameters:
        move (Move): The move from origin position to destination to be checked.
        board (Board): The current board state.
        whites_turn (bool): True iff it's white's turn.

    Returns:
        (bool): True only when the move is valid on the current board state for
                       the player whose turn it is.
    """
    origin, destination = move
    piece = piece_at_position(origin, board)
    
    #Check conditions that make the move invalid
    if out_of_bounds(origin) and out_of_bounds(destination):
        return False
    elif origin == destination:
        return False
    elif not is_current_players_piece(piece, whites_turn):
        return False
    #The move is not valid for the type of piece being moved
    elif destination not in get_possible_moves(origin, board):
        return False
    elif is_in_check(update_board(board, move), whites_turn):
        return False
    #The square the piece is being moved to contains the same color
    elif whites_turn:
        if piece_at_position(destination, board) in WHITE_PIECES:
            return False
    elif not whites_turn:
        if piece_at_position(destination, board) in BLACK_PIECES:
            return False
        
    return True

def can_move(board: Board, whites_turn: bool) -> bool:
    """Returns true only when the player can make a valid move which does not
        put them in check.
        
    Parameters:
        board (Board): The current board state.
        whites_turn (bool): True iff it's white's turn.
        
    Returns:
        (bool): True only when the player can make a valid move which does not
                       put them in check.
    """
    for board_line in board:
        #The origin positions of current player's pieces
        for piece in board_line:
            if is_current_players_piece(piece, whites_turn):
                origin = find_piece(piece, board)

                #Check valid move for the pieces
                for destination in get_possible_moves(origin, board):
                    move = (origin, destination)
                    if is_move_valid(move, board, whites_turn):
                        return True           
    return False 
                    
def is_stalemate(board: Board, whites_turn: bool) -> bool:
    """Returns true only when a stalemate has been reached. A stalemate occurs
        when the player who is about to move isn’t currently in check but can’t
        make any moves without putting themselves in check.

    Parameters:
        board (Board): The current board state.
        whites_turn (bool): True iff it's white's turn.

    Returns:
        (bool): True only when a stalemate has been reached.
    """
    
    #return not is_in_check(board, whites_turn) and not can_move(board, whites_turn)
    if not is_in_check(board, whites_turn):
        #return not can_move(board, whites_turn)
        if not can_move(board, whites_turn):
            return True
        
    return False

def is_checkmate(board: Board, whites_turn: bool) -> bool:
    """Returns true only when a checkmate has been reached. A 'checkmate'
        occurs when the player is in check and can’t make any valid moves to
        escape check. If the player is in check and can make a valid move,
        print "Player's turn is in check". e.g. "White is in check"

    Parameters:
        board (Board): The current board state.
        whites_turn (bool): True iff it's white's turn.

    Returns:
        (bool): True only when a checkmate has been reached.
    """
    if is_in_check(board, whites_turn):
        if not can_move(board, whites_turn):
            return True        
        if whites_turn:
            print("\nWhite is in check")
        else:
            print("\nBlack is in check")
       
    return False

def check_game_over(board: Board, whites_turn: bool) -> bool:
    """Returns true only when the game is over (either due to checkmate or
        stalemate).

    Parameters:
        board (Board): The current board state.
        whites_turn (bool): True iff it's white's turn.

    Returns:
        (bool): Ture only when the game is over.
    """
    if is_stalemate(board, whites_turn):
        print("\nStalemate")
        return True
    if is_checkmate(board, whites_turn):
        print("\nCheckmate")
        return True
    
    return False            
         
def main():
    """Entry point to gameplay"""  
    board = initial_state()
    i = 0
    whites_turn = True

    #Game Play
    while True:
        print_board(board)
        
        if check_game_over(board, whites_turn): 
            break

        #Current Player
        if whites_turn:
            user_input = input("\nWhite's move: ")
        else:
            user_input = input("\nBlack's move: ")
            
        #Check Help    
        if user_input == 'h' or user_input == 'H': 
            print(HELP_MESSAGE)

        #Check Quit  
        elif user_input == 'q' or user_input == 'Q':  
            response = input("Are you sure you want to quit? ")
            if response == 'y' or response == 'Y':
                break
            
        #Check invalid move        
        elif not valid_move_format(user_input): 
            print("Invalid move\n")
       
        elif not is_move_valid(process_move(user_input), board, whites_turn):
            print("Invalid move\n")
            
        #Normal valid move
        else:  
            board = update_board(board, process_move(user_input))
            i += 1
            if i % 2 == 0:
                whites_turn = True
            else:
                whites_turn = False
            
if __name__ == "__main__":
    main()

lineone \
        or linetwo
