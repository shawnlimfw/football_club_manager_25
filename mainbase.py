import csv
import random
import time
import math
import statistics

player_database = {}
epl_team_database = {}
formations_database = {}
fixtures_database = {}
teams_budget_database = {}

team_name = ''
squad = {}
league_table = {}

tactics = {}
tactics_formation = ''
tactics_mentality = ''

money = 0
income = 0
expenditure = 0
transfer_market = {}
transfer_market_seasonal = {1:{},5:{},9:{},13:{},17:{},21:{},25:{},29:{},33:{},37:{}}

league_ranking = 1
training_records = {num:True for num in range(1, 39)}
matchday = 1

match_engine_weights = {}
epl_match_engine_weights = {}

#COMMON FUNCTIONS#----------------------------------------------------------------------------------------------------------------------

def sort_squad():
    global squad
    squad = dict(sorted(squad.items(), key=lambda x:(-int(x[1]['OVR']), x[0][1])))

def update_tactics():
    global tactics

    # after transfers(selling), remove player from starting XI
    for key, value in tactics.items():
        if value != '':
            if (value['Index'], value['Name']) not in squad:
                tactics[key] = ''

    # after training, update ovr
    for key, value in tactics.items():
        if value != '':
            if value['OVR'] != squad[(value['Index'], value['Name'])]['OVR']:
                value['OVR'] = squad[(value['Index'], value['Name'])]['OVR']

    # after matchday, update P, G, A, suspended, injured
    for key, value in tactics.items():
        if value != '':
            value['Played'] = squad[(value['Index'], value['Name'])]['Played']
            value['Goals'] = squad[(value['Index'], value['Name'])]['Goals']
            value['Assists'] = squad[(value['Index'], value['Name'])]['Assists']
            value['Suspended'] = squad[(value['Index'], value['Name'])]['Suspended']
            value['Injured'] = squad[(value['Index'], value['Name'])]['Injured']

def update_league_ranking():
    global league_ranking
    global league_table
    league_table = dict(sorted(league_table.items(), key=lambda item: (-item[1]['W']*3 - item[1]['D'], -item[1]['F']+item[1]['A'], item[0])))
    for index, key in enumerate(league_table, 1):
        if key == team_name:
            league_ranking = index

#COMMON FUNCTIONS#----------------------------------------------------------------------------------------------------------------------

