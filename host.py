#!/usr/bin/env python

import argparse
import sys
import socket
import random
import struct
import re

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet, hexdump
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import Ether, StrFixedLenField, XByteField, IntField
from scapy.all import bind_layers
import readline
from myPPV import PPVheader

# class PPVheader(Packet):
#     name = "PPVheader"
#     fields_desc = [ StrFixedLenField("P", "P", length=1),
#                     StrFixedLenField("Four", "4", length=1),
#                     XByteField("version", 0x01),
#                     IntField("CTV", 0),
#                     IntField("PPV", 0),
#                     IntField("Id", 0)]

# bind_layers(Ether, PPVheader, type=0x1234)

class NumParseError(Exception):
    pass

class OpParseError(Exception):
    pass

class Token:
    def __init__(self,type,value = None):
        self.type = type
        self.value = value

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface


def num_parser(s, i, ts):
    pattern = "^\s*([0-9]+)\s*"
    match = re.match(pattern,s[i:])
    if match:
        ts.append(Token('num', match.group(1)))
        return i + match.end(), ts
    raise NumParseError('Expected number literal.')


def make_seq(p1, p2):
    def parse(s, i, ts):
        i,ts2 = p1(s,i,ts)
        return p2(s,i,ts2)
    return parse


def main():

    random.seed(2)
    addr = socket.gethostbyname("10.0.2.2")
    iface = get_if()

    

    print "sending on interface {} to IP addr {}".format(iface, str(addr))
   
#    hexdump(pkt)
#    print "len(pkt) = ", len(pkt)

    # iface = 'eth0'
    while True:
        try:
            
            id = random.randint(1,3)
            ctv = random.randint(3,7)
            ppv = random.randint(1,10)


            pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
            pkt = pkt / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535))

            pkt = pkt / PPVheader(
                                Id=id,
                                CTV=ctv,
                                PPV=ppv)
            pkt = pkt/' '
            pkt = pkt/ str('CTV=' + str(ctv) + ', PPV=' + str(ppv) + ', Id=' + str(id))
            pkt = pkt/' '

            pkt.show()
            print "-----------------"
            pkt.show2()

            # resp = srp1(pkt, iface=iface, timeout=1, verbose=False)
            sendp(pkt, iface=iface, verbose=False)  

            
            # if resp:
            #     pPVheader=resp[PPVheader]
            #     if pPVheader:

            #         print pPVheader.result
            #     else:
            #         print "cannot find PPVheader in the packet"
            # else:
            #     print "Didn't receive response"
        except Exception as error:
            print "--------------------------tesa------------------"
            print error


if __name__ == '__main__':
    main()

