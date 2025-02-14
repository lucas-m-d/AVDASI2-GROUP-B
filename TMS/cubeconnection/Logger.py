import csv
import time

class Logger:
    def __init__(self):
        self.logging_parameters = ["sys_time", "time_boot_ms", "message","connected", "mode", 
                                   "pitch", "pitchrate",
                                   "roll", "rollrate",
                                   "yaw", "yawrate",
                                   "aileronL", "aileronR", "elevator", "rudder", "flapRequested",
                                   "flapSensorPosition", "armed", "command", "command_result"]
     
        self.filePath = "./log-" + time.strftime("%Hh%Mm%Ss_%d-%m") + ".csv" #hours, mins, day, month, year without century
        
        self.writer = csv.writer(open(self.filePath, "w", newline="")) # initialise csv writer
        self.writer.writerow(self.logging_parameters)


    def log(self, **kwargs):

        newLine=["" for _ in self.logging_parameters] # generate a blank array of strings for the length of the logging_parameters
        newLine[0] = time.time() # add current system time
    
        for key, value in kwargs.items():  ## go through kwargs and see if an argument is in the params to be logged
            try: 
                newLine[self.logging_parameters.index(key)] = value
            except:
                print("No key logged for: ", key)
            
                
        self.writer.writerow(newLine) ## actually write


        