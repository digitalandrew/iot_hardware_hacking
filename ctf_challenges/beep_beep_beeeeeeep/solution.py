# Solution for microCTF Challenge "Alien Tranmission!?!"

import csv

# Dictionary to translate morse code symbols to hex characters, only A-F are required for letters as we know it's hex.
morse_library = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    "-----": "0",
    "start": "",
}

# Blank array to add the data points from the CSV file into
data_points = []

# Open CSV file and write the data points into an array for easier access
with open("digital.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data_points.append({"time": row["Time [s]"], "data": row["Channel 0"]})


# Variables for storing the last data point initialized with the first index of the csv
past_time_point = data_points[0]["time"]
past_data_point = data_points[0]["data"]

# Variable to store the current symbol being parsed and the entire transmission
character = "start"
transmission = ""

# Loop over each data point that was read from the CSV starting at index 1
for data in data_points[1:]:
    # Calculate the pulse duration
    pulse_duration = float(data["time"]) - float(past_time_point)

    # If the pulse is a 0 and the pulse duration is greater than 0.145 then this indicates a space between symbols, first the current symbol is appeneded to the transmission using the dictionary and then it's cleared to start the next symbol
    if past_data_point == "0" and pulse_duration > 0.145:
        transmission += morse_library[character]
        character = ""
    # If the pulse is a 1 and the pulse duration is greater than 0.145 then a dash is added to the current symbol
    if past_data_point == "1" and pulse_duration > 0.145:
        character += "-"
    # Else If the pulse is a 1 and the pulse duration is greater than 0.045 then a dash is added to the current symbol
    elif past_data_point == "1" and pulse_duration > 0.045:
        character += "."
    # Note that we can safely ignore the shorter pauses between each morse dash or dot and just move on to the next data point. This method allows for maximum variation in those pauses, as long as they are less than 0.145 the message can still be parsed.

    # After parsing out the pulse to space, dash or dot we then move the current data and time into the past data and time variables
    past_time_point = data["time"]
    past_data_point = data["data"]

# As the message is hex encoded it can then be decoded before being printed.
print(bytes.fromhex(transmission).decode("utf-8"))
