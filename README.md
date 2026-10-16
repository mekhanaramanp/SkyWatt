# Weather-Based Energy Consumption Prediction Using Machine Learning

## Project Overview
Electricity demand is heavily dependent on weather conditions. High temperatures in summer trigger extensive air conditioning use, while sub-zero winter temperatures drive heating loads. Conversely, pleasant spring or autumn days see lower energy consumption. 

This project implements a complete end-to-end Machine Learning pipeline to predict hourly grid energy consumption (in Megawatts, MW) based on historical weather variables. 

### Real-Life Applications
- **Smart Grid Operations**: Load balancing and scheduling generator sets.
- **Power Distribution Companies**: Peak load forecasting to prevent blackouts.
- **Renewable Energy Planning**: Matching load profiles with weather-dependent solar/wind generation.
- **BEMS (Building Energy Management Systems)**: Optimizing climate control in large buildings.

---

## Dataset Description
The project merges two sources:
1. **Energy Consumption Data**: Hourly electricity demand (in MW) from American Electric Power (AEP), a major regional utility in the Eastern US.
2. **Weather Data**: Historical hourly weather metrics (Temperature, Humidity, Wind Speed, Pressure, Cloud Cover, and Weather Condition) fetched for Columbus, Ohio (the core load center of AEP) spanning October 2004 to August 2018.

### Features Utilized:
- **Temperature** (°C)
- **Humidity** (%)
- **Wind Speed** (km/h)
- **Pressure** (hPa)
- **Cloud Cover** (%)
- **Weather Condition** (Sunny, Cloudy, Rainy)
- **Hour** (0–23)
- **Day of Week** (Monday–Sunday)
- **Month** (1–12)
- **Year** (2004–2018)

---

## Machine Learning Pipeline
1. **Data Preprocessing & Cleaning**: Missing values were checked and duplicates removed.
2. **Feature Engineering**:
   - Parsed `Datetime` to extract `Hour`, `Day`, `Month`, `Year`, and `Weekday`.
   - Mapped `Weather Condition` categories to numerical codes (Sunny: 0, Cloudy: 1, Rainy: 2).
3. **Model Selection**: Trained and compared multiple regression algorithms.
4. **Evaluation**: Assessed performance using MAE, RMSE, and $R^2$ Score.

### Model Evaluation Results:

| Model | MAE (MW) | RMSE (MW) | $R^2$ Score |
| :--- | :--- | :--- | :--- |
| **Linear Regression** | 1,769.81 | 2,197.80 | 0.2798 |
| **Decision Tree Regressor** | 1,237.70 | 1,627.00 | 0.6053 |
| **Gradient Boosting Regressor** | 1,156.55 | 1,500.80 | 0.6642 |
| **Random Forest Regressor** | **976.32** | **1,291.95** | **0.7511** |

The **Random Forest Regressor** was selected as the deployment model due to its high accuracy ($R^2 = 0.7511$) and ability to learn non-linear decision bounds for weather-electricity dependencies.

---

## Streamlit Application
A premium, glassmorphism-themed Streamlit application was built to deploy the model.

### Key Features:
- **Interactive Sidebar**: Real-time slider inputs for weather elements (temperature, humidity, wind speed, pressure, cloud cover) and dropdown selectors for weather condition, hour, day, and month.
- **Dynamic Demand Gauge**: A polar gauge chart showing the predicted demand relative to historical bounds (9.5k MW to 25.7k MW), categorizing demand level as **Low**, **Medium**, or **High**.
- **Historical Comparison**: A bar chart comparing the live predicted value against the average historical consumption for that specific month and hour.
- **Contextual AI Insights**: Generates a natural-language description explaining *why* the demand level is predicted (e.g., thermal limits, peak hour effects) and provides operational advice for grid operators.
- **Historical Analytics**: Expander section displaying pre-rendered EDA visualizations (Temperature vs. Energy, Monthly boxplots, and Hourly lines).

---

## Installation & Setup

1. Clone or copy the `Weather_Energy_Prediction` project directory.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

### 1. View Model Training and EDA
To inspect or re-execute the training code, open and run the Jupyter notebook:
```bash
jupyter notebook notebook/model_training.ipynb
```

### 2. Launch the Web Application
Start the Streamlit dashboard:
```bash
streamlit run app.py
```
This will open the dashboard in your default web browser (typically at `http://localhost:8501`).
