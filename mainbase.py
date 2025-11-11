import csv
import random

player_database = {}
epl_team_database = {}
formations_database = {}
fixtures_database = {}

team_name = ''
squad = {}

money = 0
league_ranking = 1
matchday = 1


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
            avg = sum(value) / len(value)
            epl_team_database[key] = round(avg, 1)

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

    setup_player_database()
    setup_epl_team_database()
    setup_formations_database()
    setup_fixtures_database()

def game_setup():

    def game_setup_firstpage():
        global team_name
        print('')
        print('Welcome to Football Manager 2025!')
        print('To continue, please choose a team.')
        while True:
            try:
                print('')
                print(f"{'Press:':8}{'Team':25}{'Rating'}")
                print('-------------------------------------------------------------------------')
                placeholder = [key for key in epl_team_database]
                placeholder.sort()
                for index, key in enumerate(placeholder, 1):
                    print(f"{index:<8}{key:25}{epl_team_database[key]}")
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

    game_setup_firstpage()
    set_squad()

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
    print(f"Finances: {money}")
    print(f"League Position: {league_ranking}")
    print(f"Matchday {matchday}")
    print('')
    while True:
        try:
            print(f"{'Press:':8}{'Command:':25}")
            print('------------------------------------')
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
    print(f"{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':11}{'OVR':4}")
    print('--------------------------------------------------------------------------------------------------------------------------------------------')
    for key,value in squad.items():
        print(f"{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{'Yes' if value['Suspended'] else 'No':<13}{'Yes' if value['Injured'] else 'No':<11}{value['OVR']:<4}")
    print('')
    while True:
        if input('Press X to go back to MAIN MENU: ') == 'X':
            print('')
            return

def fixtures_page():

    def fixtures_main_page():
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
        print('--------------------------------------------------------------------')
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


#main code starts here?
initilisation()
game_setup()
while True:
    command = main_menu()
    if command == 1:
        squad_page()
    if command == 4:
        fixtures_page()