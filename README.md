# Visualizing synthetic Medicare claims data

This repository visualizes the synthetic Medicare claims data provided by [the Center for Medicare & Medicaid Services](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf).

Data should go in a directory called "data" on the top level. The dashboard also relies on the [County Boundaries of New Jersey shapefile hosted by NJGIN](https://njogis-newjersey.opendata.arcgis.com/datasets/newjersey::county-boundaries-of-nj-hosted-3857/explore), which goes in the same folder.

## TODO

* Data-dependent tooltips (e.g. county, bar)
* Summarize beneficiary demographics
    * Race, sex
* Figure out and implement filtering (e.g., by demographics)
* Figure out and implement data-dependent ordering (e.g., order county sum of reimbursement by that sum, not by county name)
* Incorporate all data
    * Improve I/O, everything's hard-coded now
* Improve install instructions
* Function to fetch data
* Post to shinyapps.io
