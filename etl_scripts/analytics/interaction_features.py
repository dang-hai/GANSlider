
from typing import List
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm

from pathlib import Path

def process(args):
	conf = pd.read_parquet(args.config_file)
	conf = conf[['taskid', 'slider_id', 'target_value']].drop_duplicates()

	tasks = pd.read_parquet(args.tasksfile)
	tasks = tasks[['taskid', 'start', 'end']].drop_duplicates()
	tasks = tasks[~tasks.taskid.duplicated()]

	df = pd.read_parquet(args.interactions)

	df = df.merge(tasks, on='taskid', suffixes=["", "_y"])
	df = df.merge(conf[['taskid', 'slider_id', 'target_value']].drop_duplicates(), on=['taskid', 'slider_id'])

	df.loc[df['changed_slider_id'] == "START", "changed_slider_id"] = -1
	df['changed_slider_id'] = df['changed_slider_id'].astype(int)
	df['deviation_from_target'] = df['last_edit_value'].astype(float) - df['target_value'].astype(float)
	df.sort_values(['taskid', 'start'])

	tqdm.pandas()
	features = df.groupby(['PROLIFIC_PID', 'taskid', 'num_sliders', 'slider_type', 'completed']).progress_apply(extract_features)
	features.to_parquet(args.outfile)

def zero_crossings(grp):
	grp = grp.sort_values('start')
	num_zero_crossings = grp.groupby('slider_id')['last_edit_value'].apply(lambda arr: sum(np.diff(np.sign(arr)) != 0)).sum()
	return num_zero_crossings

def slider_switches(grp):
  ids = grp[['start', 'changed_slider_id']].drop_duplicates()
  ids = ids.sort_values('start')['changed_slider_id']
  num_slider_switches = max(sum(np.diff(ids) != 0) - 1, 0)
  return num_slider_switches

def overshoots(grp):
  grp = grp.sort_values('start')
  num_overshoots = grp.groupby('slider_id')['deviation_from_target'].apply(lambda arr: sum(np.diff(np.sign(arr)) != 0)).sum()
  return num_overshoots

def num_interactions(grp):
	return grp['start'].drop_duplicates().shape[0]

def get_counts(grp):
  res = grp[['start', 'action_type']].drop_duplicates()['action_type'].value_counts()
  return res

def get_milliseconds(grp):
  trange = int(grp['end'].max() - grp['start'].min())
  trange = int(trange)
  return trange

def time_until_first_interaction(grp):
  return max(0, float(grp['start'].min()) - float(grp['start_y'].min()))

def extract_features(grp):
  out = pd.DataFrame()
  out['time_until_first_interaction'] = [time_until_first_interaction(grp)]
  out['zero_crossings'] = [zero_crossings(grp)]
  out['overshoots'] = [overshoots(grp)]
  out['slider_switches'] = [slider_switches(grp)]
  out['num_interactions'] = [num_interactions(grp)]
  return out	
	
if __name__ == "__main__":
	interactions_file = f"{Path.cwd()}/data/integrated/GANSLIDER_INTERACTIONS_CONSOLIDATED.parquet"
	config_file = f"{Path.cwd()}/data/integrated/GANSLIDER_CONFIGS_FLAT.parquet"
	tasks_file = f"{Path.cwd()}/data/integrated/GANSLIDER_TASKS_TRANSFORMED.parquet"
	outfile = f"{Path.cwd()}/data/analysis/GANSLIDER_INTERACTIONS_FEATURES.parquet"

	parser = argparse.ArgumentParser()
	parser.add_argument("--interactions",
		default=interactions_file,
		type=str,
		help=f"Path to the interactions parquet file (default: {interactions_file}")
	
	parser.add_argument("--tasksfile",
		default=tasks_file,
		type=str,
		help=f"Path to the interactions parquet file (default: {tasks_file}")
	
	parser.add_argument("--config_file",
		default=config_file,
		type=str,
		help=f"Path to the interactions parquet file (default: {tasks_file}")

	parser.add_argument("--outfile",
		default=outfile,
		type=str,
		help=f"Output path for the table (default: {outfile}")

	args = parser.parse_args()
	
	print("*"*80)
	print("Interactions File: ", args.interactions)
	print("Tasks File: ", args.tasksfile)
	print("Configs File: ", args.tasksfile)
	print("Outfile: ", args.outfile)
	print("*"*80)

	process(args)
	print(f"WRITING TABLE [{args.outfile}] FINISHED.")