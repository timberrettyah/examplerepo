"""
Unit tests for download functionality for Google Trends
"""

from examplerepo.testdata.create.googletrends import download_data_keyword_by_keyword


class TestDownloadGoogletrends:
    def test_format_data(self, spark):
        googletrends_data_final = download_data_keyword_by_keyword(["aardbeien", "peer", "appel", "banaan"])

        print(googletrends_data_final.columns)

        assert [str(item) for item in googletrends_data_final.columns] == [
            "date",
            "isPartial",
            "keyword",
            "interest",
        ]
        assert [str(item) for item in googletrends_data_final.dtypes] == ["object", "bool", "object", "int64"]
        assert len(googletrends_data_final.index) > 0
