# GuardianVPN Telegram Bot

![GuardianVPN](https://user-images.githubusercontent.com/125820963/227031972-c2d5c1ba-9b0d-4b47-9860-c3abc8a0d392.png)

The GuardianVPN Telegram Bot allows users to generate configuration files for OpenVPN and WireGuard servers, which can then be used to connect to servers via the official OpenVPN or WireGuard app. In addition, the bot also enables users to purchase VPN access passes for a selected duration and pay with their preferred payment method. 
## Features
• Telegram integration: Generate VPN configuration files with ease via Telegram  
• VPN protocol support: Connect to OpenVPN and WireGuard servers  
• Payment options: Enable payment processing for VPN access passes with the payment provider token  
• Anti-tracking measures: Integrates Pi-Hole to offer pre-configured filter lists such as EasyList or NoTrack to deliver a tracking-free VPN service  
• Additional command handlers: Provide information about the VPN service for a better user experience  

To learn more about the bot's features, visit the bot at [GuardianVPN](https://t.me/GuardianVPNBot).

## Installation
1. Create a new Telegram bot using [BotFather](https://t.me/BotFather):  
    • Open Telegram and search for BotFather  
    • Type `/start` to start the conversation with BotFather  
    • Type `/newbot` and follow the instructions to create a new bot  
    • BotFather will provide you with a `TELEGRAM_API_TOKEN`. Save it for later use  
2. Clone this repository and navigate to the project directory
3. Create a `.env` file in the project directory and define the necessary variables (`TELEGRAM_API_TOKEN`, `PAYMENT_PROVIDER_TOKEN`) as well as custom file paths. The contents of your `.env` file should look like this:
```python
TELEGRAM_API_TOKEN = 'YOUR_TELEGRAM_API_TOKEN'
PAYMENT_PROVIDER_TOKEN = 'YOUR_PAYMENT_PROVIDER_TOKEN'
OVPN_FILE_PATH = '/path/to/ovpns/files/'
WG_FILE_PATH = '/path/to/configs/files/'
QR_CODE_PATH = '/path/to/qr/code/files/'

```
4. In your existing `config.py` file within the project directory, make sure to adjust the setup accordingly to load and use these environmental variables
   
5. To generate QR codes, you might need to install `qrencode`:
```console
sudo apt-get install qrencode
```
6. If you are installing `PiVPN` or `Pi-Hole`, you can do so with the following commands:
```console
curl -L https://install.pivpn.io | bash
curl -sSL https://install.pi-hole.net | bash
```
For a detailed guide and further information on setting up Pi-Hole and PiVPN, you may check the following guide: [Setting Up PiHole with PiVPN and Unbound](https://blog.crankshafttech.com/2021/03/how-to-setup-pihole-pivpn-unbound.html?m=1).

7. Install the required Python dependencies using pip
```console
pip3 install -r requirements.txt
```
8. Execute the `bot.py` script to run the application:
```console
python3 bot.py
```

Start the bot in Telegram by searching for the bot name and clicking on the `Start` button  

**Note: By default, this project uses PiVPN to configure a VPN server and Pi-Hole for network-wide ad-blocking. However, the code can be modified to include other desired options.**  

**Note: If you install PiVPN, some commands may require root privileges. You have two options:  
• Run commands as root.  
• Use `sudo` with `pexpect`. Uncomment relevant code in `bot.py` and provide your sudo password if necessary. This option is specific to PiVPN installation and may not be needed on all systems.**

## Payment Options

The payment options feature enables users to purchase VPN access passes for a selected duration using their preferred payment method. After payment, the configuration file will be generated. To enable payments in your bot, you will need to set up a payment provider and obtain a payment provider token. Telegram's BotFather provides instructions for setting up payments in your bot.

## Usage
Once the bot is running, users can interact with it by sending commands via Telegram. The available commands are:  
• `/about`: Get information about the bot and its features  
• `/generate_config`: Generate a new configuration file  
• `/getapp`: Get a download link for both OpenVPN and WireGuard apps  
• `/limitations`: Learn about bot's limitations  
• `/privacy`: View privacy policy  
• `/start`: Start the bot and get a welcome message  
• `/status`: Check the status of VPN server  
• `/support`: Contact us  
• `/terms`: Read our terms and conditions  
• `/tutorial`: Instructions on how to use a VPN configuration files  
• `/whatsnew`: Latest updates and improvements  

## Future Development
Here are some ideas for potential future developments for this project:  
• Multiple server locations: Allow users to choose from multiple server locations for their VPN connection  
• User dashboard: Create a customized user dashboard to allow users to manage their subscriptions and settings

## Contributions
Contributions to this project are welcome. If you find a bug or have a feature request, please open an issue on the [GitHub repository](https://github.com/mearashadowfax/GuardianVPN/issues). If you'd like to contribute code, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/mearashadowfax/GuardianVPN/blob/main/LICENSE) file for details.
