from __future__ import unicode_literals

import click
import tablib.formats

from . import scraper
from . import utils
from . import cache

year_range = [min(scraper.available_years()), max(scraper.available_years())]


@click.group()
@click.option('--log/--no-log',
              default=False,
              help='Print log of all HTTP requests',
              show_default=True)
@click.option('--persistant-cache/--in-memory-cache',
              default=True,
              help='Cache all responses to a file.',
              show_default=True)
def cli(log, persistant_cache):
    if log:
        utils.enable_logging()
    if persistant_cache:
        cache.use_persistant_cache()


@cli.command(short_help='Clear persistant cache')
def clear_cache():
    cache.clear_persistant_cache()


@cli.command(short_help='Prints the path of the persistant cache.')
def cache_file():
    click.echo(cache.CACHE_FILE_NAME)


@cli.command(short_help='List of records')
@click.option('--office',
              type=click.Choice(scraper.offices()))
@click.option('--election-year',
              type=click.IntRange(*year_range))
@click.option('--report-type',
              default='con',
              help='exp -> expenses, con -> contributions',
              type=click.Choice(['exp', 'con']),
              show_default=True)
@click.option('--from-date',
              default='01/01/1999',
              help='First date of records.',
              show_default=True)
@click.option('--to-date',
              default='01/01/9999',
              help='Last date of records. Future dates are allowed.',
              show_default=True)
@click.option('--format',
              help='Format of out output.',
              type=click.Choice(map(lambda fmt: fmt.title, tablib.formats.available)))
def records(format, office, election_year, **kwargs):
    '''
    A list all transactions for all campaigns, between FROM-DATE and TO-DATE.

    Also, if specified, only those for the elction in ELECTION-YEAR and
    running for the office OFFICE.

    Either the expenses of the campaign or the contributions of the
    campaign, based on REPORT-TYPE.
    '''
    records = scraper.records_with_office_and_election_year(**kwargs)

    if office:
        records.filter(lambda r: r['Office'] == office)
    if election_year:
        records.filter(lambda r: r['Election Year'] == str(election_year))

    if format:
        output = getattr(records, format)
    else:
        output = records
    click.echo(
        output,
        nl=False
    )


@cli.command(short_help='Available Election Years')
def years():
    '''
    A list of all all the available election years.

    Returns each year on a new line.
    '''
    years = scraper.available_years()

    click.echo(
        '\n'.join(map(str, years)),
        nl=False
    )


@cli.command(short_help='Offices that are contested')
@click.option('--election-year',
              type=click.IntRange(*year_range))
def offices(election_year=None):
    '''
    A list of all the offices that are contested, in a certain ELECTION-YEAR.
    If no ELECTION-YEAR provided, returns all the offices.

    Returns each office on a new line.
    '''
    if election_year:
        offices = scraper.races(election_year)
    else:
        offices = scraper.offices()

    click.echo(
        '\n'.join(offices),
        nl=False
    )


@cli.command(short_help='Checks to see if any committees are duplicated in multiple race')
def committees_dup():
    '''
    Logs and committee names that show up running for more than one office.
    This means these are problematic, because we have to infer what records
    go with each race, and can not tell exactly what race they are for
    '''
    for log in scraper.commitees_in_multiple_years():
        click.echo(log)


if __name__ == '__main__':
    cli()
