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
        self.other_DCB = {}
        self.num_assembled = 0
        self.num_unassembled = 0
        self.num_other = 0
        self.num_total = 0

        self.DCB_columns = {} 

    def set_DCB_columns(self, start_idx):
        #Set the starting column, the DCB serial numbers.
        self.DCB_columns["Serial"] = start_idx

        #After setting the DCB serial number's column,
        #set the other indices.
        self.DCB_columns["ID"] = self.DCB_columns["Serial"] + 1
        self.DCB_columns["Location"] = self.DCB_columns["Serial"] + 2
        self.DCB_columns["Assembled"] = self.DCB_columns["Serial"] + 3
        self.DCB_columns["Fused"] = self.DCB_columns["Serial"] + 4
        self.DCB_columns["PRBS"] = self.DCB_columns["Serial"] + 5
        self.DCB_columns["1.5V"] = self.DCB_columns["Serial"] + 6
        self.DCB_columns["2.5V"] = self.DCB_columns["Serial"] + 7
        self.DCB_columns["Burned_In"] = self.DCB_columns["Serial"] + 8
        self.DCB_columns["Stave_Test_JD10"] = self.DCB_columns["Serial"] + 9
        self.DCB_columns["Stave_Test_JD11"] = self.DCB_columns["Serial"] + 10
        self.DCB_columns["Comments"] = self.DCB_columns["Serial"] + 11
    
    def process_line(self, line):
        assembled_idx = self.get_idx("Assembled")
        if (line[assembled_idx] == "Yes" or line[assembled_idx] == 'yes'):
            return 1
        elif(not line[assembled_idx]):
            return 2
        else:
            return 3

    def increment_total(self):
        self.num_total += 1

    def pyplot(self):
        # Data to plot
        labels = 'Assembled\nDCBs', 'Unassembled\nand other DCBs'
        sizes = [self.get_num_assembled(), self.get_num_unassembled() + self.get_num_other()]
        colors = ['blue', 'red']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)

        #texts, the output of the above plt.pie call, is required for plt.legend() to function properly.
        #This suppresses an unnecessary warning on the otherwise only implicitly used texts variable.
        texts = texts

        # Plot
        plt.rcParams.update({'font.size': 20})
        plt.figure(figsize=(14,10))
        plt.title("Ratio of Assembled DCBs\n(out of a total of " + str(self.num_total) + ')')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Assembled DCBs: " + str(self.get_num_assembled()) + 
        " | Unassembled DCBs: " + str(self.get_num_unassembled()) + 
        " | Other DCBs: " + str(self.get_num_other()))
        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)
        plt.tight_layout()
        plt.savefig('DCB_AssemblyPieChart.png', bbox_inches='tight', pad_inches = 0.2)

        # Bar Plot
        # plt.style.use('ggplot')
        colors = ['blue', 'red', 'yellow']
        labels = ['Assembled DCBs', 'Unassembled DCBs', 'Other DCBs']
        num_totals = [self.get_num_assembled(), self.get_num_unassembled(), self.get_num_other()]
        plt.figure(figsize = (14, 10))
        index = np.arange(len(labels))
        patches = plt.bar(index, num_totals, color = colors)

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
        plt.title("Ratio of Fused DCBs\n(out of a total of " + str(self.get_num_assembled()) + ' Assembled DCBs)')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Fused DCBs: " + str(sizes[0]) + 
        " | Assembled DCBs: " + str(sizes[1]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=45)
        plt.tight_layout()
        plt.savefig('DCB_FusedPieChart.png', bbox_inches='tight', pad_inches = 0.2)

        # Initial QA Vs. All Assembled DCBs
        labels = 'Initial QA\'d,\nAssembled DCBs', 'Other Assembled DCBs'
        sizes = self.process_initial_QA()
        colors = ['blue', 'red']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        
        # Plot
        plt.figure(figsize=(16,12))
        plt.title("Ratio of Initial QA\'d DCBs\n(out of a total of " + str(self.get_num_assembled()) + ' Assembled DCBs)')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Initial QA'd DCBs: " + str(sizes[0]) + 
        " | Other Assembled DCBs: " + str(sizes[1]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=120)
        plt.tight_layout()
        plt.savefig('DCB_InitialQAPieChart.png', bbox_inches='tight', pad_inches = 0.2)

    def process_fused(self):
        number_fused = 0
        fused_idx = self.get_idx("Fused")

        for value in self.good_DCB.values():
            if (value[fused_idx] == 'yes' or value[fused_idx] == 'Yes'):
                number_fused += 1

        result = [number_fused, self.get_num_assembled() - number_fused]
        return result

    def process_initial_QA(self):
        number_passed = 0
        fused_idx = self.get_idx("Fused")
        PRBS_idx = self.get_idx("PRBS")
        first_volt_idx = self.get_idx("1.5V")
        second_volt_idx = self.get_idx("2.5V")

        for value in self.good_DCB.values():
            if ((value[fused_idx] == "Yes" or value[fused_idx] == "yes")
            and (value[PRBS_idx] == "Yes" or value[PRBS_idx] == "yes")
            and (value[first_volt_idx] and value[second_volt_idx])):
                number_passed += 1

        return [number_passed, self.get_num_assembled() - number_passed]

    def assembled_dict_update(self, line):
        self.good_DCB[line[self.get_idx("Serial")]] = line[self.get_idx("Serial"):self.get_idx("Comments") + 1]
        self.num_assembled += 1
    
    def unassembled_dict_update(self, line):
        self.bad_DCB[line[self.get_idx("Serial")]] = line[self.get_idx("Serial"):self.get_idx("Comments") + 1]
        self.num_unassembled += 1

    def other_dict_update(self, line):
        self.other_DCB[line[self.get_idx("Serial")]] = line[self.get_idx("Serial"):self.get_idx("Comments") + 1]
        self.num_other += 1

    def get_idx(self, key):
        return self.DCB_columns[key]

    def get_num_assembled(self):
        return self.num_assembled
    
    def get_num_unassembled(self):
        return self.num_unassembled
    
    def get_num_other(self):
        return self.num_other

