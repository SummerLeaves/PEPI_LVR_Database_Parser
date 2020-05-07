# Raymond's database parser.

import csv
import re as re
import matplotlib.pyplot as plt
import numpy as np

# regex pattern for DCB
pattern_DCB = re.compile('^(WVJCE-)[\\d\\d\\d]')

# regex patterns for LVR
pattern_LVR_CZ = re.compile('^(WVJCZ-)[\\d\\d\\d]')
pattern_LVR_EN = re.compile('^(WVJEN-)[\\d\\d\\d]')
pattern_LVR_ER = re.compile('^(WVJER-)[\\d\\d\\d]')
pattern_LVR_ES = re.compile('^(WVJES-)[\\d\\d\\d]')

# regex patterns for CCM
pattern_CCM_12A = re.compile('^(12A)[\\d|(\\d\\d)]')
pattern_CCM_12M = re.compile('^(12M)[\\d|(\\d\\d)]')
pattern_CCM_12S = re.compile('^(12S)[\\d|(\\d\\d)]')
pattern_CCM_15M = re.compile('^(15M)[\\d|(\\d\\d)]')
pattern_CCM_15S = re.compile('^(15S)[\\d|(\\d\\d)]')
pattern_CCM_25A = re.compile('^(25A)[\\d|(\\d\\d)]')

# Support function. Checks if string is equal to "Yes" or "yes",
# returning boolean True if so. Returns False otherwise.
def check_yes(target):
    if (target == "Yes" or target == "yes"):
        return True
    else:
        return False

