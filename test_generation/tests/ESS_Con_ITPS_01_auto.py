import sys
import textx
import os

class ESS_Con_ITPS_01():
    pathToEss = 'berlin_heart.ess'
    pathToGrammar = 'less.tx'
    bracket1 = "{"
    bracket2 = "}"
    preCondition = ""
    testInput = ""
    behavior = ""
    conditions = []
    listPreconditions = []
    listTestInput = []
    listTestcases = []
    testNr = 0

    def __init__(self):
        super().__init__()        
        self.initUI()
        
    def okReqId(self):
        for condition in self.conditions:
            #self.reqDescr = self.dialog2.plainTextEdit.toPlainText()
            self.addPreCon(condition)

        self.preCondition = ' AND '.join(self.listPreconditions)   
        # are there any preconditions to this test case?
        self.otherPrecon1()
            
    def initUI(self):
        self.ReqID = "Req_gen1"
        #check if there is a pre-condition that has temporal keywords like:
        #(IF, WHILE, DURING, BEFORE, AFTER)
        self.conditions = self.findReqCond() 
        print('conditions = ' + str(self.conditions))
        if len(self.conditions) > 0:
            #continue only if the requirement has temporal condition
            self.okReqId()

   
    # def button_no_clicked(self):
    #     self.close()
    #     return

    # def button_later_clicked(self):
    #     self.close()
    #     return





    def addPreCon(self, condition):
        self.listPreconditions.append(condition)
    
    def makeTestCases(self):
        testInput = ""
        
        for testInput1 in self.listTestInput[0]:
            testInput = testInput1
            if len(self.listTestInput) > 1:
                for testInput2 in self.listTestInput[1]:
                    testInput = testInput1 + " AND " + testInput2
                    newTest = Testcase(self.generateTestNr(), self.preCondition, testInput, self.behavior)
                    self.listTestcases.append(newTest)
            else:
                newTest = Testcase(self.generateTestNr(), self.preCondition, testInput, self.behavior)
                self.listTestcases.append(newTest)
                

    def cancelReqId(self):
        self.hide()
        return
        
    def otherPrecon1(self):
        if self.behavior == "":
            self.behavior = self.getBehaviorFromFile()
        if len(self.listTestcases) == 0:
            if self.listTestInput:
                #newTest = Testcase(self.generateTestNr(), self.preCondition, self.listTestInput[0], self.behavior)
                self.makeTestCases()
            else: 
                newTest = Testcase(self.generateTestNr(), self.preCondition, "", self.behavior)
                self.listTestcases.append(newTest)
                
        else:
            self.updateExpectedBehavior()
            self.updatePreCondition()
        self.table()    

    def table (self):
        print("build table:")
        for index, testcase in enumerate( self.listTestcases) :
            print("index: ", index)
            print("testNr: ", testcase.testNr)
            print("preCondition: ", testcase.preCondition)
            print("testInput: ", testcase.testInput)
            print("expected Behaviour: ", testcase.expectedBeh)
            print("FIN\n")
 
    def getCondFromFile (self):    
        with open(self.pathToEss) as f:
            contents = f.readlines()
            reqFound = False
            conditions = []
            for line in contents:
                if reqFound:
                    print(line)
                if self.ReqID in line:
                   reqFound = True
                   continue
                if  reqFound and ('IF' in line or 'WHILE' in line or 'BEFORE' in line or 'DURING' in line or 'AFTER' in line):
                    #print(line)
                    conditions.extend(line.strip().split('AND'))
                    continue
                if  reqFound and line.strip().startswith('AND'):
                    addConditions = line.strip().split('AND')
                    print('addCond = ' + str(addConditions))
                    addConditions.pop(0)
                    conditions.extend(addConditions)
                    continue

                if  reqFound and not line.strip().startswith('AND') and len(conditions) > 0 :   
                    return conditions
        


    #NEW_TODO
    def getBehaviorFromFile (self):     
        with open(self.pathToEss) as f:
            contents = f.readlines()
            reqFound = False
            inSpecification = False
            behavior = ''
            for line in contents:
                if reqFound:
                    print(line)
                if self.ReqID in line:
                   reqFound = True
                   continue
                
                if reqFound and "{" in line:
                    inSpecification = True
                    continue   

                if reqFound and inSpecification and not ('IF' in line or 'WHILE' in line or 'BEFORE' in line 
                or 'DURING' in line or 'AFTER' in line or 'AS SOON AS' in line 
                or  'IN CASE OF' in line or "}" in line) and not line.strip().startswith('AND'): 
                    behavior=behavior + line.strip()
                    #print (bahavior)
                    continue

                if reqFound and inSpecification and behavior !='' :
                    print (behavior)
                    return behavior  

    def findReqCond(self):
        """
        Gives requirements Id
    
        :return: condition
        :rtype: 
        """
  
        files = os.listdir()

        print("getting conditional requirements from", files)

        metamodel = textx.metamodel_from_file(self.pathToGrammar)
        model = metamodel.model_from_file(self.pathToEss)
      
        #model = metamodel.model_from_file('Methods/testdata/EGAS2.ess')
        print(model.requirements)

        for requirement in model.requirements:
            #if not requirement.req.specification.conditionals is None:
            if requirement.name == self.ReqID:
                if not requirement.req.specification.conditionals is None:
                    conditions = self.getCondFromFile()
                    print (conditions)
                    return conditions
                else: 
                    self.showPopUP("This requirement doesn't containt any conditions!")     
                    return None         
        return None               


    def generateTestNr(self):
        self.testNr+=1
        newNr = "TC_00" + str(self.testNr) + " (" + self.ReqID + ")"
        return newNr

    def updatePreCondition(self):
        for testcase in self.listTestcases: 
            testcase.preCondition = self.preCondition

    def updateExpectedBehavior(self):
        for testcase in self.listTestcases: 
            testcase.expectedBeh = self.behavior
               

class Testcase ():  
    def __init__(self, testNr = "", preCond = "", testInput = "", expectedBeh = ""):
        super().__init__()
        self.testNr = testNr
        self.preCondition = preCond
        self.testInput = testInput
        self.expectedBeh = expectedBeh

if __name__ == "__main__":
    win = ESS_Con_ITPS_01()