import time
import random
import threading
import pandas as pd
from queue import Queue
from gmail import gmail
from colorama import Fore
from ohlc_api import mexi, forex
from concurrent.futures import ThreadPoolExecutor

# Shared state
shared_data = {}
lock = threading.Lock()

# Thread pool executor
executor = ThreadPoolExecutor(max_workers=10)  # Adjust max_workers as needed

# Queue for input processing
input_queue = Queue()

forex_pair = [
    "GBPUSD",
    "EURUSD",
    "AUDUSD",
    "USDCAD",
    "USDJPY",
    "GBPJPY",
    "NZDUSD",
    "XAUUSD",
]


def show_the_list():
    for key, value in shared_data.items():
        print(
            f" {Fore.BLUE} Key: {key} {Fore.WHITE} has {Fore.RED}{len(value)} {Fore.WHITE} items \n "
        )


def define_symbol_market_data(ticker, timeframe):
    try:

        if ticker.upper() in forex_pair:
            data = forex(ticker=f"{ticker}=X", timeframe=5)
        else:
            data = mexi(ticker=ticker, limit=10000, timeframe=timeframe)

        if len(data) != 0:

            return data
        else:
            print(
                Fore.RED(),
                "data_fetching got an error",
                Fore.WHITE(),
            )
    except:
        print(Fore.RED(), "we have an error with defining ticker_name!!!", Fore.WHITE())


# RSI tracking function
def track_rsi(ticker, timeframe, type_pos, set_rsi, start_point, id):
    try:

        # Simulate fetching RSI data
        data = define_symbol_market_data(ticker=ticker, timeframe=timeframe)
        sample = data.loc[start_point:]

        alarm_triggered = False

        # Loop through each index of the sliced data
        for i in sample.index:

            rsi = sample.loc[i]["rsi"]

            if type_pos.upper() == "SHORT" and rsi >= set_rsi:
                print(
                    f"{Fore.GREEN}RSI alarm triggered for {ticker} ({type_pos}) on {i}: RSI={rsi:.2f}{Fore.WHITE}"
                )
                alarm_triggered = True
                break
            elif type_pos.upper() == "LONG" and rsi <= set_rsi:
                print(
                    f"{Fore.GREEN}RSI alarm triggered for {ticker} ({type_pos}) on {i}: RSI={rsi:.2f}{Fore.WHITE}"
                )
                alarm_triggered = True
                break

        if alarm_triggered:
            print(
                f"{Fore.GREEN}RSI alarm triggered, deleting {ticker} entry with id[{id}].{Fore.WHITE}"
            )
            with lock:
                # Send email for more information and further investigation
                gmail(ticker=ticker, pos_type=type_pos, rsi=set_rsi)

                # Delete the triggered alarm
                if ticker in shared_data:
                    shared_data[ticker] = [
                        item for item in shared_data[ticker] if item["id"] != id
                    ]
                    if len(shared_data[ticker]) == 0:
                        del shared_data[ticker]
        else:
            print(
                f"{Fore.YELLOW}No RSI alarm triggered for {ticker} within the dataset.{Fore.WHITE}"
            )

    except Exception as e:
        print(f"{Fore.RED}Error in track_rsi for {ticker}: {e}{Fore.WHITE}")


# Listener function: Enqueue user inputs
def listener():
    while True:

        user_input = input("Enter a Ticker (e.g., TICKER TIMEFRAME TYPE RSI): ").strip()
        input_queue.put(user_input)


