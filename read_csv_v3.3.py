import csv
import os
import shutil
import subprocess
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

# global variables
list_chipid_bin1 = []
qty_camstar = 0
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
    source_file = "wip_processed.csv"
    destination_path = "//bthsa1082.ap.infineon.com/web_shares$/chipID/application/history/Lot_History.csv"
    shutil.copy2(source_file, destination_path)
    print("Processed file copied successfully!")

# function to move extracted data to the EBS_LOT_LOG folder
def log():
    print(f"Moving extracted data to the EBS_LOT_LOG folder...")
    source_file = "//e2asia12.intra.infineon.com/eSquare_user/hidayattaufi_infineon/delivery/"+lot_camstar+".csv"
    destination_path = "//bthsdv004.infineon.com/PTE_Project/AUTOMATION/000.AUTO_EXTRACTION/BAKE_IN_LOT/EBS_LOT_LOG/"+lot_camstar+".csv"
    shutil.move(source_file, destination_path)
    print(f"Extracted data moved successfully to the EBS_LOT_LOG folder at {destination_path}")

def log1():
    print(f"Moving extracted data to the EBS_LOT_LOG folder...")
    source_file = "//e2asia12.intra.infineon.com/eSquare_user/hidayattaufi_infineon/delivery/"+lot_camstar+".csv"
    destination_path = "//bthsdv004.infineon.com/PTE_Project/AUTOMATION/000.AUTO_EXTRACTION/BAKE_IN_LOT/EBS_LOT_LOG/"+lot_camstar+".csv"
    shutil.copy(source_file, destination_path)
    print(f"Extracted data moved successfully to the EBS_LOT_LOG folder at {destination_path}")

# function to create MeasLotID.txt file and move it to the _FILEMONITOR folder
def measlotid():
    print("Creating MeasLotID.txt file...")
    message = f"MeasLotID\n{lot_camstar}"
    file_path = 'MeasLotID.txt'
    with open(file_path, 'w') as file:
        file.write(message)
    destination_folder = "//e2asia12.intra.infineon.com/eSquare_user/_FILEMONITOR/hidayattaufi_infineon/MeasLotID.txt"
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
            
# Open the wip_processed file in read mode
with open('wip_processed.csv', 'r') as wip_processed_file:
    print("Reading wip_processed file...")
    wip_processed_reader = list(csv.DictReader(wip_processed_file))
    for row in wip_processed_reader:
        lot = row['LotNo']
        result = row['Result']
        tested = row['Tested Date']
        lots.append(lot)
        results[lot] = {'result': result, 'tested': tested}

fail_lots = {lot: data for lot, data in results.items() if data['result'] == 'FAIL'}
ok_lots = {lot: data for lot, data in results.items() if data['result'] == 'OK'}

# find the latest file in the folder that starts with 'BAKEIN_LOT_MVIN'
folder_path = "//bthsdv004.infineon.com/PTE_Project/AUTOMATION/000.AUTO_EXTRACTION/BAKE_IN_LOT"
files = os.listdir(folder_path)
filtered_files = [file for file in files if file.startswith('BAKEIN_LOT_MVIN')]
if not filtered_files:
    print("No matching files found.")
else:
    latest_file = max(filtered_files, key=lambda file: os.path.getmtime(os.path.join(folder_path, file)))
    latest_file_path = os.path.join(folder_path, latest_file)
    print(f"Latest file found: {latest_file_path}")

