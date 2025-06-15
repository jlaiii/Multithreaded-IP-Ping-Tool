import threading
import random
import time
import subprocess
import os
import sys
from collections import deque

GREEN = '\033[92m'
RED = '\033[91m'
ENDC = '\033[0m'

online_ips_global_storage = []
recent_pings = deque(maxlen=20)
current_data_lock = threading.Lock()

total_scanned_count = 0
total_online_count = 0
total_offline_count = 0

stop_event = threading.Event()

start_time = 0

MAX_CONCURRENT_PINGS = 100
DISPLAY_UPDATE_INTERVAL = 0.1

def install_ping3():
    try:
        import ping3
        print("ping3 is already installed.")
    except ImportError:
        print("ping3 not found. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ping3"])
            print("ping3 installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing ping3: {e}")
            print("Please install ping3 manually: pip install ping3")
            sys.exit(1)
    finally:
        global ping
        from ping3 import ping

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def ping_ip(ip):
    try:
        result = ping(ip, timeout=1)
        if result is not None and result is not False:
            return ip
    except Exception as e:
        pass
    return None

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def ping_worker(ip):
    global total_scanned_count, total_online_count, total_offline_count

    result_ip = ping_ip(ip)

    with current_data_lock:
        total_scanned_count += 1
        if result_ip:
            total_online_count += 1
            recent_pings.append((result_ip, "online"))
            online_ips_global_storage.append(result_ip)
        else:
            total_offline_count += 1
            recent_pings.append((ip, "offline"))

def update_display_live():
    while not stop_event.is_set():
        with current_data_lock:
            current_scanned = total_scanned_count
            current_online = total_online_count
            current_offline = total_offline_count

        clear_console()
        print("--- Live IP Scanner (Non-Stop) ---")

        elapsed_time_seconds = time.time() - start_time
        hours, remainder = divmod(elapsed_time_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\nTime Running: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

        print(f"Total IPs Pinged: {current_scanned}")
        print(f"Total Online: {current_online}")
        print(f"Total Offline/Dead: {current_offline}")

        print(f"\nOnline IPs are being logged to 'online_ips.txt'.")

        time.sleep(DISPLAY_UPDATE_INTERVAL)

def start_continuous_pinging():
    global start_time
    start_time = time.time()

    with open("online_ips.txt", "a"):
        pass

    active_ping_threads = []

    display_thread = threading.Thread(target=update_display_live, daemon=True)
    display_thread.start()

    print("Starting continuous IP ping tool...")
    print("Press Ctrl+C to stop the scanner at any time.")

    try:
        while not stop_event.is_set():
            active_ping_threads = [t for t in active_ping_threads if t.is_alive()]

            if len(active_ping_threads) < MAX_CONCURRENT_PINGS:
                ip_to_ping = generate_random_ip()
                thread = threading.Thread(target=ping_worker, args=(ip_to_ping,))
                thread.start()
                active_ping_threads.append(thread)
            
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        for thread in active_ping_threads:
            if thread.is_alive():
                thread.join(timeout=2)

if __name__ == "__main__":
    install_ping3()

    try:
        start_continuous_pinging()
    except KeyboardInterrupt:
        print("\nScanner stopped by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        stop_event.set()
        clear_console()
        print("--- Scanner Stopped ---")
        with current_data_lock:
            print(f"Total IPs Pinged since start: {total_scanned_count}")
            print(f"Total Online IPs found: {total_online_count}")
            print(f"Total Offline/Dead IPs: {total_offline_count}")
            
            unique_online_ips_final = sorted(list(set(online_ips_global_storage)))
            print("\nAll Unique Online IPs found (saved to online_ips.txt):")
            with open("online_ips.txt", "w") as f:
                for ip in unique_online_ips_final:
                    f.write(ip + "\n")
                    print(f"  {GREEN}{ip}{ENDC}")
            print(f"Total unique online IPs overall: {len(unique_online_ips_final)}")

        print("\nExiting.")