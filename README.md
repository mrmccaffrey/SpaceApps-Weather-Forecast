ClimaCast
A Streamlit tool for checking 40-year historical weather patterns at specific coordinates. It hits the NASA POWER API to pull temperature, wind, and precip data for a specific calendar day across the last four decades to help estimate "likely" conditions for future outdoor planning.

How it works

The app takes a latitude, longitude, and a target date. It then:

Queries NASA's daily point API for that date for every year from (Year-40) to (Year-1).

Converts metric values (C and m/s) to Fahrenheit and MPH.

Classifies each day into labels like "Very Hot" or "Very Windy" based on set thresholds.

Plots the trends using Plotly to show if that specific day is getting warmer or wetter over time.

Setup

You'll need streamlit, requests, plotly, and pandas installed.

Bash
pip install streamlit requests plotly pandas
streamlit run test.py
Notes

Data Source: All data is pulled live from the NASA POWER (Prediction of Worldwide Energy Resources) project.

Accuracy: This is historical data, not a forecast. It calculates probability (e.g., "In the last 40 years, this day has been over 90°F 60% of the time").

Export: There is a built-in CSV download button if you want to pull the raw 40-year stack into Excel.
