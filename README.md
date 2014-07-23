# dc-campaign-finance-scraper

## Install
```bash
$ pip install dc-campaign-finance-scraper
Downloading/unpacking dc-campaign-finance-scraper
...
```

## CLI Usage

The easiest way to get data out from the scraper is to use the CLI. Once you
it installed, you should be able to run the `dc-campaign-finance-scraper`
command

```bash
$ dc-campaign-finance-scraper --help
Usage: dc-campaign-finance-scraper [OPTIONS] COMMAND [ARGS]...

Options:
  --log / --no-log      Print log of all HTTP requests  [default: False]
  --cache / --no-cache  Cache all requests to file.  [default: True]
  --help                Show this message and exit.

Commands:
  committees_dup  Checks to see if any committees are duplicated in multiple
                  race
  records         List of records
```

To get a list of records of all contributions or expenditures, use the `records`
subcommand.

```bash
$ Usage: dc-campaign-finance-scraper records [OPTIONS]

  A list all transactions for all campaigns, between FROM-DATE and TO-DATE.

  Also, if specified, only those for the elction in ELECTION-YEAR and
  running for the office OFFICE.

  Either the expenses of the campaign or the contributions of the campaign,
  based on REPORT-TYPE.

Options:
  --office [Mayor|Council Chairman|Council At-Large|Council Ward 1|Council Ward 2|Council Ward 3|Council Ward 4|Council Ward 5|Council Ward 6|Council Ward 7|Council Ward 8|US Representative|Democratic National Committeeman|Democratic National Committeewoman|Alternate Democratic National Committeeman|Alternate Democratic National Committeewoman|At-Large DC Democratic State Committee|Ward 1 DC Democratic State Committee |Ward 2 DC Democratic State Committee|Ward 3 DC Democratic State Committee|Ward 4 DC Democratic State Committee|Ward 5 DC Democratic State Committee|Ward 6 DC Democratic State Committee|Ward 7 DC Democratic State Committee|Ward 8 DC Democratic State Committee|Democratic Delegates|Democratic Delegates Alternates|Republican Delegates|Republican Delegates Alternates|Republican National Committeeman|Republican National Committeewoman|At-Large DC Republican Committee Official|Ward 1 of the DC Republican Committee|Ward 2 of the DC Republican Committee|Ward 3 of the DC Republican Committee|Ward 4 of the DC Republican Committee|Ward 5 of the DC Republican Committee|Ward 6 of the DC Republican Committee|Ward 7 of the DC Republican Committee|Ward 8 of the DC Republican Committee|Other Political Party|Non Supporting|Supporting|US Senator|School Board Ward 1|School Board Ward 2|School Board Ward 3|School Board Ward 4|School Board Ward 5|School Board Ward 6|School Board Ward 7|School Board Ward 8|School Board At-Large|Attorney General]
  --election-year INTEGER RANGE
  --report-type [exp|con]         exp -> expenses, con -> contributions
                                  [default: con]
  --from-date TEXT                First date of records.  [default:
                                  01/01/1999]
  --to-date TEXT                  Last date of records. Future dates are
                                  allowed.  [default: 01/01/9999]
  --format [json|xls|yaml|csv|tsv|html|xlsx|ods]
                                  Format of out output.
  --help                          Show this message and exit.
```
Although the `records` command can be run without any arguments, this
will return every record in the system, and will take a long time.

If you don't specify a `format` it will default to a text based table
like output.

However, for something more interesting, let's try finding all the mayoral
donation in 2014, for the election in 2014.

```bash
$ dc-campaign-finance-scraper records --office Mayor --election-year 2014 --from-date 01/01/2014 --to-date 01/01/2015
Committee Name                            |Candidate Name |Contributor                                  |Address                                 |city                        |state|Zip  |Contributor Type       |Contribution Type|Employer Name                                     |Employer Address                                                 |Amount     |Date of Receipt|Office|Election Year
------------------------------------------|---------------|---------------------------------------------|----------------------------------------|----------------------------|-----|-----|-----------------------|-----------------|--------------------------------------------------|-----------------------------------------------------------------|-----------|---------------|------|-------------
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Rufer, Chris                                 |724 Main                                |Woodland                    |CA   |95695|Individual             |Check            |Retired                                           | CA                                                              |$2,000.00  |3/3/2014       |Mayor |2014
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Majors, Mary                                 |11 Redbud                               |Shelbyville                 |TN   |37160|Individual             |Check            |Retired                                           | TN                                                              |$300.00    |2/27/2014      |Mayor |2014
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Majors, Bruce                                |1200 23rd Street, NW. #711              |Washington                  |DC   |20037|Candidate              |Check            |                                                  |                                                                 |$1,500.00  |3/1/2014       |Mayor |2014
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Snead, Edward                                |111 redbud                              |Georgetown                  |TX   |67676|Individual             |Check            |                                                  |                                                                 |$1,000.00  |4/8/2014       |Mayor |2014
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Delhomme, Laura                              |1515 North Couthouse                    |Arlington                   |VA   |22203|Individual             |Check            |CKI                                               | 1515 North Couthouse, VA 22201                                  |$150.00    |6/7/2014       |Mayor |2014
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Palmer, Tom                                  |1735                                    |17th Street NW              |DC   |20009|Individual             |CASH             |Atlas Foundation                                  | 1201 L Street NW, Washington, DC 20005                          |$25.00     |6/8/2014       |Mayor |2014
Bruce Majors, Libertarian for Mayor       |Bruce Majors   |Majors, Bruce                                |1200 23rd Street, NW. #711              |Washington                  |DC   |20037|Candidate              |Check            |                                                  |                                                                 |$500.00    |6/1/2014       |Mayor |2014
Carlos Allen For Mayor                    |Carlos Allen   |Sewell, Anthony                              |507 Louise Avenue                       |Linthicum Heights           |MD   |21090|Individual             |Credit Card      |                                                  |                                                                 |$100.00    |2/5/2014       |Mayor |2014
Carlos Allen For Mayor                    |Carlos Allen   |Brooks, Karen                                |9709 Manteo Ct                          |Ft Washington               |MD   |20744|Individual             |Credit Card      |                                                  |                                                                 |$15.00     |2/25/2014      |Mayor |2014
Carlos Allen For Mayor                    |Carlos Allen   |Alsbrook, Darrell                            |2470                                    |LakeMeadow Ln               |GA   |30017|Individual             |Credit Card      |                                                  |                                                                 |$20.00     |3/4/2014       |Mayor |2014
...
```

*Notice* Behind the scenes, all the records between the `from-date`
and `to-date` are requested from the server, and only filtered locally.
Also, because office and election year are not included in the source
record set, it is neccesary to try to guess them from the committee
name and date of donation. What this ends up meaning is that
a whole lot of HTTP requests must happen if you request the whole
date range, which will in turn, take a while.

## API Usage

Feel free to access the pythonn api. Take a look at the functions in
[dc_campaign_finance-scraper/scraper.py](dc_campaign_finance-scraper/scraper.py).


## Release instructions
1. `pip install -e .` to make sure it works
2. Bump version in `./setup.py`
3. Commit and create tag for version prefixed with "v"
4. `pip install wheel`
5. `python setup.py sdist bdist_wheel upload`


## Developing locally with Docker

```bash
fig build python
fig run fig run python dc-campaign-finance-scraper --help
fig run fig run python test
```

## How did I do it?
### Manual Process
1. Go to
   [www.ocf.dc.gov/serv/download.asp](http://www.ocf.dc.gov/serv/download.asp)
   ![Screenshot of unfilled in serv/download.asp](http://f.cl.ly/items/3J2k2O05223Y1K2T0C43/District%20of%20Columbia%20%20Office%20of%20Campaign%20Finance%20%20Contribution%20%20%20Expenditure%20Search.png)
2. Fill in `From Date`, `To Date`, and `Payment Type`.
   ![Screenshot of filled in serv/download.asp](http://f.cl.ly/items/0T3N0O1I1W0A1t2W1t3N/District%20of%20Columbia%20%20Office%20of%20Campaign%20Finance%20%20Contribution%20%20%20Expenditure%20Search%20filled%20in.png)
3. Click `Submit` and it sends a `POST` to
   [www.ocf.dc.gov/serv/download.asp](http://www.ocf.dc.gov/serv/download.asp)
   and displays the entered form.
   ![Screenshot of submitted form](http://f.cl.ly/items/0Z3k1P2W0l1G2P080o2K/District%20of%20Columbia%20%20Office%20of%20Campaign%20Finance%20%20Contribution%20%20%20Expenditure%20Search%20submitted.png)
4. Click `Click here to download the CSV File` and it sends a `POST` to
   [www.ocf.dc.gov/serv/download_conexp.asp](http://www.ocf.dc.gov/serv/download_conexp.asp)
5. Returns `POST` with CSV text.

### Automation
#### Selenium
At first I tried using
[Selenium with Python](http://selenium-python.readthedocs.org) to fill in
the forms and click the buttons. This will actually run a real(ish) browser
and execute all the the JS and simulate user input. This worked, but
it couldn't really handle the returned CSV text from step 5. In a browser
this opens in a new window and downloads to your computer, but the
[PhantomJS driver for Selenium and Python](http://www.realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/)
wasn't really working for that new window. I might have been able to get
it to work eventually, but it prompted me to search for a different approach.

#### Requests
I then started experimenting with
[Requests for Python](http://docs.python-requests.org/en/latest) to just
call the to just make the actual HTTP calls, instead of pretending to be a
human and filling in the form. This was 1) faster 2) less verbose 3) easier
to understand.

##### Chrome Dev Tools
I fired up my Chrome Dev Tools and looked at what requests
were being made. So I tried to figure out in step 4, what request was actually being sent,
so that I could replay it programatically. However, since that opened
in a new window, the Dev Tools didn't save the request.
![GIF of clicking on download button and it downloading in chrome](http://zippy.gfycat.com/PinkAccomplishedBuffalo.gif)
It [isn't possible](http://stackoverflow.com/a/13747562) with chrome
to open a new window with Dev Tools already open.

##### Chrome Net Internals
I then tried [chrome://net-internals/#events](chrome://net-internals/#events)
to see the actual HTTP request being processed. I could see it was sending
a `POST` to`/serv/download_conexp.asp`
and the returned CSV. However it didn't show the `POST` data or the
cookies.
![chrome net internals events showing POST](http://f.cl.ly/items/050P46040W3o2t30431M/Screen%20Shot%202014-06-15%20at%2012.54.33%20PM.png)

##### Charles
For that I found [Charles](http://www.charlesproxy.com/)
(`brew cask install charles`) which provides a HTTP proxy to run your web
traffic through and then you can inspect every request.

#### Cookie
I checked the `POST` headers for the request and tried making it myself.
I got a response of

```html
    <script language="javascript">
        alert("Your Session is expired. Please try again");
        opener.location.href="/serv/download.asp";
        window.close();
    </script>
```

I found that it was setting a cookie when I requested
`/serv/download.asp`. I first tried it with a cookie I got  from the browser
and IT WORKED! I got back the CSV.

So I began using
[Requests Sessions](http://docs.python-requests.org/en/latest/user/advanced/#session-objects)
to first `GET` at `/serv/download.asp` to get a session cookie and then
`POST` to `/serv/download_conexp.asp` with that cookie. That didn't work,
I got the `Your Session is expired. Please try again` response.
So then I tried doing step 3, sending a `POST` to `/serv/download.asp` and then
the identical post to `/serve/download_conexp.asp`, thinking maybe the server
checked to see if I submitted the form before letting me download. It worked!
However the next day when I tried again I go the
`Your Session is expired. Please try again`. Very weird. I tried getting a
cookie from the my chrome session and using that and it forked. So something
about how I get my session on chrome is different from how I get my session
on Requests. I needed to figure out what the difference was.

Then I tried it again and it worked. So who knows. Maybe their site is weird.

