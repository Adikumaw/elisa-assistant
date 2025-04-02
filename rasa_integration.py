# rasa_integration.py
import requests

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

def process_command(command, sender="user1"):
    """
    Sends the command to Rasa and gets the response.

    :param command: User's voice command.
    :param sender: Unique sender ID to identify the conversation.
    :return: The response text from Rasa.
    """
    payload = {"sender": sender, "message": command}

    try:
        response = requests.post(RASA_URL, json=payload)
        response_data = response.json()

        if response_data:
            # Get the first message from Rasa (you can modify this if Rasa returns multiple responses)
            print("response" + response)
            return response_data[0]['text']
        else:
            return "Sorry, I didn't understand that."
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to Rasa: {e}")
        return "I'm having trouble connecting to the server."
