from dc_campaign_finance_scraper import scraper
from dc_campaign_finance_scraper import utils


class TestRecords(object):
    def test_gets_ellissa(self):

        records = scraper.records('01/01/2014', '01/01/2015', 'con')
        candidates = set(map(lambda record: utils.dict_from_dataset_row(record, records)['Candidate Name'], records))
        assert "Elissa Silverman" in candidates
