
# Test Details

## Target Information

**Manufacturer:** TP-Link

**Part Number:** TL-WR841N

**Serial Number:** 22295L6001357
 
## Test-Equipment
 
**Multimeter:** ASTRO AI AM33D

**Logic Analyzer:** Comidox USB Logic Analyzer

**USB to UART Adapter:** Silicon Labs CP210x UART Bridge

**Software:** 
- Sigrok Pulsview (for logic captures)
- NMAP
- Firefox
- Screen


# Initial Recon

## Visual Inspection

Inspected exterior of router, noted label on the back that contained FCC ID for further review. 

FCC ID: 2AXJ4WR841NV14

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/router_ffc_id.jpg)

Opened router case by removing two phillips screws and applying pressure between pressure fit parts with spudger tool.

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/router_opened.jpg)

Noted three chips of interest on the PCB for further inspection (shown as details A, B, and C in picture below)

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/router_areas_of_interest.jpg)

## On-board testing

Noted presence of a test connection that appears to be a UART connection based on the 4 pins labelled with VCC, GND, RX and TX (shown as detail D above)

Verified operating voltage of PCB is 9V by testing voltage drop across input jack with multimeter. 

Identified ground connection on P1 (detail E above) by testing continuity with the ground connection on the input jack.

Tested the suspected UART connection with a multimeter to verify pins matched the silk screen labels, each was pin tested as follows:

- VCC: Measured voltage drop between VCC and ground as 3.3V confirming operating voltage of UART at 3.3V
- GND: Checked for continuity between GND pin on UART and known ground on board and confirmed GND is infact a ground. 
- RX: Measured voltage drop between RX and ground as 0V, test to ensure it was not connected to ground by checking continuity between RX and known ground connections, no continuity found
- TX: Measured Voltage drop between RX and ground as ~3.3V during standard operation. 

After confirming pinout, based on the observations of the pins this appears to be a UART connection, checked for transmission on TX pin during boot up by powercylcing router and measuring voltage drop. Noted fluctuation on TX pin from ~1V - 3V suggesting and busy and active transmission during bootup.

Soldered through hole inline header pins to suspected UART connection to facilitate further testing with logic analyzer and later on USB to Serial Adapter. 

Attached Logic Analyzer to TX and GND pins of UART connection and captured a transmission during boot up, screenshot of single tranmission frame shown below. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/Uart_Capture_Single_Frame.png)

Manual framing of the signal confirmed a UART transmission, noted the start bit, 8 data bits, one stop bit and no parity bit. 

Measured the baud rate as 125,000 however based on standard serial baud rates suspect that it is actually 115,200. 

Based on these findings applied a UART decoder to the channel with the below settings. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/uart_decoder_settings.png)

Decoded UART signal confirmed UART parameters and showed presence of boot loader and boot up logs to be investigated further. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/uart_decoded_message.png)

## OSINT and Online Recon

Used previously locataed FCC ID to find FCC Equipment Authorization filing for the router (https://fccid.io/2AXJ4WR841NV14)

Noted in the filing that the ID had been changed from the previoous TE7WR841NV14. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ffc_id_change_request.png)

Inspectng the previous filing (https://fccid.io/TE7WR841NV14) internal photos of the router were located. Unfortunately schematics, functional description and block diagram were redacted as confidential. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/fcc-id-1.png)

Detailed pictures of two chips of interest were shown that detailed the chip manufacturer and part number. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ffc-id-mediatek.png)

Previously denoted chip A Id'd as MEDIATEK MT7628NN

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/fcc-id-zentel.png)

Previously denoted chip B Id'd as Zentel A3S56D40GTP -50L

Unfortunately the markers on chip C were not readable in the FCC pictures. Returning to the test router, high resolution pictures were taken and blown up to Id chip. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/cfeon_chip_id.jpg)

Chip C was Id'd as cFeon QH32B-104HIP.

Data sheets were located online for each of the chips. 

**MEDIATEK MT7628NN:** System On Chip (SOC) containing CPU. Important details included that this is a purpose built SOC for N300 routers. The CPU is MIPS24KEc, supports Linux 2.6.36 SDK and Linux 3.10 SDK. Interfaces with flash memory via SPI.

