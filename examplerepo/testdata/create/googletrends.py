import datetime
from typing import Any, List

import pandas as pd
from pytrends.request import TrendReq
from dateutil.relativedelta import relativedelta

from examplerepo.helperfunctions.combine_pandas_dataframes import combine_pandas_dataframes


def reformat_date(date: Any, dateformat: str) -> datetime.date:
    """
    Function to reformat a datestring into a proper datefield.

    Parameters:

    date: field containing the datestring.
    dateformat: format in which the current datestring is captured.

    """

    date = datetime.datetime.strptime(date, dateformat)
    date = date.date()

    return date


def validate_enddate(enddate: Any, dateformat: str) -> datetime.date:
    """
    Function to ensure proper encoding of the enddate of the googletrends
    timefilter. When the enddate is empty the current date is used
    as the enddate.

    Parameters:

    enddate: enddate of the googletrends timefilter.
    dateformat: format in which the enddatefield is captured.

    """

    # If end date is defined ensure the proper encoding
    if enddate is not None:
        enddate = reformat_date(enddate, dateformat)

    # If no end date is defined for the filter use today as end date
    if enddate is None:
        enddate = datetime.date.today()
    return enddate


def determine_startdate(enddate: Any, duration: int) -> datetime.date:
    """
    Function to use the enddate and duration of the googletrends
    timefilter to determine the startdate.

    Parameters:

    enddate: enddate of the googletrends timefilter.
    duration: duration of the googletrends timefilter.

    """

    startdate = enddate + relativedelta(months=-duration)

    return startdate


def create_datefilter(duration: int, enddate: Any = None, dateformat: str = "%Y-%m-%d") -> str:
    """
    Function to use the duration and the enddate to create a
    googletrends timefilter.

    Parameters:

    duration: duration of the googletrends timefilter.
    enddate: enddate of the googletrends timefilter.
    dateformat: format in which the enddatefield is captured.

    """

    # Validate enddate
    print("Duration filter Google Trends", duration)
    enddate = validate_enddate(enddate, dateformat)

    print("End Date time filter Google Trends", enddate)

    # Use enddate and filter duration to determine teh startdate
    startdate = determine_startdate(enddate, duration)
    datefilter = str(startdate) + " " + str(enddate)
    print("date filter for Google Trends: ", datefilter)
    return datefilter


def check_keywords(keywords: Any) -> str:
    """
    Function to check whether the keywords are supplied in the correct
    manner and format.

    Parameters:

    keywords: List of keywords to be collected from googletrends API.

    """

    assert keywords is not None, (
        "Supplied list of keywords is empty." "Please make sure to supply a list of keywords"
    )
    assert len(keywords) > 0, (
        "Supplied list of keywords is empty." "Please make sure to supply a list of keywords"
    )
    assert type(keywords) is list, (
        "Keywords are supplied in the wrong format." "Please make sure to supply a list of keywords"
    )

    return "Keywords checked"


def download_data(
    keywords: List,
    datefilter: str,
    countrycode: str,
    language: str,
    searchcategory: int,
    tz: int,
    timeout: tuple,
    retries: int,
    backoff_factor: float,
) -> pd.DataFrame:
    """
    Function to download the googletrends data.

    Parameters:

    keywords: List of keywords for which the google trends
      data needs to be downloaded
    datefilter: filter that indicates the timeframe
      for the google trends results
    countrycode: Two letter country abbreviation
    language:  host language for accessing Google Trends
    searchcategory: Category to narrow results
    tz: Timezone Offset (in minutes).
    timeout: timeout, in case the server is not responding in a timely manner.
    retries: number of retries total/connect/read all represented by one scalar.
    backoff_factor: backoff factor to apply between attempts after the second try.

    """

    # Configure quasi-API
    pytrends = TrendReq(hl=language, tz=tz, timeout=timeout, retries=retries, backoff_factor=backoff_factor)

    # Set the right configuration for request query Google trends.
    # Where needed make sure the request is a global one.
    if countrycode != "WORLD":
        print(keywords, searchcategory, datefilter)
        pytrends.build_payload(kw_list=keywords, cat=searchcategory, timeframe=datefilter, geo=countrycode)
    if countrycode == "WORLD":
        pytrends.build_payload(kw_list=keywords, cat=searchcategory, timeframe=datefilter)

    # Download timeseries
    googletrendsresults_load = None
    googletrendsresults_load = pytrends.interest_over_time()

    return googletrendsresults_load


