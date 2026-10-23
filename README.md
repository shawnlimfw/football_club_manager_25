# Football Club Manager 25

A text-based Premier League management game written in Python. Pick one of the 20 EPL clubs, set your tactics, trade players, train your squad and manage your budget across a full 38-matchday season, while the match engine decides results using probabilities derived from real Premier League scorelines.

Built with the Python standard library only (no external packages), as a personal project from November 2025 to January 2026.

## Features

- **Squad management:** view your squad sorted by rating, with injuries and suspensions shown
- **Tactics:** choose a formation (for example 4-3-3, 3-5-2, 4-1-2-1-2), set a mentality, and pick your starting XI by position
- **League season:** a 38-matchday fixture list and a live league table that updates after every matchday
- **Transfers:** buy and sell players in a transfer market that refreshes every few matchdays, with prices based on player rating and age
- **Training:** train each matchday to improve players, with a bigger boost for young players
- **Finances:** each club starts with a realistic budget, and money changes with transfers and results
- **Matchday simulation:** minute-by-minute commentary with goals, assists, yellow and red cards, injuries and suspensions
- **Season summary:** a final league table and your finishing position at the end of the season

## How it works

### Data-driven match engine

The scoreline of each match is not hard-coded. It is sampled from probability distributions built from real data, using the scripts in `match_engine/`:

1. Real Premier League scorelines from the 2015/16 to 2020/21 seasons are matched with each team's FIFA team rating for that season.
2. Teams are ranked from 1 to 20 by rating in each season, and the number of goals scored by the team at each rank is counted across all matches.
3. The counts are saved to `sorted_weights.csv`: one row per rank, one column per goal tally (0 to 10).
4. During the game, each team's rating rank selects a row of weights, and the number of goals is drawn with `random.choices`.

As a result, stronger teams win more often, but upsets still happen. Goal scorers and assisters are then chosen with weights based on player rating and position.

### Team and player ratings

- A team's rating is the average rating of its best 11 available players, and it updates when you change your lineup or buy and sell players.
- Player market value is modelled as an exponential function of rating and age:

  `value = 3.07 * exp(0.1784 * (OVR - 70) + 0.0675 * (30 - age))` (in millions)

## Getting started

**Requirements:** Python 3 (no extra packages needed).

```
git clone https://github.com/shawnlimfw/football_club_manager_25.git
cd football_club_manager_25
python mainbase.py
```

Run the game from the repository folder, because it reads its data files using relative paths.

### How to play

1. Choose a team and confirm it.
2. Use the main menu to go to **Squad**, **Tactics**, **League**, **Fixtures**, **Transfers**, **Finances**, **Training** and **Matchday**.
3. Set a full lineup in **Tactics** before playing. The game will not let you play a match with an incomplete lineup or with injured or suspended players.
4. Choose **Matchday** to play the next fixture. The other fixtures that matchday are simulated automatically.
5. After matchday 38, the season-end page shows the final table.

An example match is in [`example_game_output.txt`](example_game_output.txt).

## Project structure

```
mainbase.py               Main game (run this)
mainbase_fast_copy.py     Faster copy with a preset lineup and shorter delays, for testing
formations.csv            Formation layouts
all_players.csv           Full player ratings dataset (raw)
filtered_male_players.csv Cleaned dataset used by the game
teams_budget.csv          Club budget data (raw)
filtered_teams_budget.csv Cleaned club budgets used by the game
sorted_weights.csv        Goal probability weights used by the match engine
match_engine/             Scripts and data used to build sorted_weights.csv
global_check.py           Helper script that checks for undeclared global variables
future_developments.txt   Planned improvements
```

## Data

- **Player ratings:** EA Sports FC 25 player ratings. All rights belong to their owners, and this project is for educational purposes only.
- **Match results:** real Premier League results, 2015/16 to 2020/21. Source: [add source].
- **Team ratings:** FIFA 16 to FIFA 22 team ratings. Source: [add source].

## Limitations and future work

- The match engine is less realistic for lower-rated teams (average rating below about 75), because the weights come from top-flight data only.
- Only the Premier League is supported, and there is no save and load.
- The game does not yet show past results, and mentality does not yet affect match outcomes.
- The code is currently one large file that uses global state. Planned work includes splitting it into modules and adding automated tests.

Planned features are listed in [`future_developments.txt`](future_developments.txt).

## Built with

Python 3: `csv`, `random`, `math`, `statistics`, `time` (standard library only).
