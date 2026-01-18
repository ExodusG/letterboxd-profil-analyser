# Letterboxd Profil Analyser 
Letterboxd stat | Letterboxd analysis

---

## 🚀 Overview

This is a **free and open-source project** made by movie lovers, for movie lovers.  
We wanted a fun and interactive way to explore data from our Letterboxd profiles — so we built this app.

With this tool, you can visualize your **watchlist**, **reviews**, **ratings**, and **watched movies** using beautiful interactive charts.

---

## 🛠️ Installation

1. Clone or fork the repo

2. Install python dependencies

```bash
pip install -r requirements.txt
```

3. Add your secrets in ./streamlit/secrets.tolm

```toml
API_KEY_ARRAY=["YOU_API_KEY"]
prod="true for prod"
dns="sentry dns"
sheet_name="name file of gsheet"
[gcp_service_account]
#All the google drive app key
```
4. Run the streamlit app

```bash
python3 -m streamlit run Account_analysis.py
```
or 

```bash
streamlit run Account_analysis.py
```

## ⚙️ Tech

This app is entirely built with Python

For the **back** : 
- Pandas for data manipulation
- Other utility libraries (see [requirements.txt](./requirements.txt) )

For the **front** : 

- Plotly for interactive charts
- Streamlit for the interface

For the **storage**

- Movie data is cached in a Google Spreadsheet
- We also store the name of the ZIP file for easier debugging in case of import / request error

## 🎬 Movie Data API

We use the [Open Movie Database](https://www.omdbapi.com/) to fetch movie data.

Please note : 
 - Some Letterboxd movie [title, year] may not match with OMDB, leading to missing or incorrect data
- OMDB API has a limit of 1000 requests per day

For large accounts, this can be a bottleneck — we're considering switching to the [TMDB API](https://www.themoviedb.org/) for better coverage 


## ⚙️ How the app work 

We chose not to scrape Letterboxd (due to their policies and performance concerns), and we don’t have access to their official API for public analysis.

Instead, we rely on user-exported data:

- You upload your ZIP export from Letterboxd (includes watchlist, ratings, reviews, etc.)

- We process each NEW movie with OMDb and cache the data in a Google Sheet

- Over time, as more users contribute, the dataset grows and becomes faster to process


Plus, with the letterboxd data export we can process more account data : all the watchlist, all the movie watched, all rating, the reviews ...

## 📊 Features

The app is split into 3 main sections:

- Watched: Explore your full watched history

- Watchlist: See what’s waiting to be watched

- Ratings: Analyze how you rate movies

We want to add radar graph of the profil, compare 2 profil and more ...

## 💬 Contributing / Ideas
This app is created by me and [Montro](https://github.com/Montr0-0)

We're happy to hear suggestions or feature requests!
Open an issue or create a pull request.