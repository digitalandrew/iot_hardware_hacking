
# Test Details

## Target Information

**Manufacturer:** TP-Link

**Part Number:** TL-WR841N

**Serial Number:** 22295L6001357
 
## Test-Equipment
 
**Multimeter:** ASTRO AI AM33D

**Logic Analyzer:** Comidox USB Logic Analyzer

**USB to UART Adapter:** Silicon Labs CP210x UART Bridge

**Flash ROM Programmer:** CH341a USB EPROM Programmer

**Software:** 
- Sigrok Pulsview (for logic captures)
- NMAP
- Firefox
- Screen
- Flashrom
- Binwalk
- DD (Data Duplicater)
- Openssl
- Cyberchef


# Initial Recon

## Visual Inspection

Inspected exterior of the router, and noted label on the back that contained FCC ID for further review. 

FCC ID: 2AXJ4WR841NV14

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/router_ffc_id.jpg)

Opened router case by removing two Phillips screws and applying pressure between pressure-fit parts with a spudger tool.

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/router_opened.jpg)

Noted three chips of interest on the PCB for further inspection (shown as details A, B, and C in the picture below)

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/router_areas_of_interest.jpg)

## On-board testing

Noted the presence of a test connection that appears to be a UART connection based on the 4 pins labelled with VCC, GND, RX and TX (shown as detail D above)

Verified operating voltage of the PCB is 9V by testing the voltage drop across the input jack with a multimeter. 

Identified ground connection on P1 (detail E above) by testing continuity with the ground connection on the input jack.

Tested the suspected UART connection with a multimeter to verify pins matched the silk screen labels, each was pin tested as follows:

- VCC: Measured voltage drop between VCC and ground as 3.3V confirming operating voltage of UART at 3.3V
- GND: Checked for continuity between GND pin on UART and known ground on board and confirmed GND is in fact a ground. 
- RX: Measured voltage drop between RX and ground as 0V, test to ensure it was not connected to ground by checking continuity between RX and known ground connections, no continuity found
- TX: Measured Voltage drop between RX and ground as ~3.3V during standard operation. 

After confirming pinout, based on the observations of the pins this appears to be a UART connection, checked for transmission on the TX pin during boot up by power cycling router and measuring voltage drop. Noted fluctuation on TX pin from ~1V - 3V suggests busy and active transmission during bootup.

Soldered through hole inline header pins to suspected UART connection to facilitate further testing with a logic analyzer and later on USB to Serial Adapter. 

Attached Logic Analyzer to TX and GND pins of UART connection and captured a transmission during boot up, a screenshot of single transmission frame shown below. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/Uart_Capture_Single_Frame.png)

Manual framing of the signal confirmed a UART transmission, noted the start bit, 8 data bits, one stop bit and no parity bit. 

Measured the baud rate as 125,000 however based on standard serial baud rates suspect that it is actually 115,200. 

Based on these findings applied a UART decoder to the channel with the below settings. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/uart_decoder_settings.png)

Decoded UART signal confirmed UART parameters and showed the presence of a boot loader and boot-up logs to be investigated further. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/uart_decoded_message.png)

## OSINT and Online Recon

Used previously located FCC ID to find FCC Equipment Authorization filing for the router (https://fccid.io/2AXJ4WR841NV14)

Noted in the filing that the ID had been changed from the previous TE7WR841NV14. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ffc_id_change_request.png)

Inspecting the previous filing (https://fccid.io/TE7WR841NV14) internal photos of the router were located. Unfortunately, schematics, functional descriptions and block diagrams were redacted as confidential. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/fcc-id-1.png)

Detailed pictures of two chips of interest were shown that detailed the chip manufacturer and part number. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ffc-id-mediatek.png)

Previously denoted chip A Id'd as MEDIATEK MT7628NN

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/fcc-id-zentel.png)

Previously denoted chip B Id'd as Zentel A3S56D40GTP -50L

Unfortunately, the markers on chip C were not readable in the FCC pictures. Returning to the test router, high-resolution pictures were taken and blown up to Id chip. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/cfeon_chip_id.jpg)

Chip C was Id'd as cFeon QH32B-104HIP.

Data sheets were located online for each of the chips. 

