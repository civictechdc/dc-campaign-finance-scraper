from dc_campaign_finance_scraper import scraper


class TestRecords(object):
    def test_gets_ellissa(self):

        records = scraper.records('01/01/2014', '01/01/2015', 'con')
        candidates = set(map(lambda record: record['Candidate Name'], records.dict))
        assert "Elissa Silverman" in candidates


class TestRecordsWithOfficeAndElectionYear(object):
    def test_gets_ellissa(self):
        records = scraper.records_with_office_and_election_year('01/01/2014', '01/01/2015', 'con')
        candidates = set(map(lambda record: record['Candidate Name'], records.dict))
        assert "Elissa Silverman" in candidates
