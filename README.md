# GuardianVPN Telegram Bot

![GuardianVPN](https://user-images.githubusercontent.com/125820963/227031972-c2d5c1ba-9b0d-4b47-9860-c3abc8a0d392.png)

This project is a Telegram Bot that allows users to connect to an OpenVPN server and generate configuration files via a Telegram Bot. It also includes some additional command handlers to provide information about the VPN service.

## Features
• Generate client configuration files via Telegram Bot  
• Connect to OpenVPN server  
• Additional command handlers to provide information about the VPN service  

## Installation
1. Create a new Telegram bot using BotFather
2. Clone the repository
3. Install the required dependencies using `pip install -r requirements.txt`
4. Create a `config.py` file and set the necessary environment variables (`TELEGRAM_API_TOKEN`) 
5. Run `python bot.py` script
6. Start the bot in Telegram by searching for the bot name and clicking on the `start` button

## Usage
Once the bot is running, users can interact with it by sending commands via Telegram. The available commands are:  
• `/about`: Get information about the bot and its features
• `/generate_config`: Generate a new configuration file
• `/getapp`: Get a download link for the OpenVPN app
• `/limitations`: Learn about bot's limitations
• `/privacy`: View privacy policy
• `/start`: Start the bot and get a welcome message
• `/status`: Check the status of VPN connection
• `/support`: Contact us
• `/terms`: Read our terms and conditions
• `/tutorial`: Instructions on how to use an OpenVPN config file with the OpenVPN app
• `/whatsnew`: Latest updates and improvements  

## Contributions
Contributions to this project are welcome. If you find a bug or have a feature request, please open an issue on the GitHub repository. If you'd like to contribute code, please fork the repository and submit a pull request.
