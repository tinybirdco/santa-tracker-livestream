import csv
import click
import uuid
from datetime import datetime
from faker import Faker
import random

toy_ids = []
coal_id = ''

with open('toys.csv', 'r') as toys:
    reader = csv.reader(toys)
    for row in reader:
        if row:
            toy_id = row[0]
            name = row[1]
            if name != 'Coal':
                toy_ids.append(toy_id)
            else:
                coal_id = toy_id


@click.command()
@click.option('--rows', default=10000, help='Number of rows to generate in each file')
@click.option('--files', default=1, help="The number of files to generate")
def generate(rows, files):
    # define naughty reasons
    naughty_reasons = [
        "didn't finish homework",
        "potty mouth",
        "broke neigbor's window",
        "told a lie",
        "doesn't believe in santa",
        "stole cookies from the cookie jar",
        "pushed sister",
        "cheated on test",
        "put thumbnail on teacher's chair"
    ]
    # create Faker instance
    fake = Faker()

    for f in range(files):
        print(f'Creating file {f+1}/{files}')
        # Define the file path
        file_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f'child_list_{file_suffix}.csv'

        # Open the CSV file in write mode
        with open(file_path, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write header
            csv_writer.writerow(["child_id", "child_first_name", "child_last_name",
                                "latitude", "longitude", "status", "toy_id", "naughty_reason"])

            for x in range(rows):
                child_id = str(uuid.uuid4())
                first_name = fake.first_name()
                last_name = fake.last_name()
                latitude = round(random.uniform(-90, 90), 6)
                longitude = round(random.uniform(-180, 180), 6)
                status = "nice" if random.random() < 0.8 else "naughty"
                toy_id = random.choice(
                    toy_ids) if status == "nice" else coal_id
                naughty_reason = random.choice(
                    naughty_reasons) if status == "naughty" else ""

                csv_writer.writerow([child_id, first_name, last_name,
                                    latitude, longitude, status, toy_id, naughty_reason])


if __name__ == '__main__':
    generate()
