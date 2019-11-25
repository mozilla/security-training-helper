import csv
import sys
import argparse
import logging
import time
from pathlib import Path

DATA_FOLDER = Path("../data/")
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def read_csv(file):
    # Read CSV file and return a list of contents as OrderedDict
    csv_reader = csv.DictReader(file)
    contents = []
    for odict in csv_reader:
        contents.append(odict)
    return contents

def add_missing_columns(departures):
    for item in departures:
        item.update({'New Hire': 'N'})
        item.update({'Archive': 'ARCHIVE'})
    return departures

def add_new_hire_column(active, new):
    temp_list = []
    for item in active:
        email = item['Email Address']
        item.update({'New Hire': 'N'})
        for new_hire in new:
            if email == new_hire['Email Address']:
                item.update({'New Hire': 'Y'})
        temp_list.append(item)
    return temp_list

def combine(full, departures):
    combined = full + departures
    return combined

def remove_duplicates(combined, departures):
    final = combined.copy()
    for item in final:
        for departed in departures:
            if 'Archive' in item.keys():
                if item['Email Address'] == departed['Email Address'] and item['Archive'] == '':
                    # This means we have a duplicate item
                    combined.remove(item)
            else:
                item.update({'Archive': ''})
    return combined

def write_csv(contents, output):
    field_names = [
            "First Name",
            "Last Name",
            "Email Address",
            "Cost Center",
            "Hire Date",
            "Employee Type",
            "New Hire",
            "Archive"
    ]
    writer = csv.DictWriter(output, fieldnames=field_names)
    writer.writeheader()
    for item in contents:
        writer.writerow(item)

def main(file1=None, file2=None, file3=None):
    # We would like to ensure that output file is always
    # "../data" directory to prevent accidental leakage
    if args.outfile:
        output_name = args.outfile.name
        if not Path(output_name).is_absolute():
            file_name = output_name.split("/")[-1]
            output_fd = open(DATA_FOLDER.resolve() / file_name, 'w', encoding='utf-8-sig')
        else:
            # Remove the leading slash
            file_path = str(Path(output_name).parent).lstrip("/")
            file_name = output_name.split("/")[-1]
            if not Path(file_path).exists():
                Path(DATA_FOLDER.resolve() / file_path).mkdir(parents=True, exist_ok=True)
            output_fd = open(DATA_FOLDER.resolve() / file_path / file_name, 'w', encoding='utf-8-sig')
        print(output_fd.name)
    else:
        output_fd = sys.stdout

    logging.info("Reading CSV files...")
    active_employees = read_csv(file1)
    new_hires = read_csv(file2)
    departures = read_csv(file3)
    time.sleep(2)

    # STEP 1: Compare/combine active employees vs. new hires
    logging.info("Adding missing columns to active employees...")
    temp_active_employees = add_new_hire_column(active_employees, new_hires)
    time.sleep(1)
    # STEP 2: Prepare departures list (add the missing columns)
    logging.info("Adding missing columns to departed employees...")
    temp_departures = add_missing_columns(departures)
    time.sleep(1)
    # STEP 3: Compare/combine active employees with departured ones
    logging.info("Collating all data into a single data set...")
    combined_list = combine(temp_active_employees, temp_departures)
    time.sleep(1)
    # STEP 4: Prepare the final list with all additional columns
    logging.info("Removing duplicates and finalising the data set...")
    final_list = remove_duplicates(combined_list,temp_departures)
    time.sleep(1)
    # STEP 5: Write the contents to a new CSV file.
    logging.info("Outputting the final data set...")
    write_csv(final_list, output_fd)
    time.sleep(1)
    logging.info("All done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Optional argument
    parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w', encoding='utf-8-sig'))
    required_arg_group = parser.add_argument_group('required arguments')
    required_arg_group.add_argument('-a', '--all-employees', nargs=1, type=argparse.FileType('r', encoding='utf-8-sig'), required=True)
    required_arg_group.add_argument('-n', '--new-hires', nargs=1, type=argparse.FileType('r', encoding='utf-8-sig'), required=True)
    required_arg_group.add_argument('-t', '--terminated', nargs=1, type=argparse.FileType('r', encoding='utf-8-sig'), required=True)

    args = parser.parse_args()
    main(*args.all_employees, *args.new_hires, *args.terminated)
