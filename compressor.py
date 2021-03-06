#!/usr/bin/env python

'''
BAT Compressor
Author: Derek Bredbenner
'''

import sys
import os.path
import struct

from TickerStruct import tickerStruct_Factory as tsF


class Compressor(object):

    def __init__(self):
        '''
        Compress/Decompress BAT format files.

        Parameters:
            None

        Attributes:
            tickerList (TickerList): used for collecting tickers, building 
                                     ticker dictionary and encoding tickers
            tickerDict (List:string): used for decoding tickers
            idNumber (int): file identifier
            rowCount (int): count total number of lines in BAT files and compressed files

        Return:
            None
        '''
        self.tickerStruct = tsF.TickerStruct_Factory().getTickerStruct()
        self.tickerDict = []
        self.idNumber = 19
        self.rowCount = 0

   

    def checkID(self, idNumber):
        '''
        Identifies BAT files compressed by this program.

        Parameters:
            idNumber (int): file compressed file's identifier 

        Attributes:
            None

        Return:
            None
        '''
        if idNumber != self.idNumber:
            sys.stdout.write('Cannot decompress Input file, not generated by this program\n')
            sys.exit()    

    def decodeHeader(self,  bFile):
        '''
        Decode header.
        
        Parameters:
            bFile (file): file object for compressed file

        Attributes:
            idNumber (int): file identifier
            
            tickerDecode_MemSize (int): encoded ticker's byte memory size to be decoded
            tickerDict_Length (int): the number of tickers in the Ticker Dictionary

            tickerValue (string): decoded ticker from compressed file's ticker dictionary
            tickerSize (int): decoded ticker's string length from compressed file's ticker dictionary
 
        Return:
            tickerDecode_MemSize (int): encoded ticker's byte memory size to be decoded
        '''
        #message
        sys.stdout.write('decoding header...\n')
        #decode file identifier
        idNumber = struct.unpack('H',bFile.read(2))[0]

        #check file identifier
        self.checkID(idNumber)

        #read number of lines from compressed file
        self.rowCount = struct.unpack('L',bFile.read(8))[0]
        #decode ticker decode memory size (2 bytes, unsigned short)
        tickerDecode_MemSize = struct.unpack('H',bFile.read(2))[0]
        #decode ticker array size (2 bytes, unsigned short)
        tickerDict_Length = struct.unpack('H',bFile.read(2))[0]

        #message
        sys.stdout.write('decoding ticker dictionary...\n')
        #decode ticker array
        for x in range(tickerDict_Length):
            #set ticker variable
            tickerValue = ''
            #get ticker size (2 bytes, unsigned short)
            tickerSize = struct.unpack('H',bFile.read(2))[0]
            #get ticker (1 byte, char)
            for y in range(tickerSize):
                tickerValue = tickerValue + struct.unpack('c',bFile.read(1))[0]
            #append ticker to ticker dictionary
            self.tickerDict.append(tickerValue)
            
        return tickerDecode_MemSize

    def decodePrice(self,  bFile,  oFile,  condFlags):
        '''
        Deocde price.
        
        Parameters:
            bFile (file): file object for compressed file
            oFile (file): file object for BAT file to be decompressed
            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision
        
        Attributes:
            pricePrecision (int): condition flags for the number of digits right of line 
                                  price's decimal point
        
        Return:
            None
        '''
        #get price precision from condition flags
        pricePrecision = condFlags & 7
        
        #check price precision
        if 0 == pricePrecision:
            #must decode price precision in int format if price precision is zero
            oFile.write(str(struct.unpack('i',bFile.read(4))[0])+',')
        else:
            #must decode price precision in float format with change precision if nonzero 
            precisionFormat = '{0:.' + str(pricePrecision) + 'f}'
            oFile.write(precisionFormat.format(struct.unpack('f',bFile.read(4))[0])+',')

    def decodeSize(self,  bFile,  oFile,  condFlags):
        '''
        Decode size.
        
        Parameters:
            bFile (file): file object for compressed file
            oFile (file): file object for BAT file to be decompressed
            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision
               
        Attributes:
            None
               
        Return:
            None
        '''
        #decode size based on condition flags
        #check bit #5
        if condFlags & 16:
            #decode size (4 bytes, unsigend int)
            oFile.write(str(struct.unpack('I',bFile.read(4))[0]))
        #check bit #4
        elif condFlags & 8:
            #decode size (2 bytes, unsigned short)
            oFile.write(str(struct.unpack('H',bFile.read(2))[0]))
        #bit #5 and bit #4 not on
        else:
            #decode size (1 byte, unsigned char)
            oFile.write(str(struct.unpack('B',bFile.read(1))[0]))

    def decodeTimeDiff(self,  bFile,  condFlags):
        '''
        Decode time difference.
        
        Parameters:
            bFile (file): file object for compressed file
            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision
            
        Attributes:
            None
                 
        Return:
            timeDiff (int): time difference between the line sendtime and recvtime
        '''
        #decode time diff based on condition flags
        #check bit #7
        if condFlags & 64:
            #decode time diff (4 bytes, unsigned int)
            timeDiff = struct.unpack('I',bFile.read(4))[0]
        #check bit #6
        elif condFlags & 32:
            #decode time diff (2 bytes, unsigned short)
            timeDiff = struct.unpack('H',bFile.read(2))[0]
        #bit #7 and bit #6 not on
        else:
            #decode time diff (1 byte, unsigned char)
            timeDiff = struct.unpack('B',bFile.read(1))[0]
            
        return timeDiff

    def encodeHeader(self, bFile):
        '''
        Enocode compressed file's header
        
        Parameters:
            bFile (file): file object holding BAT file

        Attributes:
            encodeHeader_ByteSize (int): encoded header's byte memory size
            tickerEncode_MemSize (int): encoded ticker's byte memory size
            
        Return:
            None
        '''
        
        #message
        sys.stdout.write('encoding header...')

        #size of encoded header in bytes
        #byte sizes for file identifier, number of lines, 
        #  encoded ticker memory size and ticker 
        #  dictionary size already added
        encodeHeader_ByteSize = 10

        #get encoded ticker's byte memory size
        tickerEncode_MemSize = self.getTickerEncode_MemSize()

        #encode file identifier (2 bytes, unsigned short)
        bFile.write(struct.pack('H',self.idNumber))
        #encode number of lines (4 bytes, unsigned long)
        bFile.write(struct.pack('L',self.rowCount))
        #encode encoded ticker memory size (2 bytes, unsigned short)
        bFile.write(struct.pack('H',tickerEncode_MemSize))
        #encode ticker dictionary size (2 bytes, unsigned short)
        bFile.write(struct.pack('H',len(self.tickerDict)))
        #encode ticker dicionary based on encoded ticker memory size
        for ticker in self.tickerDict:
            #encode ticker string length (1 byte per char, unsigned char)
            #NOTE:this information is needed during decompression since tickers 
            #  have a various string variable length
            bFile.write(struct.pack('H',(int(len(ticker)))))

            #add ticker byte size to encode header size
            encodeHeader_ByteSize += 1
            #encode ticker based on encoded ticker memory size
            #NOTE:will have to encode ticker char at a time because the tickers' 
            # various string variable length (1 byte, signed char)
            for index,value in enumerate(ticker):
                bFile.write(struct.pack('c',ticker[index]))

        #printout total encode header byte size
        sys.stdout.write('total byte size: {0}\n'.format(encodeHeader_ByteSize))

    def encodeTicker(self, bFile,  rowList,  tickerEncode_MemSize):
        '''
        Encode ticker.
        
        Parameter:
            bFile (file): file object for compressed file
            rowList (List): holds the line's seperated information
            tickerEncode_MemSize (int): encoded ticker's byte memory size

        Attributes:
            encodeTickerValue (int): encoded ticker value
            
        Return:
            None
        '''
        #get ticker encode value
        encodeTickerValue = self.getEncodeTicker(self.tickerDict,rowList[0].strip(),int(0),len(self.tickerDict)-1)

        #if encoded ticker is not found
        if -1 == encodeTickerValue:
            sys.stdout.write(
              '\nError: unable to find ticker encode value in ticker dictionary.format\n')
            sys.exit()

        #encode ticker using encoded ticker byte memory size
        if 1 == tickerEncode_MemSize:
            #(1 byte, unsigned char)
            bFile.write(struct.pack('B',int(encodeTickerValue)))
        elif 2 == tickerEncode_MemSize:
            #(2 bytes, unsigned short)
            bFile.write(struct.pack('H',encodeTickerValue))
        elif 4 == tickerEncode_MemSize:
            #(4 bytes, unsigned int)
            bFile.write(struct.pack('I',encodeTickerValue))

    def firstRead(self,  iFileName):
        '''
        Reads the input file to get row count and create TickerList
        
        Parameter:
            iFileName (file): input file

        Attributes:
            row (string): line information
            ticker (string): ticker in string value
            
        Return:
            None
        '''
        #NOTE:have to open the input file twice, once to get a row count, other to encode
        #  unable to detect EOF with reading in the lines
        sys.stdout.write('building ticker list...\n')
        with open(iFileName,'rb') as iFile:
            while True:
                row = iFile.readline()
                if not row: break
                ticker = row.split(',')[0]
                #build ticker list
                #self.tickerList.add(ticker)
                self.tickerStruct.add(ticker)
                #get row count
                self.rowCount += 1

    def getEncodeTicker(self, tickerDict, tickerName, minIndex, maxIndex):
        '''
        get encoded ticker during compression by performing a binary search 
        in the ticker dictionary.
        NOTE: Parameter passing ticker dictionary for recursion.
        NOTE: Ticker dictionary must be sorted.

        Parameters:
            tickerDict (List:string): ticker dictionary
            tickerName (string): ticker value
            minIndex (int): ticker dictionary's left boundary
            maxIndex (int): ticker dictionary's right boundary

        Attributes:
            splitIndex (int): the mid-point index in the Ticker Dictionary

        Return: 
            ticker encode value or error (-1)
        '''
        #unable to find ticker's encode value, return error
        if minIndex > maxIndex:
            return -1
        #ticker dictionary is one element
        elif minIndex == maxIndex:
            splitIndex = minIndex
        #split ticker dictionary in half
        else:
            splitIndex = (maxIndex + minIndex) // 2

        #ticker encode found, return value
        if tickerDict[splitIndex] == tickerName:
            return splitIndex
        #recurse to lesser half of ticker dictionary
        elif tickerDict[splitIndex] < tickerName:
            return self.getEncodeTicker(tickerDict, tickerName, splitIndex+1, maxIndex)
        #recurse to greater half of ticker dictionary
        elif tickerDict[splitIndex] > tickerName:
            return self.getEncodeTicker(tickerDict, tickerName, minIndex, splitIndex-1)
        #ticker encode found, return value
        else:
            return splitIndex 

    def getTickerEncode_MemSize(self):
        '''
        Get encoded ticker's byte memory size
        
        Parameter:
            None:
            
        Attributes:
            tickerEncode_MemSize (int): encoded ticker's byte memory size to be encoded
            tickerDict_Length (int): the number of tickers in the Ticker Dictionary

        Return:
            None
        '''
        #get ticker dictionary length
        tickerDict_Length = len(self.tickerDict)
        
        #use unsigned char (1 byte)
        if tickerDict_Length < 256:
           tickerEncode_MemSize = 1
        #use unsigned short (2 bytes)
        elif tickerDict_Length >= 256 and tickerDict_Length < 65536:
           tickerEncode_MemSize = 2
        #use unsigned int (4 bytes)
        elif tickerDict_Length >= 65536:
           tickerEncode_MemSize = 4
           
        return tickerEncode_MemSize
        
    def setCondFlags(self,  rowList,  condFlags,  timeDiff_Flags,  size_Flags,  pricePrecision):
        '''
        Set condition flags
        
        Parameters:
             rowList (List): holds the line's seperated information 
             
            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision
            timeDiff_Flags (int): condition flags for time difference's byte memory size
            size_Flags (int): condition flags for line size's byte memory size

            pricePrecision (int): condition flags for the number of digits right of line 
                                  price's decimal point
        
        Attributes:
            timeDiff (int): time difference between sendtime and receivetime
            change (List:string): price value before and after the decimal point
                          
        Return:
            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision
            timeDiff_Flags (int): condition flags for time difference's byte memory size
            size_Flags (int): condition flags for line size's byte memory size

            pricePrecision (int): condition flags for the number of digits right of line 
                                  price's decimal point
        '''

         #get time difference
        timeDiff = int(rowList[5].strip()) - int(rowList[4].strip())
        
        #save flags for time diff memory allocation
        timeDiff_Flags = self.setFlags(timeDiff, 1)
        size_Flags = self.setFlags(int(rowList[7].strip()), 2)

        #check for decimal point in price
        change = rowList[6].split('.')

        #if decimal point is found
        if 2 == len(change):
            #get price precision or number of digits right of the decimal point
            #NOTE: price may not have change ie - 157 instead of 157.00
            #NOTE:precision range from 0-7, using last three bits in condFlags
            pricePrecision = int(len(change[1].strip()))
           
            #check max precision on price (8 or more)
            #NOTE: price precison value > 7 will alter other condition flags, 
            #  compressing erroneous data
            if pricePrecision > 7:
                sys.stdout.write(
                  'Warning: passed max price precision on row {0}, precision degraded\n'.format(index))
                pricePrecision = 7
   
        #setup condition flags for timeDiff memory size
        condFlags = condFlags + timeDiff_Flags + size_Flags + pricePrecision
        
        return condFlags,  timeDiff_Flags, size_Flags,  pricePrecision
        
    def setFlags(self, value, type):
        '''
        Sets condition flags for byte memory size on encoded integer values.

        Parameter:
            value (int): given integer value needed to be encoded
            type (int): conditonal flags to be set

        Attributes:
            byteAllocArray (List:Tuple(int,int,int)): list of integer values to turn on condition flags
            arrayIndex (int): index to determine which byteAllocArray element to use

        Return:
            set condition flags (int)
        ''' 
        #1st array element is for time diff flags (bit 6 and 7)
        #2nd array element is for size flags (bit 4 and 5)
        byteAllocArray = [(0,32,64),(0,8,16)]
        arrayIndex = type-1

        #check for unsigned char (1 byte) (no bits)
        if value < 256:
            return byteAllocArray[arrayIndex][0]
        #check for unsigned short (2 bytes) (bits 4 and 6)
        elif value >= 256 and value < 65536:
            return byteAllocArray[arrayIndex][1]
        #check for unsigned int (4 bytes) (bit 5 and 7)
        elif value >= 65536:
            return byteAllocArray[arrayIndex][2]

    def compress(self, iFileName, bFileName):
        '''
        Compresses and encodes the BAT file.

        Parameters:
            iFileName (string): BAT file to be compressed
            bFileName (string): compressed file

        Attributes:            
            rowList (List): holds the line's seperated information  

            tickerDict_Length (int): the number of tickers from the BAT file
            tickerEncode_MemSize (int): encoded ticker's byte memory size

            metaData_ByteSize (int): the metadata's size in bytes 

            ticker (string): line ticker value

            timeDiff (int): time difference between the line send time and receive time

            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision
                          
            timeDiff_Flags (int): condition flags for time difference's byte memory size
            size_Flags (int): condition flags for line size's byte memory size

            pricePrecision (int): condition flags for the number of digits right of line 
                                  price's decimal point

        Return:
            None
        '''
        #message
        sys.stdout.write('begin compression...\n')

        #setup row count
        self.rowCount = 0
        
        #read input file to get row cont and create TickerList
        self.firstRead(iFileName)

        #build ticker dictionary
        #self.tickerList.buildTickerDict(self.tickerDict)
        self.tickerStruct.buildTickerDict(self.tickerDict)
 
        #get ticker dictionary length
        tickerDict_Length = len(self.tickerDict)
 
        #get encoded ticker's byte memory size
        tickerEncode_MemSize = self.getTickerEncode_MemSize()
        
        #open input file again and read/encode line data
        with open(iFileName,'rb') as iFile:
            with open(bFileName, 'wb') as bFile:

                #encode header
                self.encodeHeader(bFile)   
                
                #message
                sys.stdout.write('encoding records...')

                #meta-data count
                metaData_ByteSize = 0

                #read from the input records
                for index in range(self.rowCount):
                    rowList = iFile.readline().split(',')

                    #setup condition flags
                    condFlags = 0
                    timeDiff_Flags = 0
                    size_Flags = 0
                    pricePrecision = 0            

                    #set condition flags
                    condFlags,  timeDiff_Flags,  size_Flags,  pricePrecision = \
                      self.setCondFlags(rowList,  condFlags,  timeDiff_Flags,  size_Flags,  pricePrecision)
                    
                    #encode condition flags (1 byte, char)
                    bFile.write(struct.pack('c',chr(condFlags)))

                    #add to meta data
                    metaData_ByteSize += 1

                    #encode ticker
                    self.encodeTicker(bFile,  rowList,  tickerEncode_MemSize)

                    #encode exchange, side and condition (1 byte each, char)
                    bFile.write(struct.pack('c',rowList[1].strip()))
                    bFile.write(struct.pack('c',rowList[2].strip()))
                    bFile.write(struct.pack('c',rowList[3].strip()))

                    #encode sendtime (4 bytes, int)
                    bFile.write(struct.pack('i',int(rowList[4].strip())))

                    #get time difference
                    timeDiff = int(rowList[5].strip()) - int(rowList[4].strip())
                                                            
                    #encode time difference using condition flags
                    if 0 == timeDiff_Flags:
                        #(1 byte, unsigned char)
                        bFile.write(struct.pack('B',int(timeDiff)))
                    elif 32 == timeDiff_Flags:
                        #(2 bytes, unsigned short)
                        bFile.write(struct.pack('H',int(timeDiff)))
                    elif 64 == timeDiff_Flags:
                        #(4 bytes, unsigned int)
                        bFile.write(struct.pack('I',int(timeDiff)))

                    #encode price as int or float
                    #NOTE:must write binary in int format if price precision is zero
                    if 0 == pricePrecision: 
                        #(4 bytes, int)
                        bFile.write(struct.pack('i',float(rowList[6].strip())))
                    else:
                        #(4 bytes, float)
                        bFile.write(struct.pack('f',float(rowList[6].strip())))

                    #encode size using condition flags
                    if 0 == size_Flags:
                        #(1 byte, unsigned char)
                        bFile.write(struct.pack('B',int(rowList[7].strip())))
                    elif 8 == size_Flags:
                        #(2 bytes, unsigned short)
                        bFile.write(struct.pack('H',int(rowList[7].strip())))
                    elif 16 == size_Flags:
                        #(4 bytes, unsigned int)
                        bFile.write(struct.pack('I',int(rowList[7].strip())))

        #printout total meta data byte size
        sys.stdout.write('total metadata byte size: {0}\n'.format(metaData_ByteSize))

        #message
        sys.stdout.write('compression complete\n')

    def decompress(self, bFileName, oFileName):
        '''
        Decompress into file with BAT data.

        Parameters:
            bFileName (string): compressed file 
            oFileName (string): BAT file to be decompressed

        Attributes:
            condFlags (int): condition flags for line byte memory size, combination 
                             of timDiff_Flags, size_Flags and price precision

            tickerDict_Length (int): the number of tickers from the compressed file
            tickerDecode_MemSize (int): encoded ticker's byte memory size to be decoded
            tickerValue (string): decoded ticker from compressed file's ticker dictionary
            tickerSize (int): decoded ticker's string length from compressed file's ticker dictionary

            decodeIndex (int): encoded ticker value to be decoded by ticker dictionary

            sendTime (int): decoded sendtime
            receiveTime (int): decoded receivetime
            timeDiff (int): decoded time difference
            
            precisionFormat (string): output format for decoded price precision

        Return:
            None
        '''
        #message
        sys.stdout.write('begin decompression...\n')

        #setup condition flags
        condFlags = None

        #read compressed file 1st time to get decode header information
        with open(bFileName, 'rb') as bFile:
            with open(oFileName, 'wb') as oFile:

                ###beginning of header decoding###
                
                #decode header
                tickerDecode_MemSize = self.decodeHeader(bFile)

                ###beginning of record decoding###

                #message
                sys.stdout.write('decoding records...\n')
                #iterate through compressed file
                for x in range(self.rowCount):
                    #setup condition flags
                    condFlags = 0
                    #decode condition flags (1 byte, char)
                    condFlags = ord(struct.unpack('c',bFile.read(1))[0])

                    #decode ticker using its byte memory size
                    if 1 == tickerDecode_MemSize:
                        #(1 byte, unsigned char)
                        decodeIndex = struct.unpack('B',bFile.read(1))[0]
                    elif 2 == tickerDecode_MemSize:
                        #(2 bytes, unsigned short)
                        decodeIndex = struct.unpack('H',bFile.read(2))[0]
                    elif 4 == tickerDecode_MemSize:
                        #(4 bytes, unsigned int)
                        decodeIndex = struct.unpack('I',bFile.read(4))[0]

                    #write decoded ticker
                    oFile.write(self.tickerDict[decodeIndex] + ',')

                    #decode exchange, side and condition (1 byte each, char)
                    for y in range(3):
                        oFile.write(struct.unpack('c',bFile.read(1))[0]+',')

                    #read sendtime (4 bytes, unsigned int)
                    sendTime = struct.unpack('i',bFile.read(4))[0]

                    #read time difference
                    timeDiff = self.decodeTimeDiff(bFile,  condFlags)

                    #get receive time
                    receiveTime = sendTime + timeDiff
                    #write sendtime and receiveTime
                    oFile.write(str(sendTime) + ',' + str(receiveTime) + ',')

                    #decode price
                    self.decodePrice(bFile,  oFile,  condFlags)
                    #decode size
                    self.decodeSize(bFile,  oFile,  condFlags)
                    
                    #write Microsoft newline
                    oFile.write('\r\n')

        #message
        sys.stdout.write('decompression complete\n')

    def run(self, argv):
        '''
        Runs Compressor object.

        Parameters:
            argv (List): passed argument list

        Attributes:
            inputFile (string): input path and filename
            outputFile (string): output path and filename
            flagOption (string): command line flag options

        Return:
            None
        '''

        #check argument list
        if 3 != len(argv):
            sys.stdout.write(
              'Need to enter the following argument list: [-c|-d] <inputfile> <outputfile>\n')
            sys.exit()

        #assign argument list
        inputFile = argv[1]
        outputFile = argv[2]
        flagOption = argv[0]

        #check input/output file path
        if not os.path.exists(r'{0}'.format(inputFile)):
            sys.stdout.write('Input file \'{0}\' does not exist\n'.format(inputFile))
            sys.exit()

        #check flag options        
        if '-c' != flagOption and '-d' != flagOption:
            sys.stdout.write('Flag option should be -c (compress) or -d (decompress)\n')
            sys.exit()

        #check for csv file format
        if '-c' == flagOption and inputFile[-4:] != '.csv':#not re.match('^\w+.csv$',inputFile):
            sys.stdout.write('Input file must be in csv format for compression\n')
            sys.exit()            

        #run compress() or decompress()
        if '-c' == flagOption:   
            self.compress(inputFile, outputFile)
        elif '-d' == flagOption:
            self.decompress(inputFile, outputFile)


def main(argv):
    Compressor().run(argv)

if __name__ == '__main__':
        main(sys.argv[1:]) 
