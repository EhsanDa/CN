import json
import threading
from utils.handshake import *
from utils.keyReader import *
from utils.sendmessage import *

def roll_dices():
    message = "roll dice"
    x = {
        "command": message
    }
    y = json.dumps(x)
    response = send_message(y)
    data = json.loads(response)
    # Access the rolls
    rolls = data['result']
    
    return rolls