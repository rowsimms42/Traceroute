# Traceroute

Traceroute is a computer networking diagnostic tool which allows a user to trace the route from a
host running the traceroute program to any other host in the world. It is implemented
with ICMP messages.  It works by sending ICMP echo (ICMP type ‘8’) messages to the same
destination with increasing value of the time-to-live (TTL) field. The routers along the traceroute
path return ICMP Time Exceeded (ICMP type ‘11’ ) when the TTL field become zero. The final
destination sends an ICMP reply (ICMP type ’0’ ) messages on receiving the ICMP echo request.
The IP addresses of the routers which send replies can be extracted from the received packets.
The round-trip time between the sending host and a router is determined by setting a timer at the
sending host. 

Program outputs trace route, minimum, maximum, and average rtt, as well as the packet loss
percentage.
