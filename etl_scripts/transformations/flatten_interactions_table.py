import argparse
import logging

from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
logging.getLogger('pyspark').setLevel(logging.ERROR)

description_text = "This program creates a flattened version of the configs table."

def process(args):
    sess = SparkSession.builder.getOrCreate()
    logger = sess._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

    sess.read.parquet(str(args.infile))\
        .withColumn("edits_exploded", F.explode("edits")) \
        .select(
        F.col("id").alias("interaction_id"),
        "taskid",
        'timestamp',
        "status",
        "edits_exploded.*"
        )\
        .withColumnRenamed('id', 'slider_id')\
        .withColumnRenamed('value', 'edit_value')\
        .write.mode('overwrite').parquet(str(args.outfile))

    print(f"WRITING FILE [{args.outfile}] FINISHED.")

if __name__ == "__main__":
    infile = f"{Path.cwd()}/data/raw/GANSLIDER_INTERACTIONS_TABLE.parquet"
    outfile = f"{Path.cwd()}/data/transformed/GANSLIDER_INTERACTIONS_FLAT.parquet"

    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument("--infile",
                        default=infile,
                        type=Path,
                        help=f"Path to the configs parquet file (default: {infile}")

    parser.add_argument("--outfile",
                        default=outfile,
                        type=Path,
                        help=f"Output path for the flattened table (default: {outfile}")

    args = parser.parse_args()

    print("*"*80)
    print("Infile: ", args.infile)
    print("Outfile: ", args.outfile)
    print("*"*80)

    process(args)

