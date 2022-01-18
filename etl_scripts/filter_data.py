import argparse
import re
import pandas as pd

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file", type=str)

	args = parser.parse_args()

	prolific_participant_info = pd.concat([
		pd.read_csv(f'{Path.cwd()}/data/prolific_export_60f928ceda0f48bf7a1b2dec.csv'),
		pd.read_csv(f'{Path.cwd()}/data/prolific_export_60f0287709c3374c4013c3b7.csv'),
	])
	configs = pd.read_parquet(Path.cwd() / 'data' / 'raw' / 'GANSLIDER_CONFIGS_TABLE.parquet')
	duplicated_ids = configs[configs.PROLIFIC_PID.duplicated()].PROLIFIC_PID

	prolific_participant_info.loc[(prolific_participant_info.time_taken < 1000), 'VALIDITY'] = "INVALID"
	prolific_participant_info.loc[(prolific_participant_info.time_taken < 1000), 'REASON'] = "FINISHED_TOO_QUICKLY"

	prolific_participant_info.loc[ (prolific_participant_info.status == "REJECTED")
			| (prolific_participant_info.status == "TIMED-OUT") 
			| (prolific_participant_info.status == "RETURNED"), 'VALIDITY'] = "INVALID"

	prolific_participant_info.loc[ (prolific_participant_info.status == "REJECTED")
			| (prolific_participant_info.status == "TIMED-OUT") 
			| (prolific_participant_info.status == "RETURNED"), 'REASON'] = "INVALID_SUBMISSION_STATUS"

	prolific_participant_info.loc[(prolific_participant_info.participant_id == "testid"), 'VALIDITY'] = "INVALID"
	prolific_participant_info.loc[(prolific_participant_info.participant_id == "testid"), 'REASON'] = "TEST_SUBMISSIONS"

	prolific_participant_info.loc[prolific_participant_info.participant_id.isin(duplicated_ids), 'VALIDITY'] = "INVALID"
	prolific_participant_info.loc[prolific_participant_info.participant_id.isin(duplicated_ids), 'REASON'] = "DUPLICATED_SUBMISSIONS"

	prolific_participant_info.loc[prolific_participant_info.VALIDITY != 'INVALID', "VALIDITY"] = "VALID"

	prolific_participant_info.to_csv(f'{Path.cwd()}/data/prolific_detailed_info.csv')

	exclude_ids = prolific_participant_info[prolific_participant_info.VALIDITY == "INVALID"].participant_id.drop_duplicates().values

	df = pd.read_parquet(args.file)
	columns = [col.lower() for col in df.columns]

	if 'prolific_pid' in columns:
		df = df[~df['PROLIFIC_PID'].isin(exclude_ids)]
	elif "pid" in columns:
		df = df[~df['pid'].isin(exclude_ids)]
	
	parent = Path.cwd() / 'data' / 'only_valid_pids'
	filename = Path(args.file).name

	df.to_parquet(str(parent / filename))