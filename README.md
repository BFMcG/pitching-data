# pitching-data

The purpose of this project is to create a clean, accessible dataset of statistics for individual pitches thrown throughout an MLB season, made available for public use. This is accomplished through an ETL pipeline built on the Databricks platform, which collects/scrapes the data, cleans and transforms it, and finally formats it for public consumption. The resulting dataset has been published on Kaggle, where the files are available for CSV download.

pitching 2025: https://www.kaggle.com/datasets/brendanmcguinness/every-mlb-pitch-2025

pitching 2026:


## pitch-data-2025
The data for the 2025 regular season was collected through Baseball Savant but was collected using three different methods (greater detail under Baseball Webscrape 2025). The 2025 data was a one-time pipeline, since all of that year's data was already available. The data was collected all at once, and the pipeline was run once.

<img src="images/Pipeline Job 2025.png" width="400">
<img src="images/Pipeline Run 2025.png" width="400">


### Baseball Webscrape 2025
Each step in the web scraping process used the request package to collect data from the Baseball Savant website. Additionally, the data was collected one day at a time to ensure that there was an accurate number of pitches collected each day across the three methods

Web scraping steps:
  1) **Pitcher collection**
     
     Collecting the name and ID of each pitcher that pitched on the specified date using Beautiful Soup, storing them in a dictionary list.
     
  2) **Total Pitching**

     Using the pitcher names, the scraper iterates through each pitcher in the dictionary list, reading the HTML text from the get request. The collected data is stored in a temporary data frame. The most important attribute from this data is the total number of pitches thrown by a pitcher in an outing (something not directly available from other sources).
     
  3) **Attack Zone**

     This data is collected using the same process, except instead of collecting the data one player at a time, it's collected one attack zone at a time. This allows for a new column that indicates which attack zone the pitch was thrown in. The data is also reads a CSV, eliminating the need for the player dictionary list.
     
  4) **Pybaseball**
     
     Pybaseball is a Python wrapper that can collect individual pitching data. It's collected using the same method as total pitching, except the players are iterated through the stat_cast() function using the specified date and the pitcher's ID.
     
  5) **Testing and Appending**
     The final step checks whether the same number of pitches were collected across the three methods of data collection. If false, an error is raised. If true,  then the data from each of the methods are converted to a Pyspark dataframe and are appended to their respective tables in the bronze schema.

### Silver Notebook
The silver layer focuses on doing the heavy cleaning involved with each data table. The cleaning process includes filtering out all of the unnecessary columns, locating and addressing null values, and changing column types. Additionally, the Total Pitching table, since it was scraped using the HTML method needs additional cleaning including parcing data into seperate columns, extracting and deleting data from columns, and renaming columns and row values using dictionary maps.

### Gold Notebook

## pitch-data-2026
### Baseball Webscrape 2026e
### Bronze Notebook (Daily)
### Silver Notebook
### Gold Notebook
