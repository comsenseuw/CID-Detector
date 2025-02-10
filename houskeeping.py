import os
import time

folder_path = '//servername/AUTOMATION/FOLDER'
extracted_path = '//servername/AUTOMATION/FOLDER/SUBFOLDER'
current_time = time.time()

for file_name in os.listdir(folder_path):
    if file_name.startswith('filename'):
        file_path = os.path.join(folder_path, file_name)
        file_modified_time = os.path.getmtime(file_path)
        time_difference = current_time - file_modified_time
        time_difference_days = time_difference / (24 * 60 * 60)
        if time_difference_days > 7:
            os.remove(file_path)
            print(file_path+" Housekeeping has completed")

for file_extracted in os.listdir(extracted_path):
    file_db = os.path.join(extracted_path, file_extracted)
    file_modified_time = os.path.getmtime(file_db)
    time_difference = current_time - file_modified_time
    time_difference_days = time_difference / (24 * 60 * 60)
    if time_difference_days > 30:
        os.remove(file_db)
        print(file_db+" Housekeeping has completed")