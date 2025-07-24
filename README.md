# Telegram-Family-Managment

This repository contains a Telegram bot built using `aiogram`.

## 📌 How to Create a Telegram Bot

1. Open Telegram and search for **BotFather**.
2. Start a chat and send the command:
   ```
   /newbot
   ```
3. Follow the instructions:
   - Choose a name for your bot.
   - Choose a unique username (must end in `bot`).
4. After completion, BotFather will provide a **token**. Save it securely.

## 📦 Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/RarchikCreation/Telegram-Family-Managment.git
   cd Telegram-Family-Managment
   ```

2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root folder of your project and add your bot's token:
   ```
   TOKEN=your-telegram-bot-token
   ```

## 🚀 Running the Bot

Start the bot using:
```sh
python bot.py
```

## 🛠 Technologies Used
- Python
- Aiogram
- Asyncio
- Dotenv
- Selenium