Product Page: https://www.mediatek.com/products/home-networking/mt7628k-n-a

Data Sheet: https://files.seeedstudio.com/products/114992470/MT7628_datasheet.pdf

**Zentel A3S56D40GTP -50L:** DRAM 32Kb

Data Sheet: https://www.mouser.ca/datasheet/2/1130/DSA3S56D340GTPF_02-1984099.pdf

**cFeon QH32B-104HIP:** Id'd as full part number EN25Q32B-104HIP. Noted as Flash ROM that communicates via SPI. 

Data Sheet: https://www.alldatasheet.com/datasheet-pdf/pdf/675622/EON/EN25QH32A.html

Searching for the firmware found it supplied through the official support page for the router. 

https://www.tp-link.com/ca/support/download/tl-wr841n/#Firmware

## Initial Network Recon

Connected test computer to the network hosed by the router. Router IP address id'd as 192.168.0.1.

Nmap scans were performed for both TCP and UDP. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/nmap_tcp_scan.png)

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/nmap_tcp_scan_2.png)

TCP scans revealed 3 open ports:

Port 22 - ssh running Dropbear sshd 2012.55

Port 80 - http hosting the routers configuration web portal

Port 1900 - UPnP (Portable SDK for UPnP devices 1.6.19 (Linux 2.6.36))

Noteable detail confirmed suspicion that router is running Linux kernel 2.6.36. 

UDP scans reveled 2 open ports: 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/nmap_udp_scan.png)

Port 67/udp - dhcps

Port 1900/udp - UPnP

## Scouting Previously Disclosed CVEs

Scouted for previously disclosed and patched CVEs and multiple. Noted a common theme of a lack of proper user input validation on forms and inputs in the web portal that led to either buffer overflow or command injection of an underlying function or service being called.

https://www.opencve.io/cve?vendor=tp-link&product=tl-wr841n

https://blog.viettelcybersecurity.com/1day-to-0day-on-tl-link-tl-wr841n/

https://ktln2.org/2020/03/29/exploiting-mips-router/

# Enumeration via UART Connection

Connected USB to UART adapter to the previously located UART pins based on the below pinout:

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/UART+to+USB+pinout.jpg)

Opened Terminal Session via Screen with the previously identified baud rate.

After powering on the router the bootloader logging and linux initilization logging from init and init scripts was displayed over the serial console session:

**Command: `screen /dev/ttyUSB0 115200`

