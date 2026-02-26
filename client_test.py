import requests
import json

BASE_URL = "http://127.0.0.1:8090"

def send_message(to_email: str, subject: str, body: str, from_email: str = None):
    """
    Sends a POST request to the /mail/send endpoint.
    """
    url = f"{BASE_URL}/mail/send"
    payload = {
        "to": to_email,
        "subject": subject,
        "body": body,
        "from_email": from_email
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Successfully sent message:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        if hasattr(e.response, 'text'):
            print(f"Details: {e.response.text}")

def get_all_messages(username: str, password: str):
    """
    Sends a GET request to the /mail/inbox/{username} endpoint.
    """
    url = f"{BASE_URL}/mail/inbox/{username}"
    headers = {
        "X-Password": password
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Successfully retrieved inbox for {username}:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving messages: {e}")
        if hasattr(e.response, 'text'):
            print(f"Details: {e.response.text}")

if __name__ == "__main__":
    # Example usage:
    # 1. Send a message
    print("--- Sending Message ---")
    send_message(
        to_email="vosadchuk@vo.lehrwerkstatt",
        subject="Test from Python Scriptggggggggg",
        body="This is a test body sent from the Python client scrihhhhhpt.",
        from_email="bnerushev@bnerushev.lehrwerkstatt"
    )
    
    print("\n" + "="*30 + "\n")
    
    # 2. Get all messages
    print("--- Getting Inbox ---")
  #  get_all_messages(
  #      username="bnerushev",
  #     password="SicheresPasswort123!"  # Replace with actual password
  #  )
