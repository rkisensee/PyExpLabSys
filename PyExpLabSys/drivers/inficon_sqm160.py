import serial
import time

class InficonSQM160():
    def __init__(self, port='/dev/ttyUSB0'):
        self.f = serial.Serial(port=port,
                               baudrate=9600,
                               timeout=2,
                               bytesize=serial.EIGHTBITS,
                               xonxoff=True)
        
    def comm(self,command):
        length = chr(len(command) + 34)
        crc = self.crc_calc(length + command)        
        command = '!' + length + command + crc[0] + crc[1]
        error = 0
        while (error > -1) and (error < 20):
            self.f.write(command)
            time.sleep(0.1)
            reply = self.f.read(self.f.inWaiting())
            crc = self.crc_calc(reply[1:-2])
            try:
                crc_ok = (reply[-2] == crc[0] and reply[-1] == crc[1])
            except IndexError:
                crc_ok = False
            if crc_ok:
                error = -1
                return_val = reply[3:-2]
            else:
                error = error + 1 
        return return_val


    def crc_calc(self, input_string):
        """ Calculate crc value of command """
        command_string = []
        for i in range(0, len(input_string)):
            command_string.append(ord(input_string[i]))
            
        crc = int('3fff', 16)
        mask = int('2001', 16)
        for command in command_string:
            crc = command ^ crc
            for i in range(0, 8):
                old_crc = crc
                crc  = crc >> 1
                if old_crc % 2 == 1:
                    crc = crc ^ mask
        crc1_mask = int('1111111', 2)
        crc1 = chr((crc & crc1_mask) + 34)
        crc2 = chr((crc >> 7) + 34)
        return(crc1,crc2)
        
    def show_version(self):
        command = '@'
        return(self.comm(command))

    def show_film_parameters(self, film):
        command = 'A1?'
        print self.comm(command)
        
    def rate(self, channel):
        """ Return the deposition rate """
        command = 'L' + str(channel)
        value_string = self.comm(command)
        rate = float(value_string)
        return(rate)

    def thickness(self, channel=1):
        """ Return the film thickness """
        command = 'N' + str(channel)
        value_string = self.comm(command)
        thickness = float(value_string)        
        return(thickness)
        
    def frequency(self, channel=1):
        """ Return the frequency of the crystal """
        command = 'P' + str(channel)
        value_string = self.comm(command)
        frequency = float(value_string)        
        return(frequency)

    def crystal_life(self,channel=1):
        command = 'R' + str(channel)
        value_string = self.comm(command)
        life = float(value_string)        
        return(life)
		
if __name__ == "__main__":
    inficon = InficonSQM160()
    inficon.show_version()

    #inficon.rate(1)
    #inficon.thickness(1)
    #inficon.frequency(1)
    #inficon.CrystalLife(1)
    #inficon.show_film_parameters(1)
    

