import geopandas as gpd
import json
import numpy as np
import pandas as pd
import yaml

from pathlib import Path
from typing import Optional

# Keep this for when we unf*** I/O
app_dir = Path(__file__).parent

with open("../config.yml", "r") as cfg:
    config = yaml.safe_load(cfg)

INDICATORS = config["default"]["BENE_INDICATORS"]

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

reimb_amt_ip_by_race = nj.groupby("Race/Ethnicity")["MEDREIMB_IP"].sum().to_frame(name="MEDREIMB_IP").reset_index()
reimb_amt_ip_by_sex = nj.groupby("Sex")["MEDREIMB_IP"].sum().to_frame(name="MEDREIMB_IP").reset_index()

# Reimbursement by responsibility (Medicare reimbursement, beneficiary, payer) and type of care
# (inpatient, outpatient, carrier (?))
# Create it aggregated by all relevant groups -- we'll aggregate it further on the app end.
# TODO: move to config
# TODO: functionize for testing (also applicable to uh everything here)
groups = ["County Name", "Race/Ethnicity", "Sex"]
fields = [
    "MEDREIMB_IP",
    "MEDREIMB_OP",
    "MEDREIMB_CAR",
    "BENRES_IP",
    "BENRES_OP",
    "BENRES_CAR",
    "PPPYMT_IP",
    "PPPYMT_OP",
    "PPPYMT_CAR"
]
responsibility = {
    "MEDREIMB_IP": "Medicare",
    "MEDREIMB_OP": "Medicare",
    "MEDREIMP_CAR": "Medicare",
    "BENRES_IP": "Beneficiary",
    "BENRES_OP": "Beneficiary",
    "BENRES_CAR": "Beneficiary",
    "PPPYMT_IP": "Payer",
    "PPPYMT_OP": "Payer",
    "PPPYMT_CAR": "Payer"
}
care = {
    "MEDREIMB_IP": "Inpatient",
    "MEDREIMB_OP": "Outpatient",
    "MEDREIMP_CAR": "Carrier",
    "BENRES_IP": "Inpatient",
    "BENRES_OP": "Outpatient",
    "BENRES_CAR": "Carrier",
    "PPPYMT_IP": "Inpatient",
    "PPPYMT_OP": "Outpatient",
    "PPPYMT_CAR": "Carrier"    
}

# Sum fields
rxr = nj.groupby(groups)[fields].sum().reset_index()
# Wide to long
rxr = pd.melt(rxr, id_vars = groups)

rxr["Responsibility"] = rxr["variable"].map(responsibility)
rxr["Care Type"] = rxr["variable"].map(care)
rxr = rxr.rename(columns={"value": "Amount"})

#import pdb; pdb.set_trace()

def create_responsibility_pie_df(df: pd.DataFrame, care_type: str) -> pd.DataFrame:

    df_ = df[df["Care Type"] == care_type]
    df_ = df_[["Responsibility", "Care Type", "Amount"]]\
            .groupby(["Responsibility", "Care Type"])\
            .sum()\
            .reset_index()
    df_["Pct"] = df_["Amount"] / df_["Amount"].sum()

    return df_

def cooccurrence(
    df: pd.DataFrame, 
    columns: Optional[list[str]] = None, 
    convert_pct_by: Optional[str] = None
) -> pd.DataFrame:

    cooccurrence = df[columns].T.dot(df[columns]) if columns else df.T.dot(df)
    divide_by = pd.Series(np.diag(cooccurrence), index=cooccurrence.index)
    normed = cooccurrence / divide_by

    if convert_pct_by == "rows":
        cooccurrence = normed.T
    elif convert_pct_by == "columns":
        cooccurrence = normed

    return cooccurrence

#def indicator_frequency():
#indicators_bin = nj[INDICATORS].replace({2: 0})
#indicators_count = indicators_bin.sum().reset_index().rename(columns={"index": "Indicator", 0: "count"})
#indicators_count["percent"] = indicators_count["count"] / indicators_count["count"].sum()


#sorted = nj_counties.sort_values(input.var(), ascending=True)

#import pdb; pdb.set_trace()