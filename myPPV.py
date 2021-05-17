
from scapy.all import *
import sys, os

TYPE_IPV4 = 0x800

class PPVheader(Packet):
    name = "PPVheader"
    fields_desc = [ StrFixedLenField("P", "P", length=1),
                    StrFixedLenField("Four", "4", length=1),
                    XByteField("version", 0x01),
                    IntField("CTV", 0),
                    IntField("PPV", 0),
                    IntField("Id", 0)]
    def mysummary(self):
        return self.sprintf("CTV=%CTV%, PPV=%PPV%, Id=%Id%")


bind_layers(Ether, IP, type=TYPE_IPV4)
bind_layers(IP, PPVheader)