**MEDIATEK MT7628NN:** System On Chip (SOC) containing CPU. Important details included that this is a purpose-built SOC for N300 routers. The CPU is MIPS24KEc, which supports Linux 2.6.36 SDK and Linux 3.10 SDK. Interfaces with flash memory via SPI.

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

Notable detail confirmed the suspicion that the router is running Linux kernel 2.6.36. 

UDP scans revealed 2 open ports: 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/nmap_udp_scan.png)

Port 67/udp - dhcps

Port 1900/udp - UPnP

## Scouting Previously Disclosed CVEs

Scouted for previously disclosed and patched CVEs and multiple. Noted a common theme of a lack of proper user input validation on forms and inputs in the web portal that led to either buffer overflow or command injection of an underlying function or service being called.

https://www.opencve.io/cve?vendor=tp-link&product=tl-wr841n

https://blog.viettelcybersecurity.com/1day-to-0day-on-tl-link-tl-wr841n/

https://ktln2.org/2020/03/29/exploiting-mips-router/

# Enumeration via UART Connection

## Reviewing Bootlogs
Connected USB to UART adapter to the previously located UART pins based on the below pinout:

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/UART+to+USB+pinout.jpg)

Opened Terminal Session via Screen with the previously identified baud rate.

After powering on the router the bootloader logging and Linux initialization logging from init and init scripts were displayed over the serial console session:

**Command**: `screen /dev/ttyUSB0 115200`

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

Some key information of note from the boot logs were:

**Bootloader:** 

Appears to be a repurposed build of open source version `U-Boot 1.1.3 (Feb  3 2021 - 10:10:08)`, denoted as `Ralink UBoot Version: 4.3.0.0`

Bootloader default selected `3: System Boot system code via Flash.(0xbc010000)` as the boot option, may be able to interrupt boot process and select another boot option

**Linux Initilization**:

Version: `Linux version 2.6.36 (jenkins@mobile-System) (gcc version 4.6.3 (Buildroot 2012.11.1) ) #1 Wed Feb 3 10:13:07 CST 2021`

CPU Information:  `CPU revision is: 00019655 (MIPS 24Kc)`

Kernel Command Line: `Kernel command line: console=ttyS1,115200 root=/dev/mtdblock2 rootfstype=squashfs init=/sbin/init`

Shows the console being set to ttyS1 with a baud rate of 115200 (this is the console session we are connected to). Show the root file system as type squashfs which is a compressed read-only file system. Show the initialization bin is /sbin/init.

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

Shows the location of the initialization script. 

Configuration Files:

Multiple configuration files are listed for use during start-up, the below appears to be a main configuration file.

`[ dm_readFile ] 2061:  can not open xml file /var/tmp/pc/reduced_data_model.xml!, about to open file /etc/reduced_data_model.xml`

Dropbear: 

Multiple details about Dropbear initialization including the below line also reveal what is most likely a writeable filepath. 

`[ util_execSystem ] 141:  prepareDropbear cmd is "dropbearkey -t rsa -f /var/tmp/dropbear/dropbear_rsa_host_key"`

## Interupting Bootloader

Through online research, it was discovered that the bootloader interrupt command is "tpl". There is a very small window to interrupt the bootloader so the easiest way to do it is to issue a reboot command and then immediately being typing "tpl" repeatedly. 

```
~ # reboot
The system is going down NOW!
Sent SIGTERM to all processes
Terminated
Sent SIGKILL toRestarting system.
```

Doing so interrupted the bootloader and provided access to the bootloaders Command Line Interface. 

```

switch BootType:
   
4: System Enter Boot Command Line Interface.

U-Boot 1.1.3 (Feb  3 2021 - 10:10:08)
MT7628 # help     
Unknown command 'help' - try 'help'
MT7628 #   

```
Usually this CLI provides access to tools to read and write to memory, set environment details and gather further information about the board. Unfortunately, the repurposed version of U-Boot has removed this functionality. The only functionality remaining is to perform a TFTP boot. This can be done to boot from firmware over the network as a recovery method. 


## Enumeration via UART Shell

Pressing Enter revealed there was shell access with no login as root user:

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/initial_shell_access.png)

Checking over the available binaries in the bin folder, busybox was discovered: 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/busbox_bin_id.png)

Busybox is a popular binary used on embedded systems as it packages many common Linux/Unix binaries into one smaller package. 

