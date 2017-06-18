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
        self.associated_hands = {hand_nr : {'gains':0.0,'cards':"",'Initial state':0,'FLOP':0,'RIVER':0,'TURN':0}}
        self.gains = 0.0
        self.current_hand = hand_nr

    def add_hand_nr(self, hand_nr):
        self.current_hand = hand_nr
        self.associated_hands[self.current_hand] = {'gains':0.0,'cards':"",'Initial state':0,'FLOP':0,'RIVER':0,'TURN':0}
        
    def set_cards(self,cards):
        self.associated_hands[self.current_hand]['cards'] = cards
    
    def gain(self,amount):
        self.gains += amount
        self.associated_hands[self.current_hand]['gains'] += amount
        
    def bet(self,amount):
        self.gains -= amount
        self.associated_hands[self.current_hand]['gains'] -= amount  
    def calc_avg_gain(self):
        #associated hands can't be zero and players without association to any hand shouldn't be added
        return self.gains/len(self.associated_hands)
        
    def calc_activity(self):
        init = 0
        flop = 0
        turn = 0
        river = 0
        n_hands = len(self.associated_hands)
        for key in self.associated_hands.keys():
            init += self.associated_hands[key]['Initial state']
            flop += self.associated_hands[key]['FLOP']
            river += self.associated_hands[key]['RIVER']
            turn += self.associated_hands[key]['TURN']
            
        return (init/n_hands,flop/n_hands,turn/n_hands,river/n_hands)
    
    def actions(self,gamestate):
        #print("action: " + gamestate)
        self.associated_hands[self.current_hand][gamestate] = 1
    
class Card_proto:
    def __init__(self, cards, gains):
        self.cards = cards
        self.gains = gains
    def gain(self, gains):
        self.gains += gains
    
class cAction:
    def __init__(self, player, amount, action,gamestate):
        self.action = action
        self.gamestate = gamestate
        self.amount = amount
        self.player = player
          
	
class Player_action:
    active_actions = ['calls','raises','posts','Uncalled bet']
    passive_actions = ['folds','doesn\'t show hand']
    def __init__(self,action,amount):
        self.amount = amount
        self.action = action


def handle_logfile(logfile):
    global playerdb
    handle = open(logfile,'r')
    data = ""
    for line in handle:
        data += line
    re.MULTILINE = True
    for poker_round in re.split("\n\n\n\n",data):
        handle_round(poker_round)
    print_summary(logfile)

def print_summary(tablename):
    global playerdb
    def getKey(player):
        return player.name
    for player in sorted(playerdb,key=getKey):
        if player.name == "Velinektori":
            print(tablename.split("/")[-1])
            print("player "+player.name + " has gained: {0:.2f}, preflop_activity {1:.2f}, flop {2:.2f} turn: {3:.2f}, river {4:.2f},".format( player.gains, *player.calc_activity()))
            pairs = 0
            suitecards = 0
            pair_amount = 0
            suite_amount = 0
            for key in player.associated_hands.keys():
                hand_d = player.associated_hands[key]
                cards = hand_d['cards']
                
                for land in ["s","h","d","c"]:
                    if cards.count(land) > 1:
                        suite_amount += 1
                        
                        suitecards += hand_d['gains']

                valueregex = "([2-9ATKJQ9]).*([2-9ATKJQ])"
                valuematch = re.match(valueregex,cards)
                if valuematch:
                    #print(valuematch.groups())
                    if valuematch.group(1) == valuematch.group(2):
                        #print(valuematch.groups())
                        pair_amount += 1
                        pairs += hand_d['gains']
                #print("{0:.2f} {1}".format(card_data[0],card_data[1]))
            if pair_amount:
                print("pairs {0:.2f}".format(pairs/pair_amount))
                print("suite cards {0:.2f}".format(suitecards/suite_amount))
    playerdb = []
        
def handle_round(data):
    temp_hand = re.search("PokerStars Hand #(\d*):",data)
    data = data.replace("*** HOLE CARDS ***\n","")
    data = data.split("\n")
    gamestate = "Initial state"
    if temp_hand:
        hand_nr = temp_hand.group(1)
    else:
        return
    round_actions = []
    for line in data:
        player_match = re.match("(Seat [0-9]:) (.*) ([()])",line)
        gamestate_match = re.match("\*+ (.*) \*+",line)
        card_match = re.match("Dealt to (.*) \[([2-9ATJKQ][dhcs]) ([2-9ATJKQ][dhcs])\]",line)
        bet = bet_handler(line,gamestate)

        if player_match:
            player = player_match.group(2).strip()
            players = [x.name for x in playerdb]
            if player in players:
                playerdb[players.index(player)].add_hand_nr(hand_nr)
            else:
                playerdb.append(Player(player,hand_nr))        
        
        elif gamestate_match:    
            gamestate = gamestate_match.group(1)
            if gamestate == "SUMMARY":
                break
            #print(gamestate)
        elif bet:
            round_actions.append(bet)
        elif card_match:
            player, card1, card2 = card_match.groups()
            playerdb[players.index(player)].set_cards("{0} {1}".format(card1, card2))
            
    raises = ['raises','bets','posts']
    
    for action in round_actions:
        if action.action == 'raises':
            latest = len(round_actions)
            for action2 in round_actions[:round_actions.index(action)]:
                if action.player == action2.player and action.gamestate == action2.gamestate:
                    latest = round_actions.index(action2)
            for action2 in round_actions[latest:round_actions.index(action)]:
                if action2.action in raises and action.player == action2.player and action.gamestate == action2.gamestate:
                    action.amount -= action2.amount

        update_bet_status(action)


def bet_handler(line, gamestate):
    global playerdb
    if not line:
        #print("none")
        return None
        
    actregex = "(.*): (posts|bets|calls).*([€$£])([.0-9]*)"
    actmatch = re.match(actregex,line)
    player = None
    if actmatch:
        player,action,currency,amt_gained = actmatch.groups()
        amt_gained = -1*float(amt_gained)

    raiseregex = "(.*): (raises) ([€$£])([.0-9]*) to* [€$£]([.0-9]*)"
    raisematch = re.match(raiseregex,line)
    if raisematch:
        player,action,currency,bet_increase,amt_gained = raisematch.groups()
        amt_gained = -1*float(amt_gained)

    uncregex = "(Uncalled bet)[ (]*([€$£])([.0-9]*).*returned to (.*)"
    uncmatch = re.match(uncregex,line)
    if uncmatch:
        #print(uncmatch.groups())
        action,currency,amt_gained,player = uncmatch.groups()
        
    collregex = "(.+) (collected) ([€$£])([.0-9]*) from (side|main)*.*pot"
    collmatch = re.match(collregex,line)
    if collmatch:
        player,action,currency,amt_gained,side_or_main = collmatch.groups()

    if not player:
        return None
    #print(line)
    #print(amt_gained)
    return cAction(player,float(amt_gained),action,gamestate)
        
def update_bet_status(action):
    cplayer = playerdb[[x.name for x in playerdb].index(action.player)]
    cplayer.gain(action.amount)
    if action.action != "posts": 
        cplayer.actions(action.gamestate)

def main(argv):
    if len(argv) > 0:
        logfolder = argv[0]
    else:
        logfolder = None#r'C:/Programming/spyder/poker/pokerhands/'
        
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
