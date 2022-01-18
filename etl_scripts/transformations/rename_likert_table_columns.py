import argparse
import logging
import pandas as pd

from pathlib import Path
logging.getLogger('pyspark').setLevel(logging.ERROR)

description_text = "This program creates a flattened version of the configs table."

def process(args):
	df = pd.read_parquet(args.infile)
	df = df.rename(columns={
		"Strongly Agree": "SA",
		"Agree": "A",
		"NEUTRAL": "N",
		"Disagree": "D",
		"Strongly Disagree": "SD",
	})
	df.to_parquet(args.outfile)

if __name__ == "__main__":
	infile = f"{Path.cwd()}/data/raw/GANSLIDER_LIKERT_TABLE.parquet"
	outfile = f"{Path.cwd()}/data/transformed/GANSLIDER_LIKERT_TABLE.parquet"

	parser = argparse.ArgumentParser(description=description_text)
	parser.add_argument("--infile",
		default=infile,
		type=str,
		help=f"Path to the configs parquet file (default: {infile}")

	parser.add_argument("--outfile",
		default=outfile,
		type=str,
		help=f"Output path for the flattened table (default: {outfile}")

	args = parser.parse_args()
	
	print("*"*80)
	print("Infile: ", args.infile)
	print("Outfile: ", args.outfile)
	print("*"*80)

	process(args)