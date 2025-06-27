import csv
with open("actor.csv", 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(['id', 'first_name', 'last_name'])
    csvwriter.writerow(['1', 'Mohammed', 'Taher'])
