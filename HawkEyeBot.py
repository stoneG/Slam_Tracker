# coding: utf-8

#-------------------------------------------------------------------------#
#  Checks that the Grand Slam singles performance of professional tennis  #
#  players on Wikipedia matches their win/loss ratios.                    #
#-------------------------------------------------------------------------#

from numpy import *
import re
import time
import wikipedia

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

##class Player:
##    def __init__(self, name, text):
##        self.wiki_text = text
##        self.name = name
##
##    def __str__(self):
##        return(self.name)
##
##    def singles_performance(self):
##        if self.wiki_text.find('style=text-align:left|Win') > 0:
##            end = self.wiki_text.find('style=text-align:left|Win')
##            return(self.wiki_text[:end])

    

    

#-------------------------------#
#  Get List of Pages to Update  #
#-------------------------------#

##site = wikipedia.getSite('en', 'hawkeye')
##page = wikipedia.Page(site, 'List')
##player_list = re.findall(ur'\*\s([^\n]+)\n', page.get())

#------------------------------------------#
#  Setup the Singles Performance wiki-text #
#------------------------------------------#

site = wikipedia.getSite('en', 'hawkeye')
player = 'Novak Djokovic'
page = wikipedia.Page(site, player)

Original_Singles_Performance = page.get()

# Sometimes the tables extend to include performance in other tourneys
# The following will eliminate the wiki-text relating to those subsequent tables
if Original_Singles_Performance.find('style=text-align:left|Win') > 0:
    end = Original_Singles_Performance.find('style=text-align:left|Win')
    Singles_Performance = Original_Singles_Performance[:end]
else:
    Singles_Performance = Original_Singles_Performance

Singles_Performance_List = Singles_Performance.split('\n')

#----------------------------------#
#  Build list of slam performance  #
#----------------------------------#

# The round performance (3R, SF, F, W, etc..) is always the display text
# of a wiki-link for the individual slam's wiki article.
# For example, a 3R finish in the 2009 Australian Open will be displayed as:
# [[2009 Australian Open - Men's Singles|3R]]

round_performance = re.compile(ur"\|([A-Z]\w?)$|[-\u2013][^']+'[^\|]+\|'*([^'\]][^'\]]?)\]\]$")

perf = []
for line in Singles_Performance_List:
    match = round_performance.search(line)
    if match:
        perf.append(match.groups())

performance = []
for tup in perf:
    for string in tup:
        if string:
            performance.append(string)    

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

stat = re.compile(ur'[!\|]\d+\s\/\s\d+$|[!\|]\d+\-\d+$|[!\|]\d+\u2013\d+$|[!\|]\d+\.\d+$')

def is_stat(line):
    match = stat.search(line)
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

#------------------------------------------------------#
#  Output new, updated string of single's performance  #
#------------------------------------------------------#

HawkEyed_Singles_Performance = '\n'.join(Singles_Performance_List)

page = wikipedia.Page(site, '%s %s' % (player, '(hawkeyed)'))

timestamp = u"\n<!-- HawkEyeBot last run at %H:%M:%S (UTC) on %d %b, %Y -->"
currenttime = time.strftime(timestamp, time.gmtime())

def runtime():
    global HawkEyed_Singles_Performance
    comment = re.compile(ur"\n<!--\sHawkEyeBot\slast[^-]+-->")
    if comment.search(HawkEyed_Singles_Performance):
        HawkEyed_Singles_Performance = re.sub(ur"\n<!--\sHawkEyeBot\slast[^-]+-->"
                                              , currenttime
                                              , HawkEyed_Singles_Performance)
    else:
        HawkEyed_Singles_Performance = HawkEyed_Singles_Performance + currenttime

if Original_Singles_Performance == HawkEyed_Singles_Performance:
    runtime()
    page.put(Hawkeyed_Singles_Performance, '*clap* *clap* *clap* *clap* hawk-eye confirms the call!')
else:
    runtime()
    page.put(Hawkeyed_Singles_Performance, '*clap* *clap* *clap* *clap* hawk-eye overturns the call!')
