
#MIT License
#
#Copyright (c) 2020 Stijn Mijland
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import sys
import os.path

#WARNING: This version was designed (with read and write) for Linux. Windows
# files might not be the same. This was not tested on Linux.

# Read scenarios TODO Error returns, not exits
def read_scenarios(highscores_file) :
    with open(highscores_file, mode = "rb") as highscores :
        #Read the version
        version_bytes = highscores.read(4)
        if version_bytes == '' :
            raise ValueError("Version not found, exiting")
        version = int.from_bytes(version_bytes, sys.byteorder)
        #Code for version 1
        if version == 1 :
            #Read the number of entries
            count_bytes = highscores.read(4)
            if count_bytes == '' :
                raise ValueError("No item count found. Exiting")
            count = int.from_bytes(count_bytes, sys.byteorder)
            scenarios = [None] * count
            for i in range(count) :
                byte = None
                #Read the scenario name
                scenario_name = b''
                while True :
                    byte = highscores.read(1)
                    if byte == '' or ord(byte) == 0 :
                        break
                    scenario_name += byte
                if byte == '' :
                    raise ValueError("Scenario name not found for scenario ", i, ", exiting")
                #Read the player name
                player_name = b''
                while True :
                    byte = highscores.read(1)
                    if byte == '' or ord(byte) == 0 :
                        break
                    player_name += byte
                if byte == '' :
                    raise ValueError("Player name not found for ", scenario_name, ", exiting")
                #Read the money (this is money32, a custom RCT2 type)
                money_bytes = highscores.read(4)
                if money_bytes == '' :
                    raise ValueError("Money not found for ", scenario_name, ", exiting")
                money = int.from_bytes(money_bytes, sys.byteorder)
                #Read the time stamp
                time_bytes = highscores.read(8)
                if time_bytes == '' :
                    raise ValueError("Time not found for ", scenario_name, ", exiting")
                time = int.from_bytes(time_bytes, sys.byteorder)
                #Add the scenario to the list of scenarios
                scenarios[i] = (scenario_name, player_name, money, time)
            return scenarios
        else :
            raise ValueError("Version ", version, " not supported by this script, exiting")

#Save the remaining scenarios in filename
def save_scenarios(scenarios, filename) :
    with open(filename, 'wb') as save :
        #version
        save.write((1).to_bytes(4, byteorder = sys.byteorder))
        #number of entries
        save.write((len(scenarios)).to_bytes(4, byteorder = sys.byteorder))
        #scenarios
        for scenario in scenarios :
            #Write the scenario name
            save.write(scenario[0])
            #Write one null-byte to conform to file standard
            save.write((0).to_bytes(1, byteorder = sys.byteorder))
            #Write the name of the player
            save.write(scenario[1])
            #Null-byte, again
            save.write((0).to_bytes(1, byteorder = sys.byteorder))
            #Write the money
            save.write(scenario[2].to_bytes(4, byteorder = sys.byteorder))
            #Write the time it was completed
            save.write(scenario[3].to_bytes(8, byteorder = sys.byteorder))

#Print the scenarios in a nice and clear manner
def print_scenarios(scenarios, changes) :
    #Print the scenarios in a nice table
    print(" -- remaining scenarios: ")
    #Print the scenarios first
    for scenario in scenarios :
        print( scenario_format.format(scenario[0].decode()) + " by " 
             + player_format.format(scenario[1].decode()) + " score: " 
             + score_format.format(scenario[2]) + " at " 
             + time_format.format(scenario[3]))
    print(" -- scenarios pending removal: ")
    #Then print the scenarios that'll be removed
    for scenario in changes :
        print( scenario_format.format(scenario[0].decode()) + " by " 
             + player_format.format(scenario[1].decode()) + " score: " 
             + score_format.format(scenario[2]) + " at " 
             + time_format.format(scenario[3]))
    print(" -- ")

#Select the default highscores file
highscores_file = None
#Windows default
if sys.platform.startswith("win32") :
    highscores_file = os.path.expanduser("~/Documents/OpenRCT2/highscores.dat")
#Linux default
elif sys.platform.startswith("linux") :
    highscores_file = os.path.expanduser("~/.config/OpenRCT2/highscores.dat")
else :
    pass

#Interactive selection of file if needed
while True :
    #If no file was selected, ask the users to enter it
    if highscores_file == None or not os.path.isfile(highscores_file) :
        highscores_file = prompt("Please enter the location of the highscores file (exit to exit): ")
        if highscores_file == '' or highscores_file == "exit" :
            break
    #Read the scenario file
    try :
        scenarios = read_scenarios(highscores_file)
        #Create a formatting string to print the data consistently every time
        scenario_format = '{:<' + str(max(map(lambda s : len(s[0]), scenarios))) + '}'
        player_format = '{:<' + str(max(map(lambda s : len(s[1]), scenarios))) + '}'
        score_format = '{:<' + str(max(map(lambda s : len(str(s[2])), scenarios))) + '}'
        time_format = '{:<' + str(max(map(lambda s : len(str(s[3])), scenarios))) + '}'
        #If there are no scenarios, stop
        if len(scenarios) == 0 :
            print("No scenarios in this file, nothing to be done")
            sys.exit()
        #Dialogue with the user to select scenarios to remove
        print("I found the following scenarios: ")
        changes = []
        while True :
            #Stop whenever no scenario's remain
            if len(scenarios) == 0 :
                print("There are no scenarios left to remove")
                break
            #Show the remaining scenarios
            print_scenarios(scenarios, changes)
            #Require the user to type the full scenario to be sure they want to delete it
            prompt = input("Type \"exit\" to exit. Type a full scenario name to mark for removal: ")
            if prompt == "exit" :
                break
            for i in range(len(scenarios)) :
                if scenarios[i][0].decode() == prompt :
                    changes.append(scenarios[i])
                    del scenarios[i]
                    print(prompt, " removed. Changes can be reviewed at the end")
                    break
        if len(changes) > 0 :
            print("Changes were made. Current status:")
            print_scenarios(scenarios, changes)
            while True :
                prompt = input("WARNING: Your highscores will be overwritten. Save changes? (y/N): ")
                if prompt == "N" or prompt == "n" or prompt == "no" or prompt == "No" or prompt == "NO" :
                    break
                if prompt == "y" or prompt == "Y" or prompt == "yes" or prompt == "Yes" or prompt == "YES" :
                    save_scenarios(scenarios, highscores_file)
                    break
        break
    except (ValueError, e) :
        print("That file is not a valid highscores file.")
