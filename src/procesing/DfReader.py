import pandas as pd
import numpy as np
import procesing.Converter as conv

# Some column names that would be useful to develop a response
Columns = []
ColumnsNumeric = []
ResponseColumns = []
TranslateColumns = {}
ResponseUnits = {}

def readDf():
    global Columns
    global ColumnsNumeric
    global ResponseColumns
    global TranslateColumns
    global ResponseUnits
    # Read dataframe from phones.csv
    df = pd.read_csv("data/test6Phones.csv", sep=',')
    

    # Create list of columns with simplified names without units names to operate with user's inputs
    Columns = list(df.columns)
    Columns.remove("image")
    ResponseColumns = ["price_euro", "operating_system", "internal_storage_capacity_gb", "ram_gb", "screen_size_cm", "generation", "battery_mah"]
    TranslateColumns = {
        "operating_system": "OS",
        "ram_gb": "RAM",
        "internal_storage_capacity_gb": "Storage",
        "screen_size_cm": "Screen size",
        "price_euro": "Price",
        "generation": "Generation",
        "battery_mah": "Battery capacity"
    }
    ResponseUnits = {
        "operating_system": "",
        "ram_gb": "GB",
        "internal_storage_capacity_gb": "GB",
        "screen_size_cm": "cm",
        "price_euro": "€",
        "generation": "",
        "battery_mah": "mAh"
    }
    print(Columns)
    ColumnsNumeric = list(df.select_dtypes(include=np.number).columns)

    return df
    