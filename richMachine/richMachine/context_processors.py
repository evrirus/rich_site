import json
from django.contrib import messages

def messages_json(request):
    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'level': message.level_tag,
            'message': message.message,
        })
    return {
        'messages_json': json.dumps(message_list)
    }
