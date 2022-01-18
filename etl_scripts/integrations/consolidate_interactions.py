import argparse
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import numpy as np

from pyspark.sql import SparkSession
from pyspark.sql import types as T
from pyspark.sql import functions as F
from pyspark.sql.window import Window

description_text = "This program consolidates the interaction table"

def process(args):
	sess = SparkSession.builder.getOrCreate()
	df = sess.read.parquet(args.interactions)

	# transform
	df = df.withColumn('slider_id', F.col('slider_id').cast(T.IntegerType()))	
	df = df.withColumn('edit_value', F.col('edit_value').cast(T.FloatType()))
	df = df.withColumn('edits', F.struct(F.col('slider_id'), F.col('edit_value')))
	df = df.groupby('taskid', 'timestamp').agg(F.collect_list('edits').alias('edits'))
	df = df.withColumn('g1', F.array_except(F.col('edits'), F.lag('edits', 1).over(Window.partitionBy('taskid').orderBy('timestamp'))))
	df = df.withColumn('g1', F.when(F.col('g1') == F.array(), None).otherwise(F.col('g1')))
	df = df.withColumn('g1', F.last('g1', ignorenulls=True).over(Window.partitionBy('taskid').orderBy(F.col('timestamp')).rowsBetween(Window.unboundedPreceding, 0)))
	df = df.withColumn('rn', F.row_number().over(Window.partitionBy('taskid').orderBy('timestamp')))
	df = df.withColumn('g1', F.when(F.col('rn') == 1, "START").otherwise(F.col('g1').getItem(0).getField('slider_id')))
	df = df.withColumn('g1', F.last('g1', ignorenulls=True).over(Window.partitionBy('taskid').orderBy(F.col('timestamp')).rowsBetween(Window.unboundedPreceding, 0)))
	df = df.withColumn('g0', F.col('timestamp') - F.lag('timestamp', 1).over(Window.partitionBy('taskid').orderBy('timestamp')))
	df = df.withColumn('g0', F.when(F.col('g0') > 250, F.col('timestamp')).otherwise(None))
	df = df.withColumn('g0', F.when(F.col('rn') == 1, F.col('timestamp')).otherwise(F.col('g0')))
	df = df.withColumn('g0', F.last('g0', ignorenulls=True).over(Window.partitionBy('taskid').orderBy(F.col('timestamp')).rowsBetween(Window.unboundedPreceding, 0)))
	df = df.withColumn('key', F.concat(F.col('g0'), F.lit("_"), F.col('g1')))

	# df.orderBy('taskid', 'timestamp').show(n=60, truncate=False)

	# collect items
	df = df.withColumn('tmp', F.explode('edits'))
	df = df.select(
		'taskid', 'key', 'timestamp', 'tmp.*', F.col('g1').alias('changed_slider_id')
	)

	df = df.withColumn('first_edit_value', F.first('edit_value').over(Window.partitionBy('taskid', 'key', 'slider_id').orderBy('timestamp').rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)))
	df = df.withColumn('last_edit_value', F.last('edit_value').over(Window.partitionBy('taskid', 'key', 'slider_id').orderBy('timestamp').rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)))
	df = df.groupby('taskid', 'key', 'slider_id', 'last_edit_value', 'first_edit_value', 'changed_slider_id').agg(
		F.min('timestamp').alias('start'),
		F.max('timestamp').alias('end'),
		F.size(F.collect_list('edit_value')).alias('edit_value_count'),
		F.size(F.array_distinct(F.collect_list('edit_value'))).alias('distinct_edit_values'),
	)

	df = df.withColumn('action_type', F.when(F.max('distinct_edit_values').over(Window.partitionBy('taskid', 'key').rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)) <= 1, "CLICK").otherwise('DRAG'))

	# df.orderBy('taskid', 'start').show(n=60, truncate=False)

	df.write.mode('overwrite').parquet(args.outfile)

	# def transform(grp):
	# 	grp['slider_id'] = grp['slider_id'].astype(int)
	# 	grp['edit_value'] = grp['edit_value'].astype(float)

	# 	table = grp.sort_values('timestamp').pivot_table(index='timestamp', columns='slider_id', values='edit_value')

	# 	columns = []
	# 	cids = sorted(grp['slider_id'].unique())

	# 	if len(columns) == 1:
	# 		table['grp1'] = 1
	# 	else:
	# 		table['grp1'] = np.argmax((table - table.shift()) != 0)
	# 		table.iloc[0]['grp1'] = -1 
		
	# 	table['grp1'] = (table['grp1'] != table['grp1'].shift()).cumsum()
	# 	table = table.reset_index()
	# 	table['grp'] = table['timestamp']
	# 	table.loc[(table['timestamp'] - table['timestamp'].shift()) < 150, 'grp'] = None
	# 	table['grp'] = table['grp'].ffill()
	# 	table['key'] = table['grp'].astype(str) + "_" + table['grp1'].astype(str)
	# 	table = table[['timestamp', *cids, 'key']]
	# 	table['ts_diff'] = table['timestamp'] - table['timestamp'].shift()

	# 	return table.melt(id_vars=['timestamp', 'key'], value_vars=cids)

	# def collect(grp):
	# 	grp = grp.sort_values('timestamp')

	# 	newDf = pd.DataFrame(columns=['start', 'end', 'distinct_edit_values', 'first_edit_value', 'last_edit_value', 'edit_value_count'])
	# 	newDf['start'] = [grp.timestamp.min()]
	# 	newDf['end'] = [grp.timestamp.max()]
	# 	newDf['first_edit_value'] = [grp['value'].values[0]]
	# 	newDf['last_edit_value'] = [grp['value'].values[-1]]
	# 	newDf['edit_value_count'] = [grp.shape[0]]
	# 	newDf['distinct_edit_values'] = [len(grp['value'].unique())]
	# 	return newDf.set_index(['start', 'end'])

	# orig = pd.read_parquet('../data/only_valid_pids/GANSLIDER_INTERACTIONS_FLAT.parquet')

	# taskids = orig['taskid'].unique()
	# splits = np.array_split(taskids, 100)
	# np.save('../data/splits.pickle', splits)

	# for idx, s in tqdm(enumerate(splits), total=100):
	# 	tmp = orig[orig.taskid.isin(s)].groupby('taskid').apply(transform)
	# 	tmp = tmp.groupby(['taskid', 'key', 'slider_id']).apply(collect)
	# 	tmp.to_parquet(f'../data/integrated/interaction_parts/INTERACTION_PART{idx:02d}.parquet')

