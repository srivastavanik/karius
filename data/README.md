# Data Directory

This directory is used to store data files for ingestion into the Karius Market Expansion AI application.

## Expected Data Files

Place your data files in this directory using the following naming conventions:

- `who_sample.csv`: WHO health data (for use with `--source who_csv`)
- `cdc_data.csv`: CDC health data (for use with `--source cdc_api`)
- `pubmed_data.json`: PubMed research data (for use with `--source pubmed_api`)
- `market_reports.xlsx`: Purchased market reports (for use with `--source purchased`)

## Sample Data Structure

Each data source has different expected columns/structure:

### WHO CSV Format (Example)

```
IndicatorCode,IndicatorName,Location,Period,Dim1,Dim1Type,Dim2,Dim2Type,Dim3,Dim3Type,Value,Low,High,StdErr,StdDev,Comments
MALARIA_CASES,Malaria cases,United States of America,2020,TOTAL,"","","","","",1200,1100,1300,50,80,"Annual reported"
MALARIA_CASES,Malaria cases,Brazil,2020,TOTAL,"","","","","",120000,118000,122000,1000,2000,"Annual reported"
```

### CDC CSV Format (Example)

```
LocationID,Location,DataSource,Indicator,Year,TimeFrame,Value,ValueType,LowConfidenceLimit,HighConfidenceLimit,CategoryID,DataValueTypeID
1,United States,CDC Survey,Hospital Admissions,2021,Annual,1500000,Count,1450000,1550000,ID1,ID2
```

## Downloading Sample Data

You can download sample data from the following sources:

### WHO Data
Visit the WHO Athena API at https://apps.who.int/gho/athena/api/GHO and download data in CSV format.

### CDC Data
Visit the CDC Open Data Portal at https://data.cdc.gov and download datasets in CSV format.

### PubMed Data
Use the PubMed API to download medical research data. See https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/

## Adding Your Own Data

You can add your own custom data files, but make sure they have the appropriate structure that matches with the ingestion scripts. You may need to modify the ingestion scripts (`scripts/ingest.py`) to handle your custom data format. 