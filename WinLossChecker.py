# coding: utf-8
#---------------------------------------------------------------------------#
#  Checks that the Grand Slam singles performance of                        #
#  professional tennis players on Wikipedia matches their win/loss ratios.  #                               #
#---------------------------------------------------------------------------#

import re
from numpy import *

OUTCOME = ['1R', '2R', '3R', '4R', 'QF', 'SF', 'F', 'W']
wins = dict(zip(OUTCOME, range(0,8))) # Gives num of wins for round attained

#------------------------------------------#
#  Setup the Singles Performance wiki-text #
#------------------------------------------#

Singles_Performance = haase
Singles_Performance_List = Singles_Performance.split('\n')

# Sometimes the tables extend to include performance in other tourneys
# The following will eliminate the wiki-text relating to those subsequent tables
if Singles_Performance.find('style=text-align:left|Win') > 0:
    end = Singles_Performance.find('style=text-align:left|Win')
    Singles_Performance = Singles_Performance[:end]

#--------------------#
#  Helper Functions  #
#--------------------#

def trailing_zeroes(flt, AfterDecimalDigits = 0):
    """ Given a float and a number of digits to show after the decimal,
    return float as a string with the correct # of digits after the decimal"""
    i = 0
    for char in str(flt)[::-1]:
        if char == '.':
            break
        else:
            i += 1
    return(str(flt) + '0' * (AfterDecimalDigits - i))

#--------------------------------------------------------------------------#
#  The following functions work together to construct the win-loss record  #
#--------------------------------------------------------------------------#

def total_wins(li):
    """ Given a list of rounds, return the total number of wins"""
    W = 0
    for stage in li:
        if stage not in wins.keys():
            continue
        W += wins[stage]
    return(W)

def total_losses(li):
    """ Given a list of rounds, return slam losses"""
    L = 0
    for stage in li:
        if stage != 'W' and stage in OUTCOME:
            L += 1
    return(L)

def slam_wins(li):
    """ Given a list of rounds, return slam wins"""
    W = 0
    for stage in li:
        if stage == 'W':
            W += 1
    return(W)

def win_loss(li):
    """ Given a list of rounds, return win-loss record"""
    WL = str(total_wins(li)) + '–' + str(total_losses(li))
    return(WL)

def win_loss_pct(li):
    """ Given a list of rounds, return win and loss percentage"""
    WL = total_wins(li) / (float(total_wins(li)) + total_losses(li))
    WL = round(WL * 100, 2)
    return(trailing_zeroes(WL,2))

def slam_win_rec(li):
    """ Given a list of rounds, return slam win-loss record"""
    W = 0
    total = 0
    for stage in li:
        if stage == 'W':
            W += 1
        if stage in OUTCOME:
            total += 1
    slamRec = str(W) + ' / ' + str(total)
    return(slamRec)
    

#----------------------------------#
#  Build list of slam performance  #
#----------------------------------#

# The round performance (3R, SF, F, W, etc..) is always the display text
# of a wiki-link for the individual slam's wiki article.
# For example, a 3R finish in the 2009 Australian Open will be displayed as:
# [[2009 Australian Open - Men's Singles|3R]]

# Builds a list of all instances of display texts of specific slam wiki-links
perf = re.findall(r"\n\|([A-Z]\w*)|– Men\'s Singles\|\'*([^\]]+)",
                  Singles_Performance)
performance = []
for tup in perf:
    for string in tup:
        if string:
            performance.append(string)
del perf

# Unfortunately, some display text is NOT the round performance,
# so remove all display text with more than 2 characters here:
# (should get rid of all our problems)
i = 0
while i < len(performance):
    if len(performance[i]) > 2:
        performance.remove(performance[i])
    else:
        i += 1
del i

# Add in empty strings for yet to be played slams in current year
if len(performance) % 4:
    UNPLAYED = 4 - len(performance) % 4
else:
    UNPLAYED = 0
i = 0
while i < UNPLAYED:
    performance.append('')
    i += 1
del i

#--------------------------------#
#  Build arrays of performances  #
#--------------------------------#

# This is the grand slam performance table we can visually see on Wikipedia
perf_slam_array = array(performance).reshape(4,len(performance)/4)

perf_year_array = perf_slam_array.transpose()
    
#---------------------------------------------------------------#
#  Extract win/loss performance for each slam (AO, RG, W, USO)  #
#---------------------------------------------------------------#

slam_WL = []
for arr in perf_slam_array:
    slam_WL.append(win_loss(list(arr)))

year_WL = []
for arr in perf_year_array:
    year_WL.append(win_loss(list(arr)))

