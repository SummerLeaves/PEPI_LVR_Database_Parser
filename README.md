# PEPI_LVR_Database_Parser (And Analyzer)
A python script that reads .csv files sourced from the PEPI/LVR database, 
parses them with regex, 
sorts the data for further analysis, 
does the analysis, (as modular functions),
and writes the results to an arbitrary output stream.

General Framework
1) Recieve DCB, LVR, CCM, and Backplane files From CSV Scrapper.
2) Run Database Parser and Analyzer. Parses content of each CSV into dictionaries of relevant information,
and outputs completed data analysis in the form of graphs and text files.
3) Use output files in an HTML/CSS/Javascript website.

General Framework of Database Parser

As per the guidelines given, the project should be 
1) Easy to understand,
2) robust,
3) and easy to modify.

For those reasons, the program is split into explicit driver and class sections. 
This ensures that all the code and data for each board type is encapsulated safely within a single class, 
removing ambiguity, enabling flexibility, 
and creating isolation for tackling the unique problems presented by parsing the board types' corresponding files.

Classes
For each board that needs to be parsed, there is a corresponding class, all of which are built with the same framework.

Parsing Dictionary

1) Each defines several parsing dictionaries that split the results into key-value pairs. 
- The key is some kind of identifier in the parsed CSV lines that indicates it is a valid row to record.
- The value is an array of strings, with each element of the array corresponding to a category of information that needs to be recorded.
- The columns dictionary described below defines how the corresponding array indices for each category of information is identified 
for use in data analysis.
   

Columns Dictionary

2) Each defines a specialized dictionary that records the different categories of data that need to be recorded for each board,
and assigns them the corresponding array index of the column of the CSV row that the category is in. 
- i.e. the "Serial Number" is connected to a value of 0, since the CSV file contains the serial numbers of the DCB boards in the 0th column.
- The columns dictionary is, at the momemnt, defined using manual adjustments and offsets through a dedicated method.
   
Parsing Dictionary Update

3) Each defines a series of dictionary update methods, that update the parsing dictionaries with a Key (An unique unambigious identifier for each board) to a Value (An array of strings that contains the target information of that board, with what information is in what index identified by the specialized dictionary above.)
- i.e For the DCB file, a filled in Serial Number of type WVJCE-xxx indicates that this is an existing board that needs to be recorded. The value is the row it's on, and the indices that represent relevant information (Location, Assembly Status, PRBS) are recorded as key-value pairs in the columns dictionary.

Data Analysis and Output Files

4) Each defines an output, to be called after parsing is finished, that utilizes the dictionaries (or associated variables) to
do data analysis and generate output. For now, it uses the matplotlib.pyplot module to create graphs, but can also create text files and other arbitrary output.

Drivers
For each board that needs to be parsed, there is a corresponding driver, all of which are built with the same framework.
To keep the philosophy of robust, easy to understand, and easy to modify code, as much processing as possible is abstracted to the classes.
  
  Regex Identifier
1) Each uses a pre-defined regex identifier to sort out the relvant rows of the parsed CSV. The regex identifier 
is focused on some aspect of the database that conclusively defines the row that follows to contain targeted information.

   Board Object
2) Each creates an object of the board types' class. Processing and finalized data collection will be focused on
the object.
  
   CSV Reader
3) Each calls CSV reader, creating a csv_reader iterator. From this iterator, we extract an array of strings, which is placed
into a "line" variable. The line variable is subjected to basic processing that determines whether it contains valid information,
and if so, is passed to the relevant dictionary update method.

   Output
4) Each calls the object's output methods to process and then create file output, to be saved into the local directory.

At the moment, we are doing the DCB, LVR, CCM, and Backplane sections of the database.
[More infromation on each class specifically to be added later].