```
[04080B0F][04080C0C][8A7F0000][26253B38][00262539]
DU Setting Cal Done


U-Boot 1.1.3 (Feb  3 2021 - 10:10:08)

Board: Ralink APSoC DRAM:  32 MB
relocate_code Pointer at: 81fc0000
flash manufacture id: 1c, device id 70 16
Warning: un-recognized chip ID, please update bootloader!
============================================
Ralink UBoot Version: 4.3.0.0
--------------------------------------------
ASIC 7628_MP (Port5<->None)
DRAM component: 256 Mbits DDR, width 16
DRAM bus: 16 bit
Total memory: 32 MBytes
Flash component: SPI Flash
Date:Feb  3 2021  Time:10:10:08
============================================
icache: sets:512, ways:4, linesz:32 ,total:65536
dcache: sets:256, ways:4, linesz:32 ,total:32768

 ##### The CPU freq = 580 MHZ ####
 estimate memory size =32 Mbytes
RESET MT7628 PHY!!!!!!
continue to starting system.                                                                                                                                                                                                              
0
disable switch phyport...

3: System Boot system code via Flash.(0xbc010000)
do_bootm:argc=2, addr=0xbc010000
## Booting image at bc010000 ...
   Uncompressing Kernel Image ... OK
No initrd
## Transferring control to Linux (at address 8000c150) ...
## Giving linux memsize in MB, 32

Starting kernel ...


LINUX started...

 THIS IS ASIC
Linux version 2.6.36 (jenkins@mobile-System) (gcc version 4.6.3 (Buildroot 2012.11.1) ) #1 Wed Feb 3 10:13:07 CST 2021

 The CPU feqenuce set to 575 MHz

 MIPS CPU sleep mode enabled.
CPU revision is: 00019655 (MIPS 24Kc)
Software DMA cache coherency
Determined physical RAM map:
 memory: 02000000 @ 00000000 (usable)
Initrd not found or empty - disabling initrd
Zone PFN ranges:
  Normal   0x00000000 -> 0x00002000
Movable zone start PFN for each node
early_node_map[1] active PFN ranges
    0: 0x00000000 -> 0x00002000
Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 8128
Kernel command line: console=ttyS1,115200 root=/dev/mtdblock2 rootfstype=squashfs init=/sbin/init
PID hash table entries: 128 (order: -3, 512 bytes)
Dentry cache hash table entries: 4096 (order: 2, 16384 bytes)
Inode-cache hash table entries: 2048 (order: 1, 8192 bytes)
Primary instruction cache 64kB, VIPT, , 4-waylinesize 32 bytes.
Primary data cache 32kB, 4-way, PIPT, no aliases, linesize 32 bytes
Writing ErrCtl register=00048820
Readback ErrCtl register=00048820
Memory: 29228k/32768k available (2180k kernel code, 3540k reserved, 583k data, 156k init, 0k highmem)
NR_IRQS:128
console [ttyS1] enabled
Calibrating delay loop... 386.04 BogoMIPS (lpj=772096)
pid_max: default: 4096 minimum: 301
Mount-cache hash table entries: 512
NET: Registered protocol family 16
bio: create slab <bio-0> at 0
Switching to clocksource Ralink Systick timer
NET: Registered protocol family 2
IP route cache hash table entries: 1024 (order: 0, 4096 bytes)
TCP established hash table entries: 1024 (order: 1, 8192 bytes)
TCP bind hash table entries: 1024 (order: 0, 4096 bytes)
TCP: Hash tables configured (established 1024 bind 1024)
TCP reno registered
NET: Registered protocol family 1
squashfs: version 4.0 (2009/01/31) Phillip Lougher
msgmni has been set to 57
io scheduler noop registered
io scheduler deadline registered (default)
Ralink gpio driver initialized
Serial: 8250/16550 driver, 2 ports, IRQ sharing enabled
serial8250: ttyS0 at MMIO 0x10000d00 (irq = 21) is a 16550A
serial8250: ttyS1 at MMIO 0x10000c00 (irq = 20) is a 16550A
brd: module loaded
flash manufacture id: 1c, device id 70 16
Warning: un-recognized chip ID, please update SPI driver!
EN25Q32B(1c 30161c30) (4096 Kbytes)
mtd .name = raspi, .size = 0x00400000 (4M) .erasesize = 0x00010000 (64K) .numeraseregions = 0
Creating 5 MTD partitions on "raspi":
0x000000000000-0x000000010000 : "boot"
0x000000010000-0x000000100000 : "kernel"
0x000000100000-0x0000003e0000 : "rootfs"
mtd: partition "rootfs" set to be root filesystem
0x0000003e0000-0x0000003f0000 : "config"
0x0000003f0000-0x000000400000 : "radio"
Register flash device:flash0
PPP generic driver version 2.4.2
PPP MPPE Compression module registered
NET: Registered protocol family 24
Mirror/redirect action on
u32 classifier
    Actions configured
Netfilter messages via NETLINK v0.30.
nf_conntrack version 0.5.0 (456 buckets, 1824 max)
ip_tables: (C) 2000-2006 Netfilter Core Team, Type=Linux
TCP cubic registered
NET: Registered protocol family 10
ip6_tables: (C) 2000-2006 Netfilter Core Team
IPv6 over IPv4 tunneling driver
NET: Registered protocol family 17
Ebtables v2.0 registered
802.1Q VLAN Support v1.8 Ben Greear <greearb@candelatech.com>
All bugs added by David S. Miller <davem@redhat.com>
VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
Freeing unused kernel memory: 156k freed
starting pid 29, tty '': '/etc/init.d/rcS'
mount: mounting devpts on /dev/pts failed: No such device
rdm_major = 253
spiflash_ioctl_read, Read from 0x003ff100 length 0x6, ret 0, retlen 0x6
Read MAC from flash(  3ff100) ffffffac-15-ffffffa2-5f-fffffff6-ffffffb4
GMAC1_MAC_ADRH -- : 0x0000ac15
GMAC1_MAC_ADRL -- : 0xa25ff6b4
Ralink APSoC Ethernet Driver Initilization. v3.1  256 rx/tx descriptors allocated, mtu = 1500!
NAPI enable, Tx Ring = 256, Rx Ring = 256
spiflash_ioctl_read, Read from 0x003ff100 length 0x6, ret 0, retlen 0x6
Read MAC from flash(  3ff100) ffffffac-15-ffffffa2-5f-fffffff6-ffffffb4
GMAC1_MAC_ADRH -- : 0x0000ac15
GMAC1_MAC_ADRL -- : 0xa25ff6b4
PROC INIT OK!
add domain:tplinkwifi.net
add domain:tplinkap.net
add domain:tplinkrepeater.net
add domain:tplinklogin.net
tp_domain init ok
L2TP core driver, V2.0
PPPoL2TP kernel driver, V2.0
Set: phy[0].reg[0] = 3900
Set: phy[1].reg[0] = 3900
Set: phy[2].reg[0] = 3900
Set: phy[3].reg[0] = 3900
Set: phy[4].reg[0] = 3900
Set: phy[0].reg[0] = 3300
Set: phy[1].reg[0] = 3300
Set: phy[2].reg[0] = 3300
Set: phy[3].reg[0] = 3300
Set: phy[4].reg[0] = 3300
resetMiiPortV over.
Set: phy[0].reg[4] = 01e1
Set: phy[0].reg[0] = 3300
Set: phy[1].reg[4] = 01e1
Set: phy[1].reg[0] = 3300
Set: phy[2].reg[4] = 01e1
Set: phy[2].reg[0] = 3300
Set: phy[3].reg[4] = 01e1
Set: phy[3].reg[0] = 3300
Set: phy[4].reg[4] = 01e1
Set: phy[4].reg[0] = 3300
turn off flow control over.
starting pid 79, tty '/dev/ttyS1': '/bin/sh'
~ # [ util_execSystem ] 141:  ipt_init cmd is "/var/tmp/dconf/rc.router"

[ dm_readFile ] 2061:  can not open xml file /var/tmp/pc/reduced_data_model.xml!, about to open file /etc/reduced_data_model.xml
spiflash_ioctl_read, Read from 0x003e0000 length 0x10000, ret 0, retlen 0x10000
spiflash_ioctl_read, Read from 0x003e0000 length 0xa5e0, ret 0, retlen 0xa5e0
===>Enter AP modspiflash_ioctl_read, Read from 0x003ff100 length 0x6, ret 0, retlen 0x6
e
[ oal_sys_readMaspiflash_ioctl_read, Read from 0x003ff200 length 0x4, ret 0, retlen 0x4
cFlash ] 1958:  spiflash_ioctl_read, Read from 0x003ff300 length 0x4, ret 0, retlen 0x4
 3ff100 set flasspiflash_ioctl_read, Read from 0x003ff400 length 0x10, ret 0, retlen 0x10
 h mac : AC:15:A2spiflash_ioctl_read, Read from 0x003ff500 length 0x29, ret 0, retlen 0x29
:5F:F6:B4.
spiflash_ioctl_read, Read from 0x003ff600 length 0x21, ret 0, retlen 0x21
spiflash_ioctl_read, Read from 0x003ff700 length 0x10, ret 0, retlen 0x10
spiflash_ioctl_read, Read from 0x003ff700 length 0x10, ret 0, retlen 0x10
spiflash_ioctl_read, Read from 0x00010000 length 0x1d0, ret 0, retlen 0x1d0
spiflash_ioctl_read, Read from 0x003ff100 length 0x6, ret 0, retlen 0x6
[ oal_sys_readMacFlash ] 1958:   3ff100 set flash mac : AC:15:A2:5F:F6:B4.
sendto: No such file or directory
pid 78 send 2001 error
[ util_execSystem ] 141:  oal_startDynDns cmd is "dyndns /var/tmp/dconf/dyndns.conf"

Get SNTP new config
[ util_execSystem ] 141:  oal_startNoipDns cmd is "noipdns /var/tmp/dconf/noipdns.conf"

[ util_execSystem ] 141:  oal_startCmxDns cmd is "cmxdns /var/tmp/dconf/cmxdns.conf"

ioctl: No such device
[ util_execSystem ] 141:  oal_br_addBridge cmd is "brctl addbr br0;brctl setfd br0 0;brctl stp br0 off"

[ util_execSystem ] 141:  oal_ipt_addLanRules cmd is "iptables -t filter -A INPUT -i br+ -j ACCEPT
"

[ rsl_initLanIpIntfObj ] 1025:  Smart DHCP, use 192.168.0.1/255.255.255.0 as default Static IP at initial stage!

[ util_execSystem ] 141:  oal_intf_setIntf cmd is "Raeth v3.1 (ifconfig br0 192NAPI
.168.0.1 netmask,SkbRecycle 255.255.255.0 u)
p"

[ util_exe
phy_tx_ring = 0x00ca1000, tx_ring = 0xa0ca1000
cSystem ] 141:
phy_rx_ring0 = 0x00ca2000, rx_ring0 = 0xa0ca2000
oal_util_setProc[fe_sw_init:5357]rt305x_esw_init.
LanAddr cmd is "echo "br0 16820416," > /proc/net/conntract_LocalAddr"

[ util_execSystem ] 141:  oal_intf_enableIntf cmd is "ifconfig eth0 up"

disable switch phyport...
GMAC1_MAC_ADRH -- : 0x0000ac15
GMAC1_MAC_ADRL -- : 0xa25ff6b4
RT305x_ESW: Link Status Changed
[ util_execSystem ] 141:  rsl_initLanEthIntfObj cmd is "ifconfig eth0 up"

[ util_execSystem ] 141:  oal_br_addIntfIntoBridge cmd is "brctldevice eth0 entered promiscuous mode
 addif br0 eth0"br0: port 1(eth0) entering forwarding state


br0: port 1(eth0) entering forwarding state
[ util_execSystem ] 141:  oal_addVlanTagIntf cmd is "vconfig add eth0 3"

[ util_execSystem ] 141:  oal_intf_enableIntf cmd is "ifconfig eth0.3 up"

set if eth0.3 to *not wan dev
[ util_execSystem ] 141:  oal_br_device eth0.3 entered promiscuous mode
addIntfIntoBridgbr0: port 2(eth0.3) entering forwarding state
e cmd is "brctl br0: port 2(eth0.3) entering forwarding state
addif br0 eth0.3"

[ util_execSystem ] 141:  oal_addVlanTagIntf cmd is "vconfig add eth0 4"
[ util_execSystem ] 141:  oal_addVlanTagIntf cmd is "vconfig add eth0 4"

[ util_execSystem ] 141:  oal_intf_enableIntf cmd is "ifconfig eth0.4 up"

set if eth0.4 to *not wan dev
[ util_execSystem ] 141:  oal_br_device eth0.4 entered promiscuous mode
addIntfIntoBridgbr0: port 3(eth0.4) entering forwarding state
e cmd is "brctl br0: port 3(eth0.4) entering forwarding state
addif br0 eth0.4"

[ util_execSystem ] 141:  oal_addVlanTagIntf cmd is "vconfig add eth0 5"

[ util_execSystem ] 141:  oal_intf_enableIntf cmd is "ifconfig eth0.5 up"

set if eth0.5 to *not wan dev
[ util_execSystem ] 141:  oal_br_device eth0.5 entered promiscuous mode
addIntfIntoBridgbr0: port 4(eth0.5) entering forwarding state
e cmd is "brctl br0: port 4(eth0.5) entering forwarding state
addif br0 eth0.5"

[ util_execSystem ] 141:  oal_addVlanTagIntf cmd is "vconfig add eth0 6"

[ util_execSystem ] 141:  oal_intf_enableIntf cmd is "ifconfig eth0.6 up"

set if eth0.6 to *not wan dev
[ util_execSystem ] 141:  oal_br_device eth0.6 entered promiscuous mode
addIntfIntoBridgbr0: port 5(eth0.6) entering forwarding state
e cmd is "brctl br0: port 5(eth0.6) entering forwarding state
addif br0 eth0.6"

[ util_execSystem ] 141:  oal_addVlanTagIntf cmd is "vconfig add eth0 7"

[ util_execSystem ] 141:  oal_intf_enableIntf cmd is "ifconfig eth0.7 up"

set if eth0.7 to *not wan dev
[ util_execSystem ] 141:  oal_br_device eth0.7 entered promiscuous mode
addIntfIntoBridgbr0: port 6(eth0.7) entering forwarding state
e cmd is "brctl br0: port 6(eth0.7) entering forwarding state
addif br0 eth0.7"

[ util_execSystem ] 141:  oal_br_delIntfFromBridge cmd is "br0: port 1(eth0) entering forwarding state
brctl delif br0 eth0"

[ util_execSystem ] 141:  oal_eth_setIGMPSnoopParam cmd is "for i in /sys/devices/virtual/net/*/bridge/multicast_snooping;do echo 1 > $i ; done"

[ util_execSystem ] 141:  rsl_initApIgmpSnoop cmd is "for i in /sys/devices/virtual/net/*/bridge/igmp_query_version; do echo 3 > $i; done"

[ util_execSystem ] 141:  oal_wlan_ra_setCountryRegion cmd is "cp /etc/SingleSKU_FCC.dat /var/Wireless/RT2860AP/SingleSKU.dat"

[ util_execSystem ] 141:  oal_wlan_ra_setCountryRegion cmd is "iwpriv ra0 set CountryRegion=0"

ra0       no private ioctls.

[ util_execSystem ] 141:  oal_wlan_ra_loadDriver cmd is "insmod /lib/modules/kmdir/kernel/drivers/net/wireless/mt_wifi_ap/mt_wifi.ko"

[ util_execSystem ] 141:  oal_wlan_ra_initWlan cmd is "ifconfig ra0 up"

[RTMPReadParametersHook:297]wifi read profile faild.

efuse_probe: efuse = 10000012
exec!
spiflash_ioctl_read, Read from 0x003f0000 length 0x400, ret 0, retlen 0x400
eeFlashId = 0x7628!
tssi_1_target_pwr_g_band = 36
[ util_execSystem ] 141:  oal_wlan_ra_initWlan cmd is "echo 1 > /proc/tplink/led_wlan_24G"

[ util_execSystem ] 141:  oal_wlan_ra_initWlan cmd is "iwpriv ra0 set ed_chk=0"

[ util_execSystem ] 141:  oal_wlan_ra_setStaNum cmd is "iwpriv ra0 set MaxStaNum=32"

[ util_execSystem ] 141device ra0 entered promiscuous mode
:  oal_br_addIntbr0: port 1(ra0) entering forwarding state
fIntoBridge cmd br0: port 1(ra0) entering forwarding state
is "brctl addif br0 ra0"

[ util_execSystem ] 141:  oal_br_addIntfIntoBridge cdevice apcli0 entered promiscuous mode
md is "brctl addif br0 apcli0"

[ util_execSystem ] 141:  oal_br_addIntfIntoBrdevice ra1 entered promiscuous mode
idge cmd is "brctl addif br0 ra1"

[ util_execSystem ] 141:  oal_wlan_ra_initEspiflash_ioctl_read, Read from 0x003f0000 length 0x2, ret 0, retlen 0x2
nd cmd is "wlNetlinkTool &"

[ util_execSystem ] 141:  oal_wlan_ra_initEnd cmd is "killall -q wscd"

[ util_execSystem ] 141:  oal_wlan_ra_initEnd cmd is "wscd -i ra0 -m 1 -w /var/tmp/wsc_upnp/ &"

[ util_execSystem ] 141:  rsl_initLanWlanObj cmd is "echo 1 > /proc/tplink/wl_mode"

WLAN-Start wlNetlinkTool
Waiting for Wireless Events from interfaces...
swWlanChkAhbErr: netlink to do
[ oal_wlan_ra_loadDriver ] 2119:  no 5G chip.


[ rsl_initLanWlanObj ] 9620:  perror:1
wscd: SSDP UDP PORT = 1900
[ util_execSystem ] 141:  oal_ipt_setWanPort cmd is "iptables -t filter -A INPUT -p tcp --dport 80 -j ACCEPT"

[ util_execSystem ] 141:  oal_ipt_setWanPort cmd is "iptables -t nat -I PREROUTING 1 -p tcp --dport 80 -j ACCEPT"

sendto: No such file or directory
pid 78 send 2004 error
[ util_execSystem ] 141:  oal_startDhcps cmd is "dhcpd /var/tmp/dconf/udhcpd.conf"

iptables: Bad rule (does a matching rule exist in that chain?).
[ rsl_initAppObj ] 1038:  ===>Smart DHCP, use 192.168.0.1/255.255.255.0 as default Static IP at initial stage!

[ util_execSystem ] 141:  oal_intf_setIntf cmd is "ifconfig br0 192.168.0.1 netmask 255.255.255.0 up"

[ util_execSystem ] 141:  oal_util_setProcLanAddr cmd is "echo "br0 16820416," > /proc/net/conntract_LocalAddr"

[ rsl_initAppObj ] 1055:  lanCfgObj.IPRouters 192.168.0.1, lanCfgObj.X_TP_RemoteDns 192.168.0.1,0.0.0.0, lanCfgObj.DNSServers 192.168.0.1,0.0.0.0, lanCfgObj.minAddress 192.168.0.100, lanCfgObj.maxAddress 192.168.0.199.

[ rsl_initAppObj ] 1068:  ==> start dhcp client

iptables: Bad rule (does a matching rule exist in that chain?).
[ util_execSystem ] 141:  oal_ipt_fwDdos cmd is "iptables -D FORWARD -j FIREWALL_DDOS
"

iptables: No chain/target/match by that name.
[ util_execSystem ] 141:  oal_ipt_forbidLanPing cmd is "iptables -t filter -D INPUT -i br+ -p icmp --icmp-type echo-request -j DROP
iptables -t filter -D FORWARD -i br+ -p icmp --icmp-type echo-request -j DROP
"

iptables: Bad rule (does a matching rule exist in that chain?).
iptables: Bad rule (does a matching rule exist in that chain?).
[ util_execSystem ] 141:  oal_ddos_delPingRule cmd is "iptables -t filter -D INPUT ! -i br+ -p icmp --icmp-type echo-request -j ACCEPT
"

iptables: Bad rule (does a matching rule exist in that chain?).
[ util_execSystem ] 141:  oal_ipt_setDDoSRules cmd is "iptables -F FIREWALL_DDOS"

[ util_execSystem ] 141:  ddos_clearAll cmd is "rm -f /var/tmp/dosHost"

sh: diagTool: not found
[ util_execSystem ] 141:  oal_initFirewallObj cmd is "ebtables -N FIREWALL"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/netfilter/nf_conntrack_ftp.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_ftp.ko"

[ util_execSystem ] 141:  oal_openAlg cmd is "iptables -D FORWARD_VPN_PASSTHROUGH  -p udp --dport 500 -j DROP"

iptables: Bad rule (does a matching rule exist in that chain?).
[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_proto_gre.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_pptp.ko"

[ util_execSystem ] 141:  oal_openAlg cmd is "iptables -D FORWARD_VPN_PASSTHROUGH  -p tcp --dport 1723 -j DROP"

iptables: Bad rule (does a matching rule exist in that chain?).
[ util_execSystem ] 141:  oal_openAlg cmd is "iptables -D FORWARD_VPN_PASSTHROUGH  -p udp --dport 1701 -j DROP"

iptables: Bad rule (does a matching rule exist in that chain?).
[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/netfilter/nf_conntrack_tftp.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_tftp.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/netfilter/nf_conntrack_h323.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_h323.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/netfilter/nf_conntrack_sip.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_sip.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/netfilter/nf_conntrack_rtsp.ko"

[ util_execSystem ] 141:  setupModules cmd is "insmod /lib/modules/kmdir/kernel/net/ipv4/netfilter/nf_nat_rtsp.ko"

nf_nat_rtsp v0.6.21 loading
[ util_execSystem ] 141:  rsl_initPingWatchDogObj cmd is "pwdog &"

enable switch phyport...
Set: phy[0].reg[0] = 3900
Set: phy[1].reg[0] = 3900
Set: phy[2].reg[0] = 3900
Set: phy[3].reg[0] = 3900
Set: phy[4].reg[0] = 3900
Set: phy[0].reg[0] = 3300
Set: phy[1].reg[0] = 3300
Set: phy[2].reg[0] = 3300
Set: phy[3].reg[0] = 3300
Set: phy[4].reg[0] = 3300
resetMiiPortV over.
Set: phy[0].reg[4] = 01e1
Set: phy[0].reg[0] = 3300
[cmd_dutInit():1094] init shm
[tddp_taskEntry():151] tddp task start
Set: phy[1].reg[4] = 01e1
Set: phy[1].reg[0] = 3300
Set: phy[2].reg[4] = 01e1
Set: phy[2].reg[0] = 3300
Set: phy[3].reg[4] = 01e1
Set: phy[3].reg[0] = 3300
Set: phy[4].reg[4] = 01e1
Set: phy[4].reg[0] = 3300
turn off flow control over.
[ read_dhcpc_config ] 113: error, unable to open config file: /var/tmp/dconf/udhcpc.conf
[ util_execSystem ] 141:  prepareDropbear cmd is "dropbearkey -t rsa -f /var/tmp/dropbear/dropbear_rsa_host_key"

Will output 1024 bit rsa secret key to '/var/tmp/dropbear/dropbear_rsa_host_key'
Generating key, this may take a while...
[ util_execSystem ] 141:  prepareDropbear cmd is "dropbearkey -t dss -f /var/tmp/dropbear/dropbear_dss_host_key"

Will output 1024 bit dss secret key to '/var/tmp/dropbear/dropbear_dss_host_key'
Generating key, this may take a while...
[ util_execSystem ] 141:  prepareDropbear cmd is "dropbear -p 22 -r /var/tmp/dropbear/dropbear_rsa_host_key -d /var/tmp/dropbear/dropbear_dss_host_key -A /var/tmp/dropbear/dropbearpwd"

start ntp_request
[ oal_sys_getOldTZInfo ] 592:  Open TZ file error!
[ util_execSystem ] 141:  oal_sys_unsetTZ cmd is "echo "" > /etc/TZ"
```

