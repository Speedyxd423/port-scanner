import socket
import threading
from queue import Queue
from colorama import Fore, Style, init

init()

open_ports = []
# Queue is thread-safe unlike a regular list — prevents race conditions when multiple threads grab ports simultaneously
queue = Queue()
target = ""

def banner():
    print(Fore.CYAN + """
██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ █████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║
██████╔╝██║   ██║██████╔╝   ██║   ███████╗██║     ███████║██╔██╗ ██║
██╔═══╝ ██║   ██║██╔══██╗   ██║   ╚════██║██║     ██╔══██║██║╚██╗██║
██║     ╚██████╔╝██║  ██║   ██║   ███████║╚██████╗██║  ██║██║ ╚████║
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
    """ + Style.RESET_ALL)
    print(Fore.CYAN + "          Multithreaded Port Scanner  |  For authorised use only\n" + Style.RESET_ALL)

def get_input():
    print(Fore.YELLOW + "[*] " + Style.RESET_ALL + "Target IP: ", end="")
    target = input().strip()

    print(Fore.YELLOW + "[*] " + Style.RESET_ALL + "Thread count " + Fore.CYAN + "(default 100)" + Style.RESET_ALL + ": ", end="")
    thread_input = input().strip()
    threads = int(thread_input) if thread_input.isdigit() else 100

    print(Fore.YELLOW + "[*] " + Style.RESET_ALL + "Port range " + Fore.CYAN + "(default 1-1024)" + Style.RESET_ALL + ", enter start end: ", end="")
    port_input = input().strip()
    if port_input:
        parts = port_input.split()
        start, end = int(parts[0]), int(parts[1])
    else:
        start, end = 1, 1024

    return target, threads, range(start, end)

def portscan(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # without this, hung connections stall threads indefinitely
        sock.connect((target, port))
        sock.close()  # explicitly close to avoid leaving hundreds of open file descriptors
        return True
    except:
        return False

def fill_queue(port_list):
    for port in port_list:
        queue.put(port)

def worker():
    # each thread runs this loop — grabbing ports from the queue until it's empty
    while not queue.empty():
        port = queue.get()
        if portscan(port):
            print(Fore.GREEN + "[+] " + Style.RESET_ALL + "Port {} is open!".format(port))
            open_ports.append(port)

def main():
    global target

    banner()

    target, thread_count, port_list = get_input()

    print(Fore.YELLOW + "\n[*] " + Style.RESET_ALL + "Starting scan on {} with {} threads...\n".format(target, thread_count))

    fill_queue(port_list)

    thread_list = []
    for t in range(thread_count):
        thread = threading.Thread(target=worker)
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    # join() blocks main thread until all worker threads finish before printing results
    for thread in thread_list:
        thread.join()

    print(Fore.CYAN + "\n[*] Scan complete." + Style.RESET_ALL)
    if open_ports:
        # sorted() so ports print in numerical order regardless of which thread found them first
        print(Fore.GREEN + "[+] Open ports: " + Style.RESET_ALL + str(sorted(open_ports)))
    else:
        print(Fore.RED + "[-] No open ports found." + Style.RESET_ALL)

# ensures main() only runs when the script is executed directly, not when imported as a module
if __name__ == "__main__":
    main()