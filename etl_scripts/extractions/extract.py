import boto3
import pathlib
import re
import sys
import tqdm
import math

import pandas as pd

# Load all data from dynamodb

##################################################
# Important! Expensive Run
##################################################
LOAD_ALL_TABLES = 1
LOAD_SPECIFIC_TABLE_NAME = None

default_out_dir = '../user_study_data/raw/'
output_dir = input(
    f'Specify where the tables should be stored [{default_out_dir}]: \n')

if not output_dir:
    output_dir = pathlib.Path(default_out_dir).resolve()
else:
    output_dir = pathlib.Path(output_dir).resolve()

print(output_dir)

if not pathlib.Path(output_dir).exists():
    pathlib.Path(output_dir).mkdir(parents=True)

load_all = input("Load all tables? [Y/n]")
tables = list(boto3.resource('dynamodb').tables.all())
table_names_options = "\n".join(
    [f"{idx}. {t.name}" for idx, t in enumerate(tables)])

db_client = boto3.client('dynamodb')

if re.match("y|yes", load_all.lower()):
    print(f"Loading all tables ...\n{table_names_options}")
    LOAD_ALL_TABLES = 1
else:
    LOAD_ALL_TABLES = 0
    option = input(
        f"What table should be loaded? Enter number: \n{table_names_options}")

    if not option:
        print("No table selected. Exit now.")
        sys.exit(0)

    try:
        idx = int(option)
        LOAD_SPECIFIC_TABLE_NAME = tables[idx].name
    except:
        print(f"{option} is not a valid option. Please select on of the numbers.")
        sys.exit(0)

    print(f"Selected Table {LOAD_SPECIFIC_TABLE_NAME}")

for t in boto3.resource('dynamodb').tables.all():
    res = []
    last_key = None
    name = t.name

    if not LOAD_ALL_TABLES:
        if LOAD_SPECIFIC_TABLE_NAME != name:
            print(f"Skip Table: {name}")
            continue

    print(f"Loading Table: {name}")

    description = db_client.describe_table(TableName=name)
    size_mb = description['Table']['TableSizeBytes'] / 1024 / 1024
    pbar = tqdm.tqdm(total=math.ceil(size_mb))

    scan = t.scan()
    last_key = scan.get('LastEvaluatedKey')
    res += scan['Items']

    pbar.update(1)

    while last_key:
        scan = t.scan(ExclusiveStartKey=last_key)
        res += scan['Items']
        last_key = scan.get('LastEvaluatedKey')
        pbar.set_description(f"Key: {last_key}")
        pbar.refresh()
        pbar.update(1)

    print('\n')

    pbar.close()
    df = pd.DataFrame(res)
    df.to_parquet(output_dir / f'{name}.parquet')

print(f'Finished')
