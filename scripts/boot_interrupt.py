#Example script to illustrate interuppting the TP-Link WR841n bootloader programmatically
#The script reboots the router and then sends the command tpl many times in order to interrupt the boot loader
#The WR841n bootloader is locked down to remove usual U-Boot functionality, however if regular functionality was available this script could be used to dump firmware using the md command and write it to a file

#Serial and time packages are required (serial can be installed with "pip3 install pyserial"
import serial
import time

#Set this as your desired serial port
port = "/dev/ttyUSB0"

#Open serial connection on the selected port with baudrate 115200, 8 data bits and one stop bit, no parity set by default
serial_port =  serial.Serial(port, baudrate=115200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)

#Empty string to hold serial reads
serial_string = ""

#Clear the input and output buffers of any previously cached reads and writes
serial_port.reset_output_buffer()

serial_port.reset_input_buffer()

#Send the reboot command and then wait 1 second for reboot to start
serial_port.write(b"reboot \r\b")
time.sleep(0.5)

#Send the tpl command to interrupt bootloader 10000 times continuously
for i in range(10000):
    serial_port.write(b"tpl \r\b")
    print("writing tpl #: " + str(i))

#Readout response to check for bootloader command prompt
while(True):
    serial_string=serial_port.readline()
    print(serial_string.decode("Ascii"))

    #Add in additional code to send md command and read contents out to file
