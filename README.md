# GuardianVPN Telegram Bot

![GuardianVPN](https://user-images.githubusercontent.com/125820963/227031972-c2d5c1ba-9b0d-4b47-9860-c3abc8a0d392.png)

This project is a Telegram Bot that allows users to connect to an OpenVPN server and generate configuration files via a Telegram Bot. It also includes some additional command handlers to provide information about the VPN service.

## Features
• Generate VPN configuration files with ease via Telegram Bot  
• Connect to OpenVPN server  
• Additional command handlers to provide information about the VPN service  

## Installation
1. Create a new Telegram bot using BotFather:  
    • Open Telegram and search for BotFather  
    • Type `/start` to start the conversation with BotFathe  
    • Type `/newbot` and follow the instructions to create a new bot  
    • BotFather will provide you with a `TELEGRAM_API_TOKEN`. Save it for later use  
2. Clone this repository and navigate to the project directory
3. Install the required dependencies using `pip install -r requirements.txt`
4. Create a `config.py` file and set the necessary environment variables (`TELEGRAM_API_TOKEN`) 
5. Run `python bot.py` script
6. Start the bot in Telegram by searching for the bot name and clicking on the `start` button  

Note: By default, this project uses PiVPN to configure a VPN server, however, you can modify the code to add your own desired options.

## Usage
Once the bot is running, users can interact with it by sending commands via Telegram. The available commands are:  
• `/about`: Get information about the bot and its features  
• `/generate_config`: Generate a new configuration file  
• `/getapp`: Get a download link for the OpenVPN app  
• `/limitations`: Learn about bot's limitations  
• `/privacy`: View privacy policy  
• `/start`: Start the bot and get a welcome message  
• `/status`: Check the status of VPN server  
• `/support`: Contact us  
• `/terms`: Read our terms and conditions  
• `/tutorial`: Instructions on how to use an OpenVPN config file with the OpenVPN app  
• `/whatsnew`: Latest updates and improvements  

## Future Development
Here are some ideas for potential future developments to this project:  
• Adding Wireguard option: Currently, this bot only supports OpenVPN. However, adding support for the Wireguard VPN protocol could provide users with more options for securing their internet connection.  
• Allow users to choose a country for VPN connection: Currently, this bot connects to a default VPN server. Allowing users to choose a specific country for their VPN connection would give them greater control over their online privacy and security.

## Contributions
Contributions to this project are welcome. If you find a bug or have a feature request, please open an issue on the [GitHub repository](https://github.com/mearashadowfax/GuardianVPN/issues). If you'd like to contribute code, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/mearashadowfax/GuardianVPN/blob/main/LICENSE) file for details.
