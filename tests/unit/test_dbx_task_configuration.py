import logging
from pathlib import Path

import mlflow

from pyspark.sql import SparkSession

from examplerepo.tasks.sample_ml_task import SampleModelTask
from examplerepo.tasks.sample_etl_task import SampleSimulatedDataTask


def test_jobs(spark: SparkSession, tmp_path: Path):
    logging.info("Testing the ETL task")
    common_config = {"database": "default", "table": "timeseries"}
    test_etl_config = {"output": common_config}
    etl_job = SampleSimulatedDataTask(spark, test_etl_config)
    etl_job.launch()
    table_name = f"{test_etl_config['output']['database']}.{test_etl_config['output']['table']}"
    _count = spark.table(table_name).count()
    assert _count > 0
    logging.info("Testing the ETL task - done")

    logging.info("Testing the ML task")
    test_ml_config = {"input": common_config, "experiment": "/Shared/forecastingtest/sample_experiment"}
    ml_job = SampleModelTask(spark, test_ml_config)
    ml_job.launch()
    experiment = mlflow.get_experiment_by_name(test_ml_config["experiment"])
    assert experiment is not None
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
    assert runs.empty is False
    logging.info("Testing the ML task - done")
