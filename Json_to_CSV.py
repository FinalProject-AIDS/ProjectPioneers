#NOTE The below script will be used whenever we need to convert the Json data into CSV format for any additional usecases. 

import json
import os
import pandas as pd

def json_to_csv(json_folder_path, output_csv_path):
    # Initialize a list to hold all data records
    all_data = []

    # Loop through each file in the JSON folder(Change the logic if a folder is not made or being used)
    for json_file in os.listdir(json_folder_path):
        if json_file.endswith('.json'):
            file_path = os.path.join(json_folder_path, json_file)
            with open(file_path, 'r') as file:
                record = json.load(file)

                # Flatten data for each record
                row = {
                    "timestamp": record["timestamp"],
                    "day_of_week": record["day_of_week"],
                    "holiday": record["holiday"],
                    "occupancy_level": record["occupancy_level"],
                    "temperature": record["temperature"],
                    "time_of_day": record["time_of_day"],
                    "total_consumption": record["total_consumption"],
                    "peak_load": record["peak_load"],
                    "break_time_consumption": record["break_time_consumption"]
                }

                # Extract floor data
                for floor in record["floor_data"]:
                    row[f"floor_{floor['floor']}_fan_consumption"] = floor["fan_consumption"]
                    row[f"floor_{floor['floor']}_light_consumption"] = floor["light_consumption"]
                    row[f"floor_{floor['floor']}_total_floor_consumption"] = floor["total_floor_consumption"]

                # Extract shared equipment data
                row["computer_consumption"] = record["shared_equipment"]["computer_consumption"]
                row["projector_consumption"] = record["shared_equipment"]["projector_consumption"]

                # Append the flattened row to the data list
                all_data.append(row)

    # Convert list of records to a DataFrame
    df = pd.DataFrame(all_data)

    # Save DataFrame to a CSV file(Use any name needed here)
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully saved to {output_csv_path}")

# Please replace the below paths with the paths to your system
json_folder_path = '/path/to/your/json/folder'
output_csv_path = '/path/to/save/output.csv'
json_to_csv(json_folder_path, output_csv_path)
