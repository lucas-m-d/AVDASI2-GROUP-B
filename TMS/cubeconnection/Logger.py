import csv
import time

class Logger:
    def __init__(self):
        self.logging_parameters = ["time_boot_ms", "mode", "pitch", "roll", "yaw", "servo_out1", "flapSensorPosition"]
     
        self.filePath = "./log--" + time.strftime("%H-%M %d-%m-%y") + ".csv" #hours, mins, day, month, year without century
        self.file = open(self.filePath, "w") # write new file (overwrite if already exists?)
        self.writer = csv.writer(self.file) # initialise csv writer
        self.writer.writerow(self.logging_parameters)


    def log(self, time_boot_ms, **kwargs):
        newLine=["" for i in self.logging_parameters]
        newLine[0] = time_boot_ms
       
        for key, value in kwargs.items():  ## go through kwargs and see if an argument is in the params to be logged
            if key in self.logging_parameters: 
                newLine(self.logging_parameters.index(key)) = value

        self.writer.writerow(newLine) ## write
        
            
    

        

        