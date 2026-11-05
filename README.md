# MAD Baseline Anomaly Detector

A Python CLI tool that reads timestamped event data from a log file, establishes
a statistical baseline using the **Median** and **Median Absolute Deviation
(MAD)**, and flags values that exceed the expected range.

## Features

- Parses comma-separated log lines in the form `timestamp,value`
- Skips header rows (`Event_Count`), blank lines, and malformed or non-numeric entries
- Computes a robust baseline: `threshold = median + 3 × MAD`
- Reports every value that exceeds the threshold
- Safe fallback when MAD = 0 (flat data) to avoid a zero-width threshold
- Interactive file selection and graceful error handling

## How It Works

1. Reads the file line by line and splits on commas.
2. Keeps only rows where the first field looks like a time (`HH:MM`).
3. Converts the second field to an integer.
4. Computes the median and MAD of all valid values.
5. Prints the baseline statistics and every value above `median + 3 × MAD`.

## Requirements

- Python 3.8+
- numpy

```bash
pip install -r requirements.txt
```

## Usage

```bash
python baseline_generator.py
```

Enter the exact filename of your log when prompted.

## Input Format

```
Time,Event_Count
10:00,120
10:01,118
10:02,125
10:03,940
```

Rows whose first column doesn't contain an `H:MM`/`HH:MM` pattern or whose
second column isn't an integer are skipped.

## Example Output

```
Median: 121.5, MAD: 3.0, Threshold: 130.5
Anomaly detected: 940 bits exceeds the threshold of 130.5
```

(Replace with your own real output.)

## Why Median/MAD?

Mean and standard deviation are distorted by the very anomalies you're trying
to find. The median and MAD stay stable in the presence of outliers, which
makes them a better fit for baselining noisy security and network data.

## Limitations

- Static baseline: no rolling or time-of-day windows
- Detects only upper-bound anomalies (drops are ignored)
- MAD is unscaled (no 1.4826 consistency factor), so `3 × MAD` is more
  sensitive than a 3σ rule
- The MAD = 0 fallback of `1.0` is a fixed assumption

## Roadmap

- [ ] Save the computed baseline to a JSON file for reuse
- [ ] Rolling-window and per-hour baselines
- [ ] Detect low-side anomalies
- [ ] `argparse` CLI and configurable multiplier
- [ ] Unit tests

## License

MIT (see `LICENSE`)

### Sorucr Code :
``` Python
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

```