Observing the available functions in busybox it was noted that this appears to be a stripped-down version of Busybox, however, TFTP was still available. 

## Transferring Full Version of Busybox over TFTP

The full version of Busybox was downloaded from: https://busybox.net/downloads/binaries/

The TFTP from the existing busybox was then used to transfer over the full version of busybox. 

Command From Kali VM to start TFTP server as daemon: `sudo atftpd --daemon`

Created a folder to transfer over tools in `/var/tmp/_tools` /var was previously identified as writable. 

Command from Router to initiate file transfer: `tftp -r busybox-mipsel -g 192.168.0.100`

The full version of busybox was then available to use for further enumeration. 

## Enumerating /var folder

Using the new full version of Busybox grep was utilized to search for files with "pass" in it in order to identify possible hardcoded passwords. 

Command: `/var/temp/_tools/busybox-mipsel grep -r 'pass' .`

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/grepping_pass.png)

Noted three config files that may contain passwords and what appears to be a hashed password for Dropbear. 

Config file passwords were blank, Dropbear hash was saved to attempt to crack at a later time. 

Command: `/var/temp/_tools/busybox-mipsel grep -r 'pass' .`

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/grep_admin.png)

Command: `/var/temp/_tools/busybox-mipsel find -name '*.xml'`

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/find_xml.png)

Command: `/var/temp/_tools/busybox-mipsel find -name '*.conf'`

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/find_conf.png)

Further enumeration of the config files did not reveal any additional useful information. 

## Cracking Password Hashes

Admin hash from passwd file was identified as Unix Md5 hash and cracked using the below command.

Command on Kali VM: `hashcat -a 0 -m 500 admin.hash /usr/share/wordlists/rockyou.txt`
 
Admin Password cracked as "1234" 

![iamge](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/hash_cat_admin.png)

Dropbear hash form dropbearpasswd file was identified as normal MD5 hash and cracked using the below command.

Command on Kali VM: `hashcat -a 0 -m 0 dropbear.hash /usr/share/wordlists/rockyou.txt`

Dropbear password was cracked "1234qwer" this was noted to be the password that was created for the admin login of the router via the browser. 

The password file is dynamically created on startup from the router's admin password. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/dropbear_hash.png)

## Checking Running Processes and Network Connections

The busybox binary transferred was used again to check the running processes via ps. 

Command: `/var/temp/_tools/busybox-mipsel ps`

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ps.png)

Noted that all processes were running as the admin user and there was no principle of least privilege being followed. 

The same process was followed to check running processes using netstat.

Command: `/var/temp/_tools/busybox-mipsel netstat` 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/netstat+-+Copy.png)

## Prompting Additional Console Log Messages

Looking through the unprompted console log messages one repeating log message stood out:

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/util_execSystem.png)

A repeated call by `[  util_execSystem  ]` appears to be indicative of a log from a function in a shared object library. 

It also appears to be a system call which is a c function that allows the running of a system command. These can be dangerous in nature for command injection if the function uses user input. 

These console log messages, especially those which allow tracing back to specific functions can allow for easier reverse engineering. To test this the wireless setup of the router was performed using the web portal. 

Wireless Setup
![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/wireless_setup.png)

This triggered many console logs that showed the use of the execSystem function for user-supplied inputs. 


