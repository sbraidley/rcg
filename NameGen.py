# MSc Cyber Security - DMU 2016
#
# Builds a list of randomly generated names from two wordlists
#
# Sam Braidley
# P12189936
#!/usr/bin/env python3
import random

number_to_create = 50

selected_names = []
name_counter = 0
while name_counter < number_to_create:
    text_file = open("lists/default_names.txt", "r")
    first_names = text_file.read().splitlines()
    selected_first_name = random.choice(first_names)
    surname_file = open("lists/default_surnames.txt", "r")
    surnames = surname_file.read().splitlines()
    selected_surname = random.choice(surnames)
    selected_names.append(selected_first_name + ' ' + selected_surname)
    print(selected_first_name + ' ' + selected_surname)
    name_counter += 1