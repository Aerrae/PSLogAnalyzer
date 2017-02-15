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
        
    def calc_activity(self):
        return self.preflop_actions/len(self.associated_hands)
    
    def calc_flop_activity(self):
        return self.reached_flop/len(self.associated_hands)
        
    def calc_turn_activity(self):
        return self.reached_turn/len(self.associated_hands)
        
    def calc_river_activity(self):
        return self.reached_river/len(self.associated_hands)
        
    
    def actions(self,gamestate):
        #print("action: " + gamestate)
        if "Initial state" in gamestate:
            #print("adding init state")
            self.preflop_actions += 1
        elif "FLOP" in gamestate:
            #print("flop")
            self.reached_flop += 1
        elif "TURN" in gamestate:
            #print("turn")
            self.reached_turn += 1
        elif "RIVER" in gamestate:
            #print("river")
            self.reached_river += 1
        
    
    


class Player_action:
    active_actions = ['calls','raises','posts','Uncalled bet']
    passive_actions = ['folds','doesn\'t show hand']
    def __init__(self,action,amount):
        self.amount = amount
        self.action = action
    
#class Poker_hand:
#    def __init__(self,hand_nr,preflop,flop,turn,river):
#        self.hand_nr = hand_nr


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
    pattern = ".*[*]+.*.*[*]+"
    for data2 in data:
        data2 = data2.replace("*** HOLE CARDS ***","")
        hand = re.split(pattern,data2)
        dataheaders = ["*** Initial state ***"]
        dataheaders.extend(re.findall(pattern,data2))
        for line in hand:
            if line:
                1+1
                #print(line.strip())
        for splitted in zip(hand,dataheaders):
            gamestates = ["*** Initial state ***","*** FLOP ***","*** TURN ***","*** RIVER ***","*** SHOW DOWN ***", "*** SUMMARY ***"]
            gamestatefunc = [handle_initial_state]+ [handle_postflop]*4+[handle_summary]
            
            if splitted[1] in gamestates:
                #print(splitted[1])
                #print(gamestatefunc[gamestates.index(splitted[1])].__name__)
                
                gamestatefunc[gamestates.index(splitted[1])](splitted[0],gamestates[gamestates.index(splitted[1])])
    
    def getKey(player):
        return player.name
    for player in sorted(playerdb,key=getKey):
        print("player "+player.name + " has gained: {0:.2f}, preflop_activity {1:.2f}, flop {2:.2f} turn: {3:.2f}, river {4:.2f},".format( player.gains, player.calc_activity(), \
        player.calc_flop_activity(),player.calc_turn_activity(),player.calc_river_activity()))   
        
def handle_initial_state(data, gamestate):
    global playerdb
    list_data = data.split('\n')
    temp_hand = re.search("PokerStars Hand #(\d*)",list_data[0])
    
    hand_nr = temp_hand.group(1)
    for line in list_data:
        if line.startswith('Seat'):
            player = line.split()[2].strip()
            players = [x.name for x in playerdb]
            if player in players:
                playerdb[players.index(player)].add_hand_nr(hand_nr)
            else:
                playerdb.append(Player(player,hand_nr))
    handle_round(list_data[1:], gamestate)

def handle_postflop(data, gamestate):
    hand = data.split('\n')
    cards = re.findall("([0-9ATJQK]+[cdhs])",hand[0])
    if len(hand) > 1:
        handle_round(hand[1:], gamestate)
           
        
def handle_round(data, gamestate):
    #print(gamestate)
    round_actions = []
    for line in data:
        bet = bet_handler(line)
        if bet:
            round_actions.append(bet)
    raises = ['raises','bets','posts']
    #print(round_actions)
    for action in round_actions:
        if action[2] == 'raises':
            latest = len(round_actions)
            for action2 in round_actions[:round_actions.index(action)]:
                if action[0] == action2[0]:
                    latest = round_actions.index(action2)
            current_pot = 0
            for action2 in round_actions[latest:round_actions.index(action)]:
                if action2[2] in raises and action[0] == action2[0]:
                    current_pot += action2[1]
            update_bet_status(action[0],action[1]-current_pot)
        else:
            update_bet_status(action[0],action[1])
        
        
    active_players = set([x[0] for x in round_actions if x[2] != 'posts'])
    #print(active_players)
    for player in active_players:
        playerdb[[x.name for x in playerdb].index(player)].actions(gamestate)
            
def handle_showdown(data, gamestate):
    hand = data.split('\n')
    if len(hand) > 1:
        handle_round(hand[1:], gamestate)

def handle_summary(data, gamestate):
    """no longer required"""
    player_idx = 2
    reward_idx = -1
    hand = data.split('\n')   

def bet_handler(line):
    global playerdb
    line = line.split()
    sign = -1
    #print(line)
    if not line:
        #print("none")
        return None
    
    if "collected" in line[1]:
        player_idx = 0
        reward_idx = 2
        sign = 1
        action = "collected"
        
    elif "Uncalled" in line[0] and "bet" in line[1]:
        player_idx = -1
        reward_idx = 2
        sign = 1
        line[2] = line[2][1:-1]
        action = "Uncalled bet"
    elif "posts" in line[1]:
        player_idx = 0
        reward_idx = -1
        action = "posts"
    elif line[1].strip() in ["bets","calls"]:
        player_idx = 0
        reward_idx = 2
        action = line[1].strip()
    elif line[1].strip() in ['raises']:
        player_idx = 0
        reward_idx = 4
        action = line[1].strip()
    else:
        #print("none")
        return None
        
    player = line[player_idx].strip().replace(":","")
    amt_gained = sign*float(line[reward_idx][1:])
    
    return (player,amt_gained,action)
        
def update_bet_status(player,amt_gained):
    
    playerdb[[x.name for x in playerdb].index(player)].gain(amt_gained)
    #print("player "+player+" gained: % .2f" %( amt_gained))

def main(argv):
    if len(argv) > 0:
        logfolder = argv[0]
    else:
        logfolder = None #r'C:/Users/Aerrae/AppData/Local/PokerStars.EU/HandHistory/Velinektori/'
        
    if not logfolder:
        print("No logfolder given, please edit the file or add as argument")
        print("Usage: python pokertest.py logfolder")
        sys.exit()

    list_of_files = os.listdir(logfolder)
    #list_of_files = ['C:/Users/Aerrae/Desktop/HH20170202 Claudia III - $0.01-$0.02 - USD No Limit Hold'"'"'em.txt']
    for logfile in list_of_files:
        handle_logfile(logfolder +logfile)#logfile)
        
        
        
if __name__ == "__main__":
    main(sys.argv[1:])