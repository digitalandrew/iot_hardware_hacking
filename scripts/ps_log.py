#This script connects via serial to the an embedded Linux device and continuously checks the running processes writing them out to a txt file 

#serial and time packages are required (serial can be installed with "pip3 install pyserial")
import serial
import time

#Set this as your desired serial port
port = "/dev/ttyUSB0"

#Open serial connection on the selected port with baudrate 115200, 8 data bits and one stop bit, no parity set by default
serial_port = serial.Serial(port, baudrate=115200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)

#Empty string to hold serial reads
serial_string = ""

#While loop to continuously read and write while the script is running
while(True):

    #Wait 10 seconds between writes, placed at the start to allow time for serial connection to properly open on first attempt
    time.sleep(10)

    #Write ps command
    serial_port.write(b"ps \r\b")

    #Read out from the serial port until ps is read, when listing the processes the ps that was run will generally be the last in the list
    serial_string = serial_port.read_until("ps")

    #Print the contents decoding them from bytes to Ascii
    print(serial_string.decode("Ascii"))
    
    #Open a log file and add the results of the most recent read to the log file
    with open("ps_log.txt", "w") as f:
        f.write(serial_string.decode("Ascii"))

    print("Waiting 10 Seconds...")
