import serial
import keyboard
import time
import sys

#After installing Python, one needs to install following modules under command prompt
#
#    python -m pip install -U pyserial --user
#    python -m pip install -U keyboard --user
#
#This sample program will start DATAQ Instrument (11xx/2108/4108/4208/4718) usb data acquisition products
#Please make sure the device is in CDC mode (blinking yellow when conntected)
#Press key 'x' to EXIT
#since serDataq.readline waits until a line is received, low sample rate makes the program slow in response to key stroke

CONST_SER_PORT = 'COM23'   #get the com port from device manger and enter it here

serDataq = serial.Serial(CONST_SER_PORT)

#for Windows 10, one may run into the exception of "serial.serialutil.SerialException: Cannot configure port, something went wrong. Original message: WindowsError(87, 'Incorrect Parameter.') exception."
#
#Work around until pyserial has fix:, find serialwin32.py inside the folder of c:\users\??? window 10\AppData\Roaming\Python\Python37\site-packages\serial\
#then comment out the following lines in line 219:
#
#    if not win32.SetCommState(self._port_handle, ctypes.byref(comDCB)):
#    raise SerialException(
#        'Cannot configure port, something went wrong. '
#        'Original message: {!r}'.format(ctypes.WinError()))
#
#
#To single step through PY codes, follow
#https://stackoverflow.com/questions/4929251/how-to-step-through-python-code-to-help-debug-issues

acquiring=0
serDataq.write(b"stop\r")        #stop in case device was left scanning
serDataq.write(b"eol 1\r") 
serDataq.write(b"encode 1\r")    #set up the device for ascii mode
#before acquistion starts, we can simply use din() to read the status of D1/Rcrd
#once acquistion starts, we can't use din, so we add digital input to the scanlist
serDataq.write(b"slist 0 8\r")   #scan list position 0 is digital input
serDataq.write(b"slist 1 1\r")   #one analog channel
serDataq.write(b"srate 6000\r") 
serDataq.write(b"dec 500\r") 
serDataq.write(b"deca 3\r") 
time.sleep(1)  
serDataq.read_all()              #flush all command responses
#serDataq.write(b"start\r")           #start scanning

#this program will monitor the state of D1/Rcrd, if it sees a 0 (closed), it will start acquisition
#acquisition stops when D1/Rcrd turns 1 (open)

while True:
    if acquiring == 0:
        serDataq.write(b"din\r")
        line = serDataq.readline().decode("utf-8")
        din=str.split(line, " ")
        if int(din[1])&0x2:
            remoteflag=1
        else:
            remoteflag=0
        print ("Close D1//Rcrd to start acquisition")    
        if remoteflag==0:
            acquiring =1
            serDataq.write(b"start\r")             
    else:        
        try:
            if keyboard.is_pressed('x'):    #if key 'x' is pressed, stop the scanning and terminate the program
                serDataq.write(b"stop\r")
                time.sleep(1)           
                serDataq.close()
                print("Good-Bye")
                break
            else:
                i= serDataq.inWaiting()
                if i>0:
                    line = serDataq.readline().decode("utf-8")
                    din=str.split(line, ",")
                    print(line + "    Open D1//Rcrd to stop acquisition ")

                    #because digital channel is displayed as 10V range in CDC mode, we will do some dirty trick to extract the digital channel
                    if float(din[0])> 9.8:
                        serDataq.write(b"stop\r")
                        time.sleep(1)           
                        serDataq.close()
                        print("Terminted by open D1/Rcrd")
                        break                        
                pass
        except:
            pass
