import os
import re
import xlsxwriter
import shutil
from datetime import datetime
import csv
from statistics import mean
import statistics

# script starts at the bottom, scroll down to @main to understand functionality.

# this grabs the current time for naming of csv file.
now = datetime.now()
dayOfMonth = str(now.month) + "_" + str(now.day)
time = str(now.hour) + "_" + str(now.minute)

# creates blank list to hold all of the participant data
all_participants = []

# if a number is only one digit, secMinString will pad
# the left side of the number to have a 0.
def secMinString(number):
    if len(str(number)) == 1:
        return "0" + str(number)
    else:
        return str(number)

# writeCSV creates new csv files for each of the sublists in all_participants. source and dest
# are used to move the files into the summary folder.
def writeCSV(data, source, dest):
    for participant in data:
       fileName = str(participant[1][0]) + "_" + dayOfMonth +"_Circadian_Summary_" + time +".xlsx"
       summaryStats = xlsxwriter.Workbook(fileName)
       summarySheet = summaryStats.add_worksheet()
       min = 1
       column = 2
       summarySheet.write("A1", "count.ID")
       summarySheet.write("B1", "count.Day")
       #creates the headers for each minute of activity
       while min <= 1440:   #this should be changed to 1,440 once we figure out how to export data into minute intervals.
                               # write now, it is recording data every 15 minutes.
           summarySheet.write(0, column, "count.MIN" + str(min))
           min += 1
           column += 1
       midnight = "12:00:00 AM"
       curHourCounter = 12
       curMinCounter = 0
       curSecCounter = 0
       timestamp = "AM"
       adjusted = False
       currentDay = 0
       firstLoop = True
       # this loops through each data point reported for a participant
       for stat in participant:
            # checks to see if the day has changed
            # if it has, the row will need to change, and the
            # currentDay value
            if (stat[1] != currentDay):
                currentDay = stat[1]
                column = 0
                row = stat[1]
                summarySheet.write(row, column, stat[0])
                column +=1
                summarySheet.write(row, column, stat[1])
                column +=1
            # it is likely that a participant's data will not start right at midnight
            # this conditional is used to add NaN values until the first reported
            # data point is reached.
            if stat[1] == 1 & (not adjusted):
                if stat[2] != midnight:
                   adjusted = True
                   # see (@secMinString), used to add 0's if a value is not two digits.
                   while str(curHourCounter) + ":" + secMinString(curMinCounter) + ":" + secMinString(curSecCounter) + " " + timestamp != stat[2]:
                        summarySheet.write(row,column, "NaN")
                        # adds minutes at a time until first data point is reached.
                        #if (curMinCounter == 59) & (curSecCounter == 30):
                        if (curMinCounter == 59):
                            # check to see if the next hour is going to be midnight
                            if (curHourCounter + 1) == 12:
                                curHourCounter = curHourCounter + 1
                            else:
                                curHourCounter = (curHourCounter + 1)%12
                            curMinCounter = 0
                            #curSecCounter = 0
                        #if curSecCounter == 30:
                         #   curMinCounter += 1
                          #  curSecCounter = 0
                        #else:
                         #   curSecCounter += 30
                        else:
                            if (str(curHourCounter) + ":" + secMinString(curMinCounter) + ":" + secMinString(curSecCounter) == "12:00:00") & (not firstLoop):
                                timestamp = "PM"
                            curMinCounter += 1
                            firstLoop = False
                        column += 1
            summarySheet.write(row,column, stat[3])
            column += 1
       # another while loop is added so that NaN's can
       # be added to the last day reported because it is also likely
       # that an individual's data points will not end at midnight.
       while column <= 1441:
       #while column <= 2881:
            summarySheet.write(row,column, "NaN")
            column+=1
       # close the file.
       summaryStats.close()
       # finally, the file is moved to the Summary folder
       shutil.move(source + "\\" + fileName, dest + "\\" + fileName)

# intervalsOfFour calculates the average activity across a
# minute. The watch raw data outputs activity levels every
# 15 seconds, but we need activity levels per minute.
def intervalsOfFour(dataList):
    length = len(dataList)
    currentFour = []
    includeInAverage = []
    dataPointsAveraged = []
    currActivity = 0
    while length > 0:
        currentFour = dataList[:4]
        dataList.pop(0)
        dataList.pop(0)
        dataList.pop(0)
        dataList.pop(0)
        identity = currentFour[0][0]
        day = currentFour[0][1]
        time = currentFour[0][2]
        for item in currentFour:
            # does not include the data point if it is NaN
            if item[3] != 'NaN':
                currActivity += int(item[3])
                includeInAverage.append(item[3])
        # if all of the data points were NaN, then
        # the activity level for that minute will be NaN
        if len(includeInAverage) == 0:
            act_average = 'NaN'
        else:
            act_average =  currActivity
        dataPointsAveraged.append([identity, day, time, act_average])
        includeInAverage = []
        currentFour = []
        currActivity = 0
        length -= 4
    return dataPointsAveraged

def intervalsOfTwo(dataList):
    length = len(dataList)
    currentTwo = []
    includeInSum = []
    dataPointsAveraged = []
    currActivity = 0
    # this should be looked at: loses one data point i think
    while length > 1:
        currentTwo = dataList[:2]
        dataList.pop(0)
        dataList.pop(0)
        identity = currentTwo[0][0]
        day = currentTwo[0][1]
        time = currentTwo[0][2]
        for item in currentTwo:
            # does not include the data point if it is NaN
            if item[3] != 'NaN':
                currActivity += int(item[3])
                includeInSum.append(item[3])
        # if all of the data points were NaN, then
        # the activity level for that minute will be NaN
        if len(includeInSum) < 2:
            act_sum = 'NaN'
        else:
            act_sum =  currActivity
        dataPointsAveraged.append([identity, day, time, act_sum])
        includeInSum = []
        currentTwo = []
        currActivity = 0
        length -= 2
    return dataPointsAveraged


# readFile looks at each row of a csv file. Once it
# recognizes the cell that identifies Epoch-by-Epoch
# data, it will skip down 21 rows, where the first data
# point starts, and begin appending the time and activity
# levels that are reported in the raw data.
def readFile(fileToRead, participantData):
    activity = []
    fileAsList = []
    day = 1
    for row in fileToRead:
        fileAsList.append(row)
    index = 0
    while index < len(fileAsList):
        if (fileAsList[index] != []):
            if (fileAsList[index][0] == 'Identity:'):
                identity = fileAsList[index][1]
            elif (fileAsList[index][0] == '-------------------- Epoch-by-Epoch Data -------------------'):
                index += 21
                while index < len(fileAsList) - 1 :
                      if fileAsList[index][2] == "12:00:00 AM":
                            day += 1
                      activity.append([identity, day, fileAsList[index][2],fileAsList[index][4]])
                      index += 1
        index += 1
    return activity

# main loops through the reports folder and reads each file (@readFile),
# adding gathered data to all_participants list. all_participants is a
# list of lists, where each sublist represents the data from one individual's
# watch. After readFile executes, (@intervalsOfFour) takes the mean of every
# four data points.
# Once all report files have been parsed, output csv files are created for
# each sublist (@writeCSV).
def main():
    rootDir = os.getcwd()
    os.chdir('Reports')
    reports = os.listdir(os.getcwd())
    for file in reports:
        participantData = []
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            temp_data = readFile(reader, participantData)
            temp_data = intervalsOfTwo(temp_data)
            participantData = participantData + temp_data
            all_participants.append(participantData)
    writeCSV(all_participants, rootDir+"\Reports", rootDir + "\Summary")

main()