def initilisation():

    def setup_player_database():
        global player_database
        with open('filtered_male_players.csv', mode='r', newline='', encoding="utf8") as file:
            headers = []
            reader = csv.reader(file)
            for row in reader:
                try:
                    int(row[0])
                except:
                    for header in row:
                        headers.append(header)
                    continue
                identifier = (row[0], row[1])
                player_database[identifier] = {}
                for index, attribute in enumerate(row):
                    player_database[identifier][headers[index]] = attribute
                for stat in ['Played', 'Goals', 'Assists']:
                    player_database[identifier][stat] = 0
                for stat in ['Suspended', 'Injured']:
                    player_database[identifier][stat] = False
    
    def setup_teams_budget_database():
        global teams_budget_database
        with open('filtered_teams_budget.csv', mode='r', newline='', encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                teams_budget_database[row[1]] = int(float(row[2])*1000000)

    def setup_epl_team_database():
        global player_database
        global epl_team_database
        for key,value in player_database.items():
            if value['League'] != 'Premier League':
                continue
            else:
                if value['Team'] not in epl_team_database:
                    epl_team_database[value['Team']] = [int(value['OVR'])]
                else:
                    epl_team_database[value['Team']].append(int(value['OVR']))
        for key,value in epl_team_database.items():
            avg = sum(value[:11]) / len(value[:11])
            epl_team_database[key] = [round(avg, 1), teams_budget_database[key]]

    def setup_formations_database():
        global formations_database
        with open('formations.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                positions = row[1].split('/')
                formations_database[row[0]] = positions

    def setup_fixtures_database():
        global fixtures_database
        teams = list(range(1,21))
        team_based_fixtures = {team:[] for team in teams}

        temp_teams = teams[:]
        while True:
            team_based_fixtures[temp_teams[0]].append(temp_teams[1])
            if len(team_based_fixtures[temp_teams[0]]) == 19:
                break
            shifted = temp_teams[1]
            for i in range(1, 20):
                if i == 19:
                    temp_teams[i] = shifted
                    break
                temp_teams[i] = temp_teams[i+1]

        for i in range(1,20):
            focus_team = teams[i]
            temp_teams = teams[:]
            while True:
                if temp_teams.index(focus_team) == 1:
                    team_based_fixtures[focus_team].append(temp_teams[0])
                else:
                    team_based_fixtures[focus_team].append(temp_teams[21 - temp_teams.index(focus_team)])
                if len(team_based_fixtures[focus_team]) == 19:
                    break
                shifted = temp_teams[1]
                for i in range(1, 20):
                    if i == 19:
                        temp_teams[i] = shifted
                        break
                    temp_teams[i] = temp_teams[i+1]

        gameweeks = {i: [] for i in range(1,20)}

        for key, value in team_based_fixtures.items():
            for i in range(1,20):
                add = True
                for game in gameweeks[i]:
                    if key in game:
                        add = False
                if add == True:
                    gameweeks[i].append([key, value[i-1]])

        fhalf_fixtures = [value for key, value in gameweeks.items()]
        random.shuffle(fhalf_fixtures)
        for gameweek in fhalf_fixtures:
            random.shuffle(gameweek)

        shalf_fixtures = [value for key, value in gameweeks.items()]
        random.shuffle(shalf_fixtures)
        for gameweek in shalf_fixtures:
            random.shuffle(gameweek)

        check = []
        for gameweek in fhalf_fixtures:
            for game in gameweek:
                check.append(game)

        secondhalf_fixtures = []
        for gameweek in shalf_fixtures:
            secondhalf_fixtures.append([])
            for game in gameweek:
                if game in check:
                    secondhalf_fixtures[-1].append([game[1], game[0]])
                else:
                    secondhalf_fixtures[-1].append([game])

        full_fixtures = fhalf_fixtures + secondhalf_fixtures

        enumerated_teams = {}
        for index, key in enumerate(epl_team_database, 1):
            enumerated_teams[index] = key

        for index, gameweek in enumerate(full_fixtures, 1):
            fixtures_database[f"GW{index}"] = {}
            for indexx, game in enumerate(gameweek,1):
                fixtures_database[f"GW{index}"][f"G{indexx}"] = game

        for gwkey, gwdict in fixtures_database.items():
            for gkey, glist in gwdict.items():
                for index, team in enumerate(glist, 0):
                    glist[index] = enumerated_teams[team]

    def setup_league_table():
        global league_table
        for key, value in epl_team_database.items():
            league_table[key] = {
                'W':0,
                'D':0,
                'L':0,
                'F':0,
                'A':0
            }

    def setup_match_engine_weights():
        global match_engine_weights        

        with open('sorted_weights.csv', mode='r', newline='', encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                match_engine_weights[int(row[0])] = []
                for number in row[1:]:
                    match_engine_weights[int(row[0])].append(int(number))
    
    def setup_epl_match_engine_weights():
        global epl_match_engine_weights
        for index, (key, value) in enumerate(dict(sorted(epl_team_database.items(), key=lambda item:float(item[1][0]), reverse=True)).items(), 1):
            epl_match_engine_weights[key] = match_engine_weights[index]


    setup_player_database()
    setup_teams_budget_database()
    setup_epl_team_database()
    setup_formations_database()
    setup_fixtures_database()
    setup_league_table()
    setup_match_engine_weights()
    setup_epl_match_engine_weights()
    
def game_setup():

    def game_setup_firstpage():
        global team_name
        print('')
        print('Welcome to Football Manager 2025!')
        print('To continue, please choose a team.')
        while True:
            try:
                print('')
                print(f"{'Press:':8}{'Team':25}{'Rating':9}{'Starting Budget'}")
                print('-----------------------------------------------------------')
                placeholder = [key for key in epl_team_database]
                placeholder.sort()
                for index, key in enumerate(placeholder, 1):
                    print(f"{index:<8}{key:<25}{epl_team_database[key][0]:<9}${epl_team_database[key][1]:,}")
                print('')
                choice = int(input('Choose your team: '))
                if choice < 1 or choice > 20:
                    raise ValueError
                print('')
                print(f"You've chosen {placeholder[choice-1]}.")
                while True:
                    confirm = input('Press X to confirm, or Y to go back: ')
                    if confirm == 'X':
                        team_name = placeholder[choice-1]
                        print(' ')
                        return 
                    elif confirm == 'Y':
                        break
            except:
                pass

    def set_squad():
        global team_name
        global squad
        for key, value in player_database.items():
            if value['Team'] == team_name:
                squad[key] = value

    def set_default_tactics():
        global tactics
        global tactics_formation
        global tactics_mentality
        tactics_formation = '4-3-3 (Holding)'
        tactics_mentality = 'Balanced'
        for index, position in enumerate(formations_database[tactics_formation], 1):
                tactics[(index, position)] = ''

    def set_money():
        global money
        money = epl_team_database[team_name][1]

    def set_transfer_market():

        def filter_transfer_market():
            global transfer_market
            squad_ids = []
            for key, value in squad.items():
                squad_ids.append(key[0])
            for key, value in player_database.items():
                if key[0] not in squad_ids:
                    transfer_market[key] = value

        def set_transfer_market_seasonal():
            global transfer_market_seasonal
            over85 = []
            over79 = []
            over69 = []
            over46 = []

            for key, value in transfer_market.items():
                if int(value['OVR']) > 85:
                    over85.append(key)
                if int(value['OVR']) > 79 and int(value['OVR']) < 86:
                    over79.append(key)
                if int(value['OVR']) > 69 and int(value['OVR']) < 80:
                    over69.append(key)
                if int(value['OVR']) > 46 and int(value['OVR']) < 70:
                    over46.append(key)

            for key, value in transfer_market_seasonal.items():
                for i in range(4):
                    player = random.choice(over85)
                    value[player] = transfer_market[player]
                for i in range(10):
                    player = random.choice(over79)
                    value[player] = transfer_market[player]
                for i in range(6):
                    player = random.choice(over69)
                    value[player] = transfer_market[player]
                for i in range(5):
                    player = random.choice(over46)
                    value[player] = transfer_market[player]

        filter_transfer_market()
        set_transfer_market_seasonal()

    def testing():
        global tactics
        tactics = {(1, 'GK'): {'Index': '22', 'Name': 'Ederson', 'OVR': '88', 'Position': 'GK', 'Alternative positions': '', 'Age': '31', 'Nation': 'Brazil', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (2, 'LB'): {'Index': '148', 'Name': 'Joško Gvardiol', 'OVR': '83', 'Position': 'LB', 'Alternative positions': 'CB', 'Age': '22', 'Nation': 'Croatia', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (3, 'CB'): {'Index': '19', 'Name': 'Rúben Dias', 'OVR': '88', 'Position': 'CB', 'Alternative positions': '', 'Age': '27', 'Nation': 'Portugal', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (4, 'CB'): {'Index': '87', 'Name': 'John Stones', 'OVR': '85', 'Position': 'CB', 'Alternative positions': 'CDM, RB', 'Age': '30', 'Nation': 'England', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (5, 'RB'): {'Index': '130', 'Name': 'Kyle Walker', 'OVR': '84', 'Position': 'RB', 'Alternative positions': '', 'Age': '34', 'Nation': 'England', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (6, 'CM'): {'Index': '42', 'Name': 'İlkay Gündoğan', 'OVR': '87', 'Position': 'CM', 'Alternative positions': 'CDM', 'Age': '33', 'Nation': 'Germany', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (7, 'CDM'): {'Index': '2', 'Name': 'Rodri', 'OVR': '91', 'Position': 'CDM', 'Alternative positions': 'CM', 'Age': '28', 'Nation': 'Spain', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (8, 'CM'): {'Index': '6', 'Name': 'Kevin De Bruyne', 'OVR': '90', 'Position': 'CM', 'Alternative positions': 'CAM', 'Age': '33', 'Nation': 'Belgium', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (9, 'LW'): {'Index': '110', 'Name': 'Jack Grealish', 'OVR': '84', 'Position': 'LW', 'Alternative positions': 'LM', 'Age': '29', 'Nation': 'England', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (10, 'ST'): {'Index': '3', 'Name': 'Erling Haaland', 'OVR': '91', 'Position': 'ST', 'Alternative positions': '', 'Age': '24', 'Nation': 'Norway', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}, (11, 'RW'): {'Index': '16', 'Name': 'Phil Foden', 'OVR': '88', 'Position': 'RW', 'Alternative positions': 'LW, CAM, RM', 'Age': '24', 'Nation': 'England', 'League': 'Premier League', 'Team': 'Manchester City', 'Played': 0, 'Goals': 0, 'Assists': 0, 'Suspended': False, 'Injured': False}}
        #TESTING: ^^^DELETE

    game_setup_firstpage()
    set_squad()
    update_league_ranking()
    set_default_tactics()
    set_transfer_market()
    set_money()
    testing()


def main_menu():
    options = {
        '1':'Squad',
        '2':'Tactics',
        '3':'League',
        '4':'Fixtures',
        '5':'Transfers',
        '6':'Finances',
        '7':'Training',
        '8':'Matchday'
    }

    print('MAIN MENU')
    print(f"{team_name}")
    print(f"Club funds: ${money:,}")
    print(f"League Position: {league_ranking}")
    print(f"Matchday {matchday}")
    print('')
    while True:
        try:
            print(f"{'Press:':8}{'Command:':25}")
            print('----------------------------')
            for key,value in options.items():
                print(f"{key:<8}{value}")
            print('')
            command = input('Choose a command: ')
            print('')
            if int(command) > 0 and int(command) < 9:
                return int(command)
        except:
                pass

def squad_page():
    print('SQUAD')
    print(f"{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':14}{'OVR':4}")
    print('----------------------------------------------------------------------------------------------------------------------------------------------')
    for key,value in squad.items():
        print(f"{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{f"Yes ({value['Suspended']} MD)" if value['Suspended'] != False else 'No':<13}{f"Yes ({value['Injured']} MD)" if value['Injured'] != False else 'No':<14}{value['OVR']:<4}")
    print('')
    while True:
        if input('Press X to go back to MAIN MENU: ') == 'X':
            print('')
            return

def tactics_page():

    def tactics_main_page():
        while True:
            print('TACTICS')
            print(f"Formation: {tactics_formation} - Press Y to change")
            print(f"Mentality: {tactics_mentality} - Press Z to change")
            print(f"Press A to edit starting XI")
            print('')
            print_tactics()
            print('')
            while True:
                command = input('Press X to return to MAIN MENU: ')
                if command == 'X':
                    print('')
                    return
                if command == 'Y':
                    print('')
                    tactics_change_formation()
                    break
                if command == 'Z':
                    print('')
                    tactics_change_mentality()
                    break
                if command == 'A':
                    print('')
                    tactics_change_tactics()
                    break

    def print_tactics():
        print(f"{'Lineup':<9}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':14}{'OVR':4}")
        print('-------------------------------------------------------------------------------------------------------------------------------------------------------')
        for key,value in tactics.items():
            if value == '':
                print(f"{key[1]:<9}")
            else:
                print(f"{key[1]:<9}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{f"Yes ({value['Suspended']} MD)" if value['Suspended'] != False else 'No':<13}{f"Yes ({value['Injured']} MD)" if value['Injured'] != False else 'No':<14}{value['OVR']:<4}")     

    def tactics_change_formation():
        global tactics_formation
        global tactics
        base = {'1':'3', '2':'4', '3':'5'}
        print('FORMATION')
        print(f"{'Press:':8}{'Formation Type'}")
        print('-------------------------------------')
        for key,value in base.items():
            print(f"{key:8}{value + ' at the back'}")
        print('')
        while True:
            command = input('Choose a type of formation to continue (or Press X to go back to TACTICS): ')
            if command in base or command == 'X':
                break
        print('')
        if command == 'X':
            return
        print(f"{base[command]} AT THE BACK")
        print(f"{'Press:':8}{'Formation'}")
        print('----------------------------')
        formation_shortlist = []
        indexes = []
        for key, value in formations_database.items():
            if key[0] == base[command]:
                formation_shortlist.append(key)
        for index, formation in enumerate(formation_shortlist, 1):
            print(f"{index:<8}{formation}")
            indexes.append(index)
        print('')
        while True:
            new_c = input('Choose a formation (or press X to return to TACTICS): ')
            if int(new_c) in indexes or new_c == 'X':
                break
        print('')
        if new_c == 'X':
            return
        else:
            tactics_formation = formation_shortlist[int(new_c)-1]
            tactics.clear()
            for index, position in enumerate(formations_database[tactics_formation], 1):
                tactics[(index, position)] = ''
            return

    def tactics_change_mentality():
        global tactics_mentality
        print('MENTALITY')
        print(f"Current mentality: {tactics_mentality}")
        print('')
        print(f"{'Press:':8}{'Mentality'}")
        print('-------------------------------------')
        mentalities = ['Very Defensive', 'Defensive', 'Balanced', 'Attacking', 'Very Attacking']
        for mentality in mentalities:
            print(f"{mentalities.index(mentality)+1:<8}{mentality}")
        print('')
        while True:
            command = input('Choose a mentality to continue (or press X to go back to TACTICS): ')
            if command in [str(1),str(2),str(3),str(4),str(5)] or command == 'X':
                break
        print('')
        if command == 'X':
            return
        tactics_mentality = mentalities[int(command)-1]

    def tactics_change_tactics():
        while True:
            print('STARTING XI')
            print('Press the number on the left to edit each position')
            print('')
            print(f"{'Press':<8}{'Lineup':<9}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':14}{'OVR':4}")
            print('---------------------------------------------------------------------------------------------------------------------------------------------------------------')
            for index, (key,value) in enumerate(tactics.items(), 1):
                if value == '':
                    print(f"{index:<8}{key[1]:<9}")
                else:
                    print(f"{index:<8}{key[1]:<9}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{f"Yes ({value['Suspended']} MD)" if value['Suspended'] != False else 'No':<13}{f"Yes ({value['Injured']} MD)" if value['Injured'] != False else 'No':<14}{value['OVR']:<4}")
            print('')
            while True:
                exit = False
                command = input('Press X to return to TACTICS: ')
                if command == 'X':
                    print('')
                    exit = True
                    break
                if command == '':
                    continue
                if int(command) in list(range(1, 12)):
                    print('')
                    tactics_change_position(int(command))
                    break
            if exit == True:
                return

    def tactics_change_position(command):
        global tactics
        for key, value in tactics.items():
            if key[0] == command:
                position = key
        print(f"CHOOSE {position[1]}:")
        print(f"Press the number on the left to choose the player")
        print('')
        print(f"{'Press':<8}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':14}{'OVR':4}")
        print('------------------------------------------------------------------------------------------------------------------------------------------------------')
        for index, (key,value) in enumerate(squad.items(), 1):
            print(f"{index:<8}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{f"Yes ({value['Suspended']} MD)" if value['Suspended'] != False else 'No':<13}{f"Yes ({value['Injured']} MD)" if value['Injured'] != False else 'No':<14}{value['OVR']:<4}")
        print('')
        while True:
            command = input('Press X to go back to STARTING XI: ')
            if command == 'X':
                print('')
                return
            try:
                if int(command) in list(range(1,len(squad)+1)):
                    player = list(squad)[int(command)-1]
                    for key, value in tactics.items():
                        if value != '':
                            if value['Index'] == player[0]:
                                tactics[key] = ''
                    tactics[position] = squad[player]
                    print('')
                    return
            except:
                pass

    tactics_main_page()

def league_page():

    def league_main_page():

        print('English Premier League')
        print(f"Matchday {matchday}/38")
        print('')
        print(f"{'POS':<5}{'Team':<30}{'Pl':<5}{'W':<5}{'D':<5}{'L':<5}{'F':<5}{'A':<5}{'GD':<5}{'Pts':<5}")
        print('--------------------------------------------------------------------------')
        for index, (key, value) in enumerate(league_table.items(), 1):
            print(f"{index:<5}{key:<30}{value['W']+value['D']+value['L']:<5}{value['W']:<5}{value['D']:<5}{value['L']:<5}{value['F']:<5}{value['A']:<5}{value['F']-value['A']:<5}{value['W']*3+value['D']:<5}")
            if key == team_name:
                update_league_ranking(index)
        print('')
        while True:
            command = input('Press X to return to MAIN MENU: ')
            if command == 'X':
                print('')
                return
            
    def sort_league_table():
        global league_table
        league_table = dict(sorted(league_table.items(), key=lambda item: (-item[1]['W']*3 - item[1]['D'], -item[1]['F']+item[1]['A'], item[0])))

    def update_league_ranking(index):
        global league_ranking
        league_ranking = index

    sort_league_table()
    league_main_page()

def fixtures_page():

    def fixtures_main_page():
        global matchday
        command = 'X'
        while True:
            if command == 'Z':
                return
            print('FIXTURES')
            if command == 'X':
                command = show_matchday_fixtures()
            elif command == 'Y':
                command = show_team_fixtures()

    def show_matchday_fixtures():
        print(f"Matchday {matchday}")
        print(f"Press Y to view {team_name} fixtures")
        print('--------------------------------------------------------------------')
        for key, value in fixtures_database[f"GW{matchday}"].items():
            print(f"{value[0]:>30} VS {value[1]:<30}")
        print('')
        while True:
            temp_command = input('Press Z to go back to MAIN MENU: ')
            if temp_command in ['X', 'Y', 'Z']:
                print('')
                return temp_command
            
    def show_team_fixtures():
        print(f"{team_name}")  
        print(f"Press X to view Matchday {matchday} fixtures")
        print('--------------------------------------')
        for gwid, gwdict in fixtures_database.items():
            for gid, glist in gwdict.items():
                if team_name == glist[0]:
                    print(f"Matchday {gwid[2:]}: {glist[1]} (H)")
                if team_name == glist[1]:
                    print(f"Matchday {gwid[2:]}: {glist[0]} (A)")
        print('')
        while True:
            temp_command = input('Press Z to go back to MAIN MENU: ')
            if temp_command in ['X', 'Y', 'Z']:
                print('')
                return temp_command
            
    fixtures_main_page()

def transfers_page():

    def decide_transfer_market_seasonal():
        m = matchday
        while True:
            if (m - 1) % 4 == 0:
                return m
            else:
                m -= 1

    def transfers_main_page():
        command = 'X'
        while True:
            if command == 'X':
                command = transfers_buy_page()
                
            elif command == 'Y':
                command = transfers_sell_page()

            elif command == 'Z':
                return
            
            else:
                command = 'X'

    def transfers_buy_page():
        while True:
            seasonal = decide_transfer_market_seasonal()
            placeholder = {}
            print('TRANSFERS')
            print('Viewing TRANSFER MARKET')
            print(f"{(seasonal + 4) - matchday} matchdays left to market refresh")
            print('Press Y to sell squad players')
            print(f"Club funds: ${money:,}")
            print('Press the number on the left to buy player')
            print('')
            print(f"{'Press':<8}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Team':<28}{'OVR':4}{'Value':12}")
            print('----------------------------------------------------------------------------------------------------------------------------------------')
            for index, (key,value) in enumerate(transfer_market_seasonal[seasonal].items(), 1):
                print(f"{index:<8}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Team']:<28}{value['OVR']:<4}${int(value_calibrated(int(value['OVR']), int(value['Age']))):,}")
                placeholder[index] = key
            print('')
            while True:
                try:
                    command = input('Press Z to return to MAIN MENU: ')
                    if command == 'Z':
                        print('')
                        return 'Z'
                    if command == 'Y':
                        print('')
                        return 'Y'
                    if int(command) in placeholder:
                        print('')
                        transfers_confirm_buy_page(placeholder[int(command)], seasonal)
                        break
                except:
                    pass

    def transfers_confirm_buy_page(player, seasonal):
        global squad
        global transfer_market_seasonal
        global money
        global expenditure
        print('CONFIRM')
        price = int(value_calibrated(int(transfer_market_seasonal[seasonal][player]['OVR']), int(transfer_market_seasonal[seasonal][player]['Age'])))

        if money >= price:
            print(f"Buy {player[1]} for ${price:,}?")
            print('Press A to confirm')
            while True:
                command = input('Press X to go back to TRANSFER MARKET: ')
                if command == 'A':
                    print('')
                    squad[player] = player_database[player]
                    squad[player]['Team'] = team_name
                    for key, value in transfer_market_seasonal.items():
                        if player in value:
                            del value[player]
                    money -= price
                    expenditure += price
                    sort_squad()
                    return
                if command == 'X':
                    print('')
                    return
                
        else:
            print(f"Club doesn't have enough funds for {player[1]} (${price:,})")
            while True:
                command = input('Press X to go back to TRANSFER MARKET: ')
                if command == 'X':
                        print('')
                        return
    
    def transfers_sell_page():
        while True:
            placeholder = {}
            print('TRANSFERS')
            print('SELL PLAYER')
            print('Press X to view TRANSFER MARKET')
            print('Press the number on the left to sell player')
            print('')
            print(f"{'Press':<8}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Team':<28}{'OVR':4}{'Value':10}")
            print('-----------------------------------------------------------------------------------------------------------------------------------------')
            for index, (key,value) in enumerate(squad.items(), 1):
                print(f"{index:<8}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Team']:<28}{value['OVR']:<4}${int(value_calibrated(int(value['OVR']), int(value['Age']))):,}")
                placeholder[index] = key
            print('')
            while True:
                try:
                    command = input('Press Z to return to MAIN MENU: ')
                    if command == 'Z':
                        print('')
                        return 'Z'
                    if command == 'Y':
                        print('')
                        return 'Y'
                    if int(command) in placeholder:
                        print('')
                        transfers_confirm_sell_page(placeholder[int(command)])
                        return 'X'
                except:
                    pass

    def transfers_confirm_sell_page(player):
        global squad
        global money
        global income
        print('CONFIRM')
        price = int(value_calibrated(int(squad[player]['OVR']), int(squad[player]['Age'])))
        print(f"Sell {player[1]} for ${price:,}")
        print('Press A to confirm')
        while True:
            command = input('Press X to go back to TRANSFER MARKET: ')
            if command == 'A':
                del squad[player]
                money += price
                income += price
                update_tactics()
                print('')
                return
            if command == 'X':
                print('')
                return
            
    def value_calibrated(ovr, age):
        A = 3.07
        B = 0.1784
        k = 0.0675
        OVR_REF = 70.0
        AGE_REF = 30.0

        value = A * math.exp(B * (ovr - OVR_REF) + k * (AGE_REF - age))
        return value * 1000000
        
    transfers_main_page()

def training_page():
    
    def training_main_page():
        print('TRAINING')
        if training_records[matchday] == False:
            print(f"Training for Matchday {matchday} is completed")
        else:
            print(f"Press Y to proceed with Matchday {matchday} training")

        while True:
            command = input('Press X to go back to MAIN MENU: ')
            if command == 'X':
                print('')
                return
            elif command == 'Y':
                print('')
                training_matchday_page()
                return
            
    def training_matchday_page():
        global squad
        global training_records
        training_records[matchday] = False
        loads = ['Lacing up boots', 'Warming up', 'Perfecting first touches', 'Testing keeper reflexes', 'Cooling down']
        for load in loads:
            print(load, end="", flush=True)
            for dot in '........':
                print(dot, end="", flush=True)
                time.sleep(0.3)
            print('')
        print('')

        train = []
        success_train = []
        for key, value in squad.items():
            train.append(key)
        for item in train:
            success = random.randint(1, int(squad[item]['Age'])**4)
            if success < 26000:
                success_train.append(item)
        for player in success_train:
            squad[player]['OVR'] = str(int(squad[player]['OVR']) + 1)
        print('TRAINING REPORT')
        if len(success_train) == 0:
            print('No progress made.')
        else:
            for player in success_train:
                print(f"{player[1]:28} OVR +1")
        sort_squad()
        update_tactics()
        print('')

        while True:
            command = input('Press X to go back to MAIN MENU: ')
            if command == 'X':
                print('')
                return
            
    training_main_page()

def finances_page():
    print('FINANCES')
    print(f"Income: ${income:,.0f}")
    print(f"Expenditure: ${expenditure:,.0f}")
    print(f"Net Income: {'-' if income - expenditure < 0 else ''}${abs(income - expenditure):,.0f}")
    print('')
    while True:
        command = input('Press X to go back to MAIN MENU: ')
        if command == 'X':
            print('')
            return
        
def matchday_page():
    #use update_tactics() after each matchday
    #use update_league_ranking() after each matchday
    #increase budget after matchday
    def matchday_main_page():
        while True:
            print(f"MATCHDAY {matchday}")
            print('')
            for key, value in fixtures_database[f"GW{matchday}"].items():
                print(f"{value[0]:>30} VS {value[1]:<30}")
            print('')

            next_opponent = ''
            for key, value in fixtures_database[f"GW{matchday}"].items():
                for team in value:
                    if team == team_name:
                        if value[0] == team_name:
                            next_opponent = value[1]
                        else:
                            next_opponent = value[0]
            print(f"Press Y to proceed to game with {next_opponent}")
            while True:
                command = input('Press X to go back to MAIN MENU: ')
                if command == 'X':
                    print('')
                    return
                if command == 'Y':
                    print('')
                    matchday_check_eligibility_page()
                    break

    def matchday_check_eligibility_page():
        eligible = True
        for key, value in tactics.items():
            if value == '':
                eligible = False
            else:
                if value['Suspended'] != False:
                    eligible = False
                if value['Injured'] != False:
                    eligible = False
        if eligible == True:  #FOR TESTING: CHANGE TO TRUE
            matchday_game()
        if eligible == False:
            print('Lineup is incomplete or players are unavailable.')
            print('Please edit lineup in TACTICS page.')
            while True:
                command = input(f"Press X to go back to MATCHDAY {matchday}: ")
                if command == 'X':
                    print('')
                    return

    def matchday_game():
        matchday_results = {}
        self_ovr = 0
        self_weight = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        game_key = ''
        opponent = ''
        events = {}

        def simulate_other_games():
            nonlocal matchday_results
            for key, value in fixtures_database[f"GW{matchday}"].items():
                if key not in matchday_results:
                    matchday_results[key] = {value[0]:'', value[1]:''}
                if team_name not in value:
                    matchday_results[key][value[0]] = random.choices(list(range(0,11)), weights = epl_match_engine_weights[value[0]])[0]
                    matchday_results[key][value[1]] = random.choices(list(range(0,11)), weights = epl_match_engine_weights[value[1]])[0]

        def calculate_self_rating():
            nonlocal self_ovr
            total_ovr = 0
            att = ['ST', 'LW', 'RW']
            mid = ['CDM', 'CM', 'CAM', 'LM', 'RM']
            defe = ['CB', 'LB', 'RB']
            gk = ['GK']

            classes1 = {position: att for position in att}
            classes2 = {position: mid for position in mid}
            classes3 = {position: defe for position in defe}
            classes4 = {position: gk for position in gk}
            classes = {**classes1, **classes2, **classes3, **classes4}
            
            for position, player_stats in tactics.items():
                if position[1] == player_stats['Position']:
                    total_ovr += int(player_stats['OVR'])
                    continue
                if position[1] in player_stats['Alternative positions'].replace(' ', '').split(','):
                    total_ovr += int(player_stats['OVR'])*0.96
                    continue
                if position[1] in classes[position[1]]:
                    total_ovr += int(player_stats['OVR'])*0.8
                    continue
                else:
                    total_ovr += int(player_stats['OVR'])*0.6

            self_ovr = int(total_ovr/11)

        def give_self_weight():
            
            nonlocal self_weight
            self_goals = int(25.27 * self_ovr - 1713)
            self_instances = 6 * 38

            if self_ovr >= 90:
                self_weight[0] = 10
            else:
                self_weight[0] = int(-5.856 * self_ovr + 533.9)

            if self_ovr > 88:
                self_weight[4] = random.randint(20, 30)
            elif 83 <= self_ovr <= 88:
                self_weight[4] = random.randint(16, 25)
            elif 81 <= self_ovr <= 82:
                self_weight[4] = random.randint(8, 13)
            elif 78 <= self_ovr <= 80:
                self_weight[4] = random.randint(4, 9)
            elif 75 <= self_ovr <= 77:
                self_weight[4] = random.randint(1, 5)
            elif self_ovr < 75:
                self_weight[4] = random.randint(1, 3)

            if self_ovr > 88:
                self_weight[5] = random.randint(13, 20)
            elif 86 <= self_ovr <= 88:
                self_weight[5] = random.randint(10, 15)
            elif 83 <= self_ovr <= 85:
                self_weight[5] = random.randint(4, 9)
            elif 78 <= self_ovr <= 82:
                self_weight[5] = random.randint(0, 4)
            elif self_ovr < 77:
                self_weight[5] = random.randint(0, 1)

            if self_ovr > 87:
                self_weight[6] = random.randint(5, 9)
            elif 82 <= self_ovr <= 87:
                self_weight[6] = random.randint(1, 3)
            elif self_ovr < 81:
                self_weight[6] = random.choices([0, 1], weights = [90, 10])[0]

            if self_ovr > 87:
                self_weight[7] = random.randint(1, 2)
            elif 82 <= self_ovr <= 87:
                self_weight[7] = random.choices([0, 1], weights = [6, 1])[0]
            elif self_ovr < 81:
                self_weight[7] = random.choices([0, 1], weights = [10, 1])[0]

            if self_ovr > 87:
                self_weight[8] = random.randint(0, 1)
            elif 82 <= self_ovr <= 87:
                self_weight[8] = random.choices([0, 1], weights = [10, 1])[0]
            elif self_ovr < 81:
                self_weight[8] = random.choices([0, 1], weights = [20, 1])[0]

            if self_ovr > 87:
                self_weight[9] = random.choices([0, 1], weights = [3, 1])[0]
            elif 82 <= self_ovr <= 87:
                self_weight[9] = random.choices([0, 1], weights = [10, 1])[0]
            elif self_ovr < 81:
                self_weight[9] = random.choices([0, 1], weights = [20, 1])[0]

            if self_ovr > 87:
                self_weight[10] = random.choices([0, 1], weights = [10, 1])[0]
            elif 82 <= self_ovr <= 87:
                self_weight[10] = random.choices([0, 1], weights = [15, 1])[0]
            elif self_ovr < 81:
                self_weight[10] = random.choices([0, 1], weights = [25, 1])[0]

            for index, value in enumerate(self_weight, 0):
                self_goals -= value*index
                self_instances -= value

            solutions = []
            for c in range(0, self_goals//3 + 1):
                b = self_goals - self_instances - 2*c
                a = 2*self_instances - self_goals + c
                if a >= 0 and b >= 0:
                    solutions.append((a, b, c))
            if len(solutions) == 0:
                solutions.append((100, 10, 5))
            
            solution = random.choice(solutions)
            self_weight[1], self_weight[2], self_weight[3] = solution[0], solution[1], solution[2]

        def simulate_scoreline():
            nonlocal matchday_results
            nonlocal game_key
            nonlocal opponent
            
            for key, value in matchday_results.items():
                if team_name in value:
                    game_key = key
                    for team, score in value.items():
                        if team == team_name:
                            pass
                        else:
                            opponent = team

            matchday_results[game_key][team_name] = random.choices(list(range(0,11)), weights = self_weight)[0]
            matchday_results[game_key][opponent] = random.choices(list(range(0,11)), weights = epl_match_engine_weights[team])[0]
            
            att = ['ST', 'LW', 'RW']
            mid = ['CDM', 'CM', 'CAM', 'LM', 'RM']
            defe = ['CB', 'LB', 'RB']
            gk = ['GK']
            
            if tactics[(1, 'GK')]['Position'] != 'GK':
                matchday_results[game_key][opponent] += random.randint(6,10)
            for position, player in tactics.items():
                if position[1] in att:
                    if player['Position'] not in att:
                        matchday_results[game_key][team_name] -= random.randint(1,3)
                        if matchday_results[game_key][team_name] <= 0:
                            matchday_results[game_key][team_name] = 0
                if position[1] in mid:
                    if player['Position'] not in mid:
                        matchday_results[game_key][team_name] -= random.randint(1,2)
                        if matchday_results[game_key][team_name] <= 0:
                            matchday_results[game_key][team_name] = 0
                        matchday_results[game_key][opponent] += random.randint(0,1)
                if position[1] in defe:
                    if player['Position'] not in defe:
                        matchday_results[game_key][opponent] += random.randint(1,3)

        def stage_events():
            nonlocal events

            #setup 'events' dictionary
            fhalf_extra = random.randint(1,6)
            shalf_extra = random.randint(1,6)
            [events.update({f"{i}":''}) for i in range(1,46)]
            [events.update({f"45+{e}":''}) for e in range(1,fhalf_extra+1)]
            [events.update({f"{i}":''}) for i in range(46,91)]
            [events.update({f"90+{e}":''}) for e in range(1,shalf_extra+1)]

            #setup 'self' and 'opponent' pitch_players
            self_pitch_players = {key: value for key, value in tactics.items()}
            for player in self_pitch_players:
                self_pitch_players[player]['Cards'] = 'None'
            temp_opponent_pitch_players = {key: value for key, value in player_database.items() if value['Team'] == opponent}
            temp_opponent_pitch_players = dict(list(temp_opponent_pitch_players.items())[:11])
            for player in temp_opponent_pitch_players:
                temp_opponent_pitch_players[player]['Cards'] = 'None'
            opponent_pitch_players = {}
            for index, (key, value) in enumerate(temp_opponent_pitch_players.items()):
                opponent_pitch_players[(index, f"{value['Position']}")] = value

            #randomise minutes where cards, injuries, goals happen
            temp_events = [key for key in events]
            card_events = {}
            inj_events = {}
            goal_events = {}
            for minute in temp_events:
                team = random.choice([team_name, opponent])
                p = random.random()
                if p < 0.00075: #TESTING: CHANGED FROM 0.00150 TO 0.00075
                    card_events[minute] = (team, 'Red Card')
                    temp_events.remove(minute)
                elif p < 0.024: #TESTING: CHANGED FROM 0.048 TO 0.024
                    card_events[minute] = (team, 'Yellow Card')
                    temp_events.remove(minute)
            for minute in temp_events:
                team = random.choice([team_name, opponent])
                p = random.random()
                if p < 0.003: #TESTING: CHANGED FROM 0.01 TO 0.003 (MINIMISE INJURIES)
                    inj_events[minute] = (team, 'Injury')
                    temp_events.remove(minute)
            for minute in random.sample(temp_events, k=matchday_results[game_key][team_name]):
                goal_events[minute] = (team_name, 'Goal')
                temp_events.remove(minute)
            for minute in random.sample(temp_events, k=matchday_results[game_key][opponent]):
                goal_events[minute] = (opponent, 'Goal')
                temp_events.remove(minute)

            #assign goals, injuries and cards to players on pitch
            for minute in events:
                if minute in card_events:
                    carded_team = card_events[minute][0]
                    card_type = card_events[minute][1]
                    if carded_team == team_name:
                        carded_player = random.choice(list(self_pitch_players))
                        carded_player_name = self_pitch_players[carded_player]['Name']
                        if card_type == 'Red Card':
                            events[minute] = f"Red Card: {carded_player_name} ({team_name})"
                            del self_pitch_players[carded_player]
                        if card_type == 'Yellow Card':
                            if self_pitch_players[carded_player]['Cards'] == 'Yellow':
                                events[minute] = f"Red Card (Second Yellow Card): {carded_player_name} ({team_name})"
                                del self_pitch_players[carded_player]
                            elif self_pitch_players[carded_player]['Cards'] == 'None':
                                events[minute] = f"Yellow Card: {carded_player_name} ({team_name})"
                                self_pitch_players[carded_player]['Cards'] = 'Yellow'
                    elif carded_team == opponent:
                        carded_player = random.choice(list(opponent_pitch_players))
                        carded_player_name = opponent_pitch_players[carded_player]['Name']
                        if card_type == 'Red Card':
                            events[minute] = f"Red Card: {carded_player_name} ({opponent})"
                            del opponent_pitch_players[carded_player]
                        if card_type == 'Yellow Card':
                            if opponent_pitch_players[carded_player]['Cards'] == 'Yellow':
                                events[minute] = f"Red Card (Second Yellow Card): {carded_player_name} ({opponent})"
                                del opponent_pitch_players[carded_player]
                            elif opponent_pitch_players[carded_player]['Cards'] == 'None':
                                events[minute] = f"Yellow Card: {carded_player_name} ({opponent})"
                                opponent_pitch_players[carded_player]['Cards'] = 'Yellow'
                if minute in inj_events:
                    injured_team = inj_events[minute][0]
                    if injured_team == team_name:
                        injured_player = random.choice(list(self_pitch_players))
                        injured_player_name = self_pitch_players[injured_player]['Name']
                        events[minute] = f"Injury: {injured_player_name} ({team_name})"
                        del self_pitch_players[injured_player]
                    if injured_team == opponent:
                        injured_player = random.choice(list(opponent_pitch_players))
                        injured_player_name = opponent_pitch_players[injured_player]['Name']
                        events[minute] = f"Injury: {injured_player_name} ({opponent})"
                        del opponent_pitch_players[injured_player]
                if minute in goal_events:
                    #setup position_classes (used in setting up goal_weights and assist_weights)
                    position_classes = {
                        'CB':'def',
                        'LB':'def',
                        'RB':'def',
                        'CDM':'mid',
                        'CM':'mid',
                        'CAM':'mid',
                        'LM':'mid',
                        'RM':'mid',
                        'LW':'att',
                        'RW':'att',
                        'ST':'att',
                    }

                    #setup goal_pitch_pos_bonus_algo (used in setting up goal weights)
                    goal_pitch_pos_bonus_algo = {
                        'GK':0.01,
                        'CB':3.5,
                        'LB':2.5,
                        'RB':2.5,
                        'CDM':4,
                        'CM':8,
                        'CAM':13,
                        'LM':7,
                        'RM':7,
                        'LW':14,
                        'RW':14,
                        'ST':21
                    }

                    #setup assist_pitch_pos_bonus_algo (used in setting up assist weights)
                    assist_pitch_pos_bonus_algo = {
                        'GK':0.05,
                        'CB':2.5,
                        'LB':8,
                        'RB':8,
                        'CDM':6,
                        'CM':12,
                        'CAM':16,
                        'LM':9,
                        'RM':9,
                        'LW':11,
                        'RW':11,
                        'ST':8
                    }

                    if goal_events[minute][0] == team_name:

                        #setup temp_dict
                        temp_dict = {}
                        for key, value in self_pitch_players.items():
                            temp_dict[key] = value

                        #create goal_weights and assist_weights
                        goal_weights = {}
                        assist_weights = {}

                        #setup goal_weights
                        for key, value in temp_dict.items():
                            ovr_bonus = 3.07 * math.exp(0.1784 * (int(value['OVR']) - 70) + 0.0675 * (30 - 25))
                            #determining pos_fit_bonus
                            if key[1] == value['Position']:
                                pos_fit_bonus = 1
                            elif key[1] in value['Alternative positions'].replace(' ','').split(','):
                                pos_fit_bonus = 0.8
                            elif position_classes[key[1]] == position_classes[value['Position']]:
                                pos_fit_bonus = 0.5
                            else:
                                pos_fit_bonus = 0.2
                            #end
                            goal_pitch_pos_bonus = goal_pitch_pos_bonus_algo[key[1]]
                            goal_weights[key] = ovr_bonus * pos_fit_bonus * goal_pitch_pos_bonus

                        #choose goalscorer, update temp_dict
                        goal_scorer = random.choices(list(temp_dict), weights = list(goal_weights.values()), k=1)[0]
                        del temp_dict[goal_scorer]

                        #setup assist_weights
                        for key, value in temp_dict.items():
                            ovr_bonus = 3.07 * math.exp(0.1784 * (int(value['OVR']) - 70) + 0.0675 * (30 - 25))
                            #determining pos_fit_bonus
                            if key[1] == value['Position']:
                                pos_fit_bonus = 1
                            elif key[1] in value['Alternative positions'].replace(' ','').split(','):
                                pos_fit_bonus = 0.8
                            elif position_classes[key[1]] == position_classes[value['Position']]:
                                pos_fit_bonus = 0.5
                            else:
                                pos_fit_bonus = 0.2
                            #end
                            assist_pitch_pos_bonus = assist_pitch_pos_bonus_algo[key[1]]
                            assist_weights[key] = ovr_bonus * pos_fit_bonus * assist_pitch_pos_bonus

                        #choose assister, update temp_dict
                        assister = random.choices(list(temp_dict), weights = list(assist_weights.values()), k=1)[0]
                        del temp_dict[assister]

                        #update events
                        events[minute] = f"Goal for {team_name} by {self_pitch_players[goal_scorer]['Name']} (Assist: {self_pitch_players[assister]['Name']})"
                                        
                    if goal_events[minute][0] == opponent:
                        #setup temp_dict
                        temp_dict = {}
                        for key, value in opponent_pitch_players.items():
                            temp_dict[key] = value

                        #create goal_weights and assist_weights
                        goal_weights = {}
                        assist_weights = {}

                        #setup goal_weights
                        for key, value in temp_dict.items():
                            ovr_bonus = 3.07 * math.exp(0.1784 * (int(value['OVR']) - 70) + 0.0675 * (30 - 25))
                            #determining pos_fit_bonus
                            if key[1] == value['Position']:
                                pos_fit_bonus = 1
                            elif key[1] in value['Alternative positions'].replace(' ','').split(','):
                                pos_fit_bonus = 0.8
                            elif position_classes[key[1]] == position_classes[value['Position']]:
                                pos_fit_bonus = 0.5
                            else:
                                pos_fit_bonus = 0.2
                            #end
                            goal_pitch_pos_bonus = goal_pitch_pos_bonus_algo[key[1]]
                            goal_weights[key] = ovr_bonus * pos_fit_bonus * goal_pitch_pos_bonus

                        #choose goalscorer, update temp_dict
                        goal_scorer = random.choices(list(temp_dict), weights = list(goal_weights.values()), k=1)[0]
                        del temp_dict[goal_scorer]
                        del goal_weights[goal_scorer]

                        #setup assist_weights
                        for key, value in temp_dict.items():
                            ovr_bonus = 3.07 * math.exp(0.1784 * (int(value['OVR']) - 70) + 0.0675 * (30 - 25))
                            #determining pos_fit_bonus
                            if key[1] == value['Position']:
                                pos_fit_bonus = 1
                            elif key[1] in value['Alternative positions'].replace(' ','').split(','):
                                pos_fit_bonus = 0.8
                            elif position_classes[key[1]] == position_classes[value['Position']]:
                                pos_fit_bonus = 0.5
                            else:
                                pos_fit_bonus = 0.2
                            #end
                            assist_pitch_pos_bonus = assist_pitch_pos_bonus_algo[key[1]]
                            assist_weights[key] = ovr_bonus * pos_fit_bonus * assist_pitch_pos_bonus

                        #choose assister, update temp_dict
                        assister = random.choices(list(temp_dict), weights = list(assist_weights.values()), k=1)[0]
                        del temp_dict[assister]
                        del goal_weights[assister]

                        #update events
                        events[minute] = f"Goal for {opponent} by {opponent_pitch_players[goal_scorer]['Name']} (Assist: {opponent_pitch_players[assister]['Name']})"

        def game_output():
            scoreline_dupe = {}
            for key, value in matchday_results[game_key].items():
                scoreline_dupe[key] = 0
            reference = iter(scoreline_dupe)
            print(f"{next(reference)} VS {next(reference)}")
            

            for key, value in events.items():
                if value == '':
                    print(key + "' ", end='', flush=True)
                    for dot in '.....':
                        print(dot, end='', flush=True)
                        time.sleep(0.001) #TESTING: CHANGE TO 0.3
                    print('')
                elif value != '':
                    if value[:4] == 'Goal':
                        print(key + "' " + value)
                        if value[9:].startswith(team_name):
                            scoreline_dupe[team_name] += 1
                        else:
                            scoreline_dupe[opponent] += 1
                        print('')
                        for key, value in scoreline_dupe.items():
                            print(f"{key}: {value}")
                        print('')
                        for i in range(5):
                            time.sleep(0.001) #TESTING: CHANGE TO 0.3
                    else:
                        print(key + "' " + value)
                        for i in range(5):
                            time.sleep(0.001) #TESTING: CHANGE TO 0.3
            print('')
            print(f"FT")
            reference = matchday_results[game_key]
            teamone = list(reference)[0]
            teamtwo = list(reference)[1]
            print(f"{teamone}  {reference[teamone]}-{reference[teamtwo]}  {teamtwo}")
            print('')

            while True:
                command = input('Press X to continue: ')
                if command == 'X':
                    print('')
                    break

        def update_stats():
            global matchday
            global league_table
            global squad
            global tactics
            global money
            global income

            #update matchday counter for suspensions and injuries
            for key, value in squad.items():
                if value['Suspended'] != False:
                    if value['Suspended'] == 1:
                        squad[key]['Suspended'] = False
                    elif value['Suspended'] != 1:
                        squad[key]['Suspended'] -= 1
                if value['Injured'] != False:
                    if value['Injured'] == 1:
                        squad[key]['Injured'] = False
                    elif value['Injured'] != 1:
                        squad[key]['Injured'] -= 1
            update_tactics()

            #update league table
            for key, scoreline in matchday_results.items():

                teamone = list(scoreline)[0]
                teamtwo = list(scoreline)[1]

                league_table[teamone]['F'] += matchday_results[key][teamone]
                league_table[teamone]['A'] += matchday_results[key][teamtwo]
                league_table[teamtwo]['F'] += matchday_results[key][teamtwo]
                league_table[teamtwo]['A'] += matchday_results[key][teamone]
                if matchday_results[key][teamone] == matchday_results[key][teamtwo]:
                    league_table[teamone]['D'] += 1
                    league_table[teamtwo]['D'] += 1
                elif matchday_results[key][teamone] > matchday_results[key][teamtwo]:
                    league_table[teamone]['W'] += 1
                    league_table[teamtwo]['L'] += 1
                elif matchday_results[key][teamone] < matchday_results[key][teamtwo]:
                    league_table[teamone]['L'] += 1
                    league_table[teamtwo]['W'] += 1

            #update played
            for key, value in tactics.items():
                for keyy, valuee in squad.items():
                    if keyy[1] == value['Name']:
                        squad[keyy]['Played'] += 1
            update_tactics()

            #update injuries, suspensions, goals, assists
            goals_and_assisters = {} #for game overview page later
            suspenders = {} #for game overview page later
            injurers = {} #for game overview page later
            for key, event in events.items():
                if f"({team_name})" in event or f"Goal for {team_name}" in event: #to prevent incidents where players have similiar names to teams eg. Everton
                    if event[:4] == 'Goal':

                        indexx1 = len(team_name) + 13
                        indexx2 = event.find(f" (Assist: ")
                        for key, value in squad.items():
                            if key[1] == event[indexx1:indexx2]:
                                squad[key]['Goals'] += 1
                                if key[1] not in goals_and_assisters:
                                    goals_and_assisters[key[1]] = [0,0]
                                    goals_and_assisters[key[1]][0] += 1
                                else:
                                    goals_and_assisters[key[1]][0] += 1

                        indexx3 = event.find(f" (Assist: ") + 10
                        indexx4 = len(event) - 1
                        for key, value in squad.items():
                            if key[1] == event[indexx3:indexx4]:
                                squad[key]['Assists'] += 1
                                if key[1] not in goals_and_assisters:
                                    goals_and_assisters[key[1]] = [0,0]
                                    goals_and_assisters[key[1]][1] += 1
                                else:
                                    goals_and_assisters[key[1]][1] += 1
                        
                        update_tactics()

                    if event[:11] == 'Yellow Card':
                        pass
                    
                    if event[:9] == 'Red Card:':
                        indexx1 = 10
                        indexx2 = event.find(f" ({team_name})")
                        player = event[indexx1:indexx2]
                        for key, value in squad.items():
                            if key[1] == player:
                                squad[key]['Suspended'] = 3
                                suspenders[key[1]] = 3
                        update_tactics()
                        
                    if event[:30] == 'Red Card (Second Yellow Card):':
                        indexx1 = 31
                        indexx2 = event.find(f" ({team_name})")
                        player = event[indexx1:indexx2]
                        for key, value in squad.items():
                            if key[1] == player:
                                squad[key]['Suspended'] = 1
                                suspenders[key[1]] = 1
                        update_tactics()
                        
                    if event[:6] == 'Injury':
                        indexx = event.find(f"({team_name}") - 1
                        for key, value in squad.items():
                            if key[1] == event[8:indexx]:
                                number = random.randint(1,10)
                                squad[key]['Injured'] = number
                                injurers[key[1]] = number
                        update_tactics()

            #update match earnings
            for key, value in matchday_results.items():
                if team_name in value:
                    if team_name == next(iter(value)):
                        earnings = round((8 / 171) * teams_budget_database[team_name])
                    else:
                        earnings = round((1 / 171) * teams_budget_database[team_name])
            money += earnings
            income += earnings

            #update league ranking on main menu
            update_league_ranking()

            #give summary of game, inclu updated stats
            print('GAME OVERVIEW')
            print('')
            
            if goals_and_assisters != {}:
                for key, value in goals_and_assisters.items():
                    if value[0] != 0 and value[1] == 0:
                        text = f"({value[0]}G)"
                    elif value[0] == 0 and value[1] != 0:
                        text = f"({value[1]}A)"
                    else:
                        text = f"({value[0]}G, {value[1]}A)"
                    print(f"{key} {text}")
                print('')
                
            if suspenders != {}:
                print('SUSPENSIONS')
                for key, value in suspenders.items():
                    print(f"{key} (Out for {value} matchday{'s' if value > 1 else ''})")
                print('')

            if injurers != {}:
                print('INJURIES')
                for key, value in injurers.items():
                    print(f"{key} (Out for {value} matchday{'s' if value > 1 else ''})")
                print('')
                
            print(f"Matchday Income: ${earnings:,}")
            print('')
            while True:
                command = input('Press X to continue: ')
                if command == 'X':
                    print('')
                    break

            #update matchday no.
            matchday += 1
                
        def print_matchday_results():
            print(f"MATCHDAY {matchday-1} RESULTS")
            print('')
            for key, match in matchday_results.items():
                teamone = list(match)[0]
                teamtwo = list(match)[1]
                print(f"{teamone:>30}  {match[teamone]}-{match[teamtwo]}  {teamtwo:<30}")
            print('')

            while True:
                command = input('Press X to continue: ')
                if command == 'X':
                    print('')
                    break

        simulate_other_games()
        calculate_self_rating()
        give_self_weight()
        simulate_scoreline()
        stage_events()
        game_output()
        update_stats()
        print_matchday_results()

    matchday_main_page()

#main code starts here
initilisation()
game_setup()
while True:
    command = main_menu()
    if command == 1:
        squad_page()
    if command == 2:
        tactics_page()
    if command == 3:
        league_page()
    if command == 4:
        fixtures_page()
    if command == 5:
        transfers_page()
    if command == 6:
        finances_page()
    if command == 7:
        training_page()
    if command == 8:
        matchday_page()