import requests
import json

def send_discord_alert(webhook_url, message, title, url=None):
    """
    Sends a formatted embed alert message to a Discord webhook.
    """
    if not webhook_url or "YOUR_DISCORD_WEBHOOK_URL" in webhook_url:
        print("--- ALERT (Webhook not configured) ---")
        print(f"Title: {title}\n{message}")
        print("---------------------------------------")
        return

    try:
        data = {
            "content": "",
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": 5814783, # A nice blue color
                    "url": url # This makes the title a clickable link
                }
            ]
        }
        
        response = requests.post(
            webhook_url, 
            data=json.dumps(data), 
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"Successfully sent Discord message: '{title}'")
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord alert: {e}")