```
[ rsl_sendAppWlanCfg ] 1232:  Tell TMPD server that wlan/guest cfg has been c
hanged.

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set 
CountryCode=US_NOCOUNTRY"

[ util_execSystem ] 141:  oal_wlan_ra_setCountryRegion cmd is "cp /etc/Single
SKU_FCC.dat /var/Wireless/RT2860AP/SingleSKU.dat"

[ util_execSystem ] 141:  oal_wlan_ra_setCountryRegion cmd is "iwpriv ra0 set
 CountryRegion=0"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set 
WirelessMode=9"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set 
HtBw=1"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set 
HtBssCoex=0"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set AutoChannelSel=2"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set Channel=0"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanBasicCfg cmd is "iwpriv ra0 set SSID='i''o''t''h''a''c''k''i''n''g'"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set TxPower=100"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set BeaconPeriod=100"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set RTSThreshold=2346"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set FragThreshold=2346"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set DtimPeriod=1"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set HtGi=1"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set HideSSID=0"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set WmmCapable=1"

[ util_execSystem ] 141:  oal_wlan_ra_setWlanAdvCfg cmd is "iwpriv ra0 set NoForwarding=0"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set AuthMode=WPA2PSK"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set EncrypType=AES"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set IEEE8021X=0"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set DefaultKeyID=2"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set SSID='i''o''t''h''a''c''k''i''n''g'"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set RekeyInterval=0"

[ util_execSystem ] 141:  oal_wlan_ra_setSec cmd is "iwpriv ra0 set WPAPSK='1''2''3''4''5''q''w''e''r''t'"

[ util_execSystem ] 141:  oal_wlan_ra_updateWlanCfg cmd is "iwpriv ra0 set AccessPolicy=0"

[ util_execSystem ] 141:  oal_wlan_ra_updateWlanCfg cmd is "iwpriv ra0 set SSID='i''o''t''h''a''c''k''i''n''g'"

[ util_execSystem ] 141:  oal_wlan_ra_updateWlanCfg cmd is "ifconfig ra1 down"

[ util_execSystem ] 141:  oal_wlan_ra_updateWlanCfg cmd is "ifconfig ra0 down; "

br0: port 1(ra0) entering forwarding state
[ util_execSystem ] 141:  oal_wlan_ra_updateWlanCfg cmd is "ifconfig ra0 up; "

[RTMPReadParametersHook:297]wifi read profile faild.
efuse_probe: efuse = 10000012
exec!
spiflash_ioctl_read, Read from 0x003f0000 length 0x400, ret 0, retlen 0x400
eeFlashId = 0x7628!
tx or rx disable[f0000300][count=0]!!!
tx or rx disable[f0000300][count=1]!!!
tssi_1_target_pwr_g_band = 36
[ ntp_start ] 504:  ntp connect failed, return.

[APCheckBcnQHandler] check_point_num  5 == 4  ARB_SCR=[f0000001]
br0: port 1(ra0) entering forwarding state
br0: port 1(ra0) entering forwarding state
[ util_execSystem ] 141:  oal_intf_setIntf cmd is "ifconfig br0 192.168.0.1 netmask 255.255.255.0 up"

[ util_execSystem ] 141:  oal_util_setProcLanAddr cmd is "echo "br0 16820416," > /proc/net/conntract_LocalAddr"

[ util_execSystem ] 141:  oal_sys_unsetTZ cmd is "echo "" > /etc/TZ"

iptables: Bad rule (does a matching rule exist in that chain?).
spiflash_ioctl_read, Read from 0x003e0000 length 0x10000, ret 0, retlen 0x10000
.
spiflash_ioctl_erase, erase to 0x003f0000 length 0x0, nerase done
spiflash_ioctl_write, Write to 0x003e0000 length 0x10000, ret 0, retlen 0x10000
```
Primary investigation showed that some user validation was being performed on the inputs, notably the SSID and Password had their individual characters escaped. 

Further investigation to be performed by using the function names to trace back and reverse engineering the firmware. 

# Firmware Extraction and Analysis

## Firmware Extraction from onboard ROM

From the previous recon, it was confirmed that the flash ROM on the board (EN25Q32B-104HIP) was using SPI to communicate with the processor, to confirm this a logic analyzer was attached to the pins of the ROM using test clips. 

The initial boot process was captured as this process contains many reads from the processor to the flash ROM. The logic analyzer confirmed the SPI function of the flash ROM matched that of the datasheet. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/SPI_capture.png)

After confirming the SPI flash functioned as expected a ch341a flash programmer was connected to the flash ROM as per the data sheet pinout in order to read the entire contents of the flash ROM. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ch341a_programmer_setup.jpg)

The firmware was then extracted from the ROM using flashrom and the following command:

`flashrom -p ch341a_spi -r tp_link_wr841n_ext.bin`

## Firmware Analysis

To confirm the firmware extraction was successful an initial analysis was performed on it using binwalk with the following command:

`binwalk tp_link_wr841n_ext.bin`

The initial analysis by binwalk showed that the extraction appeared to be successful as it was able to pickout three partitions on the firwmare that very closely matched the partition table that was previously observed during bootup. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/binwalk_init_analysis.png)

As an additional confirmation, the entropy of the file was analyzed using binwalk. 

`binwalk -E tp_link_wr841n_ext.bin`

