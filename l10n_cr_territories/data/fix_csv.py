import csv

lista = []
with open("res.country.neighborhood.csv", "r", newline="", encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    lista = [row for row in reader]


line_count = 0
for row in lista:
    if line_count > 0:
        if str(row[3]).find(" ") > -1:
            row[3] = str(row[3]).replace(" ", "_")
    line_count += 1

with open("res.country.neighborhood.csv", mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(lista)
