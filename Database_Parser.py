#Raymond's database parser.

import csv
import re as re
import matplotlib.pyplot as plt
import numpy as np

#regex pattern for DCB
pattern_DCB = re.compile('^(WVJCE-)[\\d\\d\\d]')

#regex patterns for LVR
pattern_LVR_CZ = re.compile('^(WVJCZ-)[\\d\\d\\d]')
pattern_LVR_EN = re.compile('^(WVJEN-)[\\d\\d\\d]')
pattern_LVR_ER = re.compile('^(WVJER-)[\\d\\d\\d]')
pattern_LVR_ES = re.compile('^(WVJES-)[\\d\\d\\d]')

#regex patterns for CCM
pattern_CCM_12A = re.compile('^(12A)[\\d|(\\d\\d)]')
pattern_CCM_12M = re.compile('^(12M)[\\d|(\\d\\d)]')
pattern_CCM_12S = re.compile('^(12S)[\\d|(\\d\\d)]')
pattern_CCM_15M = re.compile('^(15M)[\\d|(\\d\\d)]')
pattern_CCM_15S = re.compile('^(15S)[\\d|(\\d\\d)]')
pattern_CCM_25A = re.compile('^(25A)[\\d|(\\d\\d)]')

class DCB:

    def __init__(self):
        self.bad_DCB = {}
        self.good_DCB = {}
        self.unknown_DCB = {}
        self.num_assembled = 0
        self.num_not_assembled = 0
        self.num_unknown = 0
        self.num_total = 0

    def increment_total(self):
        self.num_total += 1

    def py_plot(self):
        # Data to plot
        labels = 'Assembled\nDCBs', 'Unassembled\nand other DCBs'
        sizes = [self.num_assembled, self.num_not_assembled + self.num_unknown]
        colors = ['blue', 'red']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)

        # Plot
        plt.rcParams.update({'font.size': 20})
        plt.figure(figsize=(14,10))
        plt.title("Ratio of Assembled DCBs\n(out of a total of " + str(self.num_total) + ')')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Assembled DCBs: " + str(self.num_assembled) + 
        " | Unassembled DCBs: " + str(self.num_not_assembled) + 
        " | Other DCBs: " + str(self.num_unknown))
        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)
        plt.tight_layout()
        plt.savefig('DCB_AssemblyPieChart.png', bbox_inches='tight', pad_inches = 0.2)

        # Bar Plot
        # plt.style.use('ggplot')
        colors = ['blue', 'red', 'yellow']
        labels = ['Assembled DCBs', 'Unassembled DCBs', 'Other DCBs']
        num_totals = [self.num_assembled, self.num_not_assembled, self.num_unknown]
        plt.figure(figsize = (14, 10))
        index = np.arange(len(labels))
        plt.bar(index, num_totals, color = colors)

        plt.xlabel('DCB Type')
        plt.ylabel('Number of DCBs')
        plt.xticks(index, labels)
        plt.title('DCB By Type')
        plt.legend(patches, labels, loc="upper right")
        plt.savefig('DCB_AssemblyBarChart.png')

        # Data to plot
        labels = 'Fused,\nAssembled DCBs', 'Unfused,\nAssembled DCBs'
        sizes = self.process_fused()
        colors = ['blue', 'red']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        
        # Plot
        plt.figure(figsize=(16,12))
        plt.title("Ratio of Fused DCBs\n(out of a total of " + str(self.num_assembled) + ' Assembled DCBs)')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Fused DCBs: " + str(sizes[0]) + 
        " | Assembled DCBs: " + str(sizes[1]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=45)
        plt.tight_layout()
        plt.savefig('DCB_FusedPieChart.png', bbox_inches='tight', pad_inches = 0.2)

    def process_fused(self):
        number_fused = 0
        number_not_fused = 0

        for value in self.good_DCB.values():
            if (value[2] == 'yes' or value[2] == 'Yes'):
                number_fused += 1
            
        number_not_fused = self.num_assembled - number_fused

        result = [number_fused, number_not_fused]
        return result

    def assembled_dict_update(self, line):
        self.good_DCB[line[1]] = line[2:12]
        self.num_assembled += 1
    
    def not_assembled_dict_update(self, line):
        self.bad_DCB[line[1]] = line[2:12]
        self.num_not_assembled += 1

    def unknown_dict_update(self, line):
        self.unknown_DCB[line[1]] = line[2:12]
        self.num_unknown += 1