# Contains the data and methods used to parse and process
# data from the CSV_DCB file. Performs relevant output
# operations as well.
class DCB:

    def __init__(self):

        # Organizes DCB data into
        # 3 basic categories,
        # readying for additional processing.

        # assembled     = has serial number, assembled column is yes.
        # unassembled   = has serial number, never assembled, blank assembled column.
        # other         = has serial number, but has assembled as neither yes or blank.

        # When identified, the DCB is placed into the relevant dictionary with
        # the key as the DCB's assigned ID, and the value an array of strings
        # that represents the row the DCB was listed in.
        self.unassembled_DCB = {}
        self.assembled_DCB = {}
        self.other_DCB = {}

        # Dictionary for identifying which columns in each
        # row of the CSV file (and later dictionaries)
        # correspond to which categories.
        # IMPORTANT - see set_DCB_columns() method
        # for more details.
        self.DCB_columns = {} 

        # Counter variables to do some 
        # basic tracking and processing
        # as the CSV is iterated through.
        self.num_assembled = 0
        self.num_unassembled = 0
        self.num_other = 0
        self.num_total = 0

    # Used to initialize the DCB_columns dictionary.
    # Relates a key (string of a column name) to a integer value
    # that represents the keys' corresponding entry in the string array.
    def set_DCB_columns(self, start_idx):
        # Set the starting column, the DCB serial numbers.
        reference_idx = self.DCB_columns["Serial"] = start_idx

        # The value start_idx that "Serial" is linked to
        # is the array index from the parsed CSV file that the Serial Number of the DCB
        # is contained within. 
        # As the database contains the DCB's data in consecutive columns,
        # it is mirror here as offsets from the start_idx's contained value.
        self.DCB_columns["ID"] = reference_idx + 1
        self.DCB_columns["Location"] = reference_idx + 2
        self.DCB_columns["Assembled"] = reference_idx + 3
        self.DCB_columns["Fused"] = reference_idx + 4
        self.DCB_columns["PRBS"] = reference_idx + 5
        self.DCB_columns["1.5V"] = reference_idx + 6
        self.DCB_columns["2.5V"] = reference_idx + 7
        self.DCB_columns["Burned_In"] = reference_idx + 8
        self.DCB_columns["Stave_Test_JD10"] = reference_idx + 9
        self.DCB_columns["Stave_Test_JD11"] = reference_idx + 10
        self.DCB_columns["Comments"] = reference_idx + 11
    
    # Support function for the CSV processing. 
    # ID's whether a DCB listed in a row is considered
    # assembled, unassembled, or other.
    def process_line(self, line):
        assembled_idx = self.get_idx("Assembled")
        if (line[assembled_idx] == "Yes" or line[assembled_idx] == 'yes'):
            return 1
        elif(not line[assembled_idx]):
            return 2
        else:
            return 3

    # Increments the num_total object variable.
    def increment_total(self):
        self.num_total += 1

    # Updates the assembled_DCB dictionary.
    def assembled_dict_update(self, line):
        self.assembled_DCB[line[self.get_idx("Serial")]] = line[self.get_idx("Serial"):self.get_idx("Comments") + 1]
        self.num_assembled += 1
    
    # Updates the unassembled_DCB dictionary.
    def unassembled_dict_update(self, line):
        self.unassembled_DCB[line[self.get_idx("Serial")]] = line[self.get_idx("Serial"):self.get_idx("Comments") + 1]
        self.num_unassembled += 1

    # Updates the other_DCB dictionary.
    def other_dict_update(self, line):
        self.other_DCB[line[self.get_idx("Serial")]] = line[self.get_idx("Serial"):self.get_idx("Comments") + 1]
        self.num_other += 1

    # Standard getter method. Returns
    # the value associated with the key parameter
    # from the DCB_columns dictionary. 
    # Throws an error if there is no key,
    # which is intentional - all relevant
    # columns should be added to DCB_columns!
    def get_idx(self, key):
        return self.DCB_columns[key]

    # getter method, returns num_assembled integer.
    def get_num_assembled(self):
        return self.num_assembled
    
    # getter method, returns num_unassembled integer.
    def get_num_unassembled(self):
        return self.num_unassembled
    
    # getter method, returns num_other integer.
    def get_num_other(self):
        return self.num_other

    # support function for the pyplot
    # output function. Goes through
    # assembled_DCB dictionary and returns
    # a list [num_fused, num_not_fused].
    # Not required for parsing functionality.
    def process_fused(self):
        number_fused = 0
        fused_idx = self.get_idx("Fused")

        for value in self.assembled_DCB.values():
            if (value[fused_idx] == 'yes' or value[fused_idx] == 'Yes'):
                number_fused += 1

        result = [number_fused, self.get_num_assembled() - number_fused]
        return result

    # support function for  the pyplot
    # output function. Goes through
    # assembled_DCB dictionary and returns 
    # a list [num_passed_QA, num_not_passed_QA]
    # Not required for parsing functionality. 
    def process_initial_QA(self):
        number_passed = 0
        fused_idx = self.get_idx("Fused")
        PRBS_idx = self.get_idx("PRBS")
        first_volt_idx = self.get_idx("1.5V")
        second_volt_idx = self.get_idx("2.5V")

        for value in self.assembled_DCB.values():
            if ((check_yes(value[fused_idx]))
            and (check_yes(value[PRBS_idx]))
            and (value[first_volt_idx] and value[second_volt_idx])):
                number_passed += 1

        return [number_passed, self.get_num_assembled() - number_passed]

    # Dedicated output function.
    # Creates plots using the data
    # and functions of the DCB class,
    # and saves them to the local directory.
    # Not required for parsing functionality.
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

    def output_stream(self):
        result = "DCB General Stats\n"
        result += "The total number of boards (assembled, unassembled, other): " + str(self.num_total) + "\n"
        result += "The number of assembled boards: " + str(self.num_assembled) + "\n"
        result += "The number of unassembled boards: " + str(self.num_unassembled) + "\n"
        result += "The number of other boards: " + str(self.num_other) + "\n\n"        

        result += "Definitions\n"
        result += "Assembled - Has serial number, and has 'Yes' or 'yes' recorded in the 'Assembled' column.\n"
        result += "Unassembled - Has serial number, has a blank entry in the 'Assembled' column.\n"
        result += "Other - Has serial number, has an entry recorded in the 'Assembled' column that isn't yes and isn't blank. Either special condition or typo.\n"
        return result

    def output_stream_assembled_individual_stats(self):
        idx_ID = self.get_idx("ID")
        idx_location = self.get_idx("Location")
        idx_fused = self.get_idx("Fused")
        idx_PRBS = self.get_idx("PRBS")
        idx_one_p_five = self.get_idx("1.5V")
        idx_two_p_five = self.get_idx("2.5V")
        idx_comment = self.get_idx("Comments")

        result = "Assembled DCB Stats\n"
        result += "Format: [ DCB ID | Location | Fused | PRBS | 1.5V Test | 2.5V Test ]\nComment: [Text Here]\n\n"


        for y in self.assembled_DCB.values():
            comment = y[idx_comment]
            first_test = str(y[idx_one_p_five])
            second_test = str(y[idx_two_p_five])

            if (comment == ""):
                comment = "No recorded comment."

            if (first_test == ""):
                first_test = "N/A"

            if (second_test == ""):
                second_test = "N/A"

            result += "[ DCB ID: " +  y[idx_ID] + " | Location: " + y[idx_location]
            result += " | Fused: " + y[idx_fused] + " | PRBS: " + y[idx_PRBS]
            result += " | 1.5V Test: " + first_test + " | 2.5V Test: " + second_test + " ]\n"
            result += "Comment: " + comment + "\n\n"
        return result

    def output_stream_unassembled_individual_stats(self):
        idx_ID = self.get_idx("ID")
        idx_location = self.get_idx("Location")
        idx_comment = self.get_idx("Comments")

        result = "Unassembled DCB Stats\n"
        result += "Format: [ DCB ID | Location ]\nComment: [Text Here]\n\n"


        for y in self.unassembled_DCB.values():
            comment = y[idx_comment]
            if (comment == ""):
                comment = "No recorded comment."
            
            result += "[ DCB ID: " +  y[idx_ID] + " | Location: " + y[idx_location] + " ]\n"
            result += "Comment: " + comment + "\n\n"
        return result

    def output_stream_other_individual_stats(self):
        idx_ID = self.get_idx("ID")
        idx_assembled = self.get_idx("Assembled")
        idx_location = self.get_idx("Location")
        idx_fused = self.get_idx("Fused")
        idx_PRBS = self.get_idx("PRBS")
        idx_one_p_five = self.get_idx("1.5V")
        idx_two_p_five = self.get_idx("2.5V")
        idx_comment = self.get_idx("Comments")

        result = "Other DCB Stats\n"
        result += "Format: [ DCB ID | Assembled Status | Location | Fused | PRBS | 1.5V Test | 2.5V Test ]\nComment: [Text Here]\n\n"


        for y in self.other_DCB.values():
            comment = y[idx_comment]
            first_test = str(y[idx_one_p_five])
            second_test = str(y[idx_two_p_five])

            if (comment == ""):
                comment = "No recorded comment."

            if (first_test == ""):
                first_test = "N/A"

            if (second_test == ""):
                second_test = "N/A"

            result += "[ DCB ID: " +  y[idx_ID] + " | Status: " + y[idx_assembled] + " | Location: " + y[idx_location]
            result += " | Fused: " + y[idx_fused] + " | PRBS: " + y[idx_PRBS]
            result += " | 1.5V Test: " + first_test + " | 2.5V Test: " + second_test + " ]\n"
            result += "Comment: " + comment + "\n\n"

        return result
