import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output



# --SETTING UP DATA--

counties_gdf = gpd.read_file("colorado-counties.geojson")
# print("Boundary Columns:", counties_gdf.columns)

crimes_df = pd.read_csv("colorado_crimes.csv")
crimes_df["county_name"] = crimes_df["county_name"].str.split(",")
crimes_df = crimes_df.explode("county_name")
crimes_df["county_name"] = crimes_df["county_name"].str.strip().str.title()
crimes_df["incident_date"] = pd.to_datetime(crimes_df["incident_date"], format="%m/%d/%Y")
crimes_df["year"] = crimes_df["incident_date"].dt.year
crimes_df = crimes_df.dropna(subset=["year"])
crimes_df["year"] = crimes_df["year"].astype(int)
crimes_df['month'] = pd.to_datetime(crimes_df['incident_date']).dt.to_period('M').dt.to_timestamp()

# for dropdown
the_years = sorted(crimes_df["year"].unique())



shorten_name = {
        "Destruction/Damage/Vandalism of Property": "Vandalism/Property Damage",
        "Pornography/Obscene Material": "Porn/Obscene Material",
        "Theft of Motor Vehicle Parts or Accessories": "Auto Parts Theft",
        "Theft from Coin-Operated Machine or Device": "Theft from Coin-Operated Machine",
        "False Pretenses/Swindle/Confidence Game": "False Pretenses/Swindle"
    }

crimes_df["offense_name"] = crimes_df["offense_name"].map(shorten_name).fillna(crimes_df["offense_name"])
crimes_df["offense_category_name"] = crimes_df["offense_category_name"].map(shorten_name).fillna(crimes_df["offense_category_name"])


# print("Offense Categories:", crimes_df[["offense_category_name", "crime_against"]].drop_duplicates().sort_values("crime_against"))

# had plan to use crime_against for color coding but it looked unappealing and inconsistent across categories
# color_map = {
#     "Person": "Reds",
#     "Property": "Greens",
#     "Society": "Blues",
#     "All": "YlOrRd"
# }

# --SETTING UP GLOBAL STYLES--

pio.templates.default = "plotly_white"
pio.templates["plotly_white"]["layout"]["xaxis"]["showgrid"] = True
pio.templates["plotly_white"]["layout"]["yaxis"]["showgrid"] = True
pio.templates["plotly_white"]["layout"]["xaxis"]["gridcolor"] = 'lightgray'
pio.templates["plotly_white"]["layout"]["yaxis"]["gridcolor"] = 'lightgray'



# --DASHBOARD SETUP--

app = Dash(__name__)

