import argparse
import logging
import pyspark as spark

from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import window as W
from pyspark.sql.types import IntegerType
logging.getLogger('pyspark').setLevel(logging.ERROR)

description_text = "This program creates a table containing the avg duration of each task"


def process(args):
    sess = SparkSession.builder.getOrCreate()
    updates = sess.read.parquet(args.infile)\
        .sort(['taskid', 'timestamp', 'idx'])

    updates_true = updates.select("taskid", "idx", F.col("timestamp").alias(
        "timestamp_start"), "isUpdating").where(F.col("isUpdating") == "true")\
		.drop("isUpdating")
    updates_false = updates.select("taskid", "idx", F.col("timestamp").alias(
        "timestamp_end"), "isUpdating").where(F.col("isUpdating") == "false")\
		.drop("isUpdating")


    updates = updates_true.join(updates_false,
                                on=['taskid', 'idx'],
                                how="outer")\
        .withColumn("time_diff_sec", ((updates_false.timestamp_end - updates_true.timestamp_start)/1000.0).cast(IntegerType()))\
        .where(F.col('time_diff_sec') > 0)\
        .withColumn("row", F.row_number().over(W.Window.partitionBy(['taskid', 'idx']).orderBy(["timestamp_start", "timestamp_end"])))\
        .where(F.col("row") == 1)\
		.drop("row")

    updates.show()
    updates.write.mode('overwrite').parquet(args.outfile)


if __name__ == "__main__":
    infile = f"{Path.cwd()}/data/raw/GANSLIDER_FILMSTRIP_UPDATE_TABLE.parquet"
    outfile = f"{Path.cwd()}/data/transformed/GANSLIDER_TASK_WAITING_TIME.parquet"

    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument("--infile",
                        default=infile,
                        type=str,
                        help=f"Path to the parquet file (default: {infile}")

    parser.add_argument("--outfile",
                        default=outfile,
                        type=str,
                        help=f"Output path for the output table (default: {outfile}")

    args = parser.parse_args()

    print("*"*80)
    print("Infile: ", args.infile)
    print("Outfile: ", args.outfile)
    print("*"*80)

    process(args)
    print(f"WRITING TABLE [{args.outfile}] FINISHED.")
