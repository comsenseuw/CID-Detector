import os
import time

folder_path = '//bthsdv004.infineon.com/PTE_Project/AUTOMATION/000.AUTO_EXTRACTION/BAKE_IN_LOT'
extracted_path = '//bthsdv004.infineon.com/PTE_Project/AUTOMATION/000.AUTO_EXTRACTION/BAKE_IN_LOT/EBS_LOT_LOG'
current_time = time.time()

for file_name in os.listdir(folder_path):
    if file_name.startswith('BAKEIN_LOT_MVIN'):
        file_path = os.path.join(folder_path, file_name)
        file_modified_time = os.path.getmtime(file_path)
        time_difference = current_time - file_modified_time
        time_difference_days = time_difference / (24 * 60 * 60)
        if time_difference_days > 7:
            os.remove(file_path)
            print(file_path+" Completed Cleaning")

for file_extracted in os.listdir(extracted_path):
    file_ebs = os.path.join(extracted_path, file_extracted)
    file_modified_time = os.path.getmtime(file_ebs)
    time_difference = current_time - file_modified_time
    time_difference_days = time_difference / (24 * 60 * 60)
    if time_difference_days > 30:
        os.remove(file_ebs)
        print(file_ebs+" Completed Cleaning")