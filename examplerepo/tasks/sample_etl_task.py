import numpy as np
import pandas as pd

from examplerepo.common import Task
from examplerepo.testdata.create.simulation import simulate_timeseries


class SampleSimulatedDataTask(Task):
    def simulate_date(self) -> pd.DataFrame:
        arparams = np.array([0.75, -0.25])
        maparams = np.array([0.65, 0.35])

        simulated_timeseries = simulate_timeseries(
            timerange=208,
            fullyear=52,
            frequencies=[1, 2],
            amplitudes=[4, 4],
            arparams=arparams,
            maparams=maparams,
            scale=0.4,
            promotion=True,
            promotion_uplift=0.5,
            promotion_frequency=5,
            seed=12345,
        )

        return simulated_timeseries

    def _write_data(self) -> None:
        db = self.conf["output"].get("database", "default")
        table = self.conf["output"]["table"]
        self.logger.info(f"Writing simulated dataset to {db}.{table}")
        _data: pd.DataFrame = self.simulate_date()
        df = self.spark.createDataFrame(_data)
        df.write.format("delta").mode("overwrite").saveAsTable(f"{db}.{table}")
        self.logger.info("Dataset successfully written")

    def launch(self) -> None:
        self.logger.info("Launching sample ETL job")
        self._write_data()
        self.logger.info("Sample ETL job finished!")


def entrypoint() -> None:  # pragma: no cover
    task = SampleSimulatedDataTask()
    task.launch()


# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == "__main__":
    entrypoint()
