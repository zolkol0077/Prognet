# Per Packet Value Policer

## Description
The packages in the network use a special header that stores the importance of the packet. This packet value (PPV) is a number between 1 and 1024, the higher the value the more important the package. The packages also contain a congestion threshold value (CTV). Any package that has an importance value below the CTV will be dropped, except if the source supports ECN-CE, then it will be marked. We need to create a policer node that enforces the ECN compatible sources to reduce their output. The packets also contain a flow id, which identifies different packet flows. If a flow has too many packages below the CTV, then the policer node has to detect and report it.

## Implementation

### Architecture
Mininet with BMv2
Our test environment will consist of two hosts and a switch between them. One host (sender) will send packets to the other one (receiver). The switch will perform the role of the policer node.

Packet header contains the CTV, PPV and flow id values.
For every flow id (max 64 different ids for the test) a register will count the number of packets where the CTV - PPV difference is greater than a predefined value. These registers will be reset every 200 milliseconds. After every cycle before resetting the policer node will look for unnaturally high numbers.
The test will only use ECN capable sources therefore no packets will be dropped and for our case the ECN flags do not need to be flipped.
The policer node will not intervene when an outlier is detected, it will just log the results.
The sender script will provide the necessary information/packet headers. There will be multiple flows at the same time, with different behaviors (malicious or normal).
