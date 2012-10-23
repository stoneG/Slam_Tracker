# coding: utf-8

#-----------------------------------------------------------------#
#  HawkEyeBot checks that the Grand Slam singles performance of   #
#  professional tennis players on Wikipedia corresponds to their  #
#  win/loss ratios.                                               #
#-----------------------------------------------------------------#

from numpy import *
import re
import time
import wikipedia

# Open file for printing during runs.

fo = open("trial-run.txt", "w")

#--------------------#
#  Global Constants  #
#--------------------#

SLAMS = ['Australian Open', 'Roland Garros', 'Wimbledon', 'US Open']

ROUNDS = ['1R', '2R', '3R', '4R', 'QF', 'SF', 'F', 'W']

wins_for = dict(zip(ROUNDS, range(0,8))) # Gives num of wins for round attained

# TODO: put all regex's here #

#--------------------#
#  Helper Functions  #
#--------------------#

# TODO: replace this with precision #
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
    " Initialized with a list of round performances."
    def __init__(self, performance):
        self.performance = performance

    def matches_won(self):
        """ Given a list of performance, return the total match wins"""
        wins = 0
        for round_attained in self.performance:
            if round_attained in ROUNDS:
                wins += wins_for[round_attained]
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
        if self.matches_played() == 0:
            percentage = 0
        else:
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
        if self.matches_played() == 0:
            percentage = 0
        else:
            percentage = self.matches_won() / float(self.matches_played())
        percentage = round(percentage * 100, 2)
        percentage = trailing_zeroes(percentage, 2)
        return(percentage)


class Player:
    def __init__(self, name, text):
        self.wiki_text = text
        self.name = name

    def __str__(self):
        return(self.name)

    def singles_performance(self):
        """Sometimes the tables extend to include performance in other tourneys.
           The following will eliminate the wiki-text relating to those
           subsequent tables
        """
        if self.wiki_text.find('style=text-align:left|Win') > 0:
            end = self.wiki_text.find('style=text-align:left|Win')
            return(self.wiki_text[:end])
        else:
            return(self.wiki_text)

    def singles_performance_list(self):
        return(self.singles_performance().split('\n'))

    # The round performance (3R, SF, F, W, etc..) is always the display text
    # of a wiki-link for the individual slam's wiki article.
    # For example, a 3R finish in the 2009 Australian Open will be displayed as:
    # [[2009 Australian Open - Men's Singles|3R]]

    def performance(self):
        pat = re.compile(ur"\|(\dR)$|\|([A-Z]\w?)$|[-\u2013][^']+'[^\|]+\|'*([^'\]][^'\]]?)\]\]$")

        # Build list of tuples of matches
        perf = []
        for line in self.singles_performance_list():
            match = pat.search(line)
            if match:
                perf.append(match.groups())

        # Break down tuples and discard empty strings
        performance = []
        for tup in perf:
            for string in tup:
                if string:
                    performance.append(string)

        # Find how many slams are unplayed
        if len(performance) % 4:
            unplayed = 4 - len(performance) % 4
        else:
            unplayed = 0

        # How many years of slams have been played
        years = (unplayed + len(performance)) / 4

        # Add in empty strings for yet to be played slams in current year
        if unplayed > 0:
            ins = [4 * years - 1]
            i = 1
            while i < unplayed:
                ins.append(ins[-1] - years)
                i += 1
            ins.reverse()
            for index in ins:
                performance.insert(index, ' ')

        return(performance)

    #  Determine if we need SR, W-L, or Win % in wiki-table
    def has_championship_record(self):
        match = re.search(r'\d{4}[^\n]+[\w\]]!![^!S]*SR', self.wiki_text)
        return(match)

    def has_match_record(self):
        match = re.search(ur'\d{4}[^\n]+[\w\]]!![^!S]*W(-|\u2013)L', self.wiki_text)
        return(match)

    def has_match_percentage(self):
        match = re.search(r'\d{4}[^\n]+[\w\]]!![^!S]*Win\s\%', self.wiki_text)
        return(match)

    # This is the grand slam performance table we can visually see on Wikipedia
    def performance_slam_array(self):
        columns = len(self.performance())/4
        return(array(self.performance()).reshape(4, columns))

    def performance_year_array(self):
        return(self.performance_slam_array().transpose())

#-----------------------------------#
#  Regular Expressions and Strings  #
#-----------------------------------#

# Building the stat finding regular expressions
championship_record_re = ur'[!\|]\d+\s\/\s\d+$'
match_record_one_re = ur'[!\|]\d+\-\d+$'        # regular dash
match_record_two_re = ur'[!\|]\d+\u2013\d+$'    # em-dash
match_percentage_re = ur'[!\|]\d+\.\d+$'

