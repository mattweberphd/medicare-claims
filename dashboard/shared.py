import geopandas as gpd
import json
import pandas as pd

from pathlib import Path

# Keep this for when we unf*** I/O
app_dir = Path(__file__).parent

bsf = pd.read_csv("../data/DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv")

counties = pd.read_csv("../mappings/counties.csv", index_col="BENE_COUNTY_CD")
race = pd.read_csv("../mappings/race.csv", index_col="BENE_RACE_CD")
sex = pd.read_csv("../mappings/sex.csv", index_col="BENE_SEX_IDENT_CD")
nj = (
    bsf.query("SP_STATE_CODE == 31")
    .join(counties, on="BENE_COUNTY_CD")
    .join(race, on="BENE_RACE_CD")
    .join(sex, on="BENE_SEX_IDENT_CD")
)

nj["Birth Date"] = pd.to_datetime(nj["BENE_BIRTH_DT"], format="%Y%m%d")
nj["Death Date"] = pd.to_datetime(nj["BENE_DEATH_DT"], format="%Y%m%d")

# pull in counties
nj_counties = gpd.read_file(
    "../data/NJ_Counties_3857_2520527434192953465/NJ_Counties_3857.shp"
)

# Reimbursement per county
# Lots of other stuff you could do here just with the beneficiary file -- average claim amount, share of Medicare vs. beneficiary responsibility, &c
reimb_amt_ip = nj.groupby("County Name")["MEDREIMB_IP"].sum()
reimb_amt_op = nj.groupby("County Name")["MEDREIMB_OP"].sum()

nj_counties = nj_counties.join(reimb_amt_ip, on="COUNTY_LAB").join(
    reimb_amt_op, on="COUNTY_LAB"
)

# this isn't great, do the processing once
reimb_amt_ip = nj.groupby("County Name")["MEDREIMB_IP"].sum().to_frame(name="MEDREIMB_IP").reset_index()
reimb_amt_op = nj.groupby("County Name")["MEDREIMB_OP"].sum().to_frame(name="MEDREIMB_OP").reset_index()

nj_counties_json = json.load(open("../data/NJ_Counties_3857_3761882870795826402.geojson", "r"))

#import pdb; pdb.set_trace()
