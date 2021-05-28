/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<32> NUMBER_OF_IDS = 1024;
const bit<8> VIOLATION_THRESHOLD = 20;
const bit<48> RESET_INTERVAL = 2000000;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}


header myPPV_t {
    bit<16> flow_id;
    bit<16> ctv;
    bit<16> ppv;
    bit<16> debug;
    bit<16> debug2;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    myPPV_t      myPPV;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_myPPV {
        packet.extract(hdr.myPPV);
        transition accept;
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition parse_myPPV;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    register<bit<8>>(NUMBER_OF_IDS) flow_id_violation;
    register<bit<48>>(NUMBER_OF_IDS) violation_time;
    register<bit<1>>(NUMBER_OF_IDS) is_flow_id_blocked;
    bit<8> val;
    bit<48> time;
    bit<16> dtime;

    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    action reset_register(bit<16> a) {
        flow_id_violation.write((bit<32>)a, 0);
        violation_time.write((bit<32>)a, standard_metadata.ingress_global_timestamp);
        hdr.myPPV.debug =  a;
        return;
    }


    apply {

        violation_time.read(time, (bit<32>)hdr.myPPV.flow_id);
        bit<48> interval = standard_metadata.ingress_global_timestamp - time;
        if (interval > RESET_INTERVAL ){
            flow_id_violation.read(val,(bit<32>)hdr.myPPV.flow_id);
            if (val > VIOLATION_THRESHOLD){
                is_flow_id_blocked.write((bit<32>)hdr.myPPV.flow_id, 1);
            }
            reset_register(hdr.myPPV.flow_id);
        } else {
            flow_id_violation.read(val, (bit<32>)hdr.myPPV.flow_id);
            hdr.myPPV.debug = (bit<16>)val;
        }

        bit<1> boolean;
        is_flow_id_blocked.read(boolean, (bit<32>)hdr.myPPV.flow_id);
        hdr.myPPV.debug2 = (bit<16>)boolean;

        if (hdr.ipv4.isValid() ) {
            // Process only non-tunneled IPv4 packets
            ipv4_lpm.apply();
        }
        if (hdr.myPPV.ctv < hdr.myPPV.ppv){     
            flow_id_violation.read(val, (bit<32>)hdr.myPPV.flow_id);
            val = val + 1;
            flow_id_violation.write((bit<32>)hdr.myPPV.flow_id, val);
        }

        
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.myPPV);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
