from __future__ import unicode_literals

import click
import json
import datetime

from . import scraper


@click.group()
def cli(**kwargs):
    pass


@cli.command(short_help='List of records (CSV)')
@click.option('--from-date',
              default='01/01/' + str(datetime.datetime.now().year),
              help='First date of records.',
              show_default=True)
@click.option('--to-date',
              default='01/01/9999',
              help='Last date of records. Future dates are allowed.',
              show_default=True)
@click.option('--report-type',
              default='con',
              help='exp -> expenses, con -> contributions',
              type=click.Choice(['exp', 'con']),
              show_default=True)
def records(**kwargs):
    '''
    A list all transactions for all campaigns, between FROM-DATE and TO-DATE.
    Either the expenses of the campaign or the contributions of the
    campaign, based on REPORT-TYPE.
    '''
    click.echo(
        scraper.records_csv(**kwargs),
        nl=False
    )


@cli.command(short_help='Possible years (JSON)')
def years():
    '''
    Years in which there are records kept of campaign finances. (JSON)
    '''
    click.echo(
        json.dumps(scraper.available_years()),
        nl=False
    )


@cli.command(short_help='Possible offices (JSON)')
def offices():
    '''
    Offices for DC which are tracked. (JSON)
    '''
    click.echo(
        json.dumps(scraper.offices()),
        nl=False
    )

year_range = [scraper.available_years()[0], scraper.available_years()[-1]]


@cli.command(short_help='Running committees (JSON)')
@click.option('--office',
              default='Council At-Large',
              show_default=True,
              type=click.Choice(scraper.offices()))
@click.option('--year',
              default=datetime.datetime.now().year,
              show_default=True,
              type=click.IntRange(*year_range))
def committees(**kwargs):
    '''
    All committees running for OFFICE in YEAR.
    '''
    click.echo(
        json.dumps(scraper.committees(**kwargs)),
        nl=False
    )


@cli.command(short_help='Active races in a year (JSON)')
@click.option('--year',
              default=datetime.datetime.now().year,
              show_default=True,
              type=click.IntRange(*year_range))
def races(**kwargs):
    '''
    All offices that are run for in YEAR
    '''
    click.echo(
        json.dumps(list(scraper.races(**kwargs))),
        nl=False
    )

if __name__ == '__main__':
    cli()