# Open the WIP file in read mode
with open(latest_file_path, 'r') as wip_file:
    print(f"Opening WIP file {latest_file_path}...")
    wip_reader = list(csv.DictReader(wip_file))
    for row in wip_reader:
        if (row['Transaction Qty Out 1'] != 0 and row['Transcode Short Name'] == 'MVOU' and row['Product Basic Type'].startswith('U810')):
            # check if lot already processed
            lot_camstar = row['Lot Number']
            qty_camstar = row['Transaction Qty Out 1']
            if lot_camstar in ok_lots:
                processed = True
                print(f"Lot {lot_camstar} already processed, skipping...")
            elif lot_camstar in fail_lots:
                #lot_path = "//bthsdv004.infineon.com/PTE_Project/AUTOMATION/000.AUTO_EXTRACTION/BAKE_IN_LOT/EBS_LOT_LOG/"+lot_camstar+".csv"
                lot_path = "//e2asia12.intra.infineon.com/eSquare_user/hidayattaufi_infineon/delivery/"+lot_camstar+".csv"
                print(f"Lot {lot_camstar} has FAIL in previous data")               
                if os.path.exists(lot_path):
                    print(f"{lot_path} is exists")
                    with open(lot_path, 'r') as lp:
                        data_reader = list(csv.DictReader(lp))
                        lp_data = data_reader[1]
                        tested_date = f"['{lp_data['BeginTimestamp;datetime']}']"
                        print(lot_camstar+" Tested date: "+tested_date)
                        for t_date, attributes in fail_lots.items():
                            if 'tested' in attributes and attributes['tested'] == tested_date:
                                processed = True
                                print(f"{lot_camstar} have same date with attributes")
                                break
                            else:
                                #print(f"{lot_camstar} doesn't have same date")
                                processed = False
                else:
                    print(f"{lot_path} doesn't exists")
                    processed = False
                    # need to update bug here
            else:
                print(f"{lot_camstar} not found in the data.")
                processed = False

            if not processed:
                print(f"\n<==================================== Start extract EBS Data for lot: {lot_camstar} ====================================>")
                esquare_folder = "//e2asia12.intra.infineon.com/eSquare_user/hidayattaufi_infineon/delivery/"
                output_file = "auto_extract_FAR_U810x.csv"
                output_path = Path(esquare_folder + output_file)
                if output_path.exists():
                    os.remove(output_path)
                # override measlotid.txt + lot_camstar
                measlotid()
                # execute EBS extraction
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
                    new_file = esquare_folder + lot_camstar + ".csv"
                    attempt_rename(output_path, new_file)
                    with open(new_file, 'r') as csv_file:
                        data_reader = list(csv.DictReader(csv_file))
                        first_data = data_reader[1]
                        for row in data_reader:
                            if row['TestType'] != '':
                                test_seq.append(row['TestType'])
                            if row['BeginTimestamp;datetime'] != '':
                                test_date.append(row['BeginTimestamp;datetime'])
                            if row['HBIN'] == '1':
                                x = row['HBIN'] + "_" + row['FELOTID'] + "_" + row['WAFERNR'] + "_" + row['X'] + "_" + row['Y']
                                list_chipid_bin1.append(x)

                    # Count the occurrences of each element in the list
                    counter = Counter(list_chipid_bin1)
                    # Count the number of unique elements
                    unique_count = len(counter)
                    test_date = list(set(test_date))
                    test_seq = list(set(test_seq))
                    if int(qty_camstar) > unique_count:
                        log1()
                    else:
                        log()
                    # Print Summary
                    summary_text.append("Header:")
                    summary_text.append("   lot              : " + first_data['lot'])
                    summary_text.append("   measstep         : " + first_data['measstep'])
                    summary_text.append("   BeginTimestamp   : " + first_data['BeginTimestamp;datetime'])
                    summary_text.append("   HandlerID        : " + first_data['HandlerID'])
                    summary_text.append("   Loadboard        : " + first_data['Loadboard'])
                    summary_text.append("   Temperature      : " + first_data['Temperature'])
                    summary_text.append("   Tester           : " + first_data['Tester'])
                    summary_text.append("   TestprgNameRev   : " + first_data['TestprgNameRev'])
                    summary_text.append("")
                    summary_text.append("Criteria summary:")
                    summary_text.append("   Qty Unique Chip-id Bin1  : " + str(unique_count))
                    summary_text.append("   Qty Redundant Chip-id    : " + str(len(list_chipid_bin1) - unique_count))
                    summary_text.append("   Qty Camstar at Bake-in   : " + qty_camstar)

                    if int(qty_camstar) > unique_count:
                        summary_text.append("   Result                   : FAIL (Camstar Qty > ChipID Count)")
                        send_email("U810x LOT EVALUATION => " + " " + first_data['lot'] + " FAIL (Camstar Qty > ChipID Count)", '\n'.join(summary_text))
                    else:
                        summary_text.append("   Result                   : OK (Safe to Release)")
                        send_email("U810x LOT EVALUATION => " + " " + first_data['lot'] + " OK (Safe to Release)", '\n'.join(summary_text))

                    print('\n'.join(summary_text))
                    print("")
                    redundant_qty = len(list_chipid_bin1) - unique_count
                    list_chipid_bin1.clear()
                    summary_text.clear()

                    # Open the file in append mode
                    # Read the CSV file into memory
                    if int(qty_camstar) > unique_count:
                        result = 'FAIL'
                    else:
                        result = 'OK'
                    discrepency = abs(int(qty_camstar) - unique_count)
                    sum_ = (int(qty_camstar) + unique_count) / 2
                    div1 = discrepency / sum_
                    if div1 > 0.05:
                        result = 'Incomplete EBS'
                    rows = []
                    with open("wip_processed.csv", 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        rows = list(reader)

                    # Find the index of the first available blank row
                    next_blank_row = len(rows)

                    for i, row in enumerate(rows):
                        if any(row):
                            next_blank_row = i + 1

                    # Insert the data into the next available blank row
                    rows.insert(next_blank_row, [lot_camstar, unique_count, redundant_qty, qty_camstar, result, discrepency, test_date, test_seq])

                    # Write the updated data back to the CSV file
                    with open("wip_processed.csv", 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(rows)
                        copydb()
copydb()