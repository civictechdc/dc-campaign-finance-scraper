import requests
import json
import csv
import collections
import logging
from . import tablib

from bs4 import BeautifulSoup

from . import utils
from .cache import cache


class NoData(Exception):
    pass


logger = logging.getLogger(__name__)


@utils.log_function
@cache
def _records_cookies(options):
    r = requests.post("http://www.ocf.dc.gov/serv/download.asp", options)
    r.raise_for_status()
    return r.cookies


@utils.log_function
@cache
def records(from_date, to_date, report_type):
    '''
    :rtype: :py:class:`tablib.Dataset`
    '''
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
        raise(
            Exception,
            'Cant get records data. Cookie isnt working. Says session expire')

    headers, *rows = csv.reader(r.text.splitlines())

    def normalize_record(record):
        record['Candidate Name'] = record['Candidate Name'].strip()
        return record

    return tablib.Dataset(*rows, headers=headers).map(normalize_record)


@utils.log_function
@cache
def election_of_committee(committee, record_year):
    '''
    Returns the ofifce and election year, for a certain committee name.
    It starts by looking at all the elections in that year, to see if
    that committee name was running for anything.

    :rtype: tuple of str and int
    :return: The office that the committee was running for and the year it was
             running.

    '''
    try:
        for possible_office in races(record_year):
            if committee in committees(possible_office, record_year):
                return possible_office, record_year
    except NoData:
        return None, None
    return election_of_committee(committee, record_year + 1)


@utils.log_function
@cache
def records_with_office_and_election_year(from_date, to_date, report_type):
    '''
    :rtype: :py:class:`tablib.Dataset`
    '''

    def add_election_columns(record):
        record['Office'], record["Election Year"] = election_of_committee(
            record["Committee Name"],
            utils.year_from_date(record["Date of Receipt"])
        )
        return record

    return records(from_date, to_date, report_type).map(add_election_columns)


@utils.log_function
@cache
def available_years():
    '''
    :rtype: list of int
    :return: years which records exist for and office names can be generated.
    '''
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
@cache
def offices():
    '''
    :rtype: list of str
    :return: possible offices
    '''
    html_with_offices_in_it = 'http://geospatial.dcgis.dc.gov/ocf/'
    r = requests.get(html_with_offices_in_it)
    soup = BeautifulSoup(r.text)

    office_option_elements = soup.find(id='SearchByOffices')('option')
    # sort them by their form value, so they look all nice and ordered
    office_option_elements.sort(key=lambda e: int(e['value']))

    return [e.text for e in office_option_elements]


@utils.log_function
@cache
@utils.listify
def races(year):
    '''
    :rtype: list of str
    :return: all the offices that have races for them, for a certain year
    '''
    for office in offices():
        if committees(office, year):
            yield office


@utils.log_function
@cache
@utils.retry_exp_backoff
def _office_version(office):

    def _get_html():
        html_with_offices_in_it = 'http://geospatial.dcgis.dc.gov/ocf/'
        return requests.get(html_with_offices_in_it).text

    soup = BeautifulSoup(_get_html())

    return soup.find('option', text=office)['value']


@utils.log_function
@utils.listify
@cache
def commitees_in_multiple_years():
    '''
    Checks to see if any committee name runs in elections in multiple years.

    :rtype: list of str
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
@cache
@utils.retry_exp_backoff
def committees(office, year):
    '''

    :rtype: list of str
    :return: all of the committee names running for a certain office in a
             certain year.
    '''
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