# Worker function: Process inputs from the queue
def worker():
    while True:
        user_input = input_queue.get()  # Get the next input
        if user_input.lower().startswith("delete "):
            _, key_to_delete = user_input.split(maxsplit=1)
            with lock:
                if key_to_delete in shared_data:
                    del shared_data[key_to_delete]
                    print(f"Deleted: {key_to_delete}")
                else:
                    print(f"Key '{key_to_delete}' not found.")

        elif user_input.startswith("show"):
            show_the_list()
        else:
            try:
                random_id = random.randint(1000, 9999)
                with lock:
                    key, timeframe, type_pos, rsi_value = user_input.split()
                    timeframe = int(timeframe)
                    rsi_value = float(rsi_value)

                    data = define_symbol_market_data(ticker=key, timeframe=timeframe)
                    start_point = data.index[-1]

                    if key not in shared_data:
                        shared_data[key] = []

                    shared_data[key].append(
                        {
                            "id": random_id,
                            "timeframe": timeframe,
                            "type_pos": type_pos,
                            "rsi_value": rsi_value,
                            "start_point": start_point,
                        }
                    )

                    # for values in shared_data[key]:
                    #     print("T", values[0]["timeframe"])

                    # print(
                    #     f"{Fore.GREEN}Added for RSI tracking: {key} ->👇\n"
                    #     f" T: {shared_data[key]['timeframe']}   {Fore.WHITE}"
                    # )

                # Submit the tracking task to the thread pool
                executor.submit(
                    track_rsi,
                    key,
                    timeframe,
                    type_pos,
                    rsi_value,
                    start_point,
                    random_id,
                )

            except ValueError:
                print(
                    f"{Fore.RED}Invalid input! Use format: TICKER TIMEFRAME TYPE RSI{Fore.WHITE}"
                )

        input_queue.task_done()


# Function to display shared_data periodically
def display_shared_data():
    while True:
        with lock:
            if shared_data:
                print(f"{Fore.CYAN}Currently processing shared_data:{Fore.WHITE}")
                for key, value in shared_data.items():

                    if len(value) <= 1:
                        print(
                            f"{Fore.MAGENTA} {key}[{len(value)}] -> {Fore.WHITE}👇 \n"
                            f"{Fore.LIGHTGREEN_EX}T:{Fore.WHITE}{value[0]['timeframe']}{Fore.LIGHTRED_EX} |Type{Fore.WHITE}: {value[0]['type_pos']} |Id: {value[0]['id']} |Rsi: {value[0]['rsi_value']}"
                        )

                    else:
                        print(
                            f"{Fore.MAGENTA} {key}[{len(value)}n] -> {Fore.WHITE}👇 \n"
                        )
                        for index, i in enumerate(value):
                            print(
                                f"{Fore.LIGHTGREEN_EX}T:{Fore.WHITE} {i['timeframe']}{Fore.LIGHTRED_EX} |Type{Fore.WHITE}: {i['type_pos']} |Id: {i['id']} |Rsi: {i['rsi_value']}"
                            )

            else:
                print(f"{Fore.CYAN}No data currently being processed.{Fore.WHITE}")
        time.sleep(5 * 12)  # Adjust the interval for how often to display


# Scheduler function: Periodically re-run track_rsi tasks
def scheduler():
    while True:
        with lock:
            print("processing!")
            for ticker, entries in shared_data.items():
                for entry in entries:
                    executor.submit(
                        track_rsi,
                        ticker,
                        entry["timeframe"],
                        entry["type_pos"],
                        entry["rsi_value"],
                        entry["start_point"],
                        entry["id"],
                    )
        time.sleep(5 * 60)  # Run every 5 seconds


# Main function: Start the listener, worker, display, and scheduler threads
def main():
    listener_thread = threading.Thread(target=listener, daemon=True)
    worker_thread = threading.Thread(target=worker, daemon=True)
    display_thread = threading.Thread(
        target=display_shared_data, daemon=True
    )  # New thread for displaying shared_data
    scheduler_thread = threading.Thread(
        target=scheduler, daemon=True
    )  # New thread for scheduling tasks

    listener_thread.start()
    worker_thread.start()
    display_thread.start()  # Start the display thread
    scheduler_thread.start()  # Start the scheduler thread

    listener_thread.join()
    worker_thread.join()
    display_thread.join()
    scheduler_thread.join()


# Run the program
if __name__ == "__main__":
    main()