# Contains the data and methods used to parse and process
# data from the CSV_LVR file. Performs relevant output
# operations as well.
class LVR:

    def __init__(self):
        # Four LVR dictionaries
        # corresponding to the listed subtypes.
        # In case a new subtype is added,
        # or there's a typo in the database,
        # an "other" category is included.
        self.LVR_12A = {}
        self.LVR_25A = {}
        self.LVR_15MS = {}
        self.LVR_other = {}

        # Similar to the DCB,
        # this dictionary lists
        # which column in the array of strings
        # each row from the CSV becomes corresponds
        # to which category of the LVR database.
        # IMPORTANT: See set_LVR_columns().
        self.LVR_columns = {}

        # Based counter variables
        # for processing during
        # the CSV parsing.
        self.num_LVR_12A = 0
        self.num_LVR_25A = 0
        self.num_LVR_15MS = 0
        self.num_LVR_other = 0
        self.num_total = 0

    # Initializes the LVR_columns dictionary.
    def set_LVR_columns(self, serial_idx):
        
        # The relevant LVR columns in the database
        # don't start at column 0, so an offset
        # is used to simplify LVR_type dictionary operations.
        reference_idx = self.LVR_columns["Serial"] = serial_idx - 4

        # After setting the column idx of the serial numbers,
        # Set the other LVR column indices.
        # If columns move positions in the database, 
        # change the offset here.
        # If new columns are added, 
        # add the column to the dictionary and
        # modify the dictionary update mehtods.
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

    # After being identified with regex
    # in the CSV processing driver,
    # this function identifies which LVR type 
    # the row corresponds to.
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

    # setter method that increments the 
    # num_total.
    def increment_total(self):
        self.num_total += 1

    # updates the LVR_12A dictionary.
    def dict_update_LVR_12A(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_12A[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_12A += 1

    # updates the LVR_25A dictionary.
    def dict_update_LVR_25A(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_25A[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_25A += 1

    # updates the 15MS dictionary.
    def dict_update_LVR_15MS(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_15MS[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_15MS += 1

    # updates the other dictionary.
    def dict_update_LVR_other(self, line):
        start_idx = self.get_idx("ID", 4)
        end_idx = self.get_idx("Comment", 4) + 1

        self.LVR_other[line[start_idx]] = line[start_idx:end_idx]
        self.num_LVR_other += 1
    
    # standard getter method for num_total.
    def get_num_total(self):
        return self.num_total

    # standard getter method for num_LVR_12A.
    def get_num_LVR_12A(self):
        return self.num_LVR_12A
    
    # standard getter method for num_LVR_25A.
    def get_num_LVR_25A(self):
        return self.num_LVR_25A

    # standard getter method for num_LVR_15MS.
    def get_num_LVR_15MS(self):
        return self.num_LVR_15MS
    
    # Gets the relevant array index
    # from the LVR_columns dictionary.
    def get_idx(self, target, offset):
        return self.LVR_columns[target] + offset

    # Support method for the pyplot
    # processing. 
    # returns [num_passed_12A, num_passed_25A, num_passed_15MS,
    # num_not_passed_12A, num_not_passed 25A, num_not_passed 15MS].
    # Not required for parsing functionality.
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
            if ((check_yes(value[idx_voltage]))
            and (check_yes(value[idx_FPGA]))
            and (check_yes(value[idx_undervolt_overtemp_config]))
            and (check_yes(value[idx_undervolt_test]))
            and (check_yes(value[idx_overtemp_test]))
            and (check_yes(value[idx_output_config]))
            and (check_yes(value[idx_sense_line_test]))
            and (check_yes(value[idx_SPI]))):
                num_LVR_12A_QA += 1

        for value in self.LVR_25A.values():
            if ((check_yes(value[idx_voltage]))
            and (check_yes(value[idx_FPGA]))
            and (check_yes(value[idx_undervolt_overtemp_config]))
            and (check_yes(value[idx_undervolt_test]))
            and (check_yes(value[idx_overtemp_test]))
            and (check_yes(value[idx_output_config]))
            and (check_yes(value[idx_sense_line_test]))
            and (check_yes(value[idx_SPI]))):
                num_LVR_25A_QA += 1

        for value in self.LVR_15MS.values():
            if ((check_yes(value[idx_voltage]))
            and (check_yes(value[idx_FPGA]))
            and (check_yes(value[idx_undervolt_overtemp_config]))
            and (check_yes(value[idx_undervolt_test]))
            and (check_yes(value[idx_overtemp_test]))
            and (check_yes(value[idx_output_config]))
            and (check_yes(value[idx_sense_line_test]))
            and (check_yes(value[idx_SPI]))):
                num_LVR_15MS_QA += 1
        
        return [num_LVR_12A_QA, num_LVR_25A_QA, num_LVR_15MS_QA,
                self.get_num_LVR_12A() - num_LVR_12A_QA,
                self.get_num_LVR_25A() - num_LVR_25A_QA,
                self.get_num_LVR_15MS() - num_LVR_15MS_QA]

    # Output function that creates,
    # saves plots for the LVR.
    # Not required for parsing functionality.
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
        str(LVR_QA_list[0] + LVR_QA_list[1] + LVR_QA_list[2]) + " QA'd LVRs)")
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("Initial QA'd 12A LVRs: " + str(sizes[0]) + 
        " | Initial QA'd 25A LVRs: " + str(sizes[1]) +
        " | Initial QA'd 15MS LVRs: " + str(sizes[2]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=120)
        plt.tight_layout()
        plt.savefig('LVR_InitialQAPieChart.png', bbox_inches='tight', pad_inches = 0.2)

    # Text output stream.
    # Not required for parsing functionality.
    def output_stream(self):
        result = "LVR General Stats\n"
        result += "The total number of boards " + str(self.num_total) + "\n"
        result += "Number of LVR Type 12A: " + str(self.num_LVR_12A) + "\n"
        result += "Number of LVR Type 25A: " + str(self.num_LVR_25A) + "\n"
        result += "Number of LVR Type 15MS: " + str(self.num_LVR_15MS) + "\n"
        result += "Number of LVR Type Other: " + str(self.num_LVR_other) + "\n"
        return result

    # Text output stream.
    # Not required for parsing functionality.
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

# Contains the data and methods used to parse and process
# data from the CSV_CCM file. Performs relevant output
# operations as well.
class CCM:

    def __init__(self):
        # Splits parsed CCM data into
        # dictionaries based on type.
        self.CCM_12A = {}
        self.CCM_12M = {}
        self.CCM_12S = {}
        self.CCM_15M = {}
        self.CCM_15S = {}
        self.CCM_25A = {}

        # Dictionary for keeping
        # track of which entries in a parsed line
        # correspond to which categories of the database.
        self.CCM_columns = {}

        # Counter variables for basic processing.
        self.num_12A = 0
        self.num_12M = 0
        self.num_12S = 0
        self.num_15M = 0
        self.num_15S = 0
        self.num_25A = 0
        self.num_total = 0

    # Sets the CCM_columns variable.
    def set_CCM_columns(self, start_idx):
        self.CCM_columns["Roll_ID"] = start_idx

        reference_idx = self.CCM_columns["Roll_ID"]
        self.CCM_columns["Location"] = reference_idx + 1
        self.CCM_columns["CCM_Type"] = reference_idx + 2
        self.CCM_columns["Master_or_Slave"] = reference_idx + 3
        self.CCM_columns["Original_Count"] = reference_idx + 4
        self.CCM_columns["Good_Count"] = reference_idx + 5
        self.CCM_columns["Usage"] = reference_idx + 6
        self.CCM_columns["Comment"] = reference_idx + 7

    # Increments the num_total.
    def increment_total(self):
        self.num_total += 1
    
    # Updates the dictionary and count for 12A CCMs.
    def dict_update_12A(self, line):
        idx_start = self.get_idx("Roll_ID")
        idx_end = self.get_idx("Comment") + 1
        self.CCM_12A[line[idx_start]] = line[idx_start:idx_end]
        self.num_12A += int(line[self.get_idx("Good_Count")]) 

    # Updates the dictionary and count for 12M CCMs.
    def dict_update_12M(self, line):
        idx_start = self.get_idx("Roll_ID")
        idx_end = self.get_idx("Comment") + 1
        self.CCM_12M[line[idx_start]] = line[idx_start:idx_end]
        self.num_12M += int(line[self.get_idx("Good_Count")]) 

    # Updates the dictionary and count for 12S CCMs.
    def dict_update_12S(self, line):
        idx_start = self.get_idx("Roll_ID")
        idx_end = self.get_idx("Comment") + 1
        self.CCM_12S[line[idx_start]] = line[idx_start:idx_end]
        self.num_12S += int(line[self.get_idx("Good_Count")]) 

    # Updates the dictionary and count for 15M CCMs.
    def dict_update_15M(self, line):
        idx_start = self.get_idx("Roll_ID")
        idx_end = self.get_idx("Comment") + 1
        self.CCM_15M[line[idx_start]] = line[idx_start:idx_end]
        self.num_15M += int(line[self.get_idx("Good_Count")]) 

    # Updates the dictionary and count for 15S CCMs.
    def dict_update_15S(self, line):
        idx_start = self.get_idx("Roll_ID")
        idx_end = self.get_idx("Comment") + 1
        self.CCM_15S[line[idx_start]] = line[idx_start:idx_end]
        self.num_15S += int(line[self.get_idx("Good_Count")]) 

    # Updates the dictionary and count for 25A CCMs.
    def dict_update_25A(self, line):
        idx_start = self.get_idx("Roll_ID")
        idx_end = self.get_idx("Comment") + 1
        self.CCM_25A[line[idx_start]] = line[idx_start:idx_end]
        self.num_25A += int(line[self.get_idx("Good_Count")]) 

    # Updates the dictionary and count for 12A CCMs.
    def get_idx(self, target):
        return self.CCM_columns[target]

    # Output stream. Creates, save pyplots to local directory.
    # Not necessary for parsing functionality.
    def pyplot(self):
        # Bar Plot
        colors = ['blue', 'red', 'yellow', 'purple', 'orange', 'pink']
        labels = ['12A', '12M', '12S', '15M', '15S', '25A']
        num_totals = [self.num_12A, self.num_12M, self.num_12S, self.num_15M, self.num_15S, self.num_25A]
        plt.figure(figsize = (14, 10))
        index = np.arange(len(labels))
        patches = plt.bar(index, num_totals, color = colors)

        plt.xlabel('CCM Type')
        plt.ylabel("Number of QA'd CCMs")
        plt.xticks(index, labels)
        plt.title("QA'd CCMs By Type")
        plt.legend(patches, labels, loc="upper right")
        plt.savefig('CCM_QABarChart.png')

# Contains the data and methods used to parse and process
# data from the CSV_Backplane file. Performs relevant output
# operations as well.
class Backplane:
    def __init__(self):
        # Splits parsed data into true backplanes
        # and mirror backplanes dictionaries.
        self.true_backplanes = {}
        self.mirror_backplanes = {}

        # Dictionary records which entries
        # in the parsed string array (from the CSV)
        # correspond to which information in the database.
        # IMPORTANT: see set_backplane_columns.
        self.backplane_columns = {}

        # Counter variables for basic processing during
        # parsing.
        self.num_true_backplanes = 0
        self.num_mirror_backplanes = 0
        self.num_total_backplanes = 0

    # Sets the backplane_columns dictionary.
    def set_backplane_columns(self, idx_start):
        # Set the column that will serve as the key values 
        # in the parsed data dictionaries.
        idx_reference = self.backplane_columns["Type"] = idx_start

        # Afterwards, set the other entries' values as offsets
        # of the key column, mirroring the actual database.
        self.backplane_columns["Variant"] = idx_reference + 1
        self.backplane_columns["SN"] = idx_reference + 2
        self.backplane_columns["ID"] = idx_reference + 3
        self.backplane_columns["Location"] = idx_reference + 4
        self.backplane_columns["Visual_Inspection"] = idx_reference + 5
        self.backplane_columns["Burn_In"] = idx_reference + 6
        self.backplane_columns["QA"] = idx_reference + 7
        self.backplane_columns["Assembly"] = idx_reference + 8
        self.backplane_columns["Note"] = idx_reference + 9

    # Updates the true_backplanes dictionary.
    def update_true_backplanes(self, line):
        idx_backplane = self.get_num_true_backplanes()
        idx_start = self.get_idx("Type")
        idx_end = self.get_idx("Note") + 1
        self.true_backplanes[idx_backplane] = line[idx_start:idx_end]

    # Updates the mirror_backplanes dictionary.
    def update_mirror_backplanes(self, line):
        idx_backplane = self.get_num_mirror_backplanes()
        idx_start = self.get_idx("Type")
        idx_end = self.get_idx("Note") + 1
        self.mirror_backplanes[idx_backplane] = line[idx_start:idx_end]

    # Increments the num_true_backplanes variable.
    def increment_num_true_backplanes(self):
        self.num_true_backplanes += 1
    
    # Increments the num_mirror_backplanes variable.
    def increment_num_mirror_backplanes(self):
        self.num_mirror_backplanes += 1

    # Increments the num_total_backplanes variable.
    def increment_total(self):
        self.num_total_backplanes += 1

    # Returns the value the target parameter
    # is associated with the backplane_columns dictionary.
    def get_idx(self, target):
        return self.backplane_columns[target]

    # getter method, returns num_true_backplanes.
    def get_num_true_backplanes(self):
        return self.num_true_backplanes
    
    # getter method, returns num_mirror_backplanes.
    def get_num_mirror_backplanes(self):
        return self.num_mirror_backplanes

    # support function for pyplot method.
    def process_QA(self):
        idx_QA = self.get_idx("QA")
        num_true_backplanes_passed = 0
        num_mirror_backplanes_passed = 0

        for value in self.true_backplanes.values():
            if (check_yes(value[idx_QA])):
                num_true_backplanes_passed += 1
        
        for value in self.mirror_backplanes.values():
            if (check_yes(value[idx_QA])):
                num_mirror_backplanes_passed += 1

        return [num_true_backplanes_passed, self.get_num_true_backplanes() - num_true_backplanes_passed,
                num_mirror_backplanes_passed, self.get_num_mirror_backplanes() - num_mirror_backplanes_passed]

    # output function, creates, saves figures
    # based on parsed data to local directory.
    # Not necessary for parsing functionality.
    def pyplot(self):
        # QA'd True Backplanes Vs. All True Backplanes
        labels = "QA'd True Backplanes", "Other True Backplanes"
        QA_List = self.process_QA()
        sizes = QA_List[0:2]
        colors = ['blue', 'red']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        
        #To suppress warning.
        texts = texts

        # Plot
        plt.figure(figsize=(16,12))
        plt.title("Ratio of QA'd True Backplanes\n(out of a total of " + str(self.get_num_true_backplanes()) + ' True Backplanes)')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("QA'd True Backplanes: " + str(sizes[0]) + 
        " | Other True Backplanes: " + str(sizes[1]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=120)
        plt.tight_layout()
        plt.savefig('Backplane_True_QAPieChart.png', bbox_inches='tight', pad_inches = 0.2)

        # QA'd Mirror Backplanes Vs. All other Mirror Backplanes
        labels = "QA'd Mirror Backplanes", "Other Mirror Backplanes"
        sizes = QA_List[2:4]
        colors = ['blue', 'red']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        
        #To suppress warning.
        texts = texts

        # Plot
        plt.figure(figsize=(16,12))
        plt.title("Ratio of QA'd Mirror Backplanes\n(out of a total of " + str(self.get_num_true_backplanes()) + ' Mirror Backplanes)')
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.xlabel("QA'd Mirror Backplanes: " + str(sizes[0]) + 
        " | Other Mirror Backplanes: " + str(sizes[1]))

        plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=120)
        plt.tight_layout()
        plt.savefig('Backplane_Mirror_QAPieChart.png', bbox_inches='tight', pad_inches = 0.2)

# Driver for reading/parsing/writing the DCB portion of the database.
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
    
    output_stream = open("Text_Output_DCB.txt","w")
    if (output_stream):
        result = new_DCB.output_stream()
        result += "\n" + new_DCB.output_stream_assembled_individual_stats()
        result += "\n" + new_DCB.output_stream_unassembled_individual_stats()
        result += "\n" + new_DCB.output_stream_other_individual_stats()
        output_stream.write(result)
    else:
        print("Output stream failed to open.")

# Driver for reading/parsing/writing the LVR portion of the database.
with open('CSV_LVR.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    new_LVR = LVR()
    new_LVR.set_LVR_columns(6)
    idx_serial = new_LVR.get_idx("Serial", 4)

    # The csv_reader iterator returns a string array
    # corresponding to each row in the CSV file, which 
    # is named "line" here.
    for line in csv_reader:

        # If the serial number matches any 
        # of the accepted patterns,
        # it's a valid LVR that can be recorded.
        if (re.match(pattern_LVR_CZ, line[idx_serial])
        or re.match(pattern_LVR_EN, line[idx_serial])
        or re.match(pattern_LVR_ER, line[idx_serial])
        or re.match(pattern_LVR_ES, line[idx_serial])):
            subtype_code = new_LVR.process_line(line)

            # if-else chain updates LVR dictionaries
            # as appropriate, by passing the line
            # to the appropriate LVR class method.
            if (subtype_code == 1):
                new_LVR.dict_update_LVR_12A(line)

            elif (subtype_code == 2):
                new_LVR.dict_update_LVR_25A(line)

            elif (subtype_code == 3):
                new_LVR.dict_update_LVR_15MS(line)
            
            else:
                new_LVR.dict_update_LVR_other(line)

            # If the regex matched, it's an existing LVR,
            # so increment the total count.
            new_LVR.increment_total()

    # Calls output function to create and save graphs to local directory.
    new_LVR.pyplot()
    """
    output_stream = open("Demonstration_Output_LVR.txt","w")
    if (output_stream):
        output_stream.write(new_LVR.output_stream())
        output_stream.write("\n")
        output_stream.write(new_LVR.output_stream_individual_stats())
    else:
        print("Output stream failed to open.")     
    """
        
#Driver for reading/parsing/writing the CCM portion of the database.
with open('CSV_CCM.csv', 'r') as csv_file:

    # Setup. Creates CCM object, and a csv_iterator.
    csv_reader = csv.reader(csv_file)
    new_CCM = CCM()
    new_CCM.set_CCM_columns(0)
    idx_roll = new_CCM.get_idx("Good_Count")
    idx_id = new_CCM.get_idx("Roll_ID") 

    # The CSV_reader outputs an array of strings representing 
    # the CSV's row.
    for line in csv_reader:

        # A roll was placed into the database if and only if
        # the good CCM column entry was filled out.
        # If it is filled out, we place the CCM into one of the dictionaries.
        if (line[idx_roll] != ''):
            if (re.match(pattern_CCM_12A, line[idx_id])):
                new_CCM.dict_update_12A(line)
                new_CCM.increment_total()
                
            elif(re.match(pattern_CCM_12M, line[idx_id])):
                new_CCM.dict_update_12M(line)
                new_CCM.increment_total()
            
            elif(re.match(pattern_CCM_12S, line[idx_id])):
                new_CCM.dict_update_12S(line)
                new_CCM.increment_total()

            elif(re.match(pattern_CCM_15M, line[idx_id])):
                new_CCM.dict_update_15M(line)
                new_CCM.increment_total()

            elif(re.match(pattern_CCM_15S, line[idx_id])):
                new_CCM.dict_update_15S(line)
                new_CCM.increment_total()

            elif(re.match(pattern_CCM_25A, line[idx_id])):
                new_CCM.dict_update_25A(line)
                new_CCM.increment_total()
                
    new_CCM.pyplot()

#Driver for reading/parsing//writing the Backplane portion of the database.
with open('CSV_Backplane.csv', 'r') as csv_file:

    csv_reader = csv.reader(csv_file)
    new_backplane = Backplane()
    new_backplane.set_backplane_columns(0)
    idx_type = new_backplane.get_idx("Type")

    for line in csv_reader:
        if (line[idx_type] == "True"):
            new_backplane.update_true_backplanes(line)
            new_backplane.increment_num_true_backplanes()

        elif (line[idx_type] == "Mirror"):
            new_backplane.update_mirror_backplanes(line)
            new_backplane.increment_num_mirror_backplanes()
        
    new_backplane.pyplot()