The entropy confirmed the layout of the firmware matched what was expected on the ROM. The first partition was clearly the unencrypted/uncompressed bootloader as the entropy was floating around 0.5. 

The second partition matched the starting address location and length of the kernel. The entropy being around a solid 1 confirms that it is LZMA compressed as was shown by binwalk.

The third partition also matched the starting address location and length of the root file system, in addition the entropy shows that it is in fact compressed as well. 

An additional partition or section of data is visible in the entropy analysis that binwalk was not able to identify previously, this most likely indicates an encrypted section. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/binwalk_entropy.png)

Binwalk was then used to automatically extract the contents of the firmware. 

`binwalk -e tp_link_wr841n_ext.bin`

The automatic extraction by binwalk was able to carve out the LZMA compressed kernel and squashfs filesystem and then automatically decompress both of the files. 

As binwalk was not able to automatically extract the bootloader it was extracted manually using dd. 

`dd if=tp_link_ext.bin bs=1 skip=53536 count=12512 of=u_boot.bin`

After extracting the root file system the contents of it were enumerated which revealed multiple binaries and shared object files that may be of interest to reverse engineer. In addition, two config files called  *default_config.xml* and  *reduced_data_model.xml* were located however these config files appear to be encrypted. 

Strings was then used to identify any binaries or shared object files that had the above xml file names as strings in them to identify which files to reverse engineer in an attempt to decrypt them. 

`strings -f * | grep ".xml"`

This revealed that the libcmm.so shared object file had both the xml file names as strings in it. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/strings_xml_files.png)


# Reverse Engineering

## Locating Decryption Algorithm and Key

The libcmm.so was loaded in Ghidra and decompiled in an attempt to reverse engineer the encryption/decryption of the xml files. 

Running a search for "decrypt" in Ghidra revealed a function called "dm_decryptFile" that was then investigated further. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ghidra_decrypt_search.png)

Upon initial inspection of the decompiled, based on the error messaging this appeared to be the correct function to decrypt the config files. 

Some variables were renamed based on guesses of their function based on the decompiled code. 

```
int dm_decryptFile(uint dm_file_size,undefined4 param_2,uint dec_buf_size,int param_4)

{
  int iVar1;
  int iVar2;
  char enc_key [8];
  
  memcpy(enc_key,&DAT_000c9f70,8);
  if (dec_buf_size < dm_file_size) {
    cdbg_printf(8,"dm_decryptFile",0xbcf,
                "Buffer exceeded, decrypt buf size is %u, but dm file size is %u",dec_buf_size,
                dm_file_size);
    iVar2 = 0;
  }
  else {
    iVar2 = cen_desMinDo(param_2,dm_file_size,param_4,dec_buf_size,enc_key,0);
    iVar1 = iVar2;
    if (iVar2 == 0) {
      cdbg_printf(8,"dm_decryptFile",0xbd6,"DES decrypt error\n");
    }
    else {
      do {
        iVar2 = iVar1;
        if (((undefined *)(param_4 + iVar2))[-1] != '\0') break;
        iVar1 = iVar2 + -1;
      } while (iVar2 != 0);
      *(undefined *)(param_4 + iVar2) = 0;
    }
  }
  return iVar2;

```

Reverse engineering of the function revealed that based on the error messaging and the cen_desMinDo() function the encryption algorithm appears to be DES. Further research on the DES algorithm reveals that it uses 64-bit (8 x 8 bytes) keys. An array of 8 chars was noted to be created at the start of the function and then memcpy is later used to copy 8 bytes into it from a data location in the .data section of the shared object file. Inspecting the data location revealed what appears to be the DES encryption key. As DES is a symmetric encryption algorithm it can also be used for decryption. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ghidra_des_enc_key.png)

**DES Encryption Key:** 478DA50FF9E3D2CB

The *default_config.xml* file was then decrypted using OpenSSL and the above key. 

`openssl enc -d -des-ecb -K 478DA50FF9E3D2CB -nopad -in default_config.xml`

Unfortunately, this config file did not contain any notable details. 

