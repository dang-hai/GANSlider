import argparse
import logging
import pyspark as spark

from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
logging.getLogger('pyspark').setLevel(logging.ERROR)

description_text = "This program creates a flattened version of the configs table."

def process(args):
	spark = SparkSession.builder.getOrCreate()
	logger = spark._jvm.org.apache.log4j
	logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
	logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )


	sparkDF = spark.read.parquet(str(args.infile))
	sparkDF = sparkDF.withColumn(
				"GROUP",
				F.when(sparkDF.configs[0].slider_type == "FILMSTRIP", "A").otherwise("B")) \
			.withColumn("configs_exploded", F.explode("configs"))\
			.select(
				F.col("id").alias("config_id"),
				"PROLIFIC_PID",
				"PROLIFIC_SESSION_ID",
				"SESSION_ID",
				"PROLIFIC_STUDY_ID",
				"GROUP",
				"configs_exploded.*"
			)\
			.withColumn("num_sliders", F.udf(lambda row: len(row), IntegerType())("edits"))\
			.withColumn("tmp", F.explode("targ_edit"))\
			.withColumn("slider_id", F.col("tmp").getItem(0).cast(IntegerType()))\
			.withColumn("target_value", F.col("tmp").getItem(1))\
			.select(
				"config_id",
				"PROLIFIC_PID",
				"PROLIFIC_SESSION_ID",
				"SESSION_ID",
				"PROLIFIC_STUDY_ID",
				"GROUP",
				"taskid",
				"slider_type",
				"num_sliders",
				"seed",
				"slider_id",
				"target_value"
			)
	# sparkDF.show()
	sparkDF.write.mode("overwrite").parquet(str(args.outfile))

if __name__ == "__main__":
	infile = f"{Path.cwd()}/data/raw/GANSLIDER_CONFIGS_TABLE.parquet"
	outfile = f"{Path.cwd()}/data/transformed/GANSLIDER_CONFIGS_FLAT.parquet"

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