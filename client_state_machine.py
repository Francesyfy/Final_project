"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import TicTacToe as ttt
import json
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        msg = base64.b64encode(iv + cipher.encrypt(raw))
        return str(msg)[1:]

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

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

    def quit_game(self):
        msg = json.dumps({"action":"quitgame"})
        mysend(self.s, msg)
        self.peer = ''

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
                my_msg_secret = AESCipher("2333").encrypt(my_msg)
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg_secret}))
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
                    peer_msg["message"] = AESCipher("2333").decrypt(peer_msg["message"])
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
                #check if game ends
                #someone wins the game
                if ttt.isWinner(self.theBoard, self.letter):
                    self.out_msg += 'You have won the game!'
                    mysend(self.s, json.dumps({"action":"endgame", "result":"lose", "from": self.peer, "board": self.theBoard}))
                    self.quit_game()
                    self.theBoard = [' '] * 10
                    self.state = S_LOGGEDIN
                else:
                    #if the game is a tie
                    if ttt.isBoardFull(self.theBoard):
                        self.out_msg += 'The game is a tie!'
                        mysend(self.s, json.dumps({"action":"endgame", "result":"tie", "from": self.peer, "board": self.theBoard}))
                        self.quit_game()
                        self.theBoard = [' '] * 10
                        self.state = S_LOGGEDIN
                    #game continues
                    else:
                        mysend(self.s, json.dumps({"action":"game", "from": self.peer, "board": self.theBoard}))

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                #receive and print the updated board
                self.theBoard = peer_msg["board"]
                #game result
                if peer_msg["action"] == "endgame":
                    if peer_msg["result"] == "lose":
                        self.out_msg += 'Oops, you lost the game.'
                    elif peer_msg["result"] == "tie":
                        self.out_msg += 'The game is a tie!'
                    self.theBoard = [' '] * 10
                    self.state = S_LOGGEDIN
                #game continues
                else:
                    self.out_msg += "You are " + self.letter + "\n"
                    self.out_msg += ttt.drawBoard(self.theBoard)
                    self.out_msg += "What is your move? (1-9)\n"

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
