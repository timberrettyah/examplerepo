"""
Unit tests for data simulation function
"""
import numpy as np
import statsmodels.tsa.api as sm

from examplerepo.testdata.create.simulation import simulate_promotion, simulate_timeseries


class TestDataSimulation:
    def test_format_data(self, spark):

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

        assert [str(item) for item in simulated_timeseries.columns] == [
            "sales_total",
            "sales_arma",
            "promotion_timing",
        ]
        assert [str(item) for item in simulated_timeseries.dtypes] == ["float32", "float32", "float32"]
        assert len(simulated_timeseries.index) > 0

    def test_promotion_function(self, spark):
        sales = [1 for i in range(0, 100)]

        (sales_total, promotion_timing) = simulate_promotion(
            timerange=100, fullyear=100, sales_total=sales, promotion_uplift_perc=0.5, promotion_frequency=10
        )

        relative_frequency = round(sum(promotion_timing) / len(promotion_timing), 4)
        average_sales = round(sum(sales_total) / len(sales_total), 4)

        assert relative_frequency < 0.20
        assert average_sales < 1.20

    def test_arma_process(self, spark):

        arparams = np.array([0.75, -0.25])
        maparams = np.array([0.65, 0.35])

        fullyear = 52

        simulated_timeseries = simulate_timeseries(
            timerange=208,
            fullyear=fullyear,
            frequencies=[1, 2],
            amplitudes=[4, 4],
            arparams=arparams,
            maparams=maparams,
            scale=1,
            seed=12345,
        )

        # calculate sales_delta
        sales_delta = []

        for i in range(fullyear, len(simulated_timeseries.index)):
            sales_delta.append(
                simulated_timeseries.iloc[i]["sales_total"] - simulated_timeseries.iloc[i - 52]["sales_total"]
            )

        # Test arma parameters for delta
        model = sm.arima.ARIMA(endog=sales_delta, order=(2, 0, 2)).fit()
        ar_ma_params = [round(value, 7) for value in model.params[1:5]]
        print(ar_ma_params)

        assert ar_ma_params == [0.7150908, -0.2293926, 0.6903164, 0.4493204]
