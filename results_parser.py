import json
import os


def get_compiled_data():
    compiled = []
    count = 0
    for file in os.listdir('results'):
        if file.endswith('.json'):
            with open('results/' + file) as json_file:
                count += 1
                data = json.load(json_file)
                compiled.append(data)
    return compiled


def get_total_matches(data):
    total_matches = 0

    for item in data:
        total_matches += len(item)

    return total_matches


def get_elo_diff(data):
    count = 0
    elo_diff_list = []
    for item in data:
        for match_id, match_data in item.iteritems():
            team1_elo = calc_team_elo(match_data['teams']['team1'])
            team2_elo = calc_team_elo(match_data['teams']['team2'])
            elo_diff = abs(team1_elo - team2_elo)
            count += 1
            print 'Match ID: %s\nElo Diff: %s' % (match_id, elo_diff)
            elo_diff_list.append(elo_diff)

    return elo_diff_list

def calc_team_elo(team):
    team_elo = 0
    for player in team:
        if player[1] == "MASTER" or player[1] == "CHALLENGER":
            team_elo += 2500
        elif player[1] == "DIAMOND":
            team_elo += 2000
            if player[2] == "I":
                team_elo += 400
            elif player[2] == "II":
                team_elo += 300
            elif player[2] == "III":
                team_elo += 200
            elif player[2] == "IV":
                team_elo += 100
        elif player[1] == "PLATINUM":
            team_elo += 1500
            if player[2] == "I":
                team_elo += 400
            elif player[2] == "II":
                team_elo += 300
            elif player[2] == "III":
                team_elo += 200
            elif player[2] == "IV":
                team_elo += 100
        team_elo += player[3]

    return team_elo


def get_avg_elo_diff(diff_list):
    total_diff = 0
    matches = 0

    max_diff = max(diff_list)
    min_diff = min(diff_list)
    complete_diff_list = ''
    for match in diff_list:
        matches += 1
        total_diff += match
        complete_diff_list += str(match) + ','
    print 'Average diff over %s matches: %s' % (matches, float(total_diff/matches))
    print 'Minimum diff: %s' % min_diff
    print 'Maximum diff: %s' % max_diff
    with open('elo_diff.csv', 'w+') as outfile:
        outfile.write(complete_diff_list)
    outfile.close()

get_avg_elo_diff(get_elo_diff(get_compiled_data()))