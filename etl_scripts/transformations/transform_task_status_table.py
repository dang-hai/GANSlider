import pandas as pd
import numpy as np
from pathlib import Path
import argparse

description_text = "This program transfrom the task status table."

def process(args):
	tasks = pd.read_parquet(args.infile)
	start = tasks[tasks.status == 'START'][['psess_id', 'pstudy_id', 'taskid', 'sess_id', 'pid', 'timestamp']]
	finish = tasks[tasks.status == 'FINISH'][['psess_id', 'pstudy_id', 'taskid', 'sess_id', 'pid', 'extra', 'edits', 'timestamp']]
	merged = start.merge(finish, on=['psess_id', 'pstudy_id', 'taskid', 'sess_id', 'pid'],  how="outer")
	merged = merged.explode('edits')
	merged['slider_id'] = merged.edits.apply(lambda rec: rec['id'] if not isinstance(rec, float) else rec)
	merged['edit_value'] = merged.edits.apply(lambda rec: rec['value'] if not isinstance(rec, float) else rec)
	merged['duration_ms'] = merged['timestamp_y'] - merged['timestamp_x']
	merged = merged.rename(columns={'timestamp_x': 'start', 'timestamp_y': 'end', 'extra': 'completed'})
	merged = merged[['taskid', 'pid', 'psess_id', 'pstudy_id', 'sess_id', 'completed', 'start', 'end', 'duration_ms', 'slider_id', 'edit_value']]
	merged.to_parquet(args.outfile)

if __name__ == "__main__":
	infile = f"{Path.cwd()}/data/raw/GANSLIDER_TASKS_TABLE.parquet"
	outfile = f"{Path.cwd()}/data/transformed/GANSLIDER_TASKS_TRANSFORMED.parquet"

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

