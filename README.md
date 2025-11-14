# Stock News Digest Podcast Bot

This project automates the creation of a daily "podcast" (MP3 audio file)
and a web page to host it. It uses GitHub Actions to run a Python script
once a day. This script:

1. Fetches news from the Alpaca News API.
2. Generates a text digest (in Markdown) of the news using the Gemini API.
3. Generates an audio version of the digest using the Gemini TTS API.
4. Converts the raw .wav audio to a compressed .mp3 file.
5. Creates a simple index.html page to host the text and the audio player.
6. Commits the index.html and podcast.mp3 files to the /docs directory.
7. Sends a notification to a Discord channel with a link to the new digest page.
8. A separate GitHub Action runs monthly to clean up old digests.

## Directory Structure

```
/
├── .github/
│   └── workflows/
│       ├── daily-digest.yml   (GitHub Action to run daily, generate files, and notify)
│       └── cleanup.yml        (GitHub Action to run monthly and delete old files)
├── docs/
│   ├── YYYY-MM-DD/            (New directory created daily)
│   │   ├── index.html         (The web page with text and audio player)
│   │   └── podcast.mp3        (The compressed audio file for the day)
│   └── index.md               (Placeholder for the /docs directory)
├── .gitignore
├── alerter.py                 (Python script to send Discord alerts)
├── config.yml                 (Your configuration file: add/remove stock tickers here)
├── main.py                    (The main Python script: fetches, generates, converts, builds)
├── cleanup.py                 (Python script to delete digests older than 30 days)
└── requirements.txt           (The Python libraries needed for the project)
```

## Setup Instructions

To get this project running in your own repository, follow these steps:

1. Configure Tickers:
   * Open config.yml.
   * Edit the tickers list to include the stock symbols you want to follow.
2. Add Repository Secrets:
   * In your GitHub repository, go to: `Settings > Secrets and variables > Actions`.
   * Click `New repository secret` and add the following four (4) secrets. The project will NOT work without them.
     * `ALPACA_API_KEY`: Your API Key ID from your Alpaca account.
     * `ALPACA_API_SECRET`: Your API Secret Key from your Alpaca account.
     * `GEMINI_API_KEY`: Your API Key for the Gemini API (from Google AI Studio).
     * `DISCORD_WEBHOOK_URL`: The URL for the Discord webhook you want to send notifications to.
3. Enable GitHub Pages:
   * In your GitHub repository, go to: `Settings > Pages`.
   * Under "Build and deployment", set the `Source` to `Deploy from a branch`.
   * Set the `Branch` to `main` (or `master`).
   * Set the `Folder` to `/docs`.Click Save. This will host the contents of your `/docs` directory as a public website.
4. Enable GitHub Actions:
   * The workflows in `.github/workflows/` should be enabled by default. You can check this in the Actions tab of your repository.
   * You can manually run the "Generate Daily News Digest" workflow from the Actions tab to test if your setup is correct.

That's it! The `daily-digest.yml` workflow will now run on its schedule (08:00 UTC by default), and the `cleanup.yml` workflow will run on the 1st of every month.