class LVR:

    def __init__(self):
        self.LVR_12A = {}
        self.LVR_25A = {}
        self.LVR_15MS = {}
        self.LVR_other = {}

        self.num_LVR_12A = 0
        self.num_LVR_25A = 0
        self.num_LVR_15MS = 0
        self.num_LVR_other = 0
        self.num_total = 0

        self.LVR_columns = {}

    def output_stream(self):
        result = "LVR General Stats\n"
        result += "The total number of boards " + str(self.num_total) + "\n"
        result += "Number of LVR Type 12A: " + str(self.num_LVR_12A) + "\n"
        result += "Number of LVR Type 25A: " + str(self.num_LVR_25A) + "\n"
        result += "Number of LVR Type 15MS: " + str(self.num_LVR_15MS) + "\n"
        result += "Number of LVR Type Other: " + str(self.num_LVR_other) + "\n"
        return result

    def output_stream_individual_stats(self):
        result = "LVR Stats\n"
        serial_num_idx = self.get_idx("Serial", 0)
        CCM_idx = self.get_idx("CCM", 0)

        result += "\nType 12A LVR's\n"
        for x, y in self.LVR_12A.items():
            result += "For LVR with ID " + x + ", and serial number " + y[serial_num_idx] + ":"
            result += "[CCM: " + y[CCM_idx] + "]" + "\n"

        result += "\nType 25A LVR's\n"
        for x, y in self.LVR_25A.items():
            result += "For LVR with ID " + x + ", and serial number " + y[serial_num_idx] + ":"
            result += "[CCM: " + y[CCM_idx] + "]" + "\n"

        result += "\nType 15MS LVR's\n"
        for x, y in self.LVR_15MS.items():
            result += "For LVR with ID " + x + ", and serial number " + y[serial_num_idx] + ":"
            result += "[CCM: " + y[CCM_idx] + "]" + "\n"

        result += "\nType Other LVR's\n"
        for x, y in self.LVR_other.items():
            result += "For LVR with ID " + x + ", and serial number " + y[serial_num_idx] + ":"
            result += "[CCM: " + y[CCM_idx] + "]" + "\n"

        return result

    def set_LVR_columns(self, serial_idx):

        self.LVR_columns["Serial"] = serial_idx - 4

        #After setting the column idx of the serial numbers,
        #Set the other LVR column indices.
        reference_idx = self.LVR_columns["Serial"]

        self.LVR_columns["ID"] = reference_idx - 2
        self.LVR_columns["Location"] = reference_idx - 1
        self.LVR_columns["CCM"] = reference_idx + 1
        self.LVR_columns["LVR_Type"] = reference_idx + 2
        self.LVR_columns["Voltage_Check"] = reference_idx + 3
        self.LVR_columns["FPGA"] = reference_idx + 4
        self.LVR_columns["Undervolt_Overtemp_Config"] = reference_idx + 5
        self.LVR_columns["Undervolt_Test"] = reference_idx + 6
        self.LVR_columns["Overtemp_Test"] = reference_idx + 7
        self.LVR_columns["Output_Config"] = reference_idx + 8
        self.LVR_columns["Sense_Line_Test"] = reference_idx + 9
        self.LVR_columns["SPI_Test"] = reference_idx + 10
        self.LVR_columns["Assembled"] = reference_idx + 11
        self.LVR_columns["SBC_Crate"] = reference_idx + 12
        self.LVR_columns["Start_Time"] = reference_idx + 13
        self.LVR_columns["End_Time"] = reference_idx + 14
        self.LVR_columns["Final_QA"] = reference_idx + 15
        self.LVR_columns["Subtype"] = reference_idx + 16     
        self.LVR_columns["Comment"] = reference_idx + 17

    def process_line(self, line):
        LVR_Type_idx = self.get_idx("LVR_Type", 4)
        if (line[LVR_Type_idx] == "12A"):
            return 1

        elif (line[LVR_Type_idx] == "25A"):
            return 2

        elif (line[LVR_Type_idx] == "15MS"):
            return 3

        else:
            return -1

    def increment_total(self):
        self.num_total += 1

    def dict_update_LVR_12A(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_12A[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_12A += 1

    def dict_update_LVR_25A(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_25A[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_25A += 1

    def dict_update_LVR_15MS(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_15MS[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_15MS += 1

    def dict_update_LVR_other(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_other[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_other += 1
    
    def get_num_total(self):
        return self.num_total

    def get_num_LVR_12A(self):
        return self.num_LVR_12A
    
    def get_num_LVR_25A(self):
        return self.num_LVR_25A

    def get_num_LVR_15MS(self):
        return self.num_LVR_15MS
    
    def get_idx(self, target, offset):
        return self.LVR_columns[target] + offset

    def process_initial_QA(self):
        num_LVR_12A_QA = 0
        num_LVR_25A_QA = 0
        num_LVR_15MS_QA = 0
        idx_voltage = self.get_idx("Voltage_Check", 0)
        idx_FPGA = self.get_idx("FPGA", 0)
        idx_undervolt_overtemp_config = self.get_idx("Undervolt_Overtemp_Config", 0)
        idx_undervolt_test = self.get_idx("Undervolt_Test", 0)
        idx_overtemp_test = self.get_idx("Overtemp_Test", 0)
        idx_output_config = self.get_idx("Output_Config", 0)
        idx_sense_line_test = self.get_idx("Sense_Line_Test", 0)
        idx_SPI = self.get_idx("SPI_Test", 0)

        for value in self.LVR_12A.values():
            if ((self.check_yes(value[idx_voltage]))
            and (self.check_yes(value[idx_FPGA]))
            and (self.check_yes(value[idx_undervolt_overtemp_config]))
            and (self.check_yes(value[idx_undervolt_test]))
            and (self.check_yes(value[idx_overtemp_test]))
            and (self.check_yes(value[idx_output_config]))
            and (self.check_yes(value[idx_sense_line_test]))
            and (self.check_yes(value[idx_SPI]))):
                num_LVR_12A_QA += 1

        for value in self.LVR_25A.values():
            if ((self.check_yes(value[idx_voltage]))
            and (self.check_yes(value[idx_FPGA]))
            and (self.check_yes(value[idx_undervolt_overtemp_config]))
            and (self.check_yes(value[idx_undervolt_test]))
            and (self.check_yes(value[idx_overtemp_test]))
            and (self.check_yes(value[idx_output_config]))
            and (self.check_yes(value[idx_sense_line_test]))
            and (self.check_yes(value[idx_SPI]))):
                num_LVR_25A_QA += 1

        for value in self.LVR_15MS.values():
            if ((self.check_yes(value[idx_voltage]))
            and (self.check_yes(value[idx_FPGA]))
            and (self.check_yes(value[idx_undervolt_overtemp_config]))
            and (self.check_yes(value[idx_undervolt_test]))
            and (self.check_yes(value[idx_overtemp_test]))
            and (self.check_yes(value[idx_output_config]))
            and (self.check_yes(value[idx_sense_line_test]))
            and (self.check_yes(value[idx_SPI]))):
                num_LVR_15MS_QA += 1
        
        return [num_LVR_12A_QA, num_LVR_25A_QA, num_LVR_15MS_QA,
                self.get_num_LVR_12A() - num_LVR_12A_QA,
                self.get_num_LVR_25A() - num_LVR_25A_QA,
                self.get_num_LVR_15MS() - num_LVR_15MS_QA]

    def check_yes(self, target):
        if (target == "Yes" or target == "yes"):
            return True
        else:
            return False

    def pyplot(self):
        # LVR Type Breakdown
        plt.rcParams.update({'font.size': 20})
        labels = "12A LVRs", "25A LVRs", "15MS LVRs"
        sizes = [self.get_num_LVR_12A(), self.get_num_LVR_25A(), self.get_num_LVR_15MS()] 
        colors = ['blue', 'red', 'yellow']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        
        #texts, the output of the above plt.pie call, is required for plt.legend() to function properly.
        #This suppresses an unnecessary warning on the otherwise only implicitly used texts variable.
        texts = texts
        
        # Plot
        plt.figure(figsize=(16,12))
        plt.title("Relative Ratios of LVR Types\n(out of a total of " + str(self.get_num_total()) + ' Assembled LVRs)')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("12A LVRs: " + str(sizes[0]) + 
        " | 25A LVRs: " + str(sizes[1]) + " | 15MS LVRs: " + str(sizes[2]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=45)
        plt.tight_layout()
        plt.savefig('LVRs_By_Type.png', bbox_inches='tight', pad_inches = 0.2)

        LVR_QA_list = self.process_initial_QA()
        sizes = LVR_QA_list[0:3]
        labels = "Initial QA'd\n12A LVRs", "Initial QA'd\n25A LVRs", "Initial QA'd\n15MS LVRs" 
        colors = ['blue', 'red', 'yellow']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        
        # Plot
        plt.figure(figsize=(16,12))
        plt.title("Ratios of Initial QA\'d LVRs\n(out of a total of " + 
        str(LVR_QA_list[0] + LVR_QA_list[1] + LVR_QA_list[2]) + "QA'd LVRs")
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Initial QA'd 12A LVRs: " + str(sizes[0]) + 
        " | Initial QA'd 25A LVRs: " + str(sizes[1]) +
        " | Initial QA'd 15MS LVRs: " + str(sizes[2]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=120)
        plt.tight_layout()
        plt.savefig('LVR_InitialQAPieChart.png', bbox_inches='tight', pad_inches = 0.2)


        """
        # Bar Plot
        # plt.style.use('ggplot')
        colors = ['blue', 'red', 'yellow']
        labels = ['Assembled DCBs', 'Unassembled DCBs', 'Other DCBs']
        num_totals = [self.get_num_assembled(), self.get_num_unassembled(), self.get_num_other()]
        plt.figure(figsize = (14, 10))
        index = np.arange(len(labels))
        patches = plt.bar(index, num_totals, color = colors)

        plt.xlabel('DCB Type')
        plt.ylabel('Number of DCBs')
        plt.xticks(index, labels)
        plt.title('DCB By Type')
        plt.legend(patches, labels, loc="upper right")
        plt.savefig('DCB_AssemblyBarChart.png')
        """

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

    def pyplot(self):
        # Bar Plot
        colors = ['blue', 'red', 'yellow', 'purple', 'orange', 'pink']
        labels = ['12A', '12M', '12S', '15M', '15S', '25A']
        num_totals = [self.num_12A, self.num_12M, self.num_12S, self.num_15M, self.num_15S, self.num_25A]
        plt.figure(figsize = (14, 10))
        index = np.arange(len(labels))
        patches = plt.bar(index, num_totals, color = colors)

        plt.xlabel('CCM Type')
        plt.ylabel('Number of CCMs')
        plt.xticks(index, labels)
        plt.title('Produced CCMs By Type')
        plt.legend(patches, labels, loc="upper right")
        plt.savefig('CCM_AssemblyBarChart.png')

#Driver for reading/parsing/writing the DCB portion of the database.
with open('CSV_DCB.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    new_DCB = DCB()

    #Set the indices of the dictionary.
    new_DCB.set_DCB_columns(0)

    for line in csv_reader:
        if re.match(pattern_DCB, line[new_DCB.DCB_columns["Serial"]]):
            assembled = new_DCB.process_line(line)

            if (assembled == 1):
                new_DCB.assembled_dict_update(line)

            elif (assembled == 2):
                new_DCB.unassembled_dict_update(line) 

            else:
                new_DCB.other_dict_update(line)
            
            new_DCB.increment_total()

    new_DCB.pyplot()

#Driver for reading/parsing/writing the LVR portion of the database.
with open('CSV_LVR.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    new_LVR = LVR()
    new_LVR.set_LVR_columns(6)

    #increment_total() is included for symmetry with the DCB loop.
    for line in csv_reader:

        if (re.match(pattern_LVR_CZ, line[6])
        or re.match(pattern_LVR_EN, line[6])
        or re.match(pattern_LVR_ER, line[6])
        or re.match(pattern_LVR_ES, line[6])):
            subtype_code = new_LVR.process_line(line)

            if (subtype_code == 1):
                new_LVR.dict_update_LVR_12A(line)

            elif (subtype_code == 2):
                new_LVR.dict_update_LVR_25A(line)

            elif (subtype_code == 3):
                new_LVR.dict_update_LVR_15MS(line)
            
            else:
                new_LVR.dict_update_LVR_other(line)

            new_LVR.increment_total()

    new_LVR.pyplot()
    output_stream = open("Demonstration_Output_LVR.txt","w")
    if (output_stream):
        output_stream.write(new_LVR.output_stream())
        output_stream.write("\n")
        output_stream.write(new_LVR.output_stream_individual_stats())
    else:
        print("Output stream failed to open.")      
        
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
                
    new_CCM.pyplot()