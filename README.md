# 🚦 Traffic Data Analysis using PySpark

This project focuses on analyzing **real-time traffic data** to uncover congestion patterns and peak-hour trends in urban areas. The analysis leverages the **TomTom Traffic API** for data collection and **PySpark** for large-scale data processing and analysis.

---

## 📌 Features

- 🔗 **Real-time Data Collection** – Fetches live traffic data from the **TomTom API**.
- ⚡ **Big Data Processing with PySpark** – Handles large datasets efficiently using transformations and aggregations.
- 📊 **Traffic Pattern Analysis** – Identifies congestion hotspots, peak traffic hours, and speed variations.
- 🌍 **Visualization** – Plots traffic density and congestion levels using Python libraries like `matplotlib` and `seaborn`.
- 🏆 **Recognition** – This project was **well-recognized by faculty** for its real-world relevance and technical depth.

---

## 📂 Project Structure

```bash
├── fetch_data.py        # Collects live traffic data from TomTom API
├── traffic_analysis.py  # Main PySpark script for data cleaning & analysis
├── visualize.py         # Visualization of traffic patterns
├── config.json / .env   # API keys and configuration
├── analysis.ipynb       # Jupyter notebook for testing & exploration
├── data/                # Raw & processed data (CSV/Parquet)
├── results/             # Graphs, plots, and outputs
└── README.md            # Project documentation
```

---

## ⚙️ Requirements

- Python 3.x
- [Apache Spark](https://spark.apache.org/) / PySpark
- [TomTom Traffic API](https://developer.tomtom.com/)
- Pandas, NumPy, Matplotlib, Seaborn

Install dependencies:

```bash
pip install pyspark pandas numpy matplotlib seaborn requests python-dotenv
```

---

## ▶️ How to Run

1. **Clone the repo**
   ```bash
   git clone https://github.com/architkiran/traffic-data-analysis.git
   cd traffic-data-analysis
   ```

2. **Set up API Key**
   - Create a `.env` file with:
     ```bash
     TOMTOM_API_KEY=your_api_key_here
     ```
     or use a `config.json`:
     ```json
     {
       "TOMTOM_API_KEY": "your_api_key_here"
     }
     ```

3. **Fetch Traffic Data**
   ```bash
   python fetch_data.py
   ```

4. **Run PySpark Analysis**
   ```bash
   python traffic_analysis.py
   ```

5. **Visualize Results**
   ```bash
   python visualize.py
   ```

---

## 📊 Sample Results

- Heatmaps of congestion hotspots
- Line plots showing average speed over time
- Peak-hour traffic trend analysis

---

## ✨ Future Work

- Integration with **real-time dashboards** (e.g., Streamlit / Dash).
- Predictive modeling using **Machine Learning** for traffic forecasting.
- Expand to multi-city analysis for broader insights.

---

## 👨‍💻 Author

**Archit Kiran Kumar**  
Master’s Student in Computer Science @ Boston University  
🔗 [LinkedIn](https://linkedin.com/in/architkiran) | [GitHub](https://github.com/architkiran)
