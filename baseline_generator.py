import re
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
files = [item.name for item in SCRIPT_DIR.iterdir() if item.is_file()]

print("Files available to choose from:")
for file in files:
    print(f"- {file}")

log_file = input("Write the exact name of the .txt log file you want to analyze: ").strip()

number_pattern = r'\d{1,2}:\d{1,2}'
bits = []

try:
    with open(log_file, "r") as file:
        log = file.readlines()
        
       
        if log and "Event_Count" in log[0]:
            log = log[1:]
        
        for event in log:
            clean_event = event.strip()
            if not clean_event:
                continue  # Skip Empty Lines.
            
            useable_time = clean_event.split(",")
            
            
            if len(useable_time) < 2:
                continue
            
           
            if re.findall(number_pattern, useable_time[0]):
                try:
                    # making them integers.
                    bits.append(int(useable_time[1]))
                except ValueError:
                    # Skip the empty "Bits"
                    continue

    if not bits:
        print("No valid data found in the file.")
    else:
        median_bits = np.median(bits)
        mad_bits = np.median(np.abs(bits - median_bits))
        
        
        if mad_bits == 0:
            mad_bits = 1.0  # Fallback to prevent division by zero
            
        threshold = median_bits + (3 * mad_bits)
        print(f"Median: {median_bits}, MAD: {mad_bits}, Threshold: {threshold}")
        
        for bit in bits:
            if bit > threshold:
                print(f"Anomaly detected: {bit} bits exceeds the threshold of {threshold}")

except FileNotFoundError:
    print(f"File '{log_file}' not found. Please check the spelling and try again.")