# Per Packet Value Policer

## Description
The packages in the network use a special header that stores the importance of the packet.
This packet value (PPV) is a number between 1 and 1024, the higher the value the more important the package.
The packages also contain a congestion threshold value (CTV).
Any package that has an importance value below the CTV will be dropped, except if the source supports ECN-CE,
then it will be marked. We need to create a policer node that enforces the ECN compatible sources to reduce
their output. The packets also contain a flow id, which identifies different packet flows. If a flow has too
many packages below the CTV, then the policer node has to detect and report it.

## Implementation

### Architecture
Mininet with BMv2
Our test environment will consist of two hosts and a switch between them. One host (sender) will send
packets to the other one (receiver). The switch will perform the role of the policer node.

### Logic
Packet header contains the CTV, PPV and flow id values.
For every flow id a register will count the number
of packets where the CTV is bigger than the PPV value.
These registers will be reset individually per flow every 5 seconds. After every cycle before resetting
the policer node will look for number of violations above the preset threshold. Every flow id that exceeds
this threshold will be flagged.
The test will only use ECN capable sources therefore no packets will be dropped and for our case
the ECN flags do not need to be flipped. 
The policer node will not intervene when a flow is flagged.
The sender script will provide the necessary information/packet headers. There will be multiple
flows at the same time, with different behaviors (malicious or normal).

## User guide

### Environment
Virtual machine setup with vagrant for VirtualBox:
https://github.com/p4lang/tutorials/tree/master/vm

Clone the git repository then use the command `vagrant up` to creat the VM.

### Run
Open the project in the terminal then run the following commands:

Start the mininet environment: 
`make`

In the mininet environment open the two hosts:
`xterm h1 h2`

From h2 terminal start listening for the packets with:
`./receive.py` or with `./receive.py | grep FLAGGED` for easier overview

From h1 terminal start sending packets with:
`python host.py 2 3 3` 

For more information you can use `python host.py -h`



```text
usage: host.py [-h] GOOD NEUTRAL BAD Configure the number and the kind of data flows in the test run. positional arguments:

  GOOD        an integer that tells the program how many flows to create with

              good behaviour

  NEUTRAL     an integer that tells the program how many flows to create with

              neutral behaviour

  BAD         an integer that tells the program how many flows to create with

              bad behaviour optional arguments:

  -h, --help  show this help message and exit


```


### Results
We added two extra headers for logging the results.
The `debug` header contains the number of violations in the 5 seconds windows.
The `FLAGGED` header indicates if the flow has ever violated our threshold.

Our tests use 8 (2 good, 3 neutral, 3 bad) flows because P4 parameters were configured to this number of flows.