slam_pct = []
for arr in perf_slam_array:
    slam_pct.append(win_loss_pct(list(arr)))

slam_rec = []
for arr in perf_slam_array:
    slam_rec.append(slam_win_rec(list(arr)))

#-------------------------------------------------------------------------#
#  Extract win/loss aggregate performance for each slam (AO, RG, W, USO)  #
#-------------------------------------------------------------------------#

# SR total
W = T = 0
for arr in perf_slam_array:
    W += slam_wins(list(arr))
    T += slam_wins(list(arr)) + total_losses(list(arr))
slam_rec_total = str(W) + ' / ' + str(T)
del W, T

# W-L total (note that W and L are used in next total too)
W = L = 0
for arr in perf_slam_array:
    W += total_wins(list(arr))
    L += total_losses(list(arr))
slam_WL_total = str(W) + '–' + str(L)

# Win % total (W and L deleted after this total is calculated)
slam_pct_total = trailing_zeroes(round(W / (float(W) + L) * 100, 2), 2)
del W, L  

#--------------------------------------------------------#
#  Determine if we need SR, W-L, or Win % in wiki-table  #
#--------------------------------------------------------#

def has_SR(string):
    match = re.search(r'[\w\]]!![^!S]*SR', string)
    return(match)

def has_WL(string):
    match = re.search(r'[\w\]]!![^!S]*W–L', string)
    return(match)

def has_win_pct(string):
    match = re.search(r'[\w\]]!![^!S]*Win\s\%', string)
    return(match)

INC_SR = has_SR(Singles_Performance)
INC_WL = has_WL(Singles_Performance)
INC_WIN_PCT = has_win_pct(Singles_Performance)

#---------------------------------------------------#
#  Build the singles performance substitution list  #
#---------------------------------------------------#

# Order:
# (slam_rec, slam_WL, MAYBE slam_pct) * 4,
# year_WL's, slam_rec_total, slam_WL_total, MAYBE slam_pct_total

stats = []
for i in range(len(slam_rec)):
    if INC_SR:
        stats.append(slam_rec[i])
    if INC_WL:
        stats.append(slam_WL[i])
    if INC_WIN_PCT:
        stats.append(slam_pct[i])
for i in range(len(year_WL)):
    stats.append(year_WL[i])
del i
if INC_SR:
    stats.append(slam_rec_total)
if INC_WL:
    stats.append(slam_WL_total)
if INC_WIN_PCT:
    stats.append(slam_pct_total)

#-----------------------------------------------------------------------#
#  Iterate and replace singles performance in Singles_Performance_List  #
#-----------------------------------------------------------------------#

def is_stat(line):
    match = re.search(r'\d+\s\/\s\d+|\d+\–\d+|\d+\-\d+|\d+\.\d+', line)
    return(match)

# DIAGNOSTICS TO RUN IF OUTPUT GETS FUNKY #
b = -1
a = 0
for line in Singles_Performance_List:
    if is_stat(line):
        a += 1
    b += 1
    print(b, a, is_stat(line), line)
del b
del a
print('this is when the replacements stop: ' + str(len(stats)))

i = 0
for (index, line) in enumerate(Singles_Performance_List):
    if i == len(stats):
        break
    if is_stat(line):
        Singles_Performance_List[index] = re.sub(r'(\d+\D+\d+)',
                                                 stats[i], line)
        i += 1
del i

#  Output new, updated string of single's performance  #

Singles_Performance = '\n'.join(Singles_Performance_List)

##open('hithere.txt', 'w')
##fout = open('hithere.txt', 'w')
##fout.write(Singles_Performance2)


"""
array methods that i'll need:
.sum(axis=0) gives you list of column sums
.min(axis=1) gives you mins of rows
.cumsum(axis=1) gives you cumulative sum along each row

.transpose() gives you transpose
[1] gives you 2nd row as a list, but you can coerce into a list using list()

.ravel unravels the array/flattens the array
"""


"""
TODO:

0. String methods to achieve the substitution?
    Build list with correct ordering of performance scores
    Split wiki text string by newline
    For line in whole string
        if line has score,
            replace with next performance score
    

1. Build a dict/structure
    KEYS: AO, FO, W, USO
    VALUES: [(2005, 2R), (2006, 3R), (2007, F)]

   Extract performance
    AO Slam perf: List of 2nd tuple value in each dict entry for AO
    2007 Slam perf: List of second tuple value of first tuple for each key

2. Data Matrix (or list within list)
     2005 2006 2007 2008
AO    1R   3R   F    W
FO
W               etc..
USO

   Then, extract.
   
"""
