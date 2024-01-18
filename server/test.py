import json, csv

def read_csv(file_path):
    patterns = []
    extra_char_list = [',', '"']
    test = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        names = csv_reader.fieldnames
        print(names)
        for row in csv_reader:
          test.append(row)
          pattern = {}
          for col in names:
            item = row[col]

            for extra_char in extra_char_list:
              item = item.replace(extra_char, '')

            pattern[col] = item
          patterns.append(pattern)

read_csv('./db.csv')

