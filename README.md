# finance-scraper

## Instructions
```bash
$ pip install dc-campaign-finance-data
Downloading/unpacking dc-campaign-finance-data
...
$ dc-campaign-finance-data
Usage: dc-campaign-finance-data [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  committees  Running committees (JSON)
  offices     Possible offices (JSON)
  records     List of records (CSV)
  years       Possible years (JSON)
$ dc-campaign-finance-data offices
["Mayor", "Council Chairman", "Council At-Large", "Council Ward 1", ... ]
$ dc-campaign-finance-data years
[2010, 2011, 2012, 2013, 2014]⏎
$ dc-campaign-finance-data committees --help
Usage: dc-campaign-finance-data committees [OPTIONS]

  All committees running for OFFICE in YEAR.

Options:
  --office [Mayor|Council Chairman...
                                  [default: Council At-Large]
  --year INTEGER RANGE            [default: 2014]
  --help                          Show this message and exit.
$ dc-campaign-finance-data committees
["Bonds for Council 2014", "Brian Hart for DC", ...]⏎
$ dc-campaign-finance-data records --help
Usage: dc-campaign-finance-data records [OPTIONS]

  A list all transactions for all campaigns, between FROM-DATE and TO-DATE.
  Either the expenses of the campaign or the contributions of the campaign,
  based on REPORT-TYPE.

Options:
  --from-date TEXT         First date of records.  [default: 01/01/2014]
  --to-date TEXT           Last date of records. Future dates are allowed.
                           [default: 01/01/9999]
  --report-type [exp|con]  The type of report. (exp -> expenses, con ->
                           contributions)  [default: con]
  --help                   Show this message and exit.
$ dc-campaign-finance-data records
"Committee Name","Candidate Name","Contributor","Address","city","state","Zip","Contributor Type","Contribution Type","Employer Name","Employer Address","Amount","Date of Receipt"
"AJ Cooper at large","A.J  Cooper ","Cooper, A.J ","1212 Delafield Pl., NW","Washington","DC","20011","Candidate","Check","","","$2,000.00","1/24/2014"
...
```

## Release instructions
1. `pip install -e .` to make sure it works
2. Bump version in `./setup.py`
3. Commit and create tag for version prefixed with "v"
4. `pip install wheel`
5. `python setup.py sdist bdist_wheel upload`

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