The *reduced_data_model.xml* config file was then decrypted making use of Cyberchef (https://cyberchef.io/).

It also did not contain any notable details but confirmed that it was using the same encryption key and scheme as the previous xml file. 

## Checking for command injection

Based on the previous testing performed on the web portal and reviewing the console logging in UART it appears that some of the functions of the router are being performed by making system calls to execute bash commands. More specifically it appears that some of these system calls are being passed user supplied inputs from the web portal. 

Initial recon showed that some of the user supplied inputs were at a minimum being escaped as individual characters to prevent command injection, however use of system calls on user supplied inputs can lead to command injection. 

The util_execSystem function which appeared to be the one performing the system calls was located to be part of the libcmm.so shared object file by using strings to search for it through the binaries and other shared object files. 

`strings -f * | grep "util_execSystem"`

The util_execSystem function was then found via a program text search in Ghidra using the previously decompiled  libcmm.so that was investigated above. 

```
int util_execSystem(int cmd_id,char *unformat_string,undefined4 str_format_var_1,
                   undefined4 str_format_var_2)

{
  char *pcVar1;
  __pid_t _Var2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 va_ptr_format_var;
  undefined4 va_end_format_var;
  uint local_234;
  char cmd_string [512];
  int local_30;
  char *cmd_string_ptr;
  
  cmd_string_ptr = cmd_string;
  local_234 = 0;
  va_ptr_format_var = str_format_var_1;
  va_end_format_var = str_format_var_2;
  memset(cmd_string_ptr,0,0x200);
  local_30 = vsnprintf(cmd_string_ptr,0x1ff,unformat_string,&va_ptr_format_var);
  cdbg_printf(8,"util_execSystem",0xb9,"%s cmd is \"%s\"\n",cmd_id,cmd_string_ptr);
  iVar5 = 1;
  if (0 < local_30) {
    while( true ) {
      local_234 = system(cmd_string);
      uVar3 = local_234 & 0x7f;
      if ((int)local_234 < 0) {
        if (local_234 == 0xffffffff) {
          cdbg_printf(8,"util_execSystem",0xcd,"system fork failed.",cmd_id,cmd_string_ptr);
        }
        else {
          perror("util_execSystem call error:");
        }
      }
      else if (uVar3 == 0) {
        iVar6 = (int)(local_234 & 0xff00) >> 8;
        if (iVar6 == 0) {
          return 0;
        }
        if (iVar6 != 4) {
          return iVar6;
        }
        pcVar1 = strstr(cmd_string,"iptable");
        if (pcVar1 == (char *)0x0) {
          return 4;
        }
        sleep(1);
      }
      else {
        if ((int)((uVar3 + 1) * 0x1000000) >> 0x19 < 1) {
          if ((local_234 & 0xff) == 0x7f) {
            uVar4 = 0xe6;
            pcVar1 = "process stopped, signal number = %d\n";
            uVar3 = (int)(local_234 & 0xff00) >> 8;
          }
          else {
            uVar4 = 0xe8;
            pcVar1 = "Oh,no possible here. status = %d\n";
            uVar3 = local_234;
          }
        }
        else {
          uVar4 = 0xe4;
          pcVar1 = "abnormal termination, signal number = %d\n";
        }
        cdbg_printf(8,"util_execSystem",uVar4,pcVar1,uVar3,cmd_string_ptr);
        while (_Var2 = waitpid(-1,(int *)&local_234,1), 0 < _Var2) {
          cdbg_printf(8,"util_execSystem",0xee,"get a zombie process %d",_Var2);
        }
      }
      if (iVar5 == 3) break;
      cmd_id = iVar5;
      cdbg_printf(8,"util_execSystem",199,"system execute again, and %d times",iVar5);
      iVar5 = iVar5 + 1;
    }
  }
  return -1;
}
```
Review of the decompiled source code revealed that the function was in fact making system calls. The only formatting being performed on the inputs to the function which were passed to the system call was to format the specified arguments into the command string using the vsnprintf function. No further validation appeared to be performed in the util_execSystem function on the string created which would then be passed into the system call. This finding demonstrates that all validation or checking of user inputs for things like command injection characters or escaping characters must be done by what ever calls the util_execSystem. 

Previously the Wireless Setup was run and the user specified SSID and PSK were passed onto the util_execSystem however the debugging messages shown in the UART console logs showed that the user speicifed values had each individual character escaped by single quotation marks. This is done to prevent command injection as any characters such as ";" or "&" will only be interpretted as a string and not as part of the command. 

Further investigation was done to see how this escaping was performed. In order to locate the file or binary that was making the specific util_execSystem call that was printing the debug message seen earlier strings and grep was used to search for words in the string (keeping in mind the formatting of the input string performed by the util_execSystem function itself. The string used that matched the formatting previously seen in the util_execSystem function was found again in the libcmm.so shared object. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/iwpriv_strings_grep.png)

Searching for the string making use of the strings search in Ghidra led to the function that appeared to be calling util_execSystem to update the SSID when the wireless setup was being performed in the previous test. 

![image](https://iot-hw-hacking-resources.s3.us-east-2.amazonaws.com/ghidra_iwpriv_reference.png)

The string had 9 references to it in the rest of the libcmm.so, following the first external reference luckily led to the correct function that was performing the util_execSystem call from the previous wireless setup test. Unfortunately this function had it's label (name) removed in the compilation process and as such Ghidra added the generic FUN_XXXX label to it. 

```
int FUN_000aa1e8(int param_1,undefined4 param_2,char *param_3,int param_4,undefined4 unsan_ssid)

{
  int iVar1;
  undefined4 uVar2;
  char *pcVar3;
  int local_1c0;
  int local_1bc;
  char acStack_1b8 [12];
  char acStack_1ac [20];
  undefined auStack_198 [32];
  undefined auStack_178 [32];
  undefined SSID [100];
  undefined auStack_f4 [196];
  char *local_30;
  
  local_1bc = 1;
  local_1c0 = 1;
  cstr_strncpy(auStack_178,&DAT_000c1e4c,0xc);
  cstr_strncpy(auStack_198,&DAT_000c302c,4);
  iVar1 = oal_wlan_getSecMode(param_1,&local_1bc,&local_1c0);
  if (iVar1 == 0) {
    if (local_1bc - 1U < 0xb) {
                    /* WARNING: Could not find normalized switch variable to match jumptable */
                    /* WARNING: This code block may not be properly labeled as switch case */
      strcpy(acStack_1ac,"OPEN");
    }
    uVar2 = 2;
    if (local_1c0 - 1U < 5) {
                    /* WARNING: Could not find normalized switch variable to match jumptable */
                    /* WARNING: This code block may not be properly labeled as switch case */
      uVar2 = 2;
      strcpy(acStack_1b8,"NONE");
    }
    else if (local_1c0 == 2) {
      uVar2 = *(undefined4 *)(param_1 + 0x17c);
    }
    iVar1 = strcmp("Up",param_3);
    if (iVar1 != 0) {
      return 0;
    }
    util_execSystem("oal_wlan_ra_setSec","iwpriv %s set AuthMode=%s",param_2,acStack_1ac);
    util_execSystem("oal_wlan_ra_setSec","iwpriv %s set EncrypType=%s",param_2,acStack_1b8);
    util_execSystem("oal_wlan_ra_setSec","iwpriv %s set IEEE8021X=0",param_2);
    if (local_1c0 == 2) {
      if (*(char *)(param_1 + 0x180) != '\0') {
        FUN_000aa13c(auStack_f4,param_1 + 0x180);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set Key1=%s",param_2,auStack_f4);
      }
      if (*(char *)(param_1 + 0x210) != '\0') {
        FUN_000aa13c(auStack_f4,param_1 + 0x210);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set Key2=%s",param_2,auStack_f4);
      }
      if (*(char *)(param_1 + 0x2a0) != '\0') {
        FUN_000aa13c(auStack_f4,param_1 + 0x2a0);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set Key3=%s",param_2,auStack_f4);
      }
      if (*(char *)(param_1 + 0x330) != '\0') {
        FUN_000aa13c(auStack_f4,param_1 + 0x330);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set Key4=%s",param_2,auStack_f4);
      }
    }
    util_execSystem("oal_wlan_ra_setSec","iwpriv %s set DefaultKeyID=%d",param_2,uVar2);
    if (local_1c0 - 1U < 2) {
      return 0;
    }
    FUN_000aa13c(SSID,unsan_ssid);
    util_execSystem("oal_wlan_ra_setSec","iwpriv %s set SSID=%s",param_2,SSID);
    util_execSystem("oal_wlan_ra_setSec","iwpriv %s set RekeyInterval=%d",param_2,
                    *(undefined4 *)(param_1 + 0xf0));
    if ((((local_1bc - 6U < 2) || (local_1bc == 9)) || (local_1bc == 10)) || (local_1bc == 0xb)) {
      FUN_000aa13c(auStack_f4,param_1 + 0xae);
      util_execSystem("oal_wlan_ra_setSec","iwpriv %s set WPAPSK=%s",param_2,auStack_f4);
      return 0;
    }
    iVar1 = oal_wlan_getBrNamebyIfName(param_4,param_4,auStack_198);
    if (iVar1 == 0) {
      iVar1 = oal_wlan_getIfAddr(auStack_198,auStack_178);
      if (iVar1 == 0) {
        local_30 = "bObj";
        iVar1 = strcmp("2.4GHz",(char *)(param_4 + 1099));
        if (iVar1 == 0) {
          pcVar3 = "killall -q  -SIGINT rt2860apd";
        }
        else {
          pcVar3 = "killall -q  -SIGINT rtinicapd";
        }
        util_execSystem("oal_wlan_ra_setSec",pcVar3);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set IEEE8021X=0",param_2);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set SSID=%s",param_2,SSID);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set RADIUS_Server=%s",param_2,param_1 + 0xf4
                       );
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set RADIUS_Port=%d",param_2,
                        *(undefined4 *)(param_1 + 0x134));
        FUN_000aa13c(auStack_f4,param_1 + 0x138);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set RADIUS_Key=%s",param_2,auStack_f4);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set EAPifname=%s",param_2,auStack_198);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set own_ip_addr=%s",param_2,auStack_178);
        util_execSystem("oal_wlan_ra_setSec","iwpriv %s set SSID=%s",param_2,SSID);
        sleep(4);
        iVar1 = strcmp("2.4GHz",(char *)(param_4 + 1099));
        if (iVar1 == 0) {
          pcVar3 = "rt2860apd &";
        }
        else {
          pcVar3 = "rtinicapd &";
        }
        util_execSystem("oal_wlan_ra_setSec",pcVar3);
        return 0;
      }
      uVar2 = 0xbb2;
    }
    else {
      uVar2 = 0xbad;
    }
  }
  else {
    uVar2 = 0xb10;
  }
  cdbg_perror("oal_wlan_ra_setSec",uVar2,iVar1);
  return iVar1;
}

```

The util_execSystem function call in reference was located using the specific formatting string "iwpriv %s set SSID=%s" that previously found. 

The parameters being passed into the function lined up with what was expected from the investigation of the util_execSystem function. The last parameter was cleary the SSID, searching through the rest of the function for more references to the SSID variable showed that above the util_execSystem call in question another function "FUN_000aa13c" was called and passed the SSID variable. 

Following the function in libcmm.so showed that the function was responsible for performing the character escaping on the SSID. 

```

void FUN_000aa13c(int param_1,char *param_2)

{
  char cVar1;
  size_t sVar2;
  undefined *puVar3;
  int iVar4;
  int iVar5;
  
  sVar2 = strlen(param_2);
  iVar4 = 0;
  for (iVar5 = 0; puVar3 = (undefined *)(param_1 + iVar4), iVar5 < (int)sVar2; iVar5 = iVar5 + 1) {
    if (*param_2 == '\'') {
      *puVar3 = 0x5c;
      iVar4 = iVar4 + 2;
      puVar3[1] = *param_2;
    }
    else {
      *puVar3 = 0x27;
      cVar1 = *param_2;
      iVar4 = iVar4 + 3;
      puVar3[2] = 0x27;
      puVar3[1] = cVar1;
    }
    param_2 = param_2 + 1;
  }
  *puVar3 = 0;
  return;
}

```
Review of the function indicated that it iterated over the unsanitized SSID and performed individual character espacing by first checking if the character was already a single quote and if it was adding the c escape character "\" infront of it. It then padded each individual character by shifting a single quotation "'" infront of and behind each character. 

This function was also called prior to the util_execSystem call that used the PSK specified by the user. 

The character escaping appears to be properly implemented so this specific call of the util_execSystem does not appear vulnerable to command injection, however Ghidra noted that there are 510 references to the function inside the libcmm.so file. Upon initial inspection many of these appear to be other functions that are calling util_execSystem. These functions should be reviewed to check if there is anyway to pass unsatized user inputs into the util_execSystem function. 







