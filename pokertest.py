# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:25:34 2017

@author: Aerrae
"""


import os
import re
import sys


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
    pattern = ".*[*]+.*[*]+"
    dataheaders = ["*** Initial state ***"]
    dataheaders.extend(re.findall(pattern,data[1]))
    data2 = re.split(pattern,data[1])
    
    for splitted in zip(data2,dataheaders):
        #print(splitted[1])
        #print(splitted[0])
        lista = ["*** HOLE CARDS ***","*** FLOP ***","*** TURN ***","*** RIVER ***", "*** SUMMARY ***"]
        gamestatefunc = [hand_hole_cards,hand_flop,hand_turn,hand_river,hand_summary]
        if splitted[1] in lista:
            print("moro")
            print(splitted[1])
            gamestatefunc[lista.index(splitted[1])](splitted[0])
        #if "SUMMARY" in splitted[1]:
            
        #elif  in splitted[1]:
            
def hand_summary(data):
    
    hand = data.split('\n')
    print("summaryhandler")
    for line in hand:
        if "Seat" in line:
            player = line.split()[2]
            print(player)
            if 'collected' in line:
                gain = float(line.split()[-1][2:-1])
                print(line.split()[-1])
                print(gain)
                
def hand_hole_cards(data):
    print("holecard handler")
    
def hand_flop(data):
    print("flophandler")
    
def hand_turn(data):
    print("turnhandler")
    
def hand_river(data):
    print("riverhandler")            


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