# coding: utf-8

#-------------------------------------------------------------------------#
#  Checks that the Grand Slam singles performance of professional tennis  #
#  players on Wikipedia matches their win/loss ratios.                    #                               #
#-------------------------------------------------------------------------#

import re
from numpy import *

#--------------------#
#  Global Constants  #
#--------------------#

SLAMS = ['Australian Open', 'Roland Garros', 'Wimbledon', 'US Open']

ROUNDS = ['1R', '2R', '3R', '4R', 'QF', 'SF', 'F', 'W']

wins_for = dict(zip(ROUNDS, range(0,8))) # Gives num of wins for round attained

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
    return(str(flt) + u'0' * (AfterDecimalDigits - i))

#-----------#
#  Classes  # 
#-----------#

class Performance:
    def __init__(self, performance):
        self.performance = performance
        
    def matches_won(self):
        """ Given a list of performance, return the total match wins"""
        wins = 0
        for round_attained in self.performance:
            if round_attained in ROUNDS:
                wins += wins_for[round_attained]
            else:
                continue
        return(wins)

    def matches_lost(self):
        """ Given a list of performance, return the total match losses"""
        losses = 0
        for round_attained in self.performance:
            if round_attained in ROUNDS and round_attained != 'W':
                losses += 1
        return(losses)

    def matches_played(self):
        """ Given a list of performance, return the total matches played"""
        return(self.matches_won() + self.matches_lost())

    def championships(self):
        """ Given a list of performance, return the total championships"""
        wins = 0
        for round_attained in self.performance:
            if round_attained == 'W':
                wins += 1
        return(wins)

    # Note: losses would be entirely equivalent to matches_lost since
    # grand slams are knockout tournaments.  Thus, matches_lost is used
    # as an exact proxy for losses.

    def appearances(self):
        """ Given a list of performance, return the total appearances"""
        return(self.championships() + self.matches_lost())

    def match_record(self):
        """ Given a list of performance, return win-loss record"""
        record = str(self.matches_won()) + u'\u2013' + str(self.matches_lost())
        return(record)

    def match_percentage(self):
        """ Given a list of performance, return win and loss percentage"""
        percentage = self.matches_won() / float(self.matches_played())
        percentage = round(percentage * 100, 2)
        percentage = trailing_zeroes(percentage, 2)
        return(percentage)

    def championship_record(self):
        """ Given a list of performance, return slam win-loss record"""
        record = str(self.championships()) + u' / ' + str(self.appearances())
        return(record)


class Career:
    def __init__(self, performanceSlamArray, performanceYearArray):
        self.by_slams = performanceSlamArray
        self.by_years = performanceYearArray
        self.slams = []
        for slam in range(4):
            self.slams.append(Performance(list(performanceSlamArray[slam])))
        self.years = []
        for year in range(len(self.by_years)):
            self.years.append(Performance(list(performanceYearArray[year])))

    def match_records_by_slam(self):
        statistics = []
        for slam in self.slams:
            statistics.append(slam.match_record())
        return(statistics)

    def match_records_by_year(self):
        statistics = []
        for year in self.years:
            statistics.append(year.match_record())
        return(statistics)

    def match_percentage_by_slam(self):
        statistics = []
        for slam in self.slams:
            statistics.append(slam.match_percentage())
        return(statistics)

    def match_percentage_by_year(self):
        statistics = []
        for year in self.years:
            statistics.append(year.match_percentage())
        return(statistics)

    def championships_by_slam(self):
        statistics = []
        for slam in self.slams:
            statistics.append(slam.championship_record())
        return(statistics)

    def championships(self):
        wins = 0
        for slam in self.slams:
            wins += slam.championships()
        return(wins)

    def appearances(self):
        total = 0
        for slam in self.slams:
            total += slam.appearances()
        return(total)

    def championship_record(self):
        return(str(self.championships()) + u' / ' + str(self.appearances()))

    def matches_won(self):
        wins = 0
        for slam in self.slams:
            wins += slam.matches_won()
        return(wins)

    def matches_lost(self):
        losses = 0
        for slam in self.slams:
            losses += slam.matches_lost()
        return(losses)

    def matches_played(self):
        total = 0
        for slam in self.slams:
            total += slam.matches_played()
        return(total)

    def match_record(self):
        return(str(self.matches_won()) + u'\u2013' + str(self.matches_lost()))

    def match_percentage(self):
        percentage = self.matches_won() / float(self.matches_played())
        percentage = round(percentage * 100, 2)
        percentage = trailing_zeroes(percentage, 2)
        return(percentage)
           
#------------------------------------------#
#  Setup the Singles Performance wiki-text #
#------------------------------------------#

Singles_Performance = djok
Singles_Performance_List = Singles_Performance.split('\n')

# Sometimes the tables extend to include performance in other tourneys
# The following will eliminate the wiki-text relating to those subsequent tables
if Singles_Performance.find('style=text-align:left|Win') > 0:
    end = Singles_Performance.find('style=text-align:left|Win')
    Singles_Performance = Singles_Performance[:end]

#----------------------------------#
#  Build list of slam performance  #
#----------------------------------#

# The round performance (3R, SF, F, W, etc..) is always the display text
# of a wiki-link for the individual slam's wiki article.
# For example, a 3R finish in the 2009 Australian Open will be displayed as:
# [[2009 Australian Open - Men's Singles|3R]]

# Builds a list of all instances of display texts of specific slam wiki-links
perf = re.findall(ur"\n\|([A-Z]\w?)|[-\u2013][^'\n]+'[^\|\n]+\|'*([^\]]{2})",
                  Singles_Performance)
performance = []
for tup in perf:
    for string in tup:
        if string:
            performance.append(string)
del perf

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

#--------------------------------------------------------#
#  Determine if we need SR, W-L, or Win % in wiki-table  #
#--------------------------------------------------------#

def has_championship_record(string):
    match = re.search(r'[\w\]]!![^!S]*SR', string)
    return(match)

def has_match_record(string):
    match = re.search(ur'[\w\]]!![^!S]*W(-|\u2013)L', string)
    return(match)

def has_match_percentage(string):
    match = re.search(r'[\w\]]!![^!S]*Win\s\%', string)
    return(match)

INC_CHAMPIONSHIP_RECORD = has_championship_record(Singles_Performance)
INC_MATCH_RECORD = has_match_record(Singles_Performance)
INC_MATCH_PERCENTAGE = has_match_percentage(Singles_Performance)

#---------------------------------------------------#
#  Build the singles performance substitution list  #
#---------------------------------------------------#

career = Career(perf_slam_array, perf_year_array)

# Order:
# (slam_rec, slam_WL, MAYBE slam_pct) * 4,
# year_WL's, slam_rec_total, slam_WL_total, MAYBE slam_pct_total

stats = []
for i in range(len(career.championships_by_slam())):
    if INC_CHAMPIONSHIP_RECORD:
        stats.append(career.championships_by_slam()[i])
    if INC_MATCH_RECORD:
        stats.append(career.match_records_by_slam()[i])
    if INC_MATCH_PERCENTAGE:
        stats.append(career.match_percentage_by_slam()[i])
for i in range(len(career.match_records_by_year())):
    stats.append(career.match_records_by_year()[i])
del i
if INC_CHAMPIONSHIP_RECORD:
    stats.append(career.championship_record())
if INC_MATCH_RECORD:
    stats.append(career.match_record())
if INC_MATCH_PERCENTAGE:
    stats.append(career.match_percentage())

#-----------------------------------------------------------------------#
#  Iterate and replace singles performance in Singles_Performance_List  #
#-----------------------------------------------------------------------#

def is_stat(line):
    match = re.search(ur'\d+\s\/\s\d+|\d+\-\d+|\d+\u2013\d+|\d+\.\d+', line)
    return(match)

i = 0
for (index, line) in enumerate(Singles_Performance_List):
    if i == len(stats):
        break
    if is_stat(line):
        Singles_Performance_List[index] = re.sub(ur'(\d+\D+\d+)',
                                                 stats[i], line)
        i += 1
del i

#  Output new, updated string of single's performance  #

Singles_Performance = '\n'.join(Singles_Performance_List)

Singles_Performance # For now, paste me into wiki-text edit box!
