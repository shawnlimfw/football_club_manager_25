import csv

team_ratings = {num:{} for num in range(16,22)}
main_sort = {num:[] for num in range(1,21)}
main_probability = {num:{} for num in range(1,21)}
sorted_weights = {num:[] for num in range(1,21)}

def obtain_team_ratings():
    global team_ratings

    for i in range(16, 22):
        with open(rf"C:\Users\admin\Desktop\fifa\match_engine\{i}test.txt", 'r') as file:
            for line in file:
                line = line.strip()
                index = line.index(f"FIFA {i}")
                line1 = line.split(' ')
                team_ratings[i][line[:index-1]] = line1[-1][-2:]

def sort_team_ratings():
    global team_ratings
    for i in range(16, 22):
        for index, (key, value) in enumerate(team_ratings[i].items(), 1):
            team_ratings[i][key] = (value, index)

def pair_results_to_main_sort():
    global main_sort

    for season in range(16,22):
        with open(rf"C:\Users\admin\Desktop\fifa\match_engine\{season-1}-{season}.csv", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                first_position = team_ratings[season][row[2]][1]
                second_position = team_ratings[season][row[4]][1]
                score_split = row[3].split('-')
                first_goal = score_split[0]
                second_goal = score_split[1]
                main_sort[first_position].append(first_goal)
                main_sort[second_position].append(second_goal)

def derive_main_probability():
    global main_probability
    for key, index in main_sort.items():
        for goal in index:
            if goal not in main_probability[key]:
                main_probability[key][goal] = 1
            else:
                main_probability[key][goal] += 1

def set_sorted_weights():
    global sorted_weights
    
    for key, value in main_probability.items():
        for i in range(0, 11):
            if f"{i}" in value:
                sorted_weights[key].append(value[f"{i}"])
            else:
                sorted_weights[key].append(0)

def write_csv_file():
    with open("sorted_weights.csv", "w", encoding="utf-8") as f:
        for key, value in sorted_weights.items():
            output = ''
            for number in value:
                output += str(number) + ','
            f.write(f"{key},{output[:-1]}\n")


obtain_team_ratings()
sort_team_ratings()
pair_results_to_main_sort()
derive_main_probability()
set_sorted_weights()
write_csv_file()