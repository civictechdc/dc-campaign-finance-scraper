from setuptools import setup, find_packages

setup(
    name="dc-campaign-finance-scraper",
    version="0.6.1",
    packages=find_packages(exclude=["tests.*"]),
    entry_points={
        'console_scripts': [
            'dc-campaign-finance-scraper=dc_campaign_finance_scraper.cli:cli'
        ]
    },
    install_requires=[
        'requests',
        'click',
        'beautifulsoup4',
        'retrying',
        'tablib'
    ],

    # metadata for upload to PyPI
    long_description=open('README.md').read(),
    author="Saul Shanabrook",
    author_email="s.shanabrook@gmail.com",
    description="Provides data from http://www.ocf.dc.gov/serv/download.asp in a nicer way",
    url="http://github.com/codefordc/dc-campaign-finance-scraper",
)
