

import threading
from colorama import Fore



# Shared state
shared_data = {}
lock = threading.Lock()

# Listener function: Listens for user input
def listener():
    while True:
        user_input = input("Enter a Ticker... ").strip()
        try:
            # Check for delete command
            if user_input.lower().startswith("delete "):
                _, key_to_delete = user_input.split(maxsplit=1)
                with lock:  # Synchronize access to shared data
                    if key_to_delete in shared_data:
                        del shared_data[key_to_delete]
                        print(f"Deleted: {key_to_delete}")
                    else:
                        print(f"Key '{key_to_delete}' not found.")
            else:
                # Add key-value pair
                key, value = user_input.split()
                value = float(value)
                
                with lock:  # Synchronize access to shared data
                    shared_data[key] = value
                    print(f"{Fore.GREEN} Added: {key} -> {value} {Fore.WHITE}")
        except ValueError:
            print(f"{Fore.RED}Invalid input!{Fore.WHITE}")

# Processor function: Continuously processes shared data
def processor():
    while True:
        with lock:  # Synchronize access to shared data
            for key, value in shared_data.items():
                print(f"{Fore.LIGHTYELLOW_EX}Processing {key} with value {value} {Fore.WHITE}")
                # Perform some action with the data
                if value < 50:
                    print(f"ALERT: {key} value is below threshold: {value}")
        
        time.sleep(5)  # Wait before re-checking

# Main function to start threads
def main():
    listener_thread = threading.Thread(target=listener, daemon=True)
    processor_thread = threading.Thread(target=processor, daemon=True)
    
    listener_thread.start()
    processor_thread.start()
    
    listener_thread.join()

# Run the program
if __name__ == "__main__":
    main()
