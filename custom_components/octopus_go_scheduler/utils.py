
import pandas as pd
import datetime

# --- Helper functions ---

def json_to_df(json_results):
    """ Convert the JSON API results to a pandas dataframe
    """

    df_carbon = pd.json_normalize(json_results['data']['data'])
    df_carbon.drop('generationmix', axis=1, inplace=True)

    # format extra columns
    df_carbon['from'] = pd.to_datetime(df_carbon['from'], format='%Y-%m-%dT%H:%MZ')
    df_carbon['to'] = pd.to_datetime(df_carbon['to'], format='%Y-%m-%dT%H:%MZ')
    df_carbon['intensity.forecast'] = df_carbon['intensity.forecast'].astype(float)
    df_carbon['hour'] = df_carbon['from'].dt.hour + df_carbon['from'].dt.minute/60
    df_carbon['hours_ahead'] = (df_carbon['from'] - datetime.now()).dt.total_seconds()/3600
    df_carbon['days_ahead'] = (df_carbon['from'].dt.date - datetime.now().date()).dt.days

    # extract generation mix
    timeperiods = len(json_results['data']['data'])
    results = []

    for i in range(timeperiods):
        genmix = json_results['data']['data'][i]['generationmix']
        df_gm = pd.DataFrame(genmix)
        df_gm = pd.DataFrame(columns= df_gm['fuel'].values, data = df_gm['perc'].values.reshape(1, -1))
        results.append(df_gm)

    df_genmix = pd.concat(results, axis=0).reset_index(drop=True)
    # merge generation mix with carbon intensity by adding columns
    df_carbon = pd.concat([df_carbon, df_genmix], axis=1)
    return df_carbon

def format_datetimes_for_ha(timestamps):
    """Simple helper function to format datetimes for the frontend
    
    Args:
        timestamps (list): List of datetime objects
    """
    values = timestamps.dt.strftime('%Y-%m-%d %H:%M')
    formatted =  [datetime.strptime(x, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc) for x in values]

    return formatted

def get_index(intensity):
    """
    Convert carbon intensity to index
    """

    intensity_indexes = {
        2021: [50, 140, 220, 330],
        2022: [45, 130, 210, 310],
        2023: [40, 120, 200, 290],
        2024: [35, 110, 190, 270],
        2025: [30, 100, 180, 250],
        2026: [25, 90, 170, 230],
        2027: [20, 80, 160, 210],
        2028: [15, 70, 150, 190],
        2029: [10, 60, 140, 170],
        2030: [5, 50, 130, 150],
    }

    current_intensity_index = intensity_indexes[datetime.now().year]

    if intensity < current_intensity_index[0]:
        return "very low"
    elif intensity < current_intensity_index[1]:
        return "low"
    elif intensity < current_intensity_index[2]:
        return "moderate"
    elif intensity < current_intensity_index[3]:
        return "high"
    else:
        return "very high"

