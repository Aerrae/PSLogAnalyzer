# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:25:34 2017

@author: Aerrae
"""

class poker_hand:
    def __init__(self,hand_nr,preflop,flop,turn,river):
        self.hand_nr = hand_nr
        self.preflop = preflop
        self.flop = flop
        self.turn = turn
        self.river = river
class turn:
    def __init__(self,cards):
        self.cards = cards

class flop:
    def __init__(self,cards):
        self.cards = cards

class river:
    def __init__(self,cards):
        self.cards = cards
        
class preflop:
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
        if "SUMMARY" in splitted[1]:
            hand = splitted[0].split('\n')
            for line in hand:
                if "Seat" in line:
                    player = line.split()[2]
                    print(player)
                    if 'collected' in line:
                        gain = float(line.split()[-1][2:-1])
                        print(line.split()[-1])
                        print(gain)
                    
    

    
    #print(data[1])        
        
import os
import re
logfolder = r'C:/Users/Aerrae/AppData/Local/PokerStars.EU/HandHistory/Velinektori/'

list_of_files = os.listdir(logfolder)
for logfile in list_of_files:
    handle_logfile(logfolder+logfile)
    
    