class LVR:

    def __init__(self):
        self.LVR_CZ = {}
        self.LVR_EN = {}
        self.LVR_ER = {}
        self.LVR_ES = {}

        self.num_LVR_CZ = 0
        self.num_LVR_EN = 0
        self.num_LVR_ER = 0
        self.num_LVR_ES = 0
        self.num_total = 0

    def increment_total(self):
        self.num_total += 1

    def dict_update_CZ(self, line):
        self.LVR_CZ[line[4]] = line[5:24]
        self.num_LVR_CZ += 1

    def dict_update_EN(self, line):
        self.LVR_EN[line[4]] = line[5:24]
        self.num_LVR_EN += 1

    def dict_update_ER(self, line):
        self.LVR_ER[line[4]] = line[5:24]
        self.num_LVR_ER += 1

    def dict_update_ES(self, line):
        self.LVR_ES[line[4]] = line[5:24]
        self.num_LVR_ES += 1

class CCM:

    def __init__(self):
        self.CCM_12A = {}
        self.CCM_12M = {}
        self.CCM_12S = {}
        self.CCM_15M = {}
        self.CCM_15S = {}
        self.CCM_25A = {}

        self.num_12A = 0
        self.num_12M = 0
        self.num_12S = 0
        self.num_15M = 0
        self.num_15S = 0
        self.num_25A = 0
        self.num_total = 0

    def increment_total(self):
        self.num_total += 1
    
    def dict_update_12A(self, line):
        self.CCM_12A[line[0]] = line[2:9]
        self.num_12A += int(line[5]) 

    def dict_update_12M(self, line):
        self.CCM_12M[line[0]] = line[2:9]
        self.num_12M += int(line[5]) 

    def dict_update_12S(self, line):
        self.CCM_12S[line[0]] = line[2:9]
        self.num_12S += int(line[5]) 

    def dict_update_15M(self, line):
        self.CCM_15M[line[0]] = line[2:9]
        self.num_15M += int(line[5]) 

    def dict_update_15S(self, line):
        self.CCM_15S[line[0]] = line[2:9]
        self.num_15S += int(line[5]) 

    def dict_update_25A(self, line):
        self.CCM_25A[line[0]] = line[2:9]
        self.num_25A += int(line[5]) 

def process_line(line):

    if (line[3] == "Yes" or line[3] == 'yes'):
        return 1
    elif(not line[3]):
        return 2
    else:
        return 3

#Driver for reading/parsing/writing the DCB portion of the database.
with open('CSV_DCB.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    new_DCB = DCB()

    for line in csv_reader:
        if re.match(pattern_DCB, line[0]):
            assembled = process_line(line)

            if (assembled == 1):
                new_DCB.assembled_dict_update(line)

            elif (assembled == 2):
                new_DCB.not_assembled_dict_update(line) 

            else:
                new_DCB.unknown_dict_update(line)
            
            new_DCB.increment_total()

    new_DCB.py_plot()

#Driver for reading/parsing/writing the LVR portion of the database.
with open('CSV_LVR.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    new_LVR = LVR()

    #increment_total() is included for symmetry with the DCB loop.
    for line in csv_reader:

        if re.match(pattern_LVR_CZ, line[6]):
            new_LVR.dict_update_CZ(line)
            new_LVR.increment_total()
        
        elif(re.match(pattern_LVR_EN, line[6])):
            new_LVR.dict_update_EN(line)
            new_LVR.increment_total()
        
        elif(re.match(pattern_LVR_ER, line[6])):
            new_LVR.dict_update_ER(line)
            new_LVR.increment_total()

        elif(re.match(pattern_LVR_ES, line[6])):
            new_LVR.dict_update_ES(line)
            new_LVR.increment_total()        

#Driver for reading/parsing/writing the CCM portion of the database.
with open('CSV_CCM.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    new_CCM = CCM()

    for line in csv_reader:

        #increment_total() is included for symmetry with the DCB loop.
        if (line[5] != ''):
            if (re.match(pattern_CCM_12A, line[0])):
                new_CCM.dict_update_12A(line)
                new_CCM.increment_total()
                
            elif(re.match(pattern_CCM_12M, line[0])):
                new_CCM.dict_update_12M(line)
                new_CCM.increment_total()
            
            elif(re.match(pattern_CCM_12S, line[0])):
                new_CCM.dict_update_12S(line)
                new_CCM.increment_total()

            elif(re.match(pattern_CCM_15M, line[0])):
                new_CCM.dict_update_15M(line)
                new_CCM.increment_total()

            elif(re.match(pattern_CCM_15S, line[0])):
                new_CCM.dict_update_15S(line)
                new_CCM.increment_total()

            elif(re.match(pattern_CCM_25A, line[0])):
                new_CCM.dict_update_25A(line)
                new_CCM.increment_total()
