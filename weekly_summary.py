import os
import yaml
import google.generativeai as genai
import markdown
from datetime import datetime, timedelta, UTC
from pathlib import Path
import alerter
from bs4 import BeautifulSoup

# --- Configuration ---
CONFIG_FILE = "config.yml"
OUTPUT_DIR = Path("docs")
DIGEST_MODEL = "models/gemini-pro-latest"
HISTORY_DAYS = 14



def get_api_keys():
    """Fetches required API keys from environment variables."""
    print("Loading API keys from environment variables...")
    keys = {
        "gemini_key": os.environ.get("GEMINI_API_KEY"),
        "discord_webhook_url": os.environ.get("DISCORD_WEBHOOK_URL"),
        "github_repo_url": os.environ.get("GITHUB_REPO_URL")
    }
    if not all(keys.values()):
        missing = [key for key, value in keys.items() if not value]
        print(f"Error: Missing environment variables: {missing}")
        raise ValueError(f"Missing environment variables: {missing}")
    print("Successfully loaded all API keys.")
    return keys

def get_past_digests_content():
    """Reads the content of index.html from the past 14 days."""
    print(f"Reading news digests from the past {HISTORY_DAYS} days...")
    content = []
    today = datetime.now(UTC).date()
    for i in range(HISTORY_DAYS):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        digest_path = OUTPUT_DIR / date_str / "index.html"
        if digest_path.exists():
            print(f"Reading digest for {date_str}...")
            with open(digest_path, 'r', encoding='utf-8') as f:
                # Use BeautifulSoup to extract the content from the HTML
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Find the div with class "content" and get its text
                content_div = soup.find('div', class_='content')
                if content_div:
                    content.append(f"--- Digest for {date_str} ---\n{content_div.get_text()}\n")
    print(f"Found and read {len(content)} digests.")
    return "".join(content)

def generate_weekly_summary(digests_content, api_key):
    """Generates a weekly summary using the Gemini API."""
    if not digests_content:
        print("No digests content provided, skipping summary generation.")
        return "No news digests found for the past two weeks."

    print("Generating weekly summary with Gemini API...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(DIGEST_MODEL)

    prompt = f"""
    You are a financial news analyst. Your task is to create a concise, informative, and engaging summary of the past two weeks of financial news digests.
    
    Instructions:
    1.  Start with a brief, professional welcome (e.g., "This is your weekly financial summary.").
    2.  Provide a high-level overview of the market trends and sentiment over the past two weeks.
    3.  Identify and summarize the most significant news and events that occurred during this period.
    4.  Group the summary by company/ticker and highlight the key developments for each.
    5.  The tone should be professional, clear, and unbiased.
    6.  **IMPORTANT:** Format your response in Markdown (e.g., use `###` for headlines, `**bold**` for emphasis, and paragraphs).
    
    Here is the raw content from the past two weeks of daily digests:
    ---
    {digests_content}
    ---
    End of raw content. Now, please generate the weekly summary.
    """

    try:
        response = model.generate_content(prompt)
        summary = response.text
        print("Successfully generated weekly summary.")
        return summary
    except Exception as e:
        print(f"Error generating Gemini summary: {e}")
        return None

def main():
    """Main function to run the weekly summary generation process."""
    print("--- Starting Weekly News Summary ---")

    # 1. Get API Keys
    try:
        api_keys = get_api_keys()
    except Exception as e:
        print(f"Failed to load API keys: {e}")
        return

    # 2. Get Past Digests' Content
    digests_content = get_past_digests_content()

    # 3. Generate Weekly Summary
    summary_text = generate_weekly_summary(digests_content, api_keys["gemini_key"])
    if not summary_text:
        print("Failed to generate weekly summary. Exiting.")
        return

    # 4. Save Summary
    today_str = datetime.now(UTC).strftime("%Y-%m-%d")
    target_dir = OUTPUT_DIR / today_str
    target_dir.mkdir(parents=True, exist_ok=True)

    html_path = target_dir / "weekly_summary.html"
    title = f"Weekly Financial Summary - {today_str}"

    print(f"Saving weekly summary to {html_path}...")
    
    content_html = markdown.markdown(summary_text, extensions=['fenced_code', 'tables'])
    final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            background-color: #f6f8fa;
            color: #24292e;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #d1d5da;
        }}
        h1 {{
            color: #0366d6;
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 10px;
        }}
        .content {{
            margin-top: 25px;
        }}
        .content h2, .content h3 {{
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 5px;
        }}
        .content p {{
            margin-bottom: 15px;
        }}
        .content pre {{
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #d1d5da;
            overflow-x: auto;
        }}
        .content blockquote {{
            color: #586069;
            border-left: 4px solid #d1d5da;
            padding-left: 15px;
            margin-left: 0;
        }}
        footer {{
            margin-top: 30px;
            font-size: 0.9em;
            color: #586069;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>

    <div class="content">
        {content_html}
    </div>

    <footer>
        Generated by Stock News Digest Bot
    </footer>
</body>
</html>
"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Successfully saved weekly summary: {html_path}")

    # 5. Send Discord Notification
    try:
        pages_url = f"{api_keys['github_repo_url']}/{today_str}/weekly_summary.html"
        message = "View the latest weekly summary report."
        title = "📈 Your Weekly Financial Summary is Ready!"

        alerter.send_discord_alert(
            api_keys["discord_webhook_url"],
            message,
            title,
            url=pages_url
        )
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

    print("--- Weekly News Summary Finished Successfully ---")

if __name__ == "__main__":
    main()
