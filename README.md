# Visualizing synthetic Medicare claims data

This repository visualizes the synthetic Medicare claims data provided by [the Center for Medicare & Medicaid Services](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf).

Data should go in a directory called "data" on the top level. The dashboard also relies on the [County Boundaries of New Jersey shapefile hosted by NJGIN](https://njogis-newjersey.opendata.arcgis.com/datasets/newjersey::county-boundaries-of-nj-hosted-3857/explore), which goes in the same folder.

## TODO

* Frequency and ~co-occurrence~ of condition indicators
* Before anything with claims data, some basic QOL / proof of usefulness:
    * Figure out and implement filtering (e.g., by demographics -- I think by variable is not necessary, show everything?)
    * Testing? Some anyway
    * Type hinting
    * Incorporate all data (or figure out how to do so)
        * Improve I/O, everything's hard-coded now
    * Post to shinyapps.io (or posit.connect.cloud now?)
* Claims data, other datasets
    * How to make a multi-page dashboard?
* Function to fetch data
* Improve install instructions?
* ~Data-dependent tooltips (e.g. county, bar)~
* ~Summarize beneficiary demographics (NB: can't do age based on beneficiary alone unless they're dead, but can presumably do age at claim time when joined to claims based on birth date.)~
    * ~Race, sex~
* ~Figure out and implement data-dependent ordering (e.g., order county sum of reimbursement by that sum, not by county name)~
* ~Ratios~:
    * ~Looking at each of inpatient, outpatient, carrier: What's the share of Medicare vs. beneficiary vs. primary payer responsibility? (3 pie charts I think, or area charts or whatever.)~
    * ~Should be filterable by demos and county. So we need one df aggregated by race, sex, and county, with all 9 variables, [MEDREIMB, BENRES, PPPYMT] x [IP, OP, CAR].~