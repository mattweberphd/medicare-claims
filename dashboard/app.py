import plotly.express as px

from shiny import reactive
from shiny.express import input, ui
from shinywidgets import render_widget

from shared import nj_counties, nj_counties_json, reimb_amt_ip

ui.page_opts(title="DeSynPUF dashboard", fillable=True)

with ui.sidebar(title="Filter controls"):
    ui.input_selectize("var", "Select variable", choices=["MEDREIMB_IP", "MEDREIMB_OP"])


# with ui.layout_column_wrap(fill=False):
#     with ui.value_box(showcase=icon_svg("earlybirds")):
#         "Number of penguins"

#         @render.text
#         def count():
#             return filtered_df().shape[0]

#     with ui.value_box(showcase=icon_svg("ruler-horizontal")):
#         "Average bill length"

#         @render.text
#         def bill_length():
#             return f"{filtered_df()['bill_length_mm'].mean():.1f} mm"

#     with ui.value_box(showcase=icon_svg("ruler-vertical")):
#         "Average bill depth"

#         @render.text
#         def bill_depth():
#             return f"{filtered_df()['bill_depth_mm'].mean():.1f} mm"


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Reimbursement amounts")

        @render_widget
        def county_bar():

            sorted = nj_counties.sort_values(input.var(), ascending=True)

            county_bar = px.bar(
                sorted, x=input.var(), y="COUNTY_LAB", orientation="h"
            )

            return county_bar

    with ui.card(full_screen=True):
        ui.card_header("Map of reimbursement")
        @render_widget
        def county_map():
            fig = px.choropleth(
                reimb_amt_ip,
                geojson=nj_counties_json, 
                locations='County Name',
                featureidkey="properties.COUNTY_LABEL", 
                color='MEDREIMB_IP',
                color_continuous_scale="Viridis",
                #range_color=(0, 12),
                scope="usa",
                labels={'MEDREIMB_IP':'Total inpatient reimbursement'}
            )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_geos(fitbounds="locations")

            return fig

# @reactive.calc
# def filtered_df():
#     filt_df = df[df["species"].isin(input.species())]
#     filt_df = filt_df.loc[filt_df["body_mass_g"] < input.mass()]
#     return filt_df
