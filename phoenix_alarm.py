import threading
import time
from colorama import Fore
import pandas as pd
import random
from ohlc_api import mexi

# Shared state
shared_data = {}
lock = threading.Lock()

# RSI tracking function
def track_rsi(ticker, timeframe, type_pos, set_rsi, start_point, id):
    # print(f"{Fore.CYAN}Started tracking RSI for {ticker} ({type_pos}) with threshold {set_rsi}.{Fore.WHITE}")
    data = mexi(ticker=ticker, limit=10000, timeframe=timeframe)  # Simulated RSI data
    sample = data.loc[start_point:]

    alarm_triggered = False

    # Loop through each index of the sliced data
    for i in sample.index:
        rsi = sample.loc[i]['rsi']

        if type_pos.upper() == 'SHORT' and rsi > set_rsi:
            print(f"{Fore.GREEN}RSI alarm triggered for {ticker} ({type_pos}) on {i}: RSI={rsi:.2f}{Fore.WHITE}")
            alarm_triggered = True
            break
        elif type_pos.upper() == 'LONG' and rsi < set_rsi:
            print(f"{Fore.GREEN}RSI alarm triggered for {ticker} ({type_pos}) on {i}: RSI={rsi:.2f}{Fore.WHITE}")
            alarm_triggered = True
            break

    if alarm_triggered:
        print(f"{Fore.YELLOW}RSI alarm triggered, deleting {ticker} entry with id[{id}].{Fore.WHITE}")
        with lock:
            if ticker in shared_data:
                shared_data[ticker] = [item for item in shared_data[ticker] if item['id'] != id]
                if len(shared_data[ticker]) == 0:
                    del shared_data[ticker]
    else:
        print(f"{Fore.YELLOW}No RSI alarm triggered for {ticker} within the dataset.{Fore.WHITE}")

# Listener function: Listens for user input
def listener():
    while True:
        user_input = input("Enter a Ticker (e.g., TICKER TIMEFRAME TYPE RSI): ").strip()


        if user_input.lower().startswith("delete "):
            _, key_to_delete = user_input.split(maxsplit=1)
            with lock:
                if key_to_delete in shared_data:
                    del shared_data[key_to_delete]
                    print(f"Deleted: {key_to_delete}")
                else:
                    print(f"Key '{key_to_delete}' not found.")

            continue
        
        try:
        
            # Generate a random ID
            random_id = random.randint(1000, 9999)

            # Add ticker entry to shared data with a random ID
            with lock:  # Lock to avoid race conditions

                # Parse input for RSI tracking
                key, timeframe, type_pos, rsi_value = user_input.split()    
                timeframe = int(timeframe)
                rsi_value = float(rsi_value)
                data = mexi(ticker=key, limit=10000, timeframe=timeframe)
                start_point = data.index[-1]

                if key not in shared_data:
                    print(Fore.RED, 'not exist')
                    shared_data[key] = []  # Initialize list for the ticker
    
                # Append new entry for the ticker
                shared_data[key].append({"id": random_id, "timeframe": timeframe, "type_pos": type_pos, "rsi_value": rsi_value, "start_point": start_point})
                print(f"{Fore.GREEN}Added for RSI tracking: {key} -> {shared_data[key][-1]}{Fore.WHITE}")

            # Start tracking RSI in a separate thread
            t = threading.Thread(target=track_rsi, args=(key, timeframe, type_pos, rsi_value, start_point, random_id))
            t.start()
            t.join()  # Ensure we wait for the thread to finish before moving on

            
        except ValueError:
            print(f"{Fore.RED}Invalid input! Use format: TICKER TIMEFRAME TYPE RSI{Fore.WHITE}")


# Processor function: Continuously processes shared data
def processor():
    while True:
        with lock:  # Synchronize access to shared data
            for key, value in shared_data.items():


                ticker, timeframe, type_pos, set_rsi, start_point, id = key, value[0]['timeframe'], value[0]['type_pos'], value[0]['rsi_value'], value[0]['start_point'],value[0]['id']
                track_rsi(ticker, timeframe, type_pos, set_rsi, start_point, id)
                
                for entry in value:
                    print(f"{Fore.LIGHTYELLOW_EX}Processing {Fore.MAGENTA}{key}{Fore.LIGHTYELLOW_EX} with params => T:{entry['timeframe']}| type:{entry['type_pos']}| set_rsi:{entry['rsi_value']}| id:{entry['id']} <= \{Fore.WHITE}")

        time.sleep(5)  # Wait before re-checking

# Main function to start threads
def main():
    listener_thread = threading.Thread(target=listener, daemon=True)
    processor_thread = threading.Thread(target=processor, daemon=True)

    listener_thread.start()
    processor_thread.start()

    listener_thread.join()  # Wait for listener thread to complete

# Run the program
if __name__ == "__main__":
    main()
