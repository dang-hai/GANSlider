import pandas as pd
import argparse

from pathlib import Path


description_text = "This program transfrom the task status table."

def process(args):
	nasa_tlx = pd.read_parquet(args.infile)
	nasa_tlx = nasa_tlx.to_parquet(args.outfile)

if __name__ == "__main__":
	infile = f"{Path.cwd()}/data/raw/GANSLIDER_NASATLX_TABLE.parquet"
	outfile = f"{Path.cwd()}/data/transformed/GANSLIDER_NASATLX_TABLE.parquet"

	parser = argparse.ArgumentParser(description=description_text)
	parser.add_argument("--infile",
		default=infile,
		type=str,
		help=f"Path to the tasks status parquet file (default: {infile}")

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
	print(f"WRITING TABLE [{args.outfile}] FINISHED.")