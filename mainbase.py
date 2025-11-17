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

#COMMON FUNCTIONS#----------------------------------------------------------------------------------------------------------------------
def sort_squad():
    global squad
    squad = dict(sorted(squad.items(), key=lambda x:(-int(x[1]['OVR']), x[0][1])))

def update_tactics():
    pass
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
            avg = sum(value) / len(value)
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

    setup_player_database()
    setup_teams_budget_database()
    setup_epl_team_database()
    setup_formations_database()
    setup_fixtures_database()
    setup_league_table()

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
                print('-----------------------------------------------------------------')
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

    def set_league_ranking():
        global league_ranking
        global league_table
        league_table = dict(sorted(league_table.items(), key=lambda item: (-item[1]['W']*3 - item[1]['D'], -item[1]['F']+item[1]['A'], item[0])))
        for index, key in enumerate(league_table, 1):
            if key == team_name:
                league_ranking = index

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

    game_setup_firstpage()
    set_squad()
    set_league_ranking()
    set_default_tactics()
    set_transfer_market()
    set_money()


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
        print(f"{'Lineup':<9}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':11}{'OVR':4}")
        print('---------------------------------------------------------------------------------------------------------------------------------------------------')
        for key,value in tactics.items():
            if value == '':
                print(f"{key[1]:<9}")
            else:
                print(f"{key[1]:<9}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{'Yes' if value['Suspended'] else 'No':<13}{'Yes' if value['Injured'] else 'No':<11}{value['OVR']:<4}")     

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
            print('Press the letter on the left to edit each position')
            print('')
            print(f"{'Press':<8}{'Lineup':<9}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':11}{'OVR':4}")
            print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
            for index, (key,value) in enumerate(tactics.items(), 1):
                if value == '':
                    print(f"{index:<8}{key[1]:<9}")
                else:
                    print(f"{index:<8}{key[1]:<9}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{'Yes' if value['Suspended'] else 'No':<13}{'Yes' if value['Injured'] else 'No':<11}{value['OVR']:<4}")
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
        print(f"{'Press':<8}{'Name':<28}{'Position':11}{'Alt Positions':16}{'Nation':22}{'Age':6}{'Played':9}{'Goals':8}{'Assists':10}{'Suspended?':13}{'Injured?':11}{'OVR':4}")
        print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
        for index, (key,value) in enumerate(squad.items(), 1):
            print(f"{index:<8}{value['Name']:<28}{value['Position']:<11}{value['Alternative positions']:<16}{value['Nation']:<22}{value['Age']:<6}{value['Played']:<9}{value['Goals']:<8}{value['Assists']:<10}{'Yes' if value['Suspended'] else 'No':<13}{'Yes' if value['Injured'] else 'No':<11}{value['OVR']:<4}")
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
        print(f"{'POS':<5}{'Team':<30}{'Pl':<3}{'W':<3}{'D':<3}{'L':<3}{'F':<3}{'A':<3}{'GD':<3}{'Pts':<3}")
        print('-------------------------------------------------------------')
        for index, (key, value) in enumerate(league_table.items(), 1):
            print(f"{index:<5}{key:<30}{value['W']+value['D']+value['L']:<3}{value['W']:<3}{value['D']:<3}{value['L']:<3}{value['F']:<3}{value['A']:<3}{value['F']-value['A']:<3}{value['W']*3+value['D']:<3}")
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

def transfers_page():

    def decide_transfer_market_seasonal():
        m = matchday
        while True:
            if m - 1 % 4 == 0:
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
            print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
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
                time.sleep(0.000001)
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
        print('')

        while True:
            command = input('Press X to go back to MAIN MENU: ')
            if command == 'X':
                print('')
                return
            
    training_main_page()



def finances_page():
    print('FINANCES')
    print(f"Income: ${income:.0f}")
    print(f"Expenditure: ${expenditure:.0f}")
    print(f"Net spend: ${income - expenditure:.0f}")
    print('')
    while True:
        command = input('Press X to go back to MAIN MENU: ')
        if command == 'X':
            print('')
            return

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