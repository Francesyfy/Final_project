
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