stat = re.compile(ur'|'.join([championship_record_re
                              , match_record_one_re
                              , match_record_two_re
                              , match_percentage_re]))

# Build timestamp comment
timestamp = u"\n<!-- HawkEyeBot last run at %H:%M:%S (UTC) on %d %b, %Y -->"
currenttime = time.strftime(timestamp, time.gmtime())

# HawkEyeBot edit messages
changed_stats_msg = 'Corrected statistics in the Singles Performance Timeline and updated timestamp for this run. Concerns/suggestions? See [[User talk:HawkEyeBot]].'
unchanged_stats_msg = "Statistics in the Singles Performance Timeline are correct. Updated timestamp for this run. Concerns/suggestions? See [[User talk:HawkEyeBot]]."

#-------------#
#  Functions  #
#-------------#

def is_stat(line):
    match = stat.search(line)
    return(match)

def runtime(new_singles_performance):
    comment = re.compile(ur"\n<!--\sHawkEyeBot\slast[^-]+-->")
    if comment.search(new_singles_performance):
        new_singles_performance = re.sub(ur"\n<!--\sHawkEyeBot\slast[^-]+-->"
                                              , currenttime
                                              , new_singles_performance)
    else:
        new_singles_performance = new_singles_performance + currenttime
    return(new_singles_performance)

def update_page():
    is_unchanged = Original_Singles_Performance == New_Singles_Performance
    if is_unchanged:
        page.put(runtime(New_Singles_Performance), unchanged_stats_msg)
    else:
        page.put(runtime(New_Singles_Performance), changed_stats_msg)

def statistics():
    " Build list of grand slam statistics in the order of appearance in wiki-text"
    stats = []

    for i in range(len(career.championships_by_slam())):

        if player.has_championship_record():
            stats.append(career.championships_by_slam()[i])

        if player.has_match_record():
            stats.append(career.match_records_by_slam()[i])

        if player.has_match_percentage():
            stats.append(career.match_percentage_by_slam()[i])

    for each in career.match_records_by_year():
        stats.append(each)

    if player.has_championship_record():
        stats.append(career.championship_record())

    if player.has_match_record():
        stats.append(career.match_record())

    if player.has_match_percentage():
        stats.append(career.match_percentage())

    return(stats)

#-------------------------------#
#  Get List of Pages to Update  #
#-------------------------------#

site = wikipedia.getSite('en', 'wikipedia')
page = wikipedia.Page(site, 'User:HawkEyeBot/Player_List')
player_list = re.findall(ur'\*\s([^\n]+)\n', page.get())

#------------------#
#  Run HawkEyeBot  #
#------------------#

for name in player_list:

    # Instantiate player page
    page = wikipedia.Page(site, name)

    # Exceptions
    if not page.exists():
        error = '%s has no article' % name
        print(error)
        fo.write(error.encode('utf-8'))
        continue

    if not page.canBeEdited():
        error = '%s is protected and cannot be edited' % name
        print(error)
        fo.write(error.encode('utf-8'))

    if not page.botMayEdit():
        error = '%s may not be edited by HawkEyeBot' % name
        print(error)
        fo.write(error.encode('utf-8'))
        
    # Instantiate other objects
    if page.isRedirectPage():
        page = page.getRedirectTarget()
    Original_Singles_Performance = page.get() 
    player = Player(name, Original_Singles_Performance)
    career = Career(player.performance_slam_array()
                    , player.performance_year_array())

    # Constructing the correct list of statistics to go in the Singles Performance Timeline
    # This may or may not differ from the statistics currently in the page
    stats = statistics()

    # Split the wiki text by lines
    Singles_Performance_List = Original_Singles_Performance.split('\n')

    # Find and replace stats in Singles_Performance_List
    i = 0
    for (index, line) in enumerate(Singles_Performance_List):
        if i == len(stats):
            break
        if is_stat(line):
            Singles_Performance_List[index] = re.sub(ur'(\d+\D+\d+)',
                                                     stats[i], line)
            i += 1
    del i

    # Reassemble list into string
    New_Singles_Performance = '\n'.join(Singles_Performance_List)

    # Send and update player's article on Wikipedia
    update_page()

    # Note completion and sleep
    finish = '\n\nFinished updating page for %s\n' % name
    print(finish.encode('utf-8'))
    fo.write(finish.encode('utf-8'))
    fo.write('\nSingles Performance Timeline:\n')
    for li in player.performance_slam_array():
        for elem in li:
            fo.write(elem.encode('utf-8'))
            fo.write(' ')
        fo.write('\n')
    fo.write('\nStatistics:\n')
    for elem in stats:
        fo.write(elem.encode('utf-8'))
        fo.write(' ')
    #print('Sleeping for 1s\n')
    #time.sleep(1)

fo.close()

# fin
