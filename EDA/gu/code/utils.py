import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def filter_by_title_w_keyword(df, keywords):
    """_summary_

    Args:
        df (pd.DataFrame): DataFrame to which filtering will be applied
        keywords (list of str): Keywords for filtering

    Returns:
        pd.DataFrame: DataFrame filtered by title
    """
    temp = []
    for keyword in keywords:
        temp.append(df[df.title.str.contains(keyword)])

    filtered_df = temp[0]
    for i in range(1, len(temp) - 1):
        filtered_df = pd.merge(
            filtered_df, temp[i], left_on="id", right_on="id", how="inner"
        )

    filtered_df = filtered_df.drop_duplicates()
    return filtered_df


def filter_by_content_w_keyword(df, keywords):
    """_summary_

    Args:
        df (pd.DataFrame): DataFrame to which filtering will be applied
        keywords (list of str): Keywords for filtering

    Returns:
        pd.DataFrame: DataFrame filtered by content
    """
    temp = []
    for keyword in keywords:
        temp.append(df[df.content.str.contains(keyword).astype(bool).fillna(False)])

    filtered_df = temp[0]
    for i in range(1, len(temp) - 1):
        filtered_df = pd.merge(
            filtered_df, temp[i], left_on="id", right_on="id", how="inner"
        )

    filtered_df = filtered_df.drop_duplicates()
    return filtered_df


def filter_by_keyword(df, keywords):
    """_summary_

    Args:
        df (pd.DataFrame): DataFrame to which filtering will be applied
        keywords (list of str): Keywords for filtering

    Returns:
        pd.DataFrame: DataFrame filtered by content and title
    """
    title_filtered_df = filter_by_title_w_keyword(df, keywords)
    content_filtered_df = filter_by_content_w_keyword(df, keywords)
    filtered_df = pd.concat(
        [title_filtered_df, content_filtered_df], axis=0
    ).drop_duplicates()
    return filtered_df


def parse_dates(date_str):
    return pd.to_datetime(date_str, errors="coerce")


def extract_day(datetime):
    return datetime.strftime("%Y-%m-%d")


def add_created_day_col(df):
    df["created_day"] = df.created_at.apply(extract_day)
    return df


def remove_commna(val):
    return val.replace(",", "")


def convert_str_to_int(val):
    if "만" in val:
        val = int(float(val.replace(",", "").replace("만", "")) * 10000)
    else:
        val = int(val)
    return val


def convert_str_to_float(val):
    if "만" in val:
        val = float(val.replace(",", "").replace("만", "")) * 10000
    else:
        val = float(val)
    return val


def timedelta_to_seconds(timedelta):
    return timedelta.seconds


def plot_per_day_post_counts_with_events(df, title, day_start, day_end, events=None):
    """_summary_

    Args:
        df (pd.DataFrame): DataFrame filtered by keywords
        title (str): Title of the graph
        day_start (str): Start date of the graph
        day_end (str): End date of the graph
        events (list of tuple(str, str, str), optional): In the case of special events,
        display them on the graph as vertical lines. These are represented as a list of
        tuples consisting of (date, color, event name). Defaults to None.

    Functions:
        Plot the information with counts by date on a graph.
    Returns:
        pd.DataFrame: DataFrame used to create the graph.
    """
    full_date_daily = pd.date_range(start=day_start, end=day_end, freq="D").to_frame(
        index=False, name="full_range_date"
    )
    full_date_daily["full_range_date"] = full_date_daily["full_range_date"].astype(str)

    df = df.loc[:, ["created_day", "title"]]

    per_day_view = df.groupby(df.created_day).agg(
        {
            "title": ["count"],
        }
    )

    per_day_view.columns = per_day_view.columns.droplevel(0)

    full_range_df = pd.merge(
        full_date_daily,
        per_day_view,
        left_on="full_range_date",
        right_on="created_day",
        how="left",
    )
    full_range_df = full_range_df.fillna(0)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=full_range_df["full_range_date"], y=full_range_df["count"], name="count"
        )
    )

    if events is not None:
        y_max = int(full_range_df["count"].max())
        for event in events:
            date, color, text = event
            if day_start <= date <= day_end:
                fig.add_shape(
                    type="line",
                    x0=date,
                    x1=date,
                    y0=0,
                    y1=y_max,
                    line=dict(color=color, width=2, dash="dash"),
                )
                fig.add_trace(go.Scatter(x=[date], y=[-1], text=[text], mode="text"))

    fig.update_layout(
        title=title,
        xaxis_title="date",
        yaxis_title="",
    )

    fig.show()
    return full_range_df


def plot_per_day_target_val_sum_with_events(
    df, title, target_val, day_start, day_end, events=None
):
    """_summary_

    Args:
        df (pd.DataFrame): DataFrame filtered by keywords
        title (str): Title of the graph
        day_start (str): Start date of the graph
        day_end (str): End date of the graph
        target_val (str): Selection of the column to be plotted on the graph
        events (list of tuple(str, str, str), optional): In the case of special events,
        display them on the graph as vertical lines. These are represented as a list of
        tuples consisting of (date, color, event name). Defaults to None.

    Functions:
        Plot the sum of the information (selected by 'target_val') by date on a graph.

    Returns:
        pd.DataFrame: DataFrame used to create the graph
    """
    full_date_daily = pd.date_range(start=day_start, end=day_end, freq="D").to_frame(
        index=False, name="full_range_date"
    )
    full_date_daily["full_range_date"] = full_date_daily["full_range_date"].astype(str)

    df = df.loc[:, ["created_day", target_val]]

    per_day_view = df.groupby(df.created_day).agg(
        {
            target_val: ["sum"],
        }
    )

    per_day_view.columns = per_day_view.columns.droplevel(0)

    full_range_df = pd.merge(
        full_date_daily,
        per_day_view,
        left_on="full_range_date",
        right_on="created_day",
        how="left",
    )
    full_range_df = full_range_df.fillna(0)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=full_range_df["full_range_date"], y=full_range_df["sum"], name="sum")
    )

    if events is not None:
        y_max = int(full_range_df["sum"].max())
        for event in events:
            date, color, text = event
            if day_start <= date <= day_end:
                fig.add_shape(
                    type="line",
                    x0=date,
                    x1=date,
                    y0=0,
                    y1=y_max,
                    line=dict(color=color, width=2, dash="dash"),
                )
                fig.add_trace(go.Scatter(x=[date], y=[-1], text=[text], mode="text"))

    fig.update_layout(
        title=title,
        xaxis_title="date",
        yaxis_title="",
    )

    fig.show()
    return full_range_df


def get_target_val_by_percent(df, target, percent):
    return int(df[target].quantile(percent))