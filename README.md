# OPTIFINE CAPE CHECKER ACC

A tool to check if OptiFine accounts have capes associated with them. This script automates the process of logging into OptiFine accounts and checking for cape availability.

## Features

- Batch processing of multiple accounts
- Cloudflare protection bypass
- Colorful terminal output with progress bars
- Detailed statistics on processing time
- Automatic saving of results to separate files

## Requirements

- Python 3.6+
- Google Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/optifine-cape-checker.git
   cd optifine-cape-checker
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure you have Google Chrome installed on your system.

## Usage

1. Create a text file containing OptiFine accounts in the format `email:password`, with one account per line.

2. Run the script:
   ```
   python cape.py
   ```

3. When prompted, enter the path to your accounts file.

4. The script will process each account and display results in real-time.

5. Results will be saved in the `results` folder:
   - `with_cape.txt`: Accounts that have capes
   - `error_accounts.txt`: Accounts with errors or no capes

## Configuration

You can set the Chrome browser path by setting the `CHROME_PATH` environment variable:

- Windows: `set CHROME_PATH=C:\Path\To\Chrome.exe`
- macOS/Linux: `export CHROME_PATH=/path/to/chrome`

## How It Works

The script works by:

1. Reading account credentials from a text file
2. Opening a hidden Chrome browser instance for each account
3. Bypassing Cloudflare protection if present
4. Logging into the OptiFine website
5. Checking if the account has any capes
6. Saving the results to appropriate files

## Code Summary

- `OptifineLoginHandler`: Handles browser automation and login process
- `process_accounts`: Processes a batch file of accounts
- `main`: Entry point for the script

The code uses DrissionPage for browser automation, which is a lightweight alternative to Selenium. It also includes a Cloudflare bypasser to handle protection challenges.

## Troubleshooting

- **Browser Path Issues**: If the script can't find your Chrome browser, set the `CHROME_PATH` environment variable.
- **Cloudflare Bypass Failures**: If you encounter frequent Cloudflare bypass failures, try updating the CloudflareBypasser package.
- **Rate Limiting**: If you're checking many accounts, OptiFine might rate-limit your IP. Consider using a proxy or adding delays between checks.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Use it responsibly and in accordance with OptiFine's terms of service. 
