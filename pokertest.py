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
        self.associated_hands = {hand_nr : [0.0,""]}
        self.gains = 0.0
        self.current_hand = hand_nr
        #takes into account only the first preflop action
        self.preflop_actions = 0
        self.reached_flop = 0
        self.reached_turn = 0
        self.reached_river = 0
    def add_hand_nr(self, hand_nr):
        self.current_hand = hand_nr
        #print(hand_nr)
        #self.associated_hands.append(hand_nr)
        self.associated_hands[self.current_hand] = [0.0,""]
        
    def set_cards(self,cards):
        self.associated_hands[self.current_hand][1] = cards
    
        
    def gain(self,amount):
        self.gains += amount
        self.associated_hands[self.current_hand][0] += amount
        
    def bet(self,amount):
        self.gains -= amount
        self.associated_hands[self.current_hand][0] -= amount  
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
        
    
class Card_proto:
    def __init__(self, cards, gains):
        self.cards = cards
        self.gains = gains
    def gain(self, gains):
        self.gains += gains
    


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
        if player.name == "Velinektori":
            print(logfile.split("/")[-1])
            print("player "+player.name + " has gained: {0:.2f}, preflop_activity {1:.2f}, flop {2:.2f} turn: {3:.2f}, river {4:.2f},".format( player.gains, player.calc_activity(), \
            player.calc_flop_activity(),player.calc_turn_activity(),player.calc_river_activity()))
            pairs = 0
            suitecards = 0
            pair_amount = 0
            suite_amount = 0
            for key in player.associated_hands.keys():
                card_data = player.associated_hands[key]
                cards = card_data[1]
                for land in ["s","h","d","c"]:
                    if cards.count(land) > 1:
                        suite_amount += 1
                        
                        suitecards += card_data[0]

                valueregex = "([2-9ATKJQ9]).*([2-9ATKJQ])"
                valuematch = re.match(valueregex,cards)
                if valuematch:
                    #print(valuematch.groups())
                    if valuematch.group(1) == valuematch.group(2):
                        #print(valuematch.groups())
                        pair_amount += 1
                        pairs += card_data[0]
                #print("{0:.2f} {1}".format(card_data[0],card_data[1]))
            if pair_amount:
                print("pairs {0:.2f}".format(pairs/pair_amount))
                print("suite cards {0:.2f}".format(suitecards/suite_amount))
    #playerdb = []
        
def handle_initial_state(data, gamestate):
    #print(data)
    global playerdb
    list_data = data.split('\n')
    temp_hand = re.search("PokerStars Hand #(\d*)",list_data[0])
    
    hand_nr = temp_hand.group(1)
    card_regex = "Dealt to (.*) \[([2-9ATJKQ][dhcs]) ([2-9ATJKQ][dhcs])\]"
    for line in list_data:
        if line.startswith('Seat'):
            player = re.match("(Seat [0-9]:) (.*) ([()])",line).group(2).strip()
            #player = line.split()[2].strip()
            players = [x.name for x in playerdb]
            if player in players:
                playerdb[players.index(player)].add_hand_nr(hand_nr)
            else:
                playerdb.append(Player(player,hand_nr))
        card_match = re.match(card_regex,line)
        if card_match:
            player, card1, card2 = card_match.groups()
            playerdb[players.index(player)].set_cards("{0} {1}".format(card1, card2))
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
    return (player,float(amt_gained),action)
        
def update_bet_status(player,amt_gained):
    playerdb[[x.name for x in playerdb].index(player)].gain(amt_gained)
    #print("player "+player+" gained: % .2f" %( amt_gained))

def main(argv):
    if len(argv) > 0:
        logfolder = argv[0]
    else:
        logfolder = r'C:/Programming/spyder/poker/pokerhands/'
        
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
