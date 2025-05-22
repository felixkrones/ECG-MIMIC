import zipfile
import os
import wfdb
from pathlib import Path
import datetime
import pandas as pd
from tqdm.auto import tqdm

def extract_and_open_files_in_zip(zip_file_path, extension):
    """
    extracts all headers from zip file and compiles information from them into records.pkl
    """
    ecg_records = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in tqdm(zip_ref.infolist()):
            if file_info.file_name.endswith(extension):
                # Extract the file to a temporary directory
                extract_path = file_info.file_name
                os.makedirs(os.path.dirname(extract_path), exist_ok=True)
                with open(extract_path, 'wb') as extracted_file:
                    extracted_file.write(zip_ref.read(file_info.file_name))
                
                # Open the extracted file using wfdb
                metadata = wfdb.rdheader(extract_path[:-len(extension)])
                file = Path(extract_path[:-len(extension)])
                
                tmp={}
                tmp["file_name"]=f'{file.parent}/{file.stem}'
                tmp["study_id"]=int(file.stem)
                tmp["patient_id"]=int(file.parent.parent.stem[1:])
                tmp['ecg_time']= datetime.datetime.combine(metadata.base_date,metadata.base_time)
                ecg_records.append(tmp)                     
                
                # Delete the extracted file after use
                os.remove(extract_path)
    return pd.DataFrame(ecg_records)



def extract_and_open_files(zip_file_path, extension):
    """
    Extracts all headers from zip file and compiles information from them into records.pkl.
    Adds a progress bar for directory traversal.
    """
    ecg_records = []
    all_dirs = list(os.walk(zip_file_path))
    all_dirs_len = len(all_dirs)
    print(f"Found {all_dirs_len} directories in the zip file.")

    fusion_filter_file_path = "/data/wolf6245/src/mm_study/data/f_modelling/03_model_input/data-2024-12-19-01-23-23/(3) Chronic ischaemic heart disease/y_fusion_label_not_gt.parquet"
    fusion_filter_df = pd.read_parquet(fusion_filter_file_path)
    subject_ids_to_keep = fusion_filter_df['subject_id'].astype(str).unique()

    all_dirs = [(root, dirs, files) for root, dirs, files in all_dirs if root.split('/')[-2][1:] in subject_ids_to_keep]
    print(f"Filtered directories from {all_dirs_len} to {len(all_dirs)} based on fusion filter.")

    for root, _, files in tqdm(all_dirs, desc="Processing directories"):
        for file_name in files:
            if file_name.endswith(extension):
                try:
                    extract_path = os.path.join(root, file_name)
                    metadata = wfdb.rdheader(extract_path[:-len(extension)])
                    file = Path(extract_path[:-len(extension)])
                    tmp = {}
                    tmp["file_name"] = f'{file.parent}/{file.stem}'
                    tmp["study_id"] = int(file.stem)
                    tmp["patient_id"] = int(file.parent.parent.stem[1:])
                    tmp["ecg_time"] = datetime.datetime.combine(metadata.base_date, metadata.base_time)
                    ecg_records.append(tmp)
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")

    return pd.DataFrame(ecg_records)
    
# Path to the zip file and extension
#zip_file_path = 'mimic-iv-ecg-diagnostic-electrocardiogram-matched-subset-1.0.zip'
#extension = '.hea'

# Call the function
#df=extract_and_open_files_in_zip(zip_file_path, extension)
#df.to_pickle("records.pkl")
