import argparse
import sys
import logging
import pyspark as spark

from pathlib import Path

import pandas as pd

from tqdm import tqdm 

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql import Window

logging.getLogger('pyspark').setLevel(logging.ERROR)

description_text = "This program consolidates the interaction table"

def process(args):
	conf = pd.read_parquet(args.configs_file)
	conf = conf[['PROLIFIC_PID', 'taskid', 'num_sliders', 'slider_type', 'GROUP']].drop_duplicates()

	tasks = pd.read_parquet(args.tasks_file)
	tasks = tasks[['taskid', 'completed']].drop_duplicates()
	tasks = tasks[~tasks.taskid.duplicated()]

	for fn in tqdm(Path(f'{Path.cwd()}/data/only_valid_pids/').iterdir()):
		if fn.suffix == '.parquet':
			infile = pd.read_parquet(fn)
			filename = Path(fn).name
			if 'taskid' in infile.columns:
				merged = None
				if "CONFIG" in filename:
					merged = infile.merge(tasks, on='taskid')
				elif "TASK" in filename:
					merged = infile.merge(conf, on='taskid')
				else:
					merged = infile.merge(conf, on='taskid')
					merged = merged.merge(tasks, on='taskid')
				
				merged.to_parquet(f'{Path.cwd()}/data/integrated/{filename}')

if __name__ == "__main__":
	configs_file = f"{Path.cwd()}/data/only_valid_pids/GANSLIDER_CONFIGS_FLAT.parquet"
	tasks_file = f"{Path.cwd()}/data/only_valid_pids/GANSLIDER_TASKS_TRANSFORMED.parquet"

	parser = argparse.ArgumentParser(description=description_text)

	parser.add_argument("--configs_file",
		default=configs_file,
		type=str)

	parser.add_argument("--tasks_file",
		default=tasks_file,
		type=str)

	args = parser.parse_args()
	
	print("*"*80)
	print("Configs File: ", args.configs_file)
	print("Tasks File: ", args.tasks_file)
	print("*"*80)

	process(args)
