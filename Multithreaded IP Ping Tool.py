import threading
import random
import time
from ping3 import ping

# Function to ping an IP address
def ping_ip(ip):
    try:
        result = ping(ip)
        if result is not None:
            return ip
    except:
        pass

# Function to generate random IP addresses
def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

# Function to perform pinging with threading
def ping_with_threads(num_threads):
    while True:
        ips = [generate_random_ip() for _ in range(10)]
        threads = []
        
        online_ips = []
        
        for ip in ips:
            thread = threading.Thread(target=ping_and_collect, args=(ip, online_ips))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        with open("online_ips.txt", "a") as file:
            for ip in online_ips:
                file.write(ip + "\n")

        time.sleep(5)  # Wait for 5 seconds before generating new IPs

# Function to ping an IP, collect online IPs, and print the result
def ping_and_collect(ip, online_ips):
    result = ping_ip(ip)
    if result:
        online_ips.append(result)
        print(f"{result} is online")
    else:
        print(f"{ip} is offline")

if __name__ == "__main__":
    num_threads = 50
    thread_list = []

    for _ in range(num_threads):
        thread = threading.Thread(target=ping_with_threads, args=(num_threads,))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()
