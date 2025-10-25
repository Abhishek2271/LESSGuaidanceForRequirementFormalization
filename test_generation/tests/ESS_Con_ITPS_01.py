import re
from PyQt5.QtWidgets import *
import sys
import textx
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import *
from PyQt5.QtWidgets import QMessageBox



class ESS_Con_ITPS_01(QWidget):
    pathToEss = 'Methods/testdata/TestTestcases.ess'
    pathToGrammar = 'Methods/testdata/ESS.tx'
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

    def initUI(self):
   
        self.ReqID, ok = QInputDialog.getText(self, "ESS_Con_ITPS_01", "Enter Requirement ID")

        if ok:  
            #check if there is a pre-condition that has temporal keywords like:
            #(IF, WHILE, DURING, BEFORE, AFTER)
            self.conditions = self.findReqCond() 
            print('conditions = ' + str(self.conditions))
            if len(self.conditions) > 0:
                #continue only if the requirement has temporal condition
                self.okReqId()
            else:
                self.initUI()

   
    # def button_no_clicked(self):
    #     self.close()
    #     return

    # def button_later_clicked(self):
    #     self.close()
    #     return


    def okReqId(self):
        for condition in self.conditions:
            self.dialog2 = loadUi("./Methods/gui/ConditionTestcases_3.ui")     
            
            self.dialog2.labelCondition.setText("'{}'".format(condition))
            
            #self.dialog2.buttonBox.rejected.connect(QDialog.reject)
        
            #is the <conditional> precondition or test input
            okDialog2 = self.dialog2.exec_() 

            if okDialog2 == QDialog.Accepted:

                #self.reqDescr = self.dialog2.plainTextEdit.toPlainText()
                if self.dialog2.preConButton.isChecked():
                    #if it is pre-condition, add it as a precondition (so if req is "IF the car is moving THEN the car is accelerating" then "IF the car is moving" is a precondition but there is a bug, here IF the car is moving THEN the car is accelerating is added as precondition)
                    self.addPreCon(condition)
                if self.dialog2.testInputButton.isChecked():
                    #if it is test input, add it as a test input
                    self.addTestInput(condition)

        self.preCondition = ' AND '.join(self.listPreconditions)   
        # are there any preconditions to this test case?
        self.otherPrecon1()
            


    def addPreCon(self, condition):
        self.listPreconditions.append(condition)
    
    def addTestInput(self, condition):
        #if it a test input then add all the ways how this test input can be fulfilled
        #eg- if it is "unintended acceleration" write how "unintended acc." can be fulfilled
        self.dialog3 = loadUi("./Methods/gui/ConditionTestcases_4.ui")
        self.dialog3.labelCond2.setText("{}".format(condition))
        okDialog3 = self.dialog3.exec_()

        if okDialog3 == QDialog.Accepted:
            list = []
            if not self.dialog3.testInput1.toPlainText() == "":
                list.append(self.dialog3.testInput1.toPlainText())
            if not self.dialog3.testInput2.toPlainText() == "":
                list.append(self.dialog3.testInput2.toPlainText())
            if not self.dialog3.testInput3.toPlainText() == "":
                list.append(self.dialog3.testInput3.toPlainText())
            if list:
                self.listTestInput.append(list)
            #behavior = loadUi("./Methods/gui/ConditionTestcases_8.ui") 
            #if behavior.exec_() == QDialog.Accepted:
                #self.behavior = behavior.textBehavior.toPlainText()
            
            # for index, testInput in enumerate(self.listTestInput):
            #     newTest = Testcase(self.generateTestNr(), self.preCondition, testInput, self.behavior)
            #     self.listTestcases.append(newTest)

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
        # are there any preconditions to this test case?
        #if yes then ask for other preconditions in a text box, users enter by seperating with comma
        self.dialog4 = loadUi("./Methods/gui/ConditionTestcases_5.ui")    
        yesDialog4 = self.dialog4.exec_()
        if yesDialog4 == QDialog.Accepted:
            #get precondition from the text box append it to the preconditions
            self.otherPrecon2()
        else:
            if self.behavior == "":
                #get behavior from the file, but this does not work, currently it check for any line without IF, WHILE, DURING, BEFORE, AFTER, AS SOON AS, IN CASE OF, but this is not possible because we have filterred lins with these conditionals only
                    self.behavior = self.getBehaviorFromFile()
                    # behavior = loadUi("./Methods/gui/ConditionTestcases_8.ui") 
                    # if behavior.exec_() == QDialog.Accepted:
                    #     self.behavior = behavior.textBehavior.toPlainText()
            
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
            
           


    def otherPrecon2(self):
        self.dialog5 = loadUi("./Methods/gui/ConditionTestcases_6.ui")    
       
        okDialog5 = self.dialog5.exec_()

        if okDialog5 == QDialog.Accepted:
            if not self.dialog5.preCon1.toPlainText() == "":
                if self.preCondition != "":
                    self.preCondition = self.preCondition + "\nAND\n" + self.dialog5.preCon1.toPlainText()
                else:
                    self.preCondition = self.dialog5.preCon1.toPlainText()

                if self.behavior == "":
                    self.behavior = self.getBehaviorFromFile()
                    # behavior = loadUi("./Methods/gui/ConditionTestcases_8.ui") 
                    # if behavior.exec_() == QDialog.Accepted:
                    #     self.behavior = behavior.textBehavior.toPlainText()
                if len(self.listTestcases) == 0:          
                    if self.listTestInput:
                        self.makeTestCases()
                        #newTest = Testcase(self.generateTestNr(), self.preCondition, self.listTestInput[0], self.behavior)
                    else: 
                        newTest = Testcase(self.generateTestNr(), self.preCondition, "", self.behavior)
                        self.listTestcases.append(newTest)
                
                else:
                    self.updatePreCondition()
                    self.updateExpectedBehavior()

                self.table()

    def table (self):
        self.dialog6 = loadUi("./Methods/gui/ConditionTestcases_7.ui") 
        print("build table:")

        for index, testcase in enumerate( self.listTestcases) :
            #print(str(self.listPreCon))
            self.dialog6.table.insertRow(self.dialog6.table.rowCount())
            self.dialog6.table.setItem(index,0,QTableWidgetItem(testcase.testNr))
            if testcase.preCondition == "":
                self.dialog6.table.setItem(index,1,QTableWidgetItem("-"))
            else:
                self.dialog6.table.setItem(index,1,QTableWidgetItem(testcase.preCondition))
            if testcase.testInput == "":
                self.dialog6.table.setItem(index,2,QTableWidgetItem("-"))
            else:
                self.dialog6.table.setItem(index,2,QTableWidgetItem(testcase.testInput))
            self.dialog6.table.setItem(index,3,QTableWidgetItem(testcase.expectedBeh))

       
        self.dialog6.exec_()
        #self.setGeometry(200,200,400,200)
        #self.setWindowTitle ("ESS_Con_ITPS_01")
        #vbox = QVBoxLayout()
        #table = QTableWidget()
        #table.setColumnCount(3)
        #table.setRowCount(3)

        #table.setItem(1,1,QTableWidgetItem("kuku"))

        #vbox.addWidget(table)
        #self.table.show()




           



        #self.dialog3.buttonBox.rejected.connect(QDialog.reject)
        #self.dialog3.exec_()
    
    def saveNewReq(self):
        # datei = open('Methods/testdata/Test.ess','r')
        #print(datei.read())
        #datei = open('Test.ess','a')
        #datei.write("")
        pass

    def showPopUP(self, Text):
        msg = QMessageBox()
        msg.setWindowTitle("Error")  
        msg.setText(Text)  
        x = msg.exec_()
        msg.setIcon(QMessageBox.Critical)
        if x == QDialog.Accepted:
            self.initUI()

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

        print(files)

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
        self.showPopUP("ReqID not found")  
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
    app = QApplication(sys.argv)
    win = ESS_Con_ITPS_01()
    #win.show()
    #sys.exit(app.exec_())