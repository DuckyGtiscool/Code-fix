from flask import Flask, request, jsonify
import traceback
import requests
import json

app = Flask(__name__)

name_saves = {}

DISCORD_WEBHOOK_URL = ''

def send_to_discord(message):
    data = {'content': message}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

try:
    with open('banwords.txt', 'r') as file:
        ban_words = set(file.read().splitlines())
except Exception as e:
    print(f"Error loading banwords.txt: {str(e)}")
    traceback.print_exc()
    ban_words = set()

try:
    with open('kickwords.txt', 'r') as file:
        kick_words = set(file.read().splitlines())
except Exception as e:
    print(f"Error loading kickwords.txt: {str(e)}")
    traceback.print_exc()
    kick_words = set()

@app.route('/show_ban_words', methods=['GET'])
def show_ban_words():
    return jsonify(list(ban_words))

@app.route('/show_kick_words', methods=['GET'])
def show_kick_words():
    return jsonify(list(kick_words))

@app.route('/', methods=['GET'])
def show_default():
    """Endpoint to retrieve the current state of name_saves."""
    return jsonify(name_saves)

@app.route('/postname', methods=['POST'])
def handle_request():
    """Endpoint to handle POST requests for adding names to name_saves."""
    try:
        data = request.get_json()

        if 'FunctionArgument' not in data or 'name' not in data['FunctionArgument'] or 'forRoom' not in data['FunctionArgument']:
            print("Invalid input format")
            raise ValueError("Invalid input format")

        function_argument = data['FunctionArgument']

        print("Full Args : " + json.dumps(data, indent=2))

        name = function_argument['name']
        for_room = function_argument['forRoom']

        name_saves[name] = for_room

        if any(banned_word in name for banned_word in ban_words):
            result = 2
            ban_message = f"<@&1191249860779843635> BAN WORD DETECTED FOR NAME {name} ({data['CallerEntityProfile']['Lineage']['MasterPlayerAccountId']})"
            send_to_discord(ban_message)
        elif any(kick_word in name for kick_word in kick_words):
            result = 1
            kick_message = f"<@&1191249860779843635> KICK WORD DETECTED FOR NAME {name} ({data['CallerEntityProfile']['Lineage']['MasterPlayerAccountId']})"
            send_to_discord(kick_message)
        else:
            result = 0
            good_message = f"Player with {name} ({data['CallerEntityProfile']['Lineage']['MasterPlayerAccountId']}) has passed the name checker."
            send_to_discord(good_message)

        response_data = {
            'result': result
        }

        print(f"{result} for name {name} for a room is: {for_room}")

        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"Error handling request: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)