import pandas as pd
import plotly.express as px

def filter_by_title_w_keyword(df, keywords):
    temp = []
    for keyword in keywords:
        temp.append(df[df.title.str.contains(keyword)])
    filtered_df = pd.concat(temp, axis=0).drop_duplicates()
    return filtered_df

def filter_by_content_w_keyword(df, keywords):
    temp = []
    for keyword in keywords:
        temp.append(df[df.content.str.contains(keyword).astype(bool).fillna(False)])        
    filtered_df = pd.concat(temp, axis=0).drop_duplicates()
    return filtered_df

def filter_by_keyword(df, keywords):
    title_filtered_df = filter_by_title_w_keyword(df, keywords)
    content_filtered_df = filter_by_content_w_keyword(df, keywords)
    filtered_df = pd.concat([title_filtered_df, content_filtered_df], axis=0).drop_duplicates()
    return filtered_df

def extract_day(datetime):
    return datetime.strftime('%Y-%m-%d')

def parse_dates(date_str):
    return pd.to_datetime(date_str, errors='coerce')

def add_created_day_col(df):
    df['created_day'] = df.created_at.apply(extract_day)
    return df

def filter_by_date_and_save_to_csv(df, day_start, day_end, filename):
    temp_df = df.loc[day_start <= df['created_day']]
    temp_df = temp_df.loc[df['created_day'] <= day_end]
    temp_df.to_csv(filename)
    return temp_df

def remove_commna(val):
    return val.replace(',','')

def convert_views_to_int(val):
    if '만' in val:
        val = int(float(val.replace(',','').replace('만', ''))*10000)
    else:
        val = int(val)
    return val