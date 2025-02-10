import csv
import os
import shutil
import subprocess
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

# global variables
list_cid = []
system_qty = 0
first_data = None
processed = None
summary_text = []
lots = []
results = {}
extraction_success = False

# function to send email
def send_email(subject, message):
    command = ["perl", "email.pl", subject, message]
    dos_process = subprocess.run(command)

# function to copy processed file to the web share
def copydb():
    print("Copying processed file to the web share...")
    source_file = "table_data.csv"
    destination_path = "//servername/web_shares$/CID/application/data/table_data.csv"
    shutil.copy2(source_file, destination_path)
    print("Processed file copied successfully!")

# function to move extracted data to the PASS FOLDER
def log():
    print(f"Moving extracted data to the PASS FOLDER...")
    source_file = "//servername/delivery/"+lot_number+".csv"
    destination_path = "//servername/AUTOMATION/FOLDER/SUBFOLDER/PASS/"+lot_number+".csv"
    shutil.move(source_file, destination_path)
    print(f"Extracted data moved successfully to the PASS FOLDER at {destination_path}")

def log1():
    print(f"Moving extracted data to the FAIL FOLDER...")
    source_file = "//servername/delivery/"+lot_number+".csv"
    destination_path = "//servername/AUTOMATION/FOLDER/SUBFOLDER/FAIL/"+lot_number+".csv"
    shutil.copy(source_file, destination_path)
    print(f"Extracted data moved successfully to the FAIL FOLDER at {destination_path}")

# function to create MeasLotID.txt file and move it to the _FILEMONITOR folder
def measlotid():
    print("Creating MeasLotID.txt file...")
    message = f"MeasLotID\n{lot_number}"
    file_path = 'MeasLotID.txt'
    with open(file_path, 'w') as file:
        file.write(message)
    destination_folder = "//servername/_FILEMONITOR/MeasLotID.txt"
    shutil.move(file_path, destination_folder)
    print(f"MeasLotID.txt file created and moved successfully to the _FILEMONITOR folder at {destination_folder}")
    print("Waiting for extraction Data..........\n")

# Function to attempt file rename
def attempt_rename(output_path, new_file):
    while True:
        try:
            output_path.rename(Path(new_file))
            print(f"File successfully renamed to {new_file}")
            break
        except OSError as e:
            print(f"Error: {e}. Trying again...")
            time.sleep(1)  # Wait for 1 second before retrying
            
# Open the table_data.csv file in read mode
with open('table_data.csv', 'r') as td:
    print("Reading table_data.csv file...")
    table_data_reader = list(csv.DictReader(td))
    for row in table_data_reader:
        lot = row['Lot Number']
        result = row['Result']
        tested = row['Tested Date']
        lots.append(lot)
        results[lot] = {'result': result, 'tested': tested}

fail_lots = {lot: data for lot, data in results.items() if data['result'] == 'FAIL'}
ok_lots = {lot: data for lot, data in results.items() if data['result'] == 'OK'}

# find the latest file in the folder that starts with 'filename'
folder_path = "//servername/AUTOMATION/FOLDER"
files = os.listdir(folder_path)
filtered_files = [file for file in files if file.startswith('filename')]
if not filtered_files:
    print("No matching files found.")
else:
    latest_file = max(filtered_files, key=lambda file: os.path.getmtime(os.path.join(folder_path, file)))
    latest_file_path = os.path.join(folder_path, latest_file)
    print(f"Latest file found: {latest_file_path}")

