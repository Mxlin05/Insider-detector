import requests
import mysql.connector
from mysql.connector import Error
import getpass

def grab_data():
    """
    Grabs trades using Polymarket API. 
    Possible future implementation: args to the function to request specific markets, times, and how many trades in total
    
    Polymarket Trade Data Dictionary Breakdown:
    
    --- CORE TRADER IDENTIFIERS (Who is trading?) ---
    proxyWallet:     Their crypto wallet address. Used to track a single user across the whole platform. 
                     Example: '0x54a296be2fe3965b2adda449659a985b4dd25a4a'
    pseudonym:       Their display name on Polymarket. 
                     Example: 'Able-Windshield'
    name:            A backend ID that combines their wallet and account creation time. 
                     Example: '0x54a296be2FE3965b2AdDa...-1771707519343'
    bio / profileImage: User profile text and picture. 
                     Example: '' (Usually blank unless they manually set one up).
    
    --- THE TRADE MATH (What exactly did they do?) ---
    side:            Did they buy new shares or sell old ones? 
                     Example: 'BUY'
    size:            Volume. How many shares they traded. 
                     Example: 4.91177
    price:           Cost per share (in dollars). 
                     Example: 0.43 (Meaning they paid 43 cents per share)
    outcome:         What they actually bet on happening. 
                     Example: 'Up' (or 'Yes', 'Biden', etc.)
    outcomeIndex:    The backend number for that outcome (usually 0 or 1). 
                     Example: 0
    
    --- MARKET IDENTIFIERS (What market are they betting in?) ---
    title:           The plain English name of the bet. 
                     Example: 'Bitcoin Up or Down - March 30, 10:25PM-10:30PM ET'
    slug:            The URL name used for the specific market. 
                     Example: 'btc-updown-5m-1774923900'
    eventSlug:       The URL name for the broader overarching event. 
                     Example: 'btc-updown-5m-1774923900'
    conditionId:     The market's unique hex ID on the blockchain. 
                     Example: '0x687959a1a3a63bbad24d6a3221d1218cf567d22e09b83c76a9a7f9327863b89f'
    asset:           The massive token ID number for this specific contract. 
                     Example: '49308335820357757463163602967684805595944642481576126048...'
    icon:            The image link for the market's logo. 
                     Example: 'https://polymarket-upload.s3.us-east-2.amazonaws.com/BTC+fullsize.png'
    
    --- TIMING & BLOCKCHAIN TRACING (When did it happen?) ---
    timestamp:       The exact Unix time the trade executed. 
                     Example: 1774924091
    transactionHash: The blockchain receipt ID. You can search this on PolygonScan.com to see the raw crypto transaction. 
                     Example: '0x91dc814ea62ad0fc9feb0b5d25b81f5e1bdab153d6e340d07c2ca37605cadac6'

    """
    url = "https://data-api.polymarket.com/trades" #api url

    params = {
        "limit": 100, #100 trades
    }

    headers = {"accept": "application/json"} 
    print("grabbing 100 trades on polymarket today")

    response = requests.get(url, headers=headers, params=params) #wait for response
    if response.status_code == 200:
        trades = response.json()
        print(f"Downloaded {len(trades)}")
        if trades: 
            print("--- Database Planning: Field Breakdown ---")
            # Grab the first trade as a sample
            sample = trades[0]
            
            # Loop through every key and value to show the type and example
            for key, value in sample.items():
                # The : <20 just adds spaces so the columns line up perfectly
                print(f"Column: {key: <25} | Python Type: {type(value).__name__: <8} | Example: {value}")
            print("------------------------------------------\n")
    else:
        print(f"error: {response.status_code}")
        print(response.text)

def create_db():
    """
    creates database if user doesn't already have one
    """

    db_passwd = getpass.getpass("Enter MySQL root password: ") #db password

    try: 
        connection = mysql.connector.connect( #connect to db
            host='localhost',
            user='root',
            password=db_passwd
        )

        if connection.is_connected(): #try to make database if it doesn't exist
            cursor = connection.cursor() #cursor is messenger between linux and sql
            cursor.execute("create database if not exists insideDB;") #make it if it doesn't exist
            print("Success: 'insideDB' is setup!")
            
            cursor.execute("use insideDB") 
            print("Using insideDB")
            
            create_tables(cursor)
    except Error as e:
        print(f"mysql error: {e}")
    finally:
        if "connection" in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")


def create_tables(cursor):
    """
    creates the tables to store all trade and profile data
    """
    profiles = """
        create table if not exists profiles (
            proxyWallet VARCHAR(100) PRIMARY KEY,
            pseudonym VARCHAR(150),
            name VARCHAR(255),
            bio TEXT,
            profileImage TEXT,
            profileImageOptimized TEXT
        );
    """

    

if __name__ == "__main__":
    create_db()
    grab_data()
