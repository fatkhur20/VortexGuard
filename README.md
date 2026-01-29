# Autonomous Telegram Group Management AI Bot

An autonomous Telegram Group Management AI Bot designed for large-scale groups.

## Features
- **Member Lifecycle Management**: Verification for new members.
- **Auto Moderation**: Spam, scam, and toxicity detection.
- **Anti-Raid**: Join rate monitoring and slow mode.
- **Rule Enforcement**: Progressive escalation (Warn -> Mute -> Kick -> Ban).
- **Logging**: Transparent action logs.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   Create a `.env` file with:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

3. Run the bot:
   ```bash
   python -m src.main
   ```
