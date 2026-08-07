import pandas as pd
import plotly.express as px

from shiny import reactive
from shiny.express import input, ui
from shinywidgets import render_widget

# TODO: organize
from shared import nj_counties, nj_counties_json, reimb_amt_ip, reimb_amt_ip_by_race, \
    reimb_amt_ip_by_sex, rxr, create_responsibility_pie_df, INDICATORS, cooccurrence, nj, \
    COUNTIES, RACES, SEXES, FILTER_ALL, payment, payment_fields

ui.page_opts(title="DeSynPUF dashboard", fillable=False, page_fluid=True)

# Filtering functions
def f_reimbursement(aggregate_by: str) -> pd.DataFrame:

    filtered = payment.reset_index()

    if (input.County() != FILTER_ALL) & (aggregate_by != "County Name"):
        filtered = filtered[filtered["County Name"] == input.County()]
    if (input.Race() != FILTER_ALL) & (aggregate_by != "Race/Ethnicity"):
       filtered = filtered[filtered["Race/Ethnicity"] == input.Race()]
    if (input.Sex() != FILTER_ALL) & (aggregate_by != "Sex"):
       filtered = filtered[filtered["Sex"] == input.Sex()]

    aggregated = filtered.groupby(aggregate_by)[payment_fields].sum().reset_index()

    return aggregated

@reactive.calc
def f_reimbursement_county() -> pd.DataFrame:

    return f_reimbursement("County Name")

@reactive.calc
def f_reimbursement_race() -> pd.DataFrame:

    return f_reimbursement("Race/Ethnicity")

@reactive.calc
def f_reimbursement_sex() -> pd.DataFrame:

    return f_reimbursement("Sex")


@reactive.calc
def f_responsibility_ip() -> pd.DataFrame:

    filtered = rxr.reset_index()

    if (input.County() != FILTER_ALL):
        filtered = filtered[filtered["County Name"] == input.County()]
    if (input.Race() != FILTER_ALL):
       filtered = filtered[filtered["Race/Ethnicity"] == input.Race()]
    if (input.Sex() != FILTER_ALL):
       filtered = filtered[filtered["Sex"] == input.Sex()]

    pie_df = create_responsibility_pie_df(filtered, "Inpatient")

    return pie_df


with ui.sidebar(title="Filter controls"):
    ui.input_selectize("County", "Select county", choices=COUNTIES)
    ui.input_selectize("Race", "Select race", choices=RACES)
    ui.input_selectize("Sex", "Select sex", choices=SEXES)

# Row 1
with ui.layout_columns():
    # Reimbursement graph
    with ui.card(full_screen=True):
        ui.card_header("Reimbursement amounts")

        @render_widget
        def county_bar():

            fdf = f_reimbursement_county()
            sorted = fdf.sort_values("MEDREIMB_IP", ascending=True)

            county_bar = px.bar(
                sorted, x="MEDREIMB_IP", y="County Name", orientation="h"
            )

            return county_bar

    # Reimbursement map
    with ui.card(full_screen=True):
        ui.card_header("Map of reimbursement")
        @render_widget
        def county_map():

            fdf = f_reimbursement_county()

            fig = px.choropleth(
                fdf,
                geojson=nj_counties_json, 
                locations='County Name',
                featureidkey="properties.COUNTY_LABEL", 
                color='MEDREIMB_IP',
                color_continuous_scale="Viridis",
                scope="usa",
                labels={'MEDREIMB_IP':'Total inpatient reimbursement'}
            )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_geos(fitbounds="locations")

            return fig

# Row 2
with ui.layout_columns():
    # Reimbursement by race
    with ui.card(full_screen=True):
        ui.card_header("Reimbursement by race")
        @render_widget
        def race_bar():

            fdf = f_reimbursement_race()
            sorted = fdf.sort_values("MEDREIMB_IP", ascending=True)

            race_bar = px.bar(
                sorted, x="MEDREIMB_IP", y="Race/Ethnicity", orientation="h"
            )
            
            return race_bar

    # Reimbursement by sex
    with ui.card(full_screen=True):
        ui.card_header("Reimbursement by sex")
        @render_widget
        def sex_bar():

            fdf = f_reimbursement_sex()
            sorted = fdf.sort_values("MEDREIMB_IP", ascending=True)

            sex_bar = px.bar(
                sorted, x="MEDREIMB_IP", y="Sex", orientation="h"
            )
            
            return sex_bar            

# Row 3
with ui.layout_columns():
    # Inpatient cost pie
    with ui.card(full_screen=True):
        ui.card_header("Responsibility by inpatient cost")

        @render_widget
        def plot_ip_pie():

            #ip = create_responsibility_pie_df(rxr, "Inpatient")
            ip = f_responsibility_ip()

            ip_pie = px.pie(ip, names="Responsibility", values="Amount")

            return ip_pie

    # Outpatient cost pie
    with ui.card(full_screen=True):
        ui.card_header("Responsibility by outpatient cost")

        op = create_responsibility_pie_df(rxr, "Outpatient")

        @render_widget
        def plot_op_pie():
            op_pie = px.pie(op, names="Responsibility", values="Amount")

            return op_pie

    # Carrier cost pie
    with ui.card(full_screen=True):
        ui.card_header("Responsibility by carrier cost")

        car_ = create_responsibility_pie_df(rxr, "Carrier")

        @render_widget
        def plot_car_pie():
            car_pie = px.pie(car_, names="Responsibility", values="Amount")

            return car_pie            

# Row 4
with ui.layout_columns():

    # Indicator frequency
    with ui.card(full_screen=True):
        ui.card_header("Frequency of indicators")
        @render_widget
        def indicator_frequency():
            # oh jesus make this a function
            indicators_bin = nj[INDICATORS].replace({2: 0})
            indicators_count = indicators_bin.sum().reset_index().rename(columns={"index": "Indicator", 0: "count"})
            sorted = indicators_count.sort_values("count", ascending=True)
            sorted["percent"] = sorted["count"] / len(indicators_bin)

            indicator_bar = px.bar(
                sorted, x="count", y="Indicator", orientation="h", hover_data="percent"
            )

            return indicator_bar            

    # Indicator cooccurrence (raw)
    with ui.card(full_screen=True):
        ui.card_header("Raw cooccurrence of indicators")
        @render_widget
        def cooccurrence_raw():

            indicators_bin = nj[INDICATORS].replace({2: 0})
            coc = cooccurrence(indicators_bin)
            hm = px.imshow(coc)

            return hm

    # Indicator cooccurrence (col | row)
    with ui.card(full_screen=True):
        ui.card_header("Cooccurrence of indicators (col | row)")
        @render_widget
        def cooccurrence_rows():

            # TODO: move outside functions, since duplicated?
            indicators_bin = nj[INDICATORS].replace({2: 0})
            cocr = cooccurrence(indicators_bin, columns=INDICATORS, convert_pct_by="rows")
            # TODO: zero the diagonal
            hm = px.imshow(cocr)

            return hm            
