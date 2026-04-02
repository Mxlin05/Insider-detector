import requests
import mysql.connector
from mysql.connector import Error
import getpass
import time

def grab_data(connection):
    """
    Grabs trades using Polymarket API. 
    Possible future implementation: args to the function to request specific markets, times, and how many trades in total
    
    Polymarket Trade Data Dictionary Breakdown:
    """
    cursor = connection.cursor()
    url = "https://data-api.polymarket.com/trades" #api url
    
    limit = 1000
    offset = 0
    max_offset = 10000

    while offset <= max_offset:
        params = {
            "limit": limit, 
            "offset": offset
        }

        headers = {"accept": "application/json"} 

        response = requests.get(url, headers=headers, params=params) #wait for response
        if response.status_code == 200:
            trades = response.json()
            if not trades: 
                print("no more trades could be grabbed. Exiting")
                break
            else:
                print(f"Downloaded {len(trades)} trades") 
                
                profile_sql = """
                    INSERT IGNORE INTO profiles 
                    (proxyWallet, pseudonym, name, bio, profileImage, profileImageOptimized)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                trade_sql = """
                    INSERT IGNORE INTO trades 
                    (proxyWallet, side, asset, conditionId, size, price, timestamp, 
                    title, slug, eventSlug, outcome, outcomeIndex, transactionHash, icon)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                profile_buffer = []
                trade_buffer = []
                for trade in trades: #sql calls to insert trades into table
                    
                    profile_values = (
                        trade.get('proxyWallet', 'UNKNOWN'),
                        trade.get('pseudonym', ''),
                        trade.get('name', ''),
                        trade.get('bio', ''),
                        trade.get('profileImage', ''),
                        trade.get('profileImageOptimized', '')
                    )
                    profile_buffer.append(profile_values)

                    trade_values = (
                        trade.get('proxyWallet', 'UNKNOWN'),
                        trade.get('side', ''),
                        trade.get('asset', ''),
                        trade.get('conditionId', ''),
                        trade.get('size', 0.0),
                        trade.get('price', 0.0),
                        trade.get('timestamp', 0),
                        trade.get('title', ''),
                        trade.get('slug', ''),
                        trade.get('eventSlug', ''),
                        trade.get('outcome', ''),
                        trade.get('outcomeIndex', 0),
                        trade.get('transactionHash', ''),
                        trade.get('icon', '')
                    )
                    trade_buffer.append(trade_values)

                cursor.executemany(profile_sql, profile_buffer)
                cursor.executemany(trade_sql, trade_buffer)
                connection.commit()
                offset += limit
                time.sleep(0.5)
                # print("--- Database Planning: Field Breakdown ---")
                # # Grab the first trade as a sample
                # sample = trades[0]
                
                # # Loop through every key and value to show the type and example
                # for key, value in sample.items():
                #     # The : <20 just adds spaces so the columns line up perfectly
                #     print(f"Column: {key: <25} | Python Type: {type(value).__name__: <8} | Example: {value}")
                # print("------------------------------------------\n")
        else:
            print(f"error: {response.status_code}")
            print(response.text)
            break

def create_db():
    """
    creates database if user doesn't already have one
    """

    db_passwd = getpass.getpass("Enter MySQL root password: ") #db password
    cursor = None
    connection = None

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
        if cursor:
            cursor.close()
        return connection


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

    trades = """
        create table if not exists trades (
            id int auto_increment primary key,
            proxyWallet VARCHAR(100),
            side VARCHAR(20),
            asset VARCHAR(100),
            conditionId VARCHAR(100),
            size DECIMAL(18,5),
            price DECIMAL(10,4),
            timestamp BIGINT,
            title text,
            slug VARCHAR(255),
            eventSlug VARCHAR(255),
            outcome VARCHAR(100),
            outcomeIndex INT,
            transactionHash VARCHAR(200),
            icon text,

            foreign key (proxyWallet) references profiles(proxyWallet),
            unique key unique_trade (transactionHash, conditionId, side)
        );
    """ #unique key ensures that there cannot be duplicates of a trade where all 3 hash, market ID, and side is the same

    print("Building and Filling tables with data")
    cursor.execute(profiles)
    cursor.execute(trades)
    print("profile and trades tables have been setup")


if __name__ == "__main__":
    db_conn = create_db()
    if db_conn and db_conn.is_connected(): 
        grab_data(db_conn)
        db_conn.close()
        print("Tables filled and sql connection terminated")
