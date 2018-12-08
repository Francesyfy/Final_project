"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import TicTacToe as ttt
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.letter = ''
        self.theBoard = [' '] * 10

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def start_game(self, peer):
        msg = json.dumps({"action":"startgame", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            self.out_msg += 'Play Tic Tac Toe with ' + peer + '. Game start!\n\n'
            self.out_msg += '-----------------------------------\n'
            self.out_msg += 'You are ' + self.letter + '.\n'
            if response["turn"] == self.peer:
                self.out_msg += self.peer + ' goes first.\n'
            else:
                self.out_msg += 'You go first.\n'
            self.out_msg += ttt.drawBoard(self.theBoard)
            return (True)
        elif response["status"] == "chatting":
            self.out_msg += 'User is chatting with someone else. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot play game with yourself\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif my_msg[0] == 'g':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    #assign letter to each player
                    self.letter = 'X'
                    if self.start_game(peer) == True:
                        self.state = S_GAMING
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

                elif peer_msg["action"] == "startgame":
                    self.peer = peer_msg["from"]
                    self.letter = 'O'
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'Play Tic Tac Toe with ' + self.peer
                    self.out_msg += '. Game start!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.out_msg += 'You are ' + self.letter + '.\n'
                    if peer_msg["turn"] == self.peer:
                        self.out_msg += self.peer + ' goes first.\n'
                    else:
                        self.out_msg += 'You go first.\n'
                    self.out_msg += ttt.drawBoard(self.theBoard)
                    self.state = S_GAMING
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''

            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu

#==============================================================================
# gaming state
#==============================================================================
        elif self.state == S_GAMING:  
            if len(my_msg) > 0:   #make move
                if my_msg in '1 2 3 4 5 6 7 8 9'.split() and ttt.isSpaceFree(self.theBoard, int(my_msg)):
                    move = int(my_msg)
                    ttt.makeMove(self.theBoard, self.letter, move)
                    self.out_msg += ttt.drawBoard(self.theBoard)
                else:
                    self.out_msg += "What is your move? (1-9)\n"
                mysend(self.s, json.dumps({"action":"game", "from": self.peer, "board": self.theBoard}))

            if len(peer_msg) > 0:  #receive and print the updated board
                peer_msg = json.loads(peer_msg)
                self.theBoard = peer_msg["board"]
                self.out_msg += "You are " + self.letter + "\n"
                self.out_msg += ttt.drawBoard(self.theBoard)
                self.out_msg += "What is your move? (1-9)\n"
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
