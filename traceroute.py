# Adapted from companion material available for the textbook Computer Networking: A Top-Down Approach, 6th Edition
# Kurose & Ross
# source used: https://stackoverflow.com/questions/10008144/creating-an-icmp-traceroute-in-python
# source used: https://github.com/James-P-D/Traceroute/blob/master/src/Tracert/Tracert/Tracert.py

from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


def checksum(string):
    c_sum = 0
    countTo = (len(string) // 2) * 2

    count = 0
    while count < countTo:
        thisVal = ord(string[count + 1]) * 256 + ord(string[count])
        c_sum = c_sum + thisVal
        c_sum = c_sum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        c_sum = c_sum + ord(string[len(string) - 1])
        c_sum = c_sum & 0xffffffff

    c_sum = (c_sum >> 16) + (c_sum & 0xffff)
    c_sum = c_sum + (c_sum >> 16)
    answer = ~c_sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet(data_size):
    # First, make the header of the packet, then append the checksum to the header,
    # then finally append the data

    # data can be any random word
    data = b"pluto"  # b denotes a byte string

    # first, make temporary header and calculate checksum
    # type, code, checksum, id, sequence
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, 0, 0)

    temp_checksum = checksum(header + data)

    # socket.htons makes sure numbers are stored in memory in network byte order
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(temp_checksum), 0, 0)

    padding = bytes(data_size)

    # Don't send the packet yet, just return the final packet in this function.
    # So the function ending should look like this
    # Note: padding = bytes(data_size)
    packet = header + data + padding
    return packet


def get_route(hostname, data_size):
    timeLeft = TIMEOUT
    rtt_list = []
    counter = 0

    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):

            # destAddr = gethostbyname(hostname)

            # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw
            # Fill in start
            # Make a raw socket named mySocket
            # Fill in end
            icmp = socket.getprotobyname("icmp")
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)  # AF_INET specifies address family

            # setsockopt method is used to set the time-to-live field.
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet(data_size)
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []:  # Timeout
                    print("  *        *        *    Request timed out.")
                    counter += 1
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("  *        *        *    Request timed out.")
                    counter += 1

            except timeout:
                continue
            # calculates the min, max, and average rtt, as well as packet loss percentage
            except KeyboardInterrupt:
                avg = (round(sum(rtt_list)) / float(len(rtt_list)))
                print("")
                print(" min rtt: %d  max rtt: %d  avg rtt: %d " % (round(min(rtt_list)), round(max(rtt_list)), avg))
                if counter > 0:
                    i = len(rtt_list)
                    packet_loss = (counter / float((i + counter))) * 100
                else:
                    packet_loss = 0
                print(" packet loss: %d %%\n" % packet_loss)
                # exits program
                sys.exit(0)

            else:
                # Fill in start
                # Fetch the icmp type from the IP packet
                # Fill in end

                p_header = recvPacket[20:28]
                types, code, checksum, packetID, sequence = struct.unpack("bbHHh", p_header)

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print("  %d    rtt=%.0f ms    %s" % (ttl, (timeReceived - t) * 1000, addr[0]))
                    rtt_list.append((timeReceived - t) * 1000)  # adds rtt to list

                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print("  %d    rtt=%.0f ms    %s" % (ttl, (timeReceived - t) * 1000, addr[0]))
                    rtt_list.append((timeReceived - t) * 1000)  # adds rtt to list

                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print("  %d    rtt=%.0f ms    %s" % (ttl, (timeReceived - timeSent) * 1000, addr[0]))
                    rtt_list.append((timeReceived - timeSent) * 1000)  # adds rtt to list
                    return

                else:
                    print("error")
                break

            finally:
                mySocket.close()


print('Argument List: {0}'.format(str(sys.argv)))

data_size = 0
if len(sys.argv) >= 2:
    data_size = int(sys.argv[2])
dest = "gaia.cs.umass.edu"
print(dest)  # prints destination url
get_route(dest, data_size)
# get_route("gaia.cs.umass.edu", data_size)
