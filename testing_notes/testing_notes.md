
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

** Command: `screen /dev/ttyUSB0 115200`



