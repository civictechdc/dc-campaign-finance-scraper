import requests
import json
import csv
import collections
import functools
import logging

from bs4 import BeautifulSoup

from . import utils


class NoData(Exception):
    pass


logger = logging.getLogger(__name__)


@utils.log_function
def _records_cookies(options):
    r = requests.post("http://www.ocf.dc.gov/serv/download.asp", options)
    r.raise_for_status()
    return r.cookies


@utils.log_function
def records_csv(from_date, to_date, report_type):
    # we should sort these so that they are sent in the same order every
    # time and cached correctly
    options = tuple(sorted({
        "cboFilerType": "PCC",
        "txtFromDate": from_date,
        "txtToDate": to_date,
        "optReportOption": report_type,
        "cboSort1": "agyname, ",
        "filing_year": "",
        "optFormat": "CSV",
    }.items()))

    download_url = 'http://www.ocf.dc.gov/serv/download_conexp.asp'
    r = requests.post(download_url, options, cookies=_records_cookies(options))
    r.raise_for_status()

    if 'Your Session is expired. Please try again' in r.text:
        raise(Exception, 'Cant get records data. Cookie isnt working. Says session expire')

    return r.text


@utils.log_function
@functools.lru_cache(maxsize=2**9)
def election_of_committee(committee, record_year):
    '''
    Returns the ofifce and election year, for a certain committee name.
    It starts by looking at all the elections in that year, to see if
    that committee name was running for anything.
    '''
    try:
        for possible_office in races(record_year):
            if committee in committees(possible_office, record_year):
                return possible_office, record_year
    except NoData:
        return None, None
    return election_of_committee(committee, record_year + 1)


@utils.log_function
def records_for_race(office, election_year, report_type):
    '''
    All the records for races happening in a year.
    It needs to get all of the records first, because no matter when a record
    was recorded, the election year could be a different year. So if you want
    say records for Mayor in 2014, those donations could be from, technically
    any year. And because I don't feel like estimating how long before and
    after the election those donations should be from.
    '''
    from_date = '01/01/1999'
    to_date = '01/01/9999'

    records = csv.DictReader(records_csv(from_date, to_date, report_type).splitlines())

    def year_from_date(date):
        return int(date.split('/')[-1])

    for record in records:
        # Find the record commitee name and year, so that we can make a guess
        # at what the office and eleciton year the record is from
        record_committee = record["Committee Name"]
        record_submitted_year = year_from_date(record["Date of Receipt"])
        record_office, record_election_year = election_of_committee(record_committee, record_submitted_year)
        logger.debug(record_office)
        logger.debug(record_election_year)
        # if that is the office and record year we want, then we want that record!
        if record_office == office and record_election_year == election_year:
            yield record


@utils.log_function
@functools.lru_cache()
def available_years():
    js_with_years_in_it = 'http://geospatial.dcgis.dc.gov/ocf/js/process.js'
    r = requests.get(js_with_years_in_it)

    years_line = r.text.splitlines()[3]
    # This line looks like like:
    # var m_Interface_Control = [{ "year": "2010", "defaultoffice": "Mayor", "showparty": "yes", "defaultparty": "Democratic" }, { "year": "2011", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2012", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2013", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}, { "year": "2014", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}];
    years_json_text = years_line.lstrip('var m_Interface_Control =').rstrip(';')
    # Now we have just the json:
    # [{ "year": "2010", "defaultoffice": "Mayor", "showparty": "yes", "defaultparty": "Democratic" }, { "year": "2011", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2012", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": "" }, { "year": "2013", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}, { "year": "2014", "defaultoffice": "Council At-Large", "showparty": "no", "defaultparty": ""}]
    years_json = json.loads(years_json_text)

    # then we just want to return a list of the years
    return [int(year['year']) for year in years_json]


@utils.log_function
@functools.lru_cache()
def offices():
    html_with_offices_in_it = 'http://geospatial.dcgis.dc.gov/ocf/'
    r = requests.get(html_with_offices_in_it)
    soup = BeautifulSoup(r.text)

    office_option_elements = soup.find(id='SearchByOffices')('option')
    # sort them by their form value, so they look all nice and ordered
    office_option_elements.sort(key=lambda e: int(e['value']))

    return [e.text for e in office_option_elements]


@utils.log_function
@functools.lru_cache()
def races(year):
    for office in offices():
        if committees(office, year):
            yield office


@utils.log_function
@functools.lru_cache()
@utils.retry_exp_backoff
def _office_version(office):

    def _get_html():
        html_with_offices_in_it = 'http://geospatial.dcgis.dc.gov/ocf/'
        return requests.get(html_with_offices_in_it).text

    soup = BeautifulSoup(_get_html())

    return soup.find('option', text=office)['value']


@utils.log_function
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
                            yield(("commitee '{}' ran twice, in '{}' for '{}' and "
                                   "in '{}' running for '{}'").format(
                                committee, year, office, year_test, office_test))

                years_offices_committees[year][office].append(committee)


@utils.log_function
@functools.lru_cache(maxsize=2**9)
@utils.retry_exp_backoff
def committees(office, year):
    if year not in available_years():
        raise NoData("No data on {} for committees running".format(year))
    url = 'http://geospatial.dcgis.dc.gov/ocf/getData.aspx'
    payload = {
        'of': office,
        'ofv': _office_version(office),
        'yr': year,
    }
    r = requests.get(url, params=payload)
    soup = BeautifulSoup(r.text)

    try:
        return [tr.td.text for tr in soup.table.find_all('tr')][:-1]
    except AttributeError:
        return []