Some key information of note from the boot logs were"

**Bootloader:** 

Appears to be a repurposed build of open source version `U-Boot 1.1.3 (Feb  3 2021 - 10:10:08)`, denoted as `Ralink UBoot Version: 4.3.0.0`

Bootloader default selected `3: System Boot system code via Flash.(0xbc010000)` as the boot option, may be able to interrupt boot process and select another boot option

**Linux Initilization:

Version: `Linux version 2.6.36 (jenkins@mobile-System) (gcc version 4.6.3 (Buildroot 2012.11.1) ) #1 Wed Feb 3 10:13:07 CST 2021`

CPU Information:  `CPU revision is: 00019655 (MIPS 24Kc)`

Kernel Command Line: `Kernel command line: console=ttyS1,115200 root=/dev/mtdblock2 rootfstype=squashfs init=/sbin/init`

Shows the console being set to ttyS1 with baud rate 115200 (this is the console session we are connected to). Show the root file system as type squashfs which is a compressed read-only file system. Show the initilization bin is /sbin/init.

Boot Partition Details:
EN25Q32B(1c 30161c30) (4096 Kbytes)
mtd .name = raspi, .size = 0x00400000 (4M) .erasesize = 0x00010000 (64K) .numeraseregions = 0
Creating 5 MTD partitions on "raspi":
0x000000000000-0x000000010000 : "boot"
0x000000010000-0x000000100000 : "kernel"
0x000000100000-0x0000003e0000 : "rootfs"
mtd: partition "rootfs" set to be root filesystem
0x0000003e0000-0x0000003f0000 : "config"
0x0000003f0000-0x000000400000 : "radio"

Identifies flash chip as EN25Q32B (the same chip we ID'd in initial recon)

Shows the partition of the ROM. 

Initilization Script: 
`starting pid 29, tty '': '/etc/init.d/rcS'`

Shows the location of the initilization script. 

Configuration Files:

Multiple configuration files listed for use during start up, the below appears to be a main configuration file.

`[ dm_readFile ] 2061:  can not open xml file /var/tmp/pc/reduced_data_model.xml!, about to open file /etc/reduced_data_model.xml`

Dropbear: 

Mutliple details about Dropbear initilization including the below line which also reveals what is most likely a writeable filepath. 

`[ util_execSystem ] 141:  prepareDropbear cmd is "dropbearkey -t rsa -f /var/tmp/dropbear/dropbear_rsa_host_key"`




