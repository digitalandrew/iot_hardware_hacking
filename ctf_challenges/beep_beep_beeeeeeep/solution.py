import csv

data_points = []

morse_library = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '.----': '1', '..---': '2',
                 '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0', 'start': ''}

with open('digital.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data_points.append({'time': row['Time [s]'], 'data': row['Channel 0']})

    past_time_point = data_points[0]['time']
    past_data_point = data_points[0]['data']
    character = 'start'
    transmission = ''
    for data in data_points[1:]:
        pulse_duration = float(data['time']) - float(past_time_point)
        if past_data_point == '0' and pulse_duration > 0.015:
            transmission += morse_library[character]
            character = ''

        if past_data_point == '1' and pulse_duration > 0.145:
            character += '-'

        elif past_data_point == '1' and pulse_duration > 0.045:
            character += '.'

        past_time_point = data['time']
        past_data_point = data['data']

    print(bytes.fromhex(transmission).decode('utf-8'))
