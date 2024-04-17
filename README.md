# Price Scraper
## Introduction
Welcome to my price scraper. Written in python, this program is built to be used in the terminal to store webpage links and search them for a product price, then write these prices to a google sheet for easy comparison.

## Features
- **Store links**: save user inputted links into a text file for easy use
- **Edit Links**: easily edit these text files to save and delete links
- **Scrape Prices**: Automatically find product prices from the inputted links
- **Store In a Spreadsheet**: Automatically write prices to a spreadsheet

## Requirements
- Python 3.12
- ezsheets
- requests
- beautifulsoup4
- pyinputplus

## Usage
This program is intended for use by companies looking to keep prices competitive and customers trying to find the best deal on a product.

1. Clone the repository to your local machine.
2. Ensure you have Python installed.
3. Install the required dependencies using pip:
	```
    pip install ezsheets requests beautifulsoup4 pyinputplus
    ```
4. Be sure to add to the same directory (follow https://ezsheets.readthedocs.io/en/latest/)
-  Your credentials file named credentials-sheets.json
-  Your token for Google Sheets named token-sheets.pickle
-  Your token for Google Drive named token-drive.pickle
5. Edit the python file and add your desired google sheet id to line 491
	```
    spreadsheet  =  ezsheets.Spreadsheet("{your spreadsheet id}")
    ```
6. Run the program:
    ```
    python priceScraper.py
    ```
7. Follow the instructions to scrape the prices

## Disclaimer
This program is not 100% accurate and will occasionally grab the wrong price or not find a price. Manual checks will sometimes be required.
