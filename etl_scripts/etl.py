import argparse
import pathlib
import subprocess
import pandas as pd
from tqdm import tqdm
import logging

logging.getLogger('pyspark').setLevel(logging.ERROR)


description = "This program provides scripts for ETL."

def extract():
	dir = pathlib.Path(__file__).parent / "extractions"
	
	for file in dir.iterdir():
		if file.suffix.lower() == ".py":
			subprocess.run(["python", file])

def transform():
	dir = pathlib.Path(__file__).parent / "transformations"
	
	for file in dir.iterdir():
		if file.suffix.lower() == ".py":
			subprocess.run(["python", file])

def filter():
	for file in tqdm((pathlib.Path.cwd() / 'data' / 'transformed').iterdir()):
		if file.suffix.lower() == ".parquet":
			subprocess.run(["python", f"{pathlib.Path(__file__).parent}/filter_data.py", file])

def integrate():
	dir = pathlib.Path(__file__).parent / "integrations"
	
	for file in dir.iterdir():
		if file.suffix.lower() == ".py":
			subprocess.run(["python", file])

def analyse():
	dir = pathlib.Path(__file__).parent / "analytics"
	
	for file in dir.iterdir():
		if file.suffix.lower() == ".py":
			subprocess.run(["python", file])

def main():
	parser = argparse.ArgumentParser(description=description)
	
	parser.add_argument("--extract", action='store_true', help="Extracts data from aws dynamodb.")
	parser.add_argument("--filter", action='store_true', help="Filters invalid data")
	parser.add_argument("--transform", action='store_true', help="Transform tables to use for analytics.")
	parser.add_argument("--integrate", action='store_true', help="Integrates multiple tables.")
	parser.add_argument("--analyse", action='store_true', help="Creates analysis tables.")

	args = parser.parse_args()

	if args.extract:
		extract()
	elif args.filter:
		filter()
	elif args.transform:
		transform()
	elif args.integrate:
		integrate()
	elif args.analyse:
		analyse()

if __name__ == "__main__":
	main()