if __name__ == "__main__":
	interactions_file = f"{Path.cwd()}/data/only_valid_pids/GANSLIDER_INTERACTIONS_FLAT.parquet"
	configs_file = f"{Path.cwd()}/data/only_valid_pids/GANSLIDER_CONFIGS_FLAT.parquet"
	tasks_file = f"{Path.cwd()}/data/only_valid_pids/GANSLIDER_TASKS_TRANSFORMED.parquet"
	outfile = f"{Path.cwd()}/data/only_valid_pids/GANSLIDER_INTERACTIONS_CONSOLIDATED.parquet"

	parser = argparse.ArgumentParser(description=description_text)
	parser.add_argument("--interactions",
		default=interactions_file,
		type=str,
		help=f"Path to the interactions parquet file (default: {interactions_file}")

	parser.add_argument("--configs_file",
		default=configs_file,
		type=str,
		help=f"Path to the interactions parquet file (default: {interactions_file}")

	parser.add_argument("--tasks_file",
		default=tasks_file,
		type=str,
		help=f"Path to the interactions parquet file (default: {interactions_file}")

	parser.add_argument("--outfile",
		default=outfile,
		type=str,
		help=f"Output path for the flattened table (default: {outfile}")

	args = parser.parse_args()
	
	print("*"*80)
	print("Interactions File: ", args.interactions)
	print("Configs File: ", args.configs_file)
	print("Tasks File: ", args.tasks_file)
	print("Outfile: ", args.outfile)
	print("*"*80)

	process(args)
	print(f"WRITING TABLE [{args.outfile}] FINISHED.")

