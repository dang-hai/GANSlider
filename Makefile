# ETL scripts

extract-data:
	python etl_scripts/extractions/extract.py

preprocess:
	python etl_scripts/etl.py --transform
	python etl_scripts/etl.py --filter
	python etl_scripts/etl.py --integrate

analytics:
	python etl_scripts/etl.py --analyse