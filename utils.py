import json

def build_auth_file():
    riot_api_key = raw_input("Riot api key:\n")

    auth_info = {
        "riot_api_key": riot_api_key
    }

    print 'Creating auth file...'
    with open('auth.json', 'w') as auth_file:
        json.dump(auth_info, auth_file)
        auth_file.close()


def check_auth():
    try:
        temp = open('auth.json', 'r')
        temp.close()
    except IOError:
        print 'Auth file not found'
        build_auth_file()
    print 'Auth info loaded...'
