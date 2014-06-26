from __future__ import unicode_literals
from __future__ import print_function

import requests
import requests.adapters
import requests_cache.core
import json
import csv
import functools
import collections

from bs4 import BeautifulSoup


def retry_session(max_retries=20):
    s = requests_cache.core.CachedSession(
        expire_after=60 * 60 * 6,
        allowable_methods=['GET', 'POST']
    )
    s = requests.Session()
    s.mount('http', requests.adapters.HTTPAdapter(max_retries=max_retries))
    return s


#@functools.lru_cache()
def records_csv(from_date, to_date, report_type):
    options = {
        "cboFilerType": "PCC",
        "txtFromDate": from_date,
        "txtToDate": to_date,
        "optReportOption": report_type,
        "cboSort1": "agyname, ",
        "filing_year": "",
        "optFormat": "CSV",
    }
    get_some_cookies_from_url = "http://www.ocf.dc.gov/serv/download.asp"

    s = retry_session()
    s.post(get_some_cookies_from_url, options).raise_for_status()

    download_url = 'http://www.ocf.dc.gov/serv/download_conexp.asp'
    r = s.post(download_url, options)
    r.raise_for_status()

    if 'Your Session is expired. Please try again' in r.text:
        raise(Exception, 'Cant get records data. Cookie isnt working. idk')

    return r.text


#@functools.lru_cache(maxsize=2**9)
def election_of_committee(committee, record_year):
    '''
    Returns the ofifce and election year, for a certain committee name.
    It starts by looking at all the elections in that year, to see if
    that committee name was running for anything.
    '''
    for possible_office in races(record_year):
        if committee in committees(possible_office, record_year):
            return possible_office, record_year
    return election_of_committee(committee, record_year + 1)


#@functools.lru_cache()
def records_with_offices_and_year(from_date, to_date, report_type):
    records = csv.DictReader(records_csv(from_date, to_date, report_type).splitlines())

    def year_from_date(date):
        return int(date.split('/')[-1])

    for record in records:
        print(record)
        try:
            office, election_year = election_of_committee(
                record["Committee Name"],
                year_from_date(record["Date of Receipt"])
            )
        except TypeError:
            office, election_year = None, None

        record["Office"] = office
        record["Year"] = election_year
    return records


#@functools.lru_cache()
def records_for_race(office, year, report_type):
    '''
    All the records for races happening in a year
    '''
    all_records = records_with_offices_and_year('01/01/1990', '01/01/9999', report_type)
    return filter(
        lambda record: record['Office'] == office and record['Year'] == year,
        all_records
    )


#@functools.lru_cache()
def available_years():
    js_with_years_in_it = 'http://geospatial.dcgis.dc.gov/ocf/js/process.js'
    s = retry_session()
    r = s.get(js_with_years_in_it)

    years_line = r.text.splitlines()[3]
    # This line looks like like:
    # var m_Interface_Control = [{ "year": "2010", "defaultoffice": "Mayor", "showparty": "yes", "defaultparty": "Democratic" }, { "year": "2011", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2012", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2013", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}, { "year": "2014", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}];
    years_json_text = years_line.lstrip('var m_Interface_Control =').rstrip(';')
    # Now we have just the json:
    # [{ "year": "2010", "defaultoffice": "Mayor", "showparty": "yes", "defaultparty": "Democratic" }, { "year": "2011", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2012", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2013", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}, { "year": "2014", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}]
    years_json = json.loads(years_json_text)

    # then we just want to return a list of the years
    return [int(year['year']) for year in years_json]


#@functools.lru_cache()
def offices():
    html_with_offices_in_it = 'http://geospatial.dcgis.dc.gov/ocf/'
    s = retry_session()
    r = s.get(html_with_offices_in_it)
    soup = BeautifulSoup(r.text)

    office_option_elements = soup.find(id='SearchByOffices')('option')
    # sort them by their form value, so they look all nice and ordered
    office_option_elements.sort(key=lambda e: int(e['value']))

    return [e.text for e in office_option_elements]


#@functools.lru_cache()
def races(year):
    for office in offices():
        if committees(office, year):
            yield office


#@functools.lru_cache()
def _office_version(office):
    html_with_offices_in_it = 'http://geospatial.dcgis.dc.gov/ocf/'
    s = retry_session()
    r = s.get(html_with_offices_in_it)
    soup = BeautifulSoup(r.text)

    return soup.find('option', text=office)['value']


#@functools.lru_cache()
def commitees_in_multiple_years():
    '''
    Checks to see if any committee name runs in elections in multiple years.
    '''
    years_offices_committees = collections.defaultdict(lambda: collections.defaultdict(list))
    for year in available_years():
        for office in races(year):
            for committee in committees(office, year):

                for year_test, office_test_dict in years_offices_committees.items():
                    for office_test, committee_test in office_test_dict.items():
                        if committee in committee_test:
                            print(("commitee '{}' ran twice, in '{}' for '{}' and "
                                   "in '{}' running for '{}'").format(
                                committee, year, office, year_test, office_test))

                years_offices_committees[year][office].append(committee)


#@functools.lru_cache(maxsize=2**9)
def committees(office, year):
    url = 'http://geospatial.dcgis.dc.gov/ocf/getData.aspx'
    payload = {
        'of': office,
        'ofv': _office_version(office),
        'yr': year,
    }
    s = retry_session()
    r = s.get(url, params=payload, timeout=99**99)
    soup = BeautifulSoup(r.text)

    try:
        return [tr.td.text for tr in soup.table.find_all('tr')][:-1]
    except AttributeError:
        return []
