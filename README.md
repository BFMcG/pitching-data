# pitching-data

The purpose of this project is to create a clean, accessible dataset of statistics for individual pitches thrown throughout an MLB season, made available for public use. This is accomplished through an ETL pipeline built on the Databricks platform, which collects/scrapes the data, cleans and transforms it, and finally formats it for public consumption. The resulting dataset has been published on Kaggle, where the files are available for CSV download.

pitching 2025: https://www.kaggle.com/datasets/brendanmcguinness/every-mlb-pitch-2025

pitching 2026: https://www.kaggle.com/datasets/brendanmcguinness/every-mlb-pitch-2026


## pitch-data-2025
The data for the 2025 regular season was collected through Baseball Savant using three different methods (greater detail under Baseball Webscrape 2025). The 2025 data was a one-time pipeline, since all of that year's data was already available. The data was collected all at once, and the pipeline was run once.

<img src="images/Pipeline Job 2025.png" width="700">
<img src="images/Pipeline Run 2025.png" width="700">


### Baseball Webscrape 2025
Each step in the web scraping process used the request package to collect data from the Baseball Savant website. Additionally, the data is collected one day at a time to ensure that there is an accurate number of pitches collected each day across the three methods.

Web scraping steps:
  1) **Pitcher collection**
     
     Collects the name and ID of each pitcher who pitches on the specified date using Beautiful Soup and stores them in a dictionary list.
     
  2) **Total Pitching**

     Using the pitcher names, the scraper iterates through each pitcher in the dictionary list and reads the HTML text from the .get() request. The collected data is stored in a temporary data frame. The most important attribute from this data is the total number of pitches thrown by a pitcher in an outing (something not directly available from other sources).
     
  3) **Attack Zone**

     This data is collected using the same process, except instead of collecting the data one player at a time, it is collected one attack zone at a time. This allows for a new column that indicates which attack zone the pitch was thrown in. The data is also read from a CSV endpoint, eliminating the need for the player dictionary list.
     
  4) **Pybaseball**
     
     Pybaseball is a Python wrapper that can collect individual pitching data from Baseball Savant. The data is collected using the same method as total pitching, except the players are iterated through the stat_cast() function using the specified date and the pitcher's ID.
     
  5) **Testing and Appending**
     
     The final step checks whether the same number of pitches were collected across the three methods of data collection. If false, an error is raised. If true,  then the data from each of the methods are converted to a Pyspark dataframe and are appended to their respective tables in the bronze schema.

### Silver Notebook
The silver layer focuses on doing the heavy cleaning involved with each data table strictly using PySpark (no SQL). The cleaning process includes filtering out all of the unnecessary columns, locating and addressing null values, and changing column types. Additionally, the Total Pitching table, since it was scraped by reading HTML, needs additional cleaning. This includes parsing data into separate columns, extracting and deleting data from columns, and renaming columns and row values using dictionary maps. These transformations are written to the silver schema in their respective tables.

### Gold Notebook
The gold layer's responsibility is to merge and format for easy public access. The three tables are merged into one final table using multiple columns as keys. Once merged, the table is filtered and ordered for the final step, formatting. The table is split into months for easier CSV download (more convenient for storage or if someone requires only one month), and a player_identification dimension table is created with player_id as the foreign key. These tables are then written to the gold schema where they can be extracted.

## pitch-data-2026
The 2026 data was also collected from the Baseball Savant website. However, since the 2026 season is still being played, the data collection is on a fixed schedule, updating when the data is made available on Baseball Savant. Furthermore, since the data needs to be collected on a daily basis, the collection process was made more efficient to reduce run time and potential cost. This led to only one method being used since all necessary information could still be gathered from that resource. Furthermore, the data pipeline is being run on a daily schedule until the end of the regular season, which is at the end of September. 

<img src="images/Pipeline Job 2026.png" width="700">
<img src="images/Pipeline Run 2026.png" width="700">

### Baseball Webscrape 2026
This project started in the middle of the MLB season, so the purpose of this web scraper was to fetch all the pitching data until the end of July. Only steps 2. and 5. from the 2025 Webscrape were used for this collection, resulting in only one table being appended to the bronze schema.

### Bronze Notebook (Daily)
This notebook uses the same logic as the web scrape, except it isn't under a while loop and runs on a daily basis.

### Silver Notebook
This silver layer uses a similar process to the 2025 silver notebook, except Spark SQL is used in some cases. Instances of SQL usage include filtering columns and creating the total_pitch_count column.

### Gold Notebook
This gold layer replicates the same steps as the 2025 gold notebook, but doesn't require merging tables. It also uses Spark SQL logic, creating the player_identification table.
