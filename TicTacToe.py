
import random

def drawBoard(board):
    # This function draws the board that it was passed.
    # "board" is a list of 10 strings representing the board (ignore index 0)
    theBoard = '   |   |\n' +\
    ' ' + board[7] + ' | ' + board[8] + ' | ' + board[9] + '\n' +\
    '   |   |\n' +\
    '-----------\n' +\
    '   |   |\n' +\
    ' ' + board[4] + ' | ' + board[5] + ' | ' + board[6] + '\n' +\
    '   |   |\n' +\
    '-----------\n' +\
    '   |   |\n' +\
    ' ' + board[1] + ' | ' + board[2] + ' | ' + board[3] + '\n' +\
    '   |   |\n' 
    return theBoard

def whoGoesFirst(me, peer):
    # Randomly choose the player who goes first.
    if random.randint(0, 1) == 0:
        return me
    else:
        return peer

def makeMove(board, letter, move):
    # Make move by changing the element in the list.
    board[move] = letter

def isSpaceFree(board, move):
    # Return true if the passed move is free on the passed board.
    return board[move] == ' '

def isWinner(bo, le):
    # Given a board and a player’s letter, this function returns True if that player has won.
    # We use bo instead of board and le instead of letter so we don’t have to type as much.
    return ((bo[7] == le and bo[8] == le and bo[9] == le) or  # across the top
            (bo[4] == le and bo[5] == le and bo[6] == le) or  # across the middle
            (bo[1] == le and bo[2] == le and bo[3] == le) or  # across the bottom
            (bo[7] == le and bo[4] == le and bo[1] == le) or  # down the left side
            (bo[8] == le and bo[5] == le and bo[2] == le) or  # down the middle
            (bo[9] == le and bo[6] == le and bo[3] == le) or  # down the right side
            (bo[7] == le and bo[5] == le and bo[3] == le) or  # diagonal
            (bo[9] == le and bo[5] == le and bo[1] == le))  # diagonal

def isBoardFull(board):
    # Return True if every space on the board has been taken. Otherwise return False.
    for i in range(1, 10):
        if isSpaceFree(board, i):
            return False
    return True