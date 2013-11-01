
import tickerList
import pythonDict

class TickerStruct_Factory(object):
    
    def getTickerStruct(self):
        '''
        Returns a TickerStruct class object

        Parameters:
            None
        
        Attributes:
            None

        Return:
            TickerList or PythonDict object
        '''
        return tickerList.TickerList()
        #return pythonDict.PythonDict()
