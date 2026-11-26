# Telegram AI assistant bot

Your own AI assistant on Telegram, written in Python. It remembers your chat (separately for each chat),
reads photos (send a bill and ask for the total), has a `/reset` command, and answers only you.
Built with python-telegram-bot and Gemini through OpenRouter.

## Files

- `brain.py`: the AI part. It sends the chat history (the last 20 messages) plus a system prompt to
  Gemini through OpenRouter, keeps one history per chat id, and turns photos into base64 for the model.
  Run `python brain.py` to test it in the terminal.
- `bot.py`: the Telegram part. Handlers for `/start`, `/reset`, text and photos, and a check that only
  `ALLOWED_USER_ID` can use the bot. It imports `ask` and `reset` from `brain.py`.

## Run it

1. Create a bot with [@BotFather](https://t.me/BotFather) (`/newbot`) and copy the token.
2. Get an OpenRouter key at https://openrouter.ai/keys.
3. Find your Telegram user id: send your bot a message, then open
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` and look at `message.from.id`.

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in the three values
python bot.py
```

The bot runs while this terminal is open. Run only one copy at a time: two copies polling the same
token get a Conflict error.
