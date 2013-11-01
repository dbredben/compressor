import collections

import tickerStruct

class PythonDict(tickerStruct.TickerStruct):
    
    def __init__(self):
        '''
        Uses Python dictionary container to build the Ticker Dictionary.

        Parameters:
            None

        Attributes:
            None

        Return:
            None
        '''

        self.dict = {}
        
    def add(self,  tickerName):
        '''
        Add an unique Node object to the TickerList object.

        Parameters:
            tickerName (string): ticker value
        
        Attributes:
            None

        Return:
            None
        '''
        if tickerName not in self.dict:
            self.dict[tickerName] = tickerName
        
    def buildTickerDict(self,  tickerDict):
        '''
        Builds ticker dictionary.

        Parameters:
            tickerDict (List:string): Ticker Dictionary

        Attributes:
            tempList (List:string): temporary list used for sorting ticker values

        Return:
            None
        '''
        tempList = []
        for value in self.dict.values():
            tempList.append(value)
         
        tempList = sorted(tempList)
      
        for value in tempList:   
            tickerDict.append(value)
