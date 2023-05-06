# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:46:43 2023
"""

import locale
from datetime import datetime
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go

locale.setlocale(locale.LC_TIME, "us_US.UTF-8")


# Define a dictionary of colors for each country
COUNTRY_COLORS = {
    "Austria": "#FF00FF",
    "Belarus": "#0072b1",
    "Belgium": "#e6a000",
    "Bulgaria": "#bfef45",
    "Czech Republic": "#c4022b",
    "Finland": "#9300d3",
    "France": "#000000",
    "Germany": "#d45e00",
    "Hungary": "#FFD700",
    "Italy": "#5d5a5a",
    "Lithuania": "#FA8072",
    "Netherlands": "#9e9e00",
    "Poland" : "#CCCCFF",
    "Romania": "#a65959",
    "Slovakia": "#36648B",
    "Slovenia": "#7DF9FF",
    "Spain": "#c0c0c0",
    "Sweden": "#2ca02c",
    "Switzerland": "#f032e6",
    "Turkey": "#9FE2BF",
    "Ukraine": "#800080",
    "United Kingdom": "#ff0000"
}


def read_data(file_path: str) -> None:
    """Read the excel data file and preprocesses it."""
    return pd.read_excel(
        file_path,
        converters={
            "Baubeginn": pd.to_datetime,
            "erste Netzsynchronisation": pd.to_datetime,
            "Kommerzieller Betrieb": pd.to_datetime,
            "Abschaltung": pd.to_datetime,
            "Bau/Projekt eingestellt": pd.to_datetime
            }
        )

def conditions(row, date_limit):
    if row["Baubeginn"] <= date_limit:
        if pd.isnull(row["erste Netzsynchronisation"]) and pd.isnull(row["Kommerzieller Betrieb"]) and pd.isnull(row["Abschaltung"]) and pd.isnull(row["Bau/Projekt eingestellt"]):
            return True
        else:
            if (not pd.isnull(row["erste Netzsynchronisation"])) and row["erste Netzsynchronisation"] >= date_limit:
                return True
            elif (not pd.isnull(row["Kommerzieller Betrieb"])) and row["Kommerzieller Betrieb"] >= date_limit:
                return True
            elif (not pd.isnull(row["Bau/Projekt eingestellt"])) and row["Bau/Projekt eingestellt"] >= date_limit:
                return True
            return False
    return False



def process_data(df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    """Filter and compute the data and compute."""
    years = np.arange(1955, 2024)
    result = {}
    for year in years:
        mask = df.apply(conditions, axis=1, date_limit=datetime(year, 12, 31))
        data_year = df.loc[mask]
        data_year_grouped = data_year.groupby(by="Land").size()
        data_year_grouped.name = "number of reactors"
        result[year] = data_year_grouped
    return result


def plot_data(data: dict[int, pd.DataFrame]) -> None:
    """Plot the number of nuclear reactors under construction"""
    fig = go.Figure()
    
    # Get unique country names
    countries = set()
    for df in data.values():
        countries.update(df.index)
    countries = sorted(countries)

    # Loop through countries and add a trace for each country
    for country in countries:
        country_values = [df.get(country) for df in data.values()]
        
        fig.add_trace(go.Bar(
            x=list(data.keys()),
            y=country_values,
            name=country,
            marker=dict(
                color=COUNTRY_COLORS[country],
                line=dict(width=0),
                showscale=False,
                opacity=1
                ),
            hovertemplate="%{y}"
        ))

    fig.update_layout(
        title="Evolution of Nuclear Power Plant Construction in Europe:<br>Total Number of Nuclear Reactors Being Built by Country and Year",
        xaxis=dict(title=None,
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)"),
        yaxis=dict(title="Number of Nuclear Reactors under Construction",
                   showgrid=True, gridwidth=1, gridcolor="rgba(128, 128, 128, 0.1)"),
        barmode="stack",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(family="sans-serif", color="black", size=12),
        hovermode="x unified",
        hoverlabel=dict(font=dict(size=12)),
        width=997,
        height=580,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            tracegroupgap=20,
            font=dict(size=10),
            itemwidth=60
            )
        )
    
    # Apply the fixed axis ranges.
    fig.update_yaxes(range=[0, 105])

    # Save the plot as an HTML file
    fig.write_html("index.html")

    # Show the figure
    fig.show()


def main() -> None:
    """Execute the script."""
    FILE_NAME = "nuclear_power_plants.xlsx"
    # FILE_PATH = os.path.join(os.path.dirname(__file__), "data", FILE_NAME)

    FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ee-nuclear-commissioning", "data", FILE_NAME))

    # Read and preprocess the data
    df = read_data(FILE_PATH)

    # Process the data
    data = process_data(df)

    # Plot the data
    plot_data(data)


if __name__ == "__main__":
    main()
