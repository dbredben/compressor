import sys

import tickerStruct

class Node(object):

    def __init__(self, tickerName):
        '''
        Data container for TickerList. Used for 
        holding tickers and link references.
        
        Parameters:
            tickerName (string): ticker value
        
        Attributes:
            tickerName (string): ticker value
            leftNode (Node): reference to left Node object
            rightNode (Node): reference to right Node object
        '''
        self.tickerName = tickerName
        self.leftNode = None
        self.rightNode = None


class TickerList(tickerStruct.TickerStruct):

    def __init__(self):
        '''
        A link list data struct used to build the ticker dictionary.

        Parameters:
            None

        Attributes:
            anchorNode (Node): used for adding additional tickers
            firstNode (Node): Node with lowest ticker value 
        '''
        self.anchorNode = None
        self.firstNode = None
        
    def buildTickerDict(self,  tickerDict):
        '''
        Builds ticker dictionary.

        Parameters:
            None

        Attributes:
            ptrNode (Node): points to the Node being added to the ticker dictionary 
        '''
        #message
        sys.stdout.write('building ticker dictionary...\n')

        #assign first Node to begin building
        ptrNode = self.firstNode
        #add all the other Nodes based on link references
        while ptrNode:
            tickerDict.append(ptrNode.tickerName)
            ptrNode = ptrNode.rightNode        
            
    def add(self, tickerName):
        '''
        Add an unique Node object to the TickerList object.

        Parameters:
            tickerName (string): ticker value
        
        Attributes:
            currentNode (Node): Node currently compared to new Node object
            finished (Bool): indicator that a new Node object was added
        '''
        #add Node as anchor and 1st Node
        if None == self.anchorNode:
            self.anchorNode = Node(tickerName)
            self.firstNode = self.anchorNode

        else:
            finished = False
            #set anchor Node as starting point
            currentNode = self.anchorNode
            #loop until ticker is added
            while not finished:
                #don't add a duplicate ticker                
                if tickerName == currentNode.tickerName:
                    finished = True
                #if ticker is less value
                elif tickerName < currentNode.tickerName:
                    #add lesser ticker as left Node
                    if None == currentNode.leftNode:
                        currentNode.leftNode = Node(tickerName)
                        #set added Node as 1st Node
                        self.firstNode = currentNode.leftNode
                        finished = True
                    #if left Node already exists
                    else:
                        #move on to next left Node if lesser value
                        if tickerName <= currentNode.leftNode.tickerName:
                            currentNode = currentNode.leftNode
                        #add ticker as new Node between current Node and left Node
                        elif tickerName > currentNode.leftNode.tickerName:
                            self.insert(currentNode.leftNode, Node(tickerName), currentNode)
                            finished = True
                #if ticker is greater value
                elif tickerName > currentNode.tickerName:
                    #add greater ticker as right Node
                    if None == currentNode.rightNode:
                        currentNode.rightNode = Node(tickerName)
                        finished = True
                    #if right Node already exists
                    else:
                        #move on to next right Node if lesser value
                        if tickerName >= currentNode.rightNode.tickerName:
                            currentNode = currentNode.rightNode
                        #add ticker as new Node between current Node and right Node
                        elif tickerName < currentNode.rightNode.tickerName:
                            self.insert(currentNode, Node(tickerName), currentNode.rightNode)
                            finished = True

    def insert(self, leftNode, newNode, rightNode):
        '''
        Reassign link references when inserting a new Node.
       
        Parameters:
            leftNode (Node): Node object left of new Node object
            newNode (Node): inserting Node object
            rightNode (Node): Node object right of new Node object

        Attributes:
            None
        '''
        #assign new Node's link references
        newNode.leftNode = leftNode
        newNode.rightNode = rightNode
        #reassign left Node's link reference to new Node
        leftNode.rightNode = newNode
        #reassign right Node's link reference to new Node
        rightNode.leftNode = newNode
