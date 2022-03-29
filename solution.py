# gf2206 ICMP Pinger Lab

from socket import *
import os
import sys
import struct
import time
import select
import binascii
from statistics import stdev
# Should use stdev

ICMP_ECHO_REQUEST = 8


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            #print("Here")
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        #print(startedSelect)
        #print(whatReady)
        #print(struct.unpack("BBHBBBB", recPacket & 0xffffffffffffffff))
       # print(struct.unpack_from("!B", recPacket, offset=0))
        #print("Reply from {}: bytes={} time={:0.7f}".format(addr[0], len(recPacket), ))


        # Fetch the ICMP header from the IP packet

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."
        responseTime=timeout - timeLeft
        print("Reply from {}: bytes={} time={:0.7f}ms TTL={}".format(addr[0], len(recPacket), responseTime*100, struct.unpack_from("!B", recPacket, offset=8)[0]))
        return responseTime


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        #print("HERE")
        #print(type(htons(myChecksum)))
        myChecksum = htons(myChecksum) & 0xffff
    else:
        #print("HERE")
        #print(type(htons(myChecksum)))
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")


    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i This is like an "anding" process
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Calculate vars values and return them
    #  vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
    # Send ping requests to a server separated by approximately one second
    counter=0
    times=[]
    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        #print(delay)
        times.append(delay)
        time.sleep(1)  # one second
        counter+=1

    vars = [str(round(min(times)*1000, 8)), str(round(sum(times)/len(times)*1000, 8)), str(round(max(times)*1000, 8)),
            str(round(stdev(times)*1000, 8))]
    vars2="/".join(vars)
    lossRate=((counter-len(times))/counter)
    print("")
    #print((counter-len(times))/counter)
    print("--- {} ping statistics ---".format(host))
    print("{} packets transmitted, {} packets received, {}% packet loss".format(counter,len(times),lossRate*100))
    print("round-trip min/avg/max/stddev = {} ms".format(vars2))
    return vars

if __name__ == '__main__':
    ping("google.co.il")
    #stats="/".join(ping("google.co.il"))
    #print(stats)