def reshape_data(googletrendsresults_load: pd.DataFrame, longformat: bool, keywords: List) -> pd.DataFrame:
    """
    Function to reshape the downloaded googletrends data.

    Parameters:

    googletrendsresults_load: dataframe containing the data
       in the original format
    longformat: boolean to indicate whether the data needs
       to be reshaped into a long format

    """

    googletrends_data_final = None

    # Reset the index of dataframe
    googletrendsresults_load.reset_index(inplace=True)
    googletrendsresults_load = googletrendsresults_load.reset_index(drop=True)

    # Recast date field into string
    googletrendsresults_load["date"] = googletrendsresults_load["date"].astype(str).str[:10]

    # Reshape the dataframe into long format (if configured).
    if longformat is True:
        googletrends_data_final = pd.melt(
            googletrendsresults_load,
            id_vars=["date", "isPartial"],
            value_vars=keywords,
            var_name="keyword",
            value_name="interest",
            col_level=None,
        )

    # Keep the dataframe into wide format (if configured).
    if longformat is False:
        googletrends_data_final = googletrendsresults_load

    return googletrends_data_final


def download_reshape_data(
    datefilter: str,
    keywords: Any = None,
    longformat: bool = True,
    countrycode: str = "NL",
    language: str = "en-US",
    searchcategory: int = 71,
    tz: int = 360,
    timeout: tuple = (10, 25),
    retries: int = 2,
    backoff_factor: float = 0.1,
) -> pd.DataFrame:
    """
    Function to download and reshape the googletrends data.

    Parameters:

    datefilter: filter that indicates the timeframe
      for the google trends results
    keywords: List of keywords for which the google trends
      data needs to be downloaded
    longformat: boolean to indicate whether the data needs
       to be reshaped into a long format
    countrycode: Two letter country abbreviation
    language:  host language for accessing Google Trends
    searchcategory: Category to narrow results
    tz: Timezone Offset (in minutes).
    timeout: timeout, in case the server is not responding in a timely manner.
    retries: number of retries total/connect/read all represented by one scalar.
    backoff_factor: backoff factor to apply between attempts after the second try.

    """

    # Send error message if the list with keywords is not supplied
    check_keywords(keywords)

    print(datetime.datetime.now(), " - Start downloading Google Trends API Output")
    googletrendsresults_load = download_data(
        keywords, datefilter, countrycode, language, searchcategory, tz, timeout, retries, backoff_factor
    )

    googletrends_data_final = None

    if googletrendsresults_load is not None and len(googletrendsresults_load.index) > 0:
        googletrends_data_final = reshape_data(
            googletrendsresults_load=googletrendsresults_load, longformat=longformat, keywords=keywords
        )

    print(datetime.datetime.now(), " - Download finished")

    return googletrends_data_final


def download_data_keyword_by_keyword(keywords: List) -> pd.DataFrame:
    """
    Function to download and reshape the googletrends data. Download happens
    a single keyword at a time, to enable downloading more than 5 keywords.

    Parameters:

    keywords: List of keywords for which the google trends
      data needs to be downloaded

    """

    duration = 48
    datefilter = create_datefilter(duration=duration, enddate="2021-12-31")

    googletrends_data_final = None

    for keyword in keywords:
        googletrends_data_delta = download_reshape_data(datefilter, keywords=[keyword])
        googletrends_data_final = combine_pandas_dataframes(
            dataset_overall=googletrends_data_final, dataset_delta=googletrends_data_delta
        )

    if googletrends_data_final is not None:
        googletrends_data_final = googletrends_data_final.sort_values(by=["keyword", "date"])

    return googletrends_data_final
