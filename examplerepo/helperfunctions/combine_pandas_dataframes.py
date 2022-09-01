import pandas as pd


def combine_pandas_dataframes(
    dataset_overall: pd.DataFrame,
    dataset_delta: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to combine multiple dataframes into one final dataframe for repetitive tasks.

    Parameters:

    pdf_overall: The dataframe that contains the final dataset.
    pdf_delta: the dataframe that contains the data that needs to be appended.

    """

    if dataset_overall is not None:
        dataset_overall = pd.concat([dataset_overall, dataset_delta])

    if dataset_overall is None:
        dataset_overall = dataset_delta

    return dataset_overall
