import riotwatcher
from riotwatcher import RiotWatcher
import json
import time
import utils

utils.check_auth()

api_key = json.load(open('auth.json'))['riot_api_key']

w = RiotWatcher(api_key)


def parse_league(league, tier):
    player_id = league.get('playerOrTeamId')
    player = {
        'tier': tier,
        'division': league.get('division'),
        'lp': league.get('leaguePoints'),
        'player_name': league.get('playerOrTeamName')
    }

    return player_id, player


def get_master_challenger_players():
    challenger = w.get_challenger(region='na', queue='RANKED_SOLO_5x5')
    master = w.get_master(region='na', queue='RANKED_SOLO_5x5')
    master_challenger_players = {}

    for league_c in challenger['entries']:
        tier = challenger.get('tier')
        (player_id, player) = parse_league(league_c, tier)
        master_challenger_players[player_id] = player
    for league_m in master['entries']:
        tier = master.get('tier')
        (player_id, player) = parse_league(league_m, tier)
        master_challenger_players[player_id ] = player

    return master_challenger_players


def get_match_players(summonerId):
    try:
        current_match = w.get_current_game(summonerId)
    except riotwatcher.LoLException as err:
        if err == 'Game data not found':
            return '', None, '', ''
        else:
            print err
            return '', None, '', ''

    players = []
    match_id = current_match['gameId']
    queue = current_match.get('gameQueueConfigId', None)
    game_start_time = current_match['gameStartTime']

    for item in current_match['participants']:
        if item.get('summonerId') is not None:
            playerId = item.get('summonerId')
        if item.get('teamId') is not None:
            teamId = item.get('teamId')

        players.append([playerId, teamId])

    return players, match_id, queue, game_start_time


def get_league_info(id_string):
    for i in range(5):
        try:
            rankings = w.get_league_entry([id_string])
            break
        except riotwatcher.LoLException as err:
            print err
            time.sleep(1)
            pass

    player_dto = {}

    for id, info in rankings.iteritems():
        tier = info[0]['tier']
        division = info[0]['entries'][0]['division']
        lp = info[0]['entries'][0]['leaguePoints']

        player_dto[int(id)] = {'tier': str(tier), 'division': str(division), 'lp': lp}

    return player_dto


def parse_match(player_info, player_list, count1, count2):
    team1 = []
    team2 = []
    id_string = ''
    for player in player_info:
        player_id = player[0]
        id_string += str(player_id) + ','

    player_dto = get_league_info(id_string)
    count1 += 1
    count2 += 1

    for player in player_info:

        if player[1] == 100:
            team1.append([player[0], player_dto[player[0]]['tier'], player_dto[player[0]]['division'], player_dto[player[0]]['lp']])
        else:
            team2.append([player[0], player_dto[player[0]]['tier'], player_dto[player[0]]['division'], player_dto[player[0]]['lp']])

    if len(team1) != 5 and len(team2) != 5:
        raise ValueError('Team size is incorrect')

    return team1, team2, count1, count2


def build_output(output_data, player, player_list, count1, count2):
    print 'Player: %s' % player
    (player_info, match_id, queue, game_start) = get_match_players(player)

    if match_id != None:
        if queue == 410:
            if match_id not in output_data.keys():
                (team1, team2, count1, count2) = parse_match(player_info, player_list, count1, count2)
                output = {
                    'time': game_start,
                    'teams': {'team1': team1, 'team2': team2}
                }
            else:
                output = None
        else:
            output = None
    else:
        output = None
    return match_id, output, count1, count2


def flow():
    player_list = get_master_challenger_players()
    output_data = {}
    to_run = len(player_list)
    count1 = 2
    count2 = 2
    total_run = 0

    for player in player_list.keys():
        (match_id, output, count1, count2) = build_output(output_data, player, player_list, count1, count2)
        print "Loaded output for %s" % match_id
        print output
        if output != None:
            print "Appended %s to output_data" % match_id
            output_data[match_id] = output
        count1 += 1
        count2 += 1
        total_run += 1

        if count1 >= 9:
            print 'Sleeping for 8s. Zzzz...'
            print '%s of %s completed' % (total_run, to_run)
            time.sleep(8)
            count1 = 0
        if count2 >= 499:
            print 'Sleeping for 100s. Zzzz...'
            print '%s of %s completed' % (total_run, to_run)
            time.sleep(100)
            count1 = 0
            count2 = 0

    current_time = int(time.time())
    print 'Writing output to file: %s.json' % current_time
    with open('results/%s.json' % current_time, 'w+') as outfile:
        json.dump(output_data, outfile)
    outfile.close()
    print 'Done!'

def run():
    while True:
        flow()
        time.sleep(2700)

run()
