import csv

def read_all_data():
    with open('userdata.csv', 'r') as file: # r = read
        data = csv.DictReader(file)
    return data

def read_row(key, value): # key = 'name', value = 'aboushy'
    # Load the CSV and filter based on the 'name' column
    with open('userdata.csv', 'r') as file: # r = read
        data = csv.DictReader(file)
        
        for row in data:
            if row[key] == value:  # Filter by name
                return row  # Output example: {'id': '1', 'name': 'aboushy', 'userid': '295558492197093380'}

def save_row(updated_row):
    # Load all data from the CSV
    updated_data = []
    with open('userdata.csv', 'r') as file:
        data = csv.DictReader(file)
        
        for row in data:
            if row['id'] == updated_row['id']:
                row = updated_row  # Modify
            updated_data.append(row)

    # Write the updated data back to the CSV
    with open('userdata.csv', 'w', newline='') as file:
        fieldnames = ['id', 'username', 'nickname', 'userid', 'totalpingcount'] # id,username,nickname,userid,totalpingcount
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()  # Write the header
        writer.writerows(updated_data)  # Write the updated rows

def add_row(new_row):
    new_row['id'] = str(get_next_id())  # Assign the next available ID
    with open('userdata.csv', 'a', newline='') as file:
        fieldnames = ['id', 'username', 'nickname', 'userid', 'totalpingcount']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header if file is empty
        if file.tell() == 0:
            writer.writeheader()

        # Write the new row
        writer.writerow(new_row)

def userid_exists(id_to_check):
    with open('userdata.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['userid'] == str(id_to_check):  # Convert ID to string for comparison
                return True
    return False

def get_next_id():
    highest_id = 0
    try:
        with open('userdata.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Update highest_id if the current row has a higher id
                if int(row['id']) > highest_id:
                    highest_id = int(row['id'])
    except FileNotFoundError:
        # If file does not exist, start with id 1
        return 1
    return highest_id + 1