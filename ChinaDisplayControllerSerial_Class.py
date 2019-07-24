# -*- coding: utf-8 -*-

import serial, collections
from time import sleep

class ChinaDisplayControllerSerial:
    """Class to communicate with certain/several displays / large format panels with an Android controller.
    
    The Android controllers consume raw bytes and returns:
        Null/None (no commumincation), OKOK or NGNG.
    Be aware that returns that are not Null/None, OKOK or NGNG 
        may mean the controller is still booting.
    
    Attributes:
        comm_port : str 
            port/device connected to display (RS232 comm port)
        comm_speed : int : default = 38400
            port baudrate
        display_type : string !!! BEWARE: Case sensitive !!!
            Code table / Display type to use
        debugLevel : int : default 1
            0 : no debug text
               to
            3 : most debug text
	
	Some commands are not always implmented on the panel (E.G GET_SERIAL, Power_ON, number keys)
	
	Trademarks belong to their respective companies
	
	@author Simon Francklin
	@license MIT
	@status Alpha
	@version 0.1
	@date 2019/07/24
	
	@Note Tabs are used.
	
	@change v0.1 : Release to wild. Basic testing done.
    """
	
    __BAD_TEST_KEYS = ['POWER_OFF']
    CodeTable={
			# Information found from various sources (mostly Internet searches)
            "AverMedia":{ 
                #CodeTable 0 (AverMedia)
                'POWER_ON':'69 53 43',
                'POWER_OFF':'69 76 20',
                'MUTE':'69 37 5F',
                '1':'69 92 04',
                '2':'69 A2 F4',
                '3':'69 B2 E4',
                '4':'69 93 03',
                '5':'69 A3 F3',
                '6':'69 B3 E3',
                '7':'69 94 02',
                '8':'69 A4 F2',
                '9':'69 B4 E2',
                '0':'69 95 01',
                'MENU':'69 80 16',
                'LEFT':'69 63 33',
                'RIGHT':'69 66 30',
                'DOWN':'69 43 53',
                'UP':'69 46 50',
                'VOL_UP':'69 82 14',
                'VOL_DOWN':'69 85 11',
                'CH_UP':'69 C4 D2',
                'CH_DOWN':'69 C5 D1',
                'SOURCE':'69 19 7D',
                'ENTER':'69 07 8F',
                'TO_AV':'89 55 0D 14',
                'TO_VGA':'89 65 03 0E',
                'TO_YPbPr':'89 55 04 1D',
                'TO_HDMI0':'89 65 0E 03',
                'TO_HDMI1':'89 65 05 0C',
                'TO_HDMI2':'89 65 07 0A',
                'TO_HDMI3':'89 65 09 08',
                'TO_HDMI4':'89 65 0B 06',
                'TO_OPS':'89 65 0D 04',
                'FREEZE':'89 55 06 1B'
            },
            "KTC":{
                #CodeTable 1 (KTC)
                'POWER_OFF':'69 76 20',
                'POWER_ON':'69 53 43',
                'ENTER':'69 07 8F',
                'MUTE':'69 37 5F',
                '1':'79 85 01',
                '2':'79 84 02',
                '3':'79 83 03',
                '4':'79 82 04',
                '5':'79 81 05',
                '6':'79 80 06',
                '7':'79 7F 07',
                '8':'79 7E 08',
                '9':'79 7D 09',
                '0':'79 86 00',
                'VOL_UP':'79 41 45',
                'VOL_DOWN':'79 42 44',
                'CH_UP':'79 10 76',
                'CH_DOWN':'79 11 75',
                'SOURCE':'69 19 7D',
                'MENU':'69 80 16',
                'LEFT':'69 63 33',
                'RIGHT':'69 66 30',
                'DOWN':'69 43 53',
                'UP':'69 46 50',
                'SCREENSIZE':'79 13 73',
                'PICTUREMODE':'79 14 72',
                'SOUNDMODE':'79 15 71',
                'SLEEPTIMER':'79 16 70',        
                'BLANK':'79 45 41',
                'GET_POWERSTATUS':'79 33 53',
                'GET_POWERSAVEMODE':'79 30 56',
                'GET_DISPLAYSERIALNUMBER':'79 26 60',
                #Table V3? HoverCam KTC 
                'GET_MUTE':'79 44 42',
                'GET_VOLUME':'79 43 43',
                'GET_OPSINSTALLED':'79 31 55',
                'GET_OPSSTATE':'79 32 54',
                'GET_DISPLAYMODE':'79 25 61',
                'GET_CONTRAST':'79 21 65',
                'GET_BRIGHTNESS':'79 20 66',
                'GET_SHARPNESS':'79 22 64',
                'GET_COLORTEMP':'79 23 63',
                'TO_AV':'89 55 0D 14',
                'TO_VGA':'89 65 03 0E',
                'TO_YPbPr':'89 55 04 1D',
                'TO_HDMI0':'89 65 0E 03',
                'TO_HDMI1':'89 65 05 0C',
                'TO_HDMI2':'89 65 07 0A',
                'TO_HDMI3':'89 65 09 08',
                'TO_HDMI4':'89 65 0B 06',
                'TO_OPS':'89 65 0D 04',
                'FREEZE':'89 55 06 1B',
                'TO_ANDROID':'89 65 06 0B',
                'EXIT_ANDROID':'89 15 53 0E'
            }
        }

    def __init__ (self, comm_port : str, comm_speed = 38400, display_type : str = 'AverMedia', debugLevel : int = 1):
        self.debugText = debugLevel
        if (debugLevel > 1):
            _tempvar=[ct for ct in self.CodeTable.keys() if ct == display_type]
            print("Tables:",_tempvar)
        self.useCodeTable = [ct for ct in self.CodeTable.keys() if ct == display_type][0]
        
        self.serialcomm = serial.Serial()
        
        self.serialcomm.port = comm_port
        self.serialcomm.baudrate = comm_speed
        self.serialcomm.bytesize = serial.EIGHTBITS
        self.serialcomm.parity = serial.PARITY_NONE
        self.serialcomm.stopbits = serial.STOPBITS_ONE
        self.serialcomm.xonxoff = False
        self.serialcomm.rtscts = False
        self.serialcomm.dsrdtr = False
        self.serialcomm.writeTimeout = 1
        self.serialcomm.timeout = 0.1
        #self.serialcomm.readTimeout = 0.1
        #self.serialcomm.timeout = None
            
        try:
            if ( self.debugText >= 1):
                print ("Starting access to ", comm_port)
                self.serialcomm.open()
                self.serialcomm.flushInput()
                self.serialcomm.flushOutput()
                self.serialcomm.close()
        except Exception as exception:
            print ("Exception occured: %s" %str(exception))

    def sendhex (self, hexstr : str):
        """
            Sends a hex codes as bytes to the display
            
            Attributes:
            key : str 
                Key to send (MUST BE PART OF CODE TABLE)
        """
        serialreturn = ""
        if ( self.debugText >= 2):
            print("Writing %s to device" %bytes.fromhex(hexstr))
        try:
            if not(self.serialcomm.isOpen()):
                self.serialcomm.open()
            self.serialcomm.flushInput()
            self.serialcomm.flushOutput()
        
            self.serialcomm.write(bytes.fromhex(hexstr))
            sleep(0.5)
            #self.serialcomm.write(b'\r')
            numberOfLines = 0
    		
            
            while True:
                thisread = self.serialcomm.read(10)
                if (self.debugText >= 2):
                    print(thisread)
                serialreturn = serialreturn + thisread.decode('UTF8') 
                    
                numberOfLines += 1
                if (numberOfLines > 3):
                    break
                #sleep(0.05)
                    
                if (self.debugText >= 3 ):
                    print("Written...")

            self.serialcomm.close()
        except Exception as exception:
            print ("Exception occured: \n%s\n" %str(exception))
            #else:
            #S    print ("Cannot open %s", self.serialcomm.serial)
            
        return serialreturn

    def sendKey(self, key : str):
        """
            Sends a keypress to the display
            
            Attributes:
            key : str 
                Key to send (MUST BE PART OF CODE TABLE)
        """
        if (self.debugText > 1):
            print("Using CodeTable: ", self.useCodeTable)
            print(self.CodeTable[self.useCodeTable])    
            print("Key: ",key)
        
        keyhex = (self.CodeTable[self.useCodeTable]).get(key)
        if (keyhex is None):
            raise Exception("Invalid key to send")
        print("RETURNED:",self.sendhex(keyhex))
    
    def __intersection(self, list1, list2): 
        list3 = [value for value in list1 if value in list2] 
        return list3 
    
    def testVersion (self):
	""" 
	@note Broken
	@Todo change the way CodeTable is handled
	"""
        common_keys = self.__intersection( self.CodeTable[0] , self.CodeTable[1])
        common_key_commands = []
        for key in common_keys:
            if self.CodeTable[0][key] == self.CodeTable[1][key]:
                common_key_commands.append ([key, self.CodeTable[0][key]])
        delta_keys = []
        print (range(len(self.CodeTable)))
        for table in range(len(display.CodeTable)):
            print("Inspectinng table: ", table)
            for key in self.CodeTable[table]:
                if not(key in common_keys):
                    delta_keys.append([table,key])
        
        print ("Common keys:",common_keys,'\n')
        print ("Common key commands: ", common_key_commands,'\n')
        print ("Delta of keys:",delta_keys)
        
        for delta_key in delta_keys:
            keyhex = self.CodeTable[delta_key[0]][delta_key[1]]
            print("Testing table %s key:" %delta_key[0], delta_key[1], "\tRETURNED:",self.sendhex(keyhex))
        print ("Test common keys")
    def showTables (self):
        print (CodeTable.keys())
    def showTables ():
        print (CodeTable.keys())        
#ENDCLASS

#display = ChinaDisplayControllerSerial ("/dev/ttyUSB0", display_type='KTC', debugText=2)
