ClimaCast

ClimaCast is a Streamlit application for exploring 40-year historical weather patterns at specific coordinates. By leveraging NASA’s POWER API, it provides temperature, wind, and precipitation data for a given calendar day over the past four decades, helping users estimate “likely” conditions for outdoor planning.


Features
	•	Query historical weather data for a specific latitude, longitude, and date.
	•	Convert metrics from Celsius (°C) and meters per second (m/s) to Fahrenheit (°F) and miles per hour (MPH).
	•	Classify each day into categories such as “Very Hot” or “Very Windy” based on thresholds.
	•	Visualize trends over 40 years with interactive Plotly plots to see if the day is getting warmer, wetter, or windier.
	•	Export raw 40-year data to CSV for further analysis.


How It Works
	1.	Input latitude, longitude, and a target calendar day.
	2.	The app queries NASA’s POWER daily point API for that date for every year from current year minus 40 to last year.
	3.	Converts metric values to imperial units.
	4.	Classifies the weather conditions based on pre-defined thresholds.
	5.	Generates interactive plots to illustrate historical trends in temperature, precipitation, and wind.
	6.	Calculates probabilities, e.g., “In the last 40 years, this day exceeded 90°F 60% of the time.”


Setup

Requirements
	•	Python 3.8+
	•	Streamlit
	•	Requests
	•	Plotly
	•	Pandas

Install dependencies using pip:

pip install streamlit requests plotly pandas

Running the App

streamlit run test.py


Notes
	•	Data Source: All data comes from NASA POWER (Prediction of Worldwide Energy Resources) API.
	•	Accuracy: ClimaCast uses historical data, not forecasts. Results reflect past trends, not future predictions.
	•	Export: Use the built-in CSV download button to save the raw 40-year dataset for external analysis in Excel or other tools.