app.layout = html.Div(
    style={"padding": "20px", "fontFamily": "Verdana, sans-serif", "backgroundColor": "#fdfdfd"},
    children=[
        html.H1("Colorado Crimes Dashboard (2016-2023)", style={"textAlign": "center", "marginBottom": "20px"}),
        # controls
        html.Div([
            html.Div([
                html.Label("Select Year:", style={"fontWeight": "bold"}),
                dcc.Slider(
                    id="year-slider",
                    min=min(the_years),
                    max=max(the_years),
                    value=min(the_years),
                    marks={str(year): str(year) for year in the_years},
                    step=None
                )
            ], style={"marginBottom": "20px"}),
            
            html.Div([
                html.Label("Select Crime Category:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="crime-type-dropdown",
                    options=[{"label": "All Crimes", "value": "All"}] + 
                            [{"label": cat, "value": cat} for cat in crimes_df["offense_category_name"].unique()],
                    value="All",
                    clearable=False,
                    style={"width": "50%"}
                ),
            ])
        ], style={"marginBottom": "30px", "padding": "15px", "backgroundColor": "#f8f9fa", "borderRadius": "5px"}),
        
        # main dashboard
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "60% 40%", "gap": "20px", "width": "100%"},
            children=[
                
                # left col
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "width": "100%"},
                    children=[
                        html.Div(
                            style={"border": "1px solid #e3e3e3", "borderRadius": "5px", "padding": "10px", "backgroundColor": "white"},
                            children=[
                                html.H3(
                                    "Colorado Crime Map",
                                    style={"marginBottom": "10px", "textAlign": "center"}
                                ),
                                dcc.Graph(
                                    id="crime-map",
                                    style={"width": "100%", "height": "600px"},
                                    config={"responsive": True, "displayModeBar": False}
                                )
                            ]
                        ),
                        # the bottom profile summary section
                        html.Div(
                            style={"width": "100%", "padding": "20px", "borderRadius": "8px", "boxSizing": "border-box", "backgroundColor": "white", "border": "1px solid #e3e3e3"},
                            children=[
                                html.H3(id="profile-title",style={"marginBottom": "10px", "textAlign": "center"}),
                                html.Div(
                                    style={"display": "flex", "justifyContent": "space-around", "gap": "20px"},
                                    children=[
                                        html.Div([
                                            html.Label("Historical Record Total"),
                                            html.H4(id="historical-record-total")
                                        ]),
                                        html.Div([
                                            html.Label("Yearly Offense Total"),
                                            html.H4(id="yearly-offense-total")
                                        ]),
                                        html.Div([
                                            html.Label("Most Common Offense"),
                                            html.H4(id="most-common-offense")
                                        ]),
                                        html.Div([
                                            html.Label("Most Affected County"),
                                            html.H4(id="most-affected-county")
                                        ])
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                # right col
                html.Div(
                    style={
                        "width": "100%", 
                        "display": "flex", 
                        "flexDirection": "column", 
                        "gap": "25px",
                        "boxSizing": "border-box"
                    },
                    children=[
                        html.Div(
                            children=[  
                                html.Div(
                                    style={"border": "1px solid #e3e3e3", "borderRadius": "5px", "padding": "10px", "backgroundColor": "white"},
                                    children=[
                                        html.H3(
                                            "County Specific Offense Breakdown",
                                            style={"marginBottom": "10px", "textAlign": "center"}
                                        ),
                                        dcc.Graph(
                                            id="county-offense-graph",
                                            style={"width": "100%", "height": "400px"},
                                            config={"responsive": True, "displayModeBar": False}
                                        )
                                    ]
                                ),
                            ]
                        ),

                        html.Div(
                            style={
                                "border": "1px solid #e3e3e3", 
                                "borderRadius": "8px", 
                                "padding": "15px 20px", 
                                "backgroundColor": "white",
                                "boxShadow": "0 4px 6px rgba(0,0,0,0.02)"
                            },
                            children=[
                                dcc.Tabs(
                                    id="statewide-tabs", 
                                    value="tab-state-categories",
                                    parent_style={"fontFamily": "Arial, sans-serif"},
                                    children=[
                                        dcc.Tab(
                                            label="Crimes by Categories", 
                                            value="tab-state-categories", 
                                            style={"padding":"10px","fontWeight": "600"}, 
                                            selected_style={
                                                "padding":"10px",
                                                "fontWeight": "600" ,
                                                "borderTop": "3px solid #007bff"
                                                }
                                            ),
                                        dcc.Tab(
                                            label="Crimes by Age Group", 
                                            value="tab-state-age-groups", 
                                            style={"padding":"10px","fontWeight": "600"}, 
                                            selected_style={
                                                "padding":"10px",
                                                "fontWeight": "600", 
                                                "borderTop": "3px solid #9b59b6"
                                                }
                                            ),
                                        dcc.Tab(
                                            label="Crimes by Month",
                                            value="tab-state-months", 
                                            style={"padding":"10px","fontWeight": "600"},
                                            selected_style={
                                                "padding":"10px",
                                                "fontWeight": "600", 
                                                "borderTop": "3px solid #2ecc71"
                                                }
                                            ),
                                    ]
                                ),
                                html.Div(
                                    id="month-views-container",
                                    style={"marginTop": "15px", "textAlign": "center"},
                                    children = [
                                        html.Label("Trend View:", style={"fontWeight": "bold"}),
                                        dcc.RadioItems(
                                            id="trend-view-type",
                                            options=[
                                                {"label": "Overall", "value": "overall"},
                                                {"label": "By Top Categories", "value": "by_category"},
                                                {"label": "By Age Group", "value": "by_age_group"}
                                            ],
                                            value="overall",
                                            inline=True,
                                            style={"display": "inline-block"}
                                        )
                                    ]
                                ),
                                html.H3(
                                    "Statewide Crime Overview",
                                    style={
                                        "marginTop": "15px",
                                        "marginBottom": "10px",
                                        "textAlign": "center"
                                    }
                                ),
                                dcc.Graph(
                                    id="statewide-overview-graph",
                                    style={"width": "100%", "height": "400px"},
                                    config={"responsive": True, "displayModeBar": False}
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# --CALLBACKS--

# THE PROFILE SUMMARY
@app.callback(
    [
        Output("yearly-offense-total", "children"),
        Output("most-common-offense", "children"),
        Output("most-affected-county", "children"),
        Output("historical-record-total", "children"),
        Output("profile-title", "children")
    ],
    [
        Input("year-slider", "value"),
        Input("crime-type-dropdown", "value")
    ]
)
def update_profile_summary(year, crime_type):
    profile_df = crimes_df[crimes_df["year"] == year]
    
    if crime_type != "All":
        profile_df = profile_df[profile_df["offense_category_name"] == crime_type]

    if profile_df.empty:
        return "0", "None", "None", f"{len(crimes_df):,}"
    year_total = f"{len(profile_df):,}"


    if crime_type == "All":
        hist_total = len(crimes_df)
    else:
        hist_total = len(crimes_df[crimes_df["offense_category_name"] == crime_type])

    hist_total = f"{hist_total:,}"
    
    top_offense = profile_df["offense_name"].value_counts().idxmax()
    
    top_county = profile_df["county_name"].value_counts().idxmax()
    profile_title = f"Profile Summary ({crime_type})"
    return year_total, top_offense, top_county, hist_total, profile_title


# THE STATEWIDE OVERVIEW GRAPHS
@app.callback(
    Output("statewide-overview-graph", "figure"),
    [
        Input("year-slider", "value"),           
        Input("statewide-tabs", "value") ,
        Input("trend-view-type", "value")
    ]
)
def update_statewide_dashboard(year, tab, radio):
 
    filtered_df = crimes_df[crimes_df["year"] == int(year)]
    if filtered_df.empty:
        fig = px.bar(title=f"No data available for {year}")
        fig.update_layout(title_x=0.5)
        return fig
    # age_df = filtered_df.copy().dropna(subset=["age_num"])

    # age_num to age_group grouping
    filtered_df = filtered_df.dropna(subset=["age_num"])
    age_groups = ["Under 18", "18-21", "22-24", "25-34", "35-49", "50-64", "65+"]
    bins = [0, 17, 21, 24, 34, 49, 64, np.inf]

    filtered_df["age_group"] = pd.cut(filtered_df["age_num"], bins=bins, labels=age_groups)
    age_totals = filtered_df.groupby("age_group", observed=False).size().reset_index(name="total_crimes")

    
    if tab == "tab-state-age-groups":
        hover = []
        for age in age_totals["age_group"]:
            subset = filtered_df[filtered_df["age_group"] == age]
            top_offenses = (
                subset.groupby("offense_category_name")
                .size()
                .reset_index(name="count")
                .sort_values(by="count", ascending=True)
                .head(3)
            )
            if not top_offenses.empty:
                text_lines = [f" • {row['offense_category_name']}: {row['count']:,}" for _, row in top_offenses.iterrows()]
                hover.append("<br>".join(text_lines))
            else:
                hover.append("No category data")
        
        age_totals["top_offenses"] = hover


        fig = px.pie(
            age_totals, 
            names="age_group", 
            values="total_crimes", 
            title=f"Crime Distribution by Age Group in {year}",
            hole=0.4, 
            labels={"age_group": "Age Group", "total_crimes": "Total Crimes"},
            custom_data=["top_offenses"],
        )

        fig.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b>: %{value:,} crimes (%{percent})<br><br><b>Top Offenses:</b><br>%{customdata[0]}<extra></extra>",
            marker=dict(
                line=dict(color='black', width=0.5)
            )
        )

        fig.update_layout(title_x=0.5, showlegend=True, legend_title="Age Groups", margin={"l": 20, "r": 20, "t": 50, "b": 20})
        return fig
    elif tab == "tab-state-categories":
        category_counts = (
            filtered_df.groupby("offense_category_name")
            .size()
            .reset_index(name="total_crimes")
            .sort_values(by="total_crimes", ascending=False)
        )

        
        fig = px.bar(
            category_counts, 
            x="total_crimes",
            y="offense_category_name", 
            orientation="h", 
            title=f"Crimes by Category in {year}", 
            color="offense_category_name",
            labels={"offense_category_name": "Crime Category", "total_crimes": "Total Crimes"},
        )
        
        fig.update_layout(
            title_x=0.5,
            xaxis_title="Total Crimes", 
            yaxis_title="Crime Category",
            yaxis={
                "type": "category",
                "tickmode": "linear",
                "dtick": 1,
                "automargin": True 
            },
            showlegend=False,
            margin={"l": 150, "r": 20, "t": 50, "b": 50} ,
        )

        fig.update_xaxes(tick0=0, dtick=5000)
        # fig.update_coloraxes(showscale=False)

        fig.update_traces(
            marker=dict(
                line=dict(color='black', width=0.5)
            )
        )
        return fig
    elif tab == "tab-state-months":
        month_counts = (
            filtered_df.groupby("month")
            .size()
            .reset_index(name="total_crimes")
            .sort_values(by="month")
        )

        if radio == "by_category":
            top_cat = filtered_df["offense_category_name"].value_counts().head(5).index.tolist()
            trend = filtered_df[filtered_df["offense_category_name"].isin(top_cat)]
            month_category_counts = (
                trend.groupby(["month", "offense_category_name"])
                .size()
                .reset_index(name="total_crimes")
            )

         
            fig = px.line(
                month_category_counts, 
                x="month", 
                y="total_crimes", 
                color="offense_category_name",
                title=f"Top Monthly Trends by Category in {year}", 
                markers=True,
                labels={"month": "Month", "total_crimes": "Crimes", "offense_category_name": "Crime Category"}
            )
            fig.update_layout(
                title_x=0.5,
                xaxis_title="Month", 
                yaxis_title="Total Crimes",
                xaxis=dict(tickformat="%b"),
                legend_title="Crime Category",
                margin={"l": 50, "r": 20, "t": 50, "b": 50}
            )
        elif radio == "by_age_group":
            month_age_counts = (
                filtered_df.groupby(["month", "age_group"])
                .size()
                .reset_index(name="total_crimes")
            )
            fig = px.line(
                month_age_counts, 
                x="month", 
                y="total_crimes", 
                title=f"Monthly Crime Trends by Age Group in {year}", 
                markers=True,
                labels={"month": "Month", "total_crimes": "Total Crimes", "age_group": "Age Group"},
                color="age_group"
            )
            fig.update_layout(
                title_x=0.5,
                xaxis_title="Month", 
                yaxis_title="Total Crimes",
                xaxis=dict(tickformat="%b"),
                legend_title="Age Group",
                margin={"l": 50, "r": 20, "t": 50, "b": 50}
            )

            fig.update_traces(
                line=dict(width=2),
                marker=dict(line=dict(color='black', width=0.5))
            )
        
        else:
            
            fig = px.line(
                month_counts, 
                x="month", 
                y="total_crimes", 
                title=f"Monthly Crime Trends in {year}", 
                markers=True,
                labels={"month": "Month", "total_crimes": "Total Crimes"}
            )
            
            fig.update_layout(
                title_x=0.5,
                xaxis_title="Month", 
                yaxis_title="Total Crimes",
                xaxis=dict(tickformat="%b"),
                showlegend=False,
                margin={"l": 50, "r": 20, "t": 50, "b": 50}
            )
        fig.update_layout(
            xaxis=dict(
                tickformat="%b",
                dtick="M1",
                tickmode="linear"
            )
        )

        return fig


# THE COUNTY-SPECIFIC OFFENSE BREAKDOWN
@app.callback(
    Output("county-offense-graph", "figure"),
    [
        Input("year-slider", "value"),           
        Input("crime-type-dropdown", "value"),
        Input("crime-map", "clickData"),
        Input("crime-map", "selectedData")
    ]
)
def update_county_graph(year, crime_type, clickData, selectedData):

        
    trend_df = crimes_df.copy()
    trend_df = trend_df[trend_df["year"] == year]
    target_county = "All Counties"
    if clickData and (selectedData is not None or selectedData == {}):
        point = clickData["points"][0]
        loc = point.get("hovertext")
        if loc is not None and str(loc).strip() != "":
            loc = str(loc).strip()
            target_county = loc

        
    if crime_type != "All":
        trend_df = trend_df[trend_df["offense_category_name"] == crime_type]

    
    
    if target_county != "All Counties":
        trend_df = trend_df[trend_df["county_name"] == target_county]
        title = f"Top Offenses of {target_county} County in {year} ({crime_type})"
    else:
        title = f"Top Offenses of {target_county} in {year} ({crime_type})"

    
    top_offenses = (
        trend_df.groupby("offense_name")
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=True) 
        .tail(10) 
    )

    if trend_df.empty:        
        fig = px.bar(title=f"No data available for this selection")
        fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False}, title_x=0.5)
        return fig
    
    fig = px.bar(
        top_offenses,
        x="count",                      
        y="offense_name",                   
        orientation="h",                    
        title=title,
        color="count",   
        color_continuous_scale="YlOrRd",
        labels={"offense_name": "Offense", "count": "Number of Crimes"}
    )

    fig.update_traces(
        width=0.6,
        selector=dict(type="bar")
    )

    # fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(
        marker=dict(
            line=dict(color='black', width=0.5)
        )
    )
    
    return fig



# THE CHOROPLETH MAP
@app.callback(
    Output("crime-map", "figure"),
    [Input("year-slider", "value"), Input("crime-type-dropdown", "value")]
)
def update_map(year, crime_type):
    yearly_data = crimes_df[crimes_df["year"] == year]
    county_counts = yearly_data.groupby("county_name").size().reset_index(name="total_crimes")
    merged_gdf = counties_gdf.merge(county_counts, left_on="name", right_on="county_name", how="left")
    merged_gdf = merged_gdf.drop(columns=["county_name"])
    merged_gdf["total_crimes"] = merged_gdf["total_crimes"].fillna(0)

    if crime_type != "All":
        filtered_data = yearly_data[yearly_data["offense_category_name"] == crime_type]

        # color="Reds"
        county_counts = filtered_data.groupby("county_name").size().reset_index(name="total_crimes")
        merged_gdf = counties_gdf.merge(county_counts, left_on="name", right_on="county_name", how="left")
        merged_gdf = merged_gdf.drop(columns=["county_name"])
        merged_gdf["total_crimes"] = merged_gdf["total_crimes"].fillna(0)


    # empty
    if merged_gdf["total_crimes"].sum() == 0:
        fig = px.choropleth_map(
            merged_gdf,
            geojson=merged_gdf.__geo_interface__,
            locations=merged_gdf.index,
            color="total_crimes",
            hover_name="name",
            hover_data={"total_crimes": True},
            labels={"total_crimes": "Total Crimes"},
            map_style="carto-positron",
            center={"lat": 39.5501, "lon": -105.7821},
            zoom=6,
            opacity=0.7,
            color_continuous_scale=["#f0f0f0", "#f0f0f0"],
            title=f"No crime data available for {year} ({crime_type})"
        )
        fig.update_layout(title_x=0.5)
        return fig
        
    fig = px.choropleth_map(
        merged_gdf,
        geojson=merged_gdf.__geo_interface__,
        locations=merged_gdf.index,
        color="total_crimes",
        hover_name="name",
        hover_data={"total_crimes": True},
        labels={"total_crimes": "Total Crimes"},
        color_continuous_scale="YlOrRd",
        map_style="carto-positron",
        center={"lat": 39.5501, "lon": -105.7821},
        zoom=6,
        opacity=0.7
    )

    fig.update_layout(
        uirevision=True
    )
        
    fig.update_traces(
        hovertemplate="<b>%{hovertext} County</b><br>Total Crimes: %{z}<extra></extra>"
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode="event+select" 
    )
    
    return fig

# TOGGLE MONTHLY TRENDS RADIO BUTTONS
@app.callback(
    Output("month-views-container", "style"),
    [Input("statewide-tabs", "value")]
)

def toggle_radio(tab):
    if tab=="tab-state-months":
        return {"marginTop": "15px", "textAlign": "center", "display": "block"}
    else:
        return {"display": "none"}


# MAIN
if __name__ == "__main__":
    app.run(debug=True, dev_tools_ui = False)
