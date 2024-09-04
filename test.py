# Define the string to be written
my_string = "ssssss"

# Open a file in write mode ('w')
with open('targetUser.txt', 'w') as file:
    file.write(my_string)