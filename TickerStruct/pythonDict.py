import collections

import TickerStruct

class PythonDict(TickerStruct.TickerStruct):
    
    def __init__(self):
        self.dict = {}
        
    def add(self,  tickerName):
        
        if tickerName not in self.dict:
            self.dict[tickerName] = tickerName
        
    def buildTickerDict(self,  tickerDict):
         
        tempList = []
        for value in self.dict.values():
            tempList.append(value)
         
        tempList = sorted(tempList)
      
        for value in tempList:   
            tickerDict.append(value)