# Open the input file in read mode
with open(latest_file_path, 'r') as input_file:
    print(f"Opening input file {latest_file_path}...")
    infile_reader = list(csv.DictReader(input_file))
    for row in infile_reader:
        if (row['Transaction Qty Out'] != 0 and row['Transcode Short Name'] == 'MVOU' and row['Type'].startswith('UU99')):
            # check if lot already processed
            lot_number = row['Lot Number']
            system_qty = row['Transaction Qty Out']
            if lot_number in ok_lots:
                processed = True
                print(f"Lot {lot_number} already processed, skipping...")
            elif lot_number in fail_lots:
                lot_path = "//servername/delivery/"+lot_number+".csv"
                print(f"Lot {lot_number} has FAIL in previous data")               
                if os.path.exists(lot_path):
                    print(f"{lot_path} is exists")
                    with open(lot_path, 'r') as lp:
                        data_reader = list(csv.DictReader(lp))
                        lp_data = data_reader[1]
                        tested_date = f"['{lp_data['BeginTimestamp;datetime']}']"
                        print(lot_number+" Tested date: "+tested_date)
                        for t_date, attributes in fail_lots.items():
                            if 'tested' in attributes and attributes['tested'] == tested_date:
                                processed = True
                                print(f"{lot_number} have same date with attributes")
                                break
                            else:
                                processed = False
                else:
                    print(f"{lot_path} doesn't exists")
                    processed = False
            else:
                print(f"{lot_number} not found in the data.")
                processed = False

            if not processed:
                print(f"\n<==================================== Start extract Database Data for lot: {lot_number} ====================================>")
                db_folder = "//servername/delivery/"
                output_file = "auto_extract_from_db.csv"
                output_path = Path(db_folder + output_file)
                if output_path.exists():
                    os.remove(output_path)
                measlotid()
                x = 0
                while not output_path.exists():
                    time.sleep(1)
                    if x == 30000:
                        break
                    x += 1
                if output_path.exists():
                    test_date = []
                    test_seq = []
                    print("output_path exist")
                    time.sleep(60)
                    new_file = db_folder + lot_number + ".csv"
                    attempt_rename(output_path, new_file)
                    with open(new_file, 'r') as csv_file:
                        data_reader = list(csv.DictReader(csv_file))
                        first_data = data_reader[1]
                        for row in data_reader:
                            if row['TestType'] != '':
                                test_seq.append(row['TestType'])
                            if row['BeginTimestamp;datetime'] != '':
                                test_date.append(row['BeginTimestamp;datetime'])
                            if row['BIN'] == '1':
                                x = row['BIN'] + "_" + row['ID'] + "_" + row['WNR'] + "_" + row['X'] + "_" + row['Y']
                                list_cid.append(x)

                    # Count the occurrences of each element in the list
                    counter = Counter(list_cid)
                    # Count the number of unique elements
                    unique_count = len(counter)
                    test_date = list(set(test_date))
                    test_seq = list(set(test_seq))
                    if int(system_qty) > unique_count:
                        log1()
                    else:
                        log()
                    # Print Summary
                    summary_text.append("Header:")
                    summary_text.append("   lot              : " + first_data['lot'])
                    summary_text.append("   BeginTimestamp   : " + first_data['BeginTimestamp;datetime'])
                    summary_text.append("")
                    summary_text.append("Criteria summary:")
                    summary_text.append("   Unique CID Qty    : " + str(unique_count))
                    summary_text.append("   Redundant CID Qty : " + str(len(list_cid) - unique_count))
                    summary_text.append("   System Qty        : " + system_qty)

                    if int(system_qty) > unique_count:
                        summary_text.append("   Result                   : FAIL")
                        send_email("EVALUATION => " + " " + first_data['lot'] + " FAIL", '\n'.join(summary_text))
                    else:
                        summary_text.append("   Result                   : PASS")
                        send_email("EVALUATION => " + " " + first_data['lot'] + " PASS", '\n'.join(summary_text))

                    print('\n'.join(summary_text))
                    print("")
                    redundant_qty = len(list_cid) - unique_count
                    list_cid.clear()
                    summary_text.clear()

                    # Open the file in append mode
                    # Read the CSV file into memory
                    if int(system_qty) > unique_count:
                        result = 'FAIL'
                    else:
                        result = 'PASS'
                    discrepency = abs(int(system_qty) - unique_count)
                    sum_ = (int(system_qty) + unique_count) / 2
                    div1 = discrepency / sum_
                    if div1 > 0.05:
                        result = 'Incomplete DB data'
                    rows = []
                    with open("table_data.csv", 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        rows = list(reader)

                    # Find the index of the first available blank row
                    next_blank_row = len(rows)

                    for i, row in enumerate(rows):
                        if any(row):
                            next_blank_row = i + 1

                    # Insert the data into the next available blank row
                    rows.insert(next_blank_row, [lot_number, unique_count, redundant_qty, system_qty, result, discrepency, test_date, test_seq])

                    # Write the updated data back to the CSV file
                    with open("table_data.csv", 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(rows)
                        copydb()
copydb()