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

def plot_per_day_post_count_plotly_with_events(df, title, day_start, day_end, events, per_post_likes_threshold=0, per_day_views_threshold=0, x_axis='date', y_axis='count'):
    full_date_daily = pd.date_range(start=day_start, end=day_end, freq='D').to_frame(index=False, name='full_range_date')
    full_date_daily['full_range_date'] = full_date_daily['full_range_date'].astype(str)

    df = df.loc[df["likes"] > per_post_likes_threshold]
    df = df.loc[:, ["created_day", "views"]]
    
    per_day_view = df.groupby(df.created_day).agg({ # 일별 조회수의 합, 게시물의 수 count
        'views': ['sum', 'count'],  
    })

    per_day_view.columns = per_day_view.columns.droplevel(0)
    per_day_view = per_day_view.loc[per_day_view['sum'] > per_day_views_threshold]

    full_range_df = pd.merge(full_date_daily, per_day_view, left_on='full_range_date', right_on='created_day', how='left')
    full_range_df = full_range_df.fillna(0)

    # min max norm
    # full_range_df['count'] /= full_range_df['count'].max()
    
    fig = px.line(full_range_df, x="full_range_date", y="count", title=title)

    y_max = int(full_range_df['count'].max())
        
    for event in events:
        date, color = event
        if day_start <= date <= day_end:
            fig.add_shape(type="line", x0=date, x1=date, y0=0, y1=y_max, line=dict(color=color, width=2, dash='dash'))

    fig.update_layout(
        title=title,
        xaxis_title=x_axis,
        yaxis_title=y_axis,
    )

    fig.show()
    return full_range_df

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