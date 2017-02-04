# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:25:34 2017

@author: Aerrae
"""


import os
import re
import sys


playerdb = []


class Player():
    def __init__(self,player_name,hand_nr):
        self.name = player_name
        self.associated_hands = [hand_nr]
        self.gains = 0.0
        
        #takes into account only the first preflop action
        self.preflop_actions = 0
        self.reached_flop = 0
        self.reached_turn = 0
        self.reached_river = 0
    def add_hand_nr(self, hand_nr):        
        self.associated_hands.append(hand_nr)
        
    def gain(self,amount):
        self.gains += amount
        
    def bet(self,amount):
        self.gains -= amount
        
    def calc_avg_gain(self):
        #associated hands can't be zero and players without association to any hand shouldn't be added
        return self.gains/len(self.associated_hands)
        
    def calc_activitiy(self):
        return self.preflop_actions/len(self.associated_hands)
    


class Player_actions:
    actions = ['folds','calls','raises','posts','doesn\'t show hand','Uncalled bet']
    def __init__(self,action,amount):
        self.amount = amount
        self.action = action
    



class Poker_hand:
    def __init__(self,hand_nr,preflop,flop,turn,river):
        self.hand_nr = hand_nr
        self.preflop = Preflop(preflop)
        self.flop = Flop(flop)
        self.turn = Turn(turn)
        self.river = River(river)
class Turn:
    def __init__(self,cards):
        self.cards = cards

class Flop:
    def __init__(self,cards):
        self.cards = cards

class River:
    def __init__(self,cards):
        self.cards = cards
        
class Preflop:
    def __init__(self, cards):
        self.cards = cards


def handle_logfile(logfile):

    global playerdb
    handle = open(logfile,'r')
    hand_nr = 0
    count = 0
    data = []
    for line in handle:
        if "PokerStars Hand #" in line:
            hand_nr = line[line.index('#')+1:line.index(':')]
            count += 1
            data.append("")
        data[count-1] += line
    re.MULTILINE = True
    re.DOTALL = True
    print(count)
    pattern = ".*[*]+.*.*[*]+"
    dataheaders = ["*** Initial state ***"]
    dataheaders.extend(re.findall(pattern,data[1]))
    #print(data)
    
    #zip for convenience, room for optimization
    
    for data2 in data:
        hand = re.split(pattern,data2)
        #print(hand)
        for splitted in zip(hand,dataheaders):
        #    print(splitted)
            lista = ["*** Initial state ***","*** HOLE CARDS ***","*** FLOP ***","*** TURN ***","*** RIVER ***","*** SHOW DOWN ***", "*** SUMMARY ***"]
            gamestatefunc = [handle_initial_state,handle_hole_cards, handle_flop, handle_turn, handle_river, handle_showdown,handle_summary]
            if "SHOW" in splitted[1]:
                print(splitted[1])
            if splitted[1] in lista:
                print(splitted[1])
                gamestatefunc[lista.index(splitted[1])](splitted[0])
            #if "SUMMARY" in splitted[1]:
                
            #elif  in splitted[1]:
                
    for player in playerdb:
        print(player.calc_avg_gain())
            
def handle_initial_state(data):
    #print(data)
    global playerdb
    list_data = data.split('\n')
    #first line contains hand nr
    hand_nr = list_data[0][list_data[0].index('#')+1:list_data[0].index(':')]
    for line in list_data:
        if line.startswith('Seat'):
            
            player = line.split()[2].strip()
            players = [x.name for x in playerdb]
            if player in players:
                playerdb[players.index(player)].add_hand_nr(hand_nr)
            else:
                print("new player " + player + " added")
                playerdb.append(Player(player,hand_nr))
                
                
                
def handle_hole_cards(data):
    hand = data.split('\n')
    #print("holecard handler")
    for line in hand:
        if line.startswith("Dealt to "):
            
            dealthand = line[-6:-1].split()
            #print(dealthand)
        
    
    
def handle_flop(data):
    """Assumes first line contains flop cards as is in the logfile"""
    hand = data.split('\n')
    
    cards = hand[0].strip()[1:-1].split()
    #print(cards)
    #print("flophandler")
    
def handle_turn(data):
    """Assumes first line contains turn cards as is in the logfile, takes only the card added"""
    hand = data.split('\n')
    cards = hand[0].strip()[-3:-1].split()
    #print(cards)
    #print("turnhandler")
    
def handle_river(data):
    """Assumes first line contains river cards as is in the logfile, takes only the card added"""
    hand = data.split('\n')
    cards = hand[0].strip()[-3:-1].split()
    #print(cards)
    #print("riverhandler")            

def handle_showdown(data):
    global playerdb
    print("showdown")
    player_idx = 2
    reward_idx = -3
    hand = data.split('\n')
    for line in hand:
        if 'collected' in line:
            print(line.split())
            print(line.split()[reward_idx])
            player = line.split()[player_idx].strip()
            amt_gained = float(line.split()[reward_idx][2:-1])
            print(playerdb[[x.name for x in playerdb].index(player)].name)
            playerdb[[x.name for x in playerdb].index(player)].gain(amt_gained)
            print(playerdb[[x.name for x in playerdb].index(player)].gains)
            print("player "+line.split()[player_idx]+" gained: " +str(amt_gained))

def handle_summary(data):
    player_idx = 2
    reward_idx = -1
    hand = data.split('\n')
    
    #print("summaryhandler")
    for line in hand:
        if "Seat" in line:
            player = line.split()[2]
            #print(player)
            if 'collected' in line:
                amt_gained = float(line.split()[reward_idx][2:-1])
                playerdb[[x.name for x in playerdb].index(player)].gain(amt_gained)
                print("player "+line.split()[player_idx]+" gained: " +str(amt_gained))
        elif "Board" in line:
            cards = line[line.index('[')+1:-1].split()
            print(cards)
                

def handle_show_down():
    print('show_down')


def main(argv):
    if len(argv) > 0:
        logfolder = argv[0]
    else:
        logfolder = r'C:/Users/Aerrae/AppData/Local/PokerStars.EU/HandHistory/Velinektori/'
    #print(data[1])        
            

    #
    
    list_of_files = os.listdir(logfolder)
    for logfile in list_of_files:
        handle_logfile(logfolder+logfile)
        
        
if __name__ == "__main__":
    main(sys.argv[1:])