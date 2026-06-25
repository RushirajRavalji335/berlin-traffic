import os
import requests
import concurrent.futures
import gzip
import pandas as pd

# Create directories
os.makedirs('./data/gz/', exist_ok=True)
os.makedirs('./data/csv/', exist_ok=True)

years = list(range(15,26))
mq_paths = [
        "Messquerschnitte",
        "Messquerschnitt",
        "alte_qualitaetssicherung/Messquerschnitte",
        "alte_qualitaetssicherung/Messquerschnitt%20(fahrtrichtungsbezogen)",
        "Messquerschnitt%20(fahrtrichtungsbezogen)",
        ]
months = list(range(1,13))


def unzip_file(filename):
    with open(f"./data/gz/{filename}", "rb") as f_in:
        with gzip.open(f_in) as f:
            data = pd.read_csv(f, delimiter=";")
    data.to_csv(f"./data/csv/{filename[:-3]}", index=None)

def download_file(year, month):
    filename = f"mq_hr_20{year}_{month:02}.csv.gz"
    for mq_path in mq_paths:
        url = f"https://mdhopendata.blob.core.windows.net/verkehrsdetektion/20{year}/{mq_path}/{filename}"

        response = requests.get(url)
        if response.status_code == 200:
            with open(f"./data/gz/{filename}", 'wb') as f:
                f.write(response.content)
            print("Found: ", filename)
            unzip_file(filename)
            return
    print("did not find: ", filename)

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(download_file, year, month): (year, month) 
               for year in years for month in months}
    for future in concurrent.futures.as_completed(futures):
        year, month = futures[future]
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")

