import csv

player_database = {}
epl_team_database = {}
formations_database = {}

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

    setup_player_database()
    setup_epl_team_database()
    setup_formations_database()

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

#main code starts here?
initilisation()
game_setup()
while True:
    command = main_menu()