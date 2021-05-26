
from scapy.all import *
import sys, os

TYPE_IPV4 = 0x800

class PPVheader(Packet):
    name = "PPVheader"
    fields_desc = [ #XByteField("version", 0x01),
                    ShortField("Id", 0),
                    ShortField("PPV", 0),
                    ShortField("CTV", 0),
                    ShortField("Debug", 0),
                    ShortField("Debug2", 0)]
    def mysummary(self):
        return self.sprintf("CTV=%CTV%, PPV=%PPV%, Id=%Id%")


bind_layers(Ether, IP, type=TYPE_IPV4)
bind_layers(IP, PPVheader)

