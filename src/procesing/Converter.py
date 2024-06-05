# All accepted units
Units = ["b", "kb", "mb", "gb", "tb", "mp", "mah", "€", "euro", "euros", "eur", "$", "dollar", "dollars","usd", "cm", "inches", "inch", "m", "mm", "px", "pixels", "pixel"]

# Pixel related units
PxUnits = ["px", "pixels", "pixel"]

# Size related units
SizeUnits = ["b", "kb", "mb", "gb"]

# Generations
Generations = ["1g", "2g", "3g", "4g", "5g"]

# Dictionary to make the units-column_name convertion
unitsToColumn = {
    "mah" : "battery_mah",
    "€" : "price_euro",
    "euro" : "price_euro",
    "euros" : "price_euro",
    "eur" : "price_euro",
    "$" : "price_euro",
    "dollar" : "price_euro",
    "dollars" : "price_euro",
    "usd" : "price_euro",
    "cm" : "screen_size_cm",
    "inches": "screen_size_cm",
    "inch" : "screen_size_cm",
    "m": "screen_size_cm",
    "mm": "screen_size_cm",
    "px": "resolution_x",
    "pixels" : "resolution_x", 
    "pixel" : "resolution_x", 
    "mp" : "rear_camera_mp"
}

# Dictionary to make the convertions between units
conversionTable = {
    "inches" : 2.54,
    "inch" :  2.54,
    "m" : 1 / 100,
    "mm" : 10,
    "tb" : 2**10,
    "mb" : 1 / (2**10),
    "kb" : 1 / (2**20),
    "b" : 1 / (2**30),
    "inr" : 0.011,
    "usd" : 0.93,
    "$" : 0.93,
    "dollars": 0.93,
    "dollar" : 0.93
}

# Dictionary to make the convertion between non numerical words to a numerical value
adjectivesTable = {
    "battery_mah" : {
        "long" : 4500,
        "excellent" : 4500,
        "great" : 4000,
        "standard" : 3500,
        "good" : 3000,
        "bad" : 2000
    },
    "ram_gb":{
        "fast" : 12,
        "speed" : 12,
        "excellent" : 8,
        "great" : 6,
        "standard" : 4,
        "slow" : 2,
        "minimal" : 1
    },
    "internal_storage_capacity_gb":{
        "huge" : 512,
        "massive" : 256,
        "excellent": 128,
        "high": 64,
        "lot" : 32,
        "standard" : 16,
        "small" : 8,
        "little" : 8,
        "minimal" : 4
    },
    "screen_size_cm": {
    "huge" : 16.51,
    "giant" : 16.51,
    "large" : 15.24,
    "standard" : 13.97,
    "small" : 12.7,
    "tiny" : 11.43
    },
    "price_euro":{
        "cheap": 200,
        "affordable": 300,
        "reasonable": 400,
        "economical": 500,
        "standard": 600,
        "expensive": 700,
        "premium": 800,
        "luxurious": 1000
    },
    "rear_camera_mp":{
        "excellent": 45,
        "great": 30,
        "standard": 20,
        "good": 12,
        "bad": 8
    },
    "front_camera_mp":{
        "excellent": 45,
        "great": 30,
        "standard": 20,
        "good": 12,
        "bad": 8
    }
    
}

# Convert inches to cm
def inchesToCm(value):
    return round(value * conversionTable["inch"], 2)

# Convert mb to gb
def mbToGb(value):
    return round(value * conversionTable["mb"], 2)

# Convert int to eur
def inrToEuro(value):
    return round(value * conversionTable["inr"], 2)



# Convert any accepted unit to the standard units how are stored in dataframe
def unitsToStandard(units, value) -> float:
    if units in conversionTable.keys():
        return round(value * conversionTable[units], 2)
    return round(value, 2)

# Convert any qualitative word to an aproximated number
def adjAdvToStandard(value, column):
    if value in adjectivesTable[column].keys():
        return str(adjectivesTable[column][value]) + "~"
    return str(adjectivesTable[column]["standard"]) + "~"

# Get column by its units
def getColumnsByUnits(units):
    return unitsToColumn[units]