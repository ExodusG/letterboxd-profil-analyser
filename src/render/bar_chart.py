# holds functions for generating bar charts for people (actors, directors)

import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.utils import make_movies_text
from src.constants import PALETTE

def bar_chart(data_handler, view_name, x_axis_name, with_dots=False, reverse=False):
    df = data_handler.get_dataframe(view_name)
    match x_axis_name:
        case "Actors":
            data = _bar_people_data(df, "Actors")
        case "Director":
            data = _bar_people_data(df, "Director")
        case "Genre":
            data = _bar_genre_data(df)
        case "Runtime":
            data = _bar_runtime_data(df)
        case "Decade":
            data = _bar_decade_data(df)
        case _:
            raise ValueError(f"Unknown x_axis_name: {x_axis_name}")
    fig = _bar_chart_fig(data, with_dots, reverse)
    return fig


# data preparation
# output should have following structure :
# x | Count | MoviesText (used for hovertext)

def _bar_people_data(df, people_type):
    df_exploded = (
        df.dropna(subset=[people_type])
        .assign(Person=df[people_type].str.split(', '))
        .explode('Person')
    )
    top_people = df_exploded['Person'].value_counts().head(100).index
    df_exploded_top = df_exploded[df_exploded['Person'].isin(top_people)]

    people_movies = (
        df_exploded_top.groupby('Person')
        .agg(
            Count=('Title', 'count'),
            Movies=('Title', lambda x: ', '.join(sorted(set(x))))
        )
        .reset_index()
        .sort_values('Count', ascending=False)
    )
    
    people_movies['MoviesText'] = people_movies['Movies'].apply(lambda x: make_movies_text(x, split=True))

    # rename for consistency in plotting function
    people_movies.rename(columns={'Person': 'x'}, inplace=True)
    return people_movies
    
def _bar_genre_data(df):
    df_genres = df[['Name', 'Year','Genre']].dropna()
    df_genres['Genre'] = df_genres['Genre'].str.split(', ')
    df_genres_exploded = df_genres.explode('Genre')
    genre_counts = df_genres_exploded['Genre'].value_counts().sort_index().reset_index()
    genre_counts.columns = ['Genre', 'Count']
    genre_counts = genre_counts.sort_values('Count', ascending=False)

    # restructure for consistency in plotting function
    genre_counts.rename(columns={'Genre': 'x'}, inplace=True)
    genre_counts['MoviesText'] = genre_counts['x'].apply(
        lambda genre: ', '.join(
            f"{movie} ({year})" for movie, year in zip(
                df_genres_exploded[df_genres_exploded['Genre'] == genre]['Name'],
                df_genres_exploded[df_genres_exploded['Genre'] == genre]['Year']
            )
        )
    )
    return genre_counts

def _bar_runtime_data(df):
    df = df[(df['Runtime'] >= 10) & (df['Runtime'] <= 300)].copy()
    #bins = list(range(df['Runtime'].min(), df['Runtime'].max() + 10, 10))  # Bins de 10 minutes de 0 à 300 minutes
    bins = list(range(10, 301, 10))
    labels = [f'{i}-{i+9}' for i in bins[:-1]]
    df.loc[:, 'RuntimeBin'] = pd.cut(df['Runtime'], bins=bins, labels=labels, right=True, include_lowest=True)
    runtime_counts = df['RuntimeBin'].value_counts().sort_index().reset_index()
    runtime_counts.columns = ['RuntimeBin', 'Count']
    # restructure for consistency in plotting function
    runtime_counts.rename(columns={'RuntimeBin': 'x'}, inplace=True)
    runtime_counts['MoviesText'] = runtime_counts['x'].apply(
        lambda runtime_bin: ', '.join(
            f"{movie} ({runtime} min)" for movie, runtime in zip(
                df[df['RuntimeBin'] == runtime_bin]['Name'],
                df[df['RuntimeBin'] == runtime_bin]['Runtime']
            )
        )
    )
    return runtime_counts

def _bar_decade_data(df):
    df = df.dropna(subset=['Year']).copy()
    df['Year'] = df['Year'].astype(int)

    # Calcul du bin de 5 ans
    df['FiveYearBin'] = df['Year'].apply(lambda y: f"{(y//5)*5}-{(y//5)*5+4}")

    # Groupby sur la tranche de 5 ans
    grouped = (
        df.groupby('FiveYearBin')
        .agg(Number=('Title', 'count'), Movies=('Title', list))
        .reset_index()
        .sort_values('FiveYearBin')
    )
    grouped['MoviesText'] = grouped['Movies'].apply(make_movies_text)

    # restructure for consistency in plotting function
    grouped.rename(columns={'FiveYearBin': 'x', 'Number': 'Count'}, inplace=True)
    grouped = grouped[['x', 'Count', 'MoviesText']]
    return grouped

# plotting function

def _bar_chart_fig(data, with_dots, reverse):

    if not with_dots:
        colors = [PALETTE['orange'], PALETTE['vert'], PALETTE['bleu']]
        color_seq = [colors[i % len(colors)] for i in range(len(data))]

        fig = go.Figure(data=go.Bar(
            x=data['x'],
            y=data['Count'],
            text=data['Count'],
            textposition='inside',
            marker_color=color_seq,
            customdata=data['MoviesText'],
            hovertemplate='<b>%{x}</b><br>Films:<br>%{customdata}<extra></extra>',
        ))

        fig.update_layout(
            xaxis=dict(
                tickangle=-35,
                showgrid=False,
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=False,  # Prevent zooming or panning
                range=[-0.5, 14.5],  # Show 15 bars initially
            ),
            yaxis=dict(
                title='',
                showgrid=True,
                tickmode='array',
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True  # Prevent zooming or panning
            ),
            bargap=0.17,
            barcornerradius=8,
            showlegend=False,
            dragmode="pan",  # Disable dragging
        )

        if reverse:
            fig.update_xaxes(autorange="reversed")

        return fig

    else:  # with_dots
        bins = data['x'].tolist()
        bin_pos = np.arange(len(bins))
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=bin_pos,
            y=data['Count'],
            marker_color=PALETTE['orange'],
            opacity=0.10,
            width=0.95,
            showlegend=False,
            text=data['Count'],
            hovertemplate=None,
            hoverinfo='skip'
        ))

        for i, bin_label in enumerate(bins):
            sub_df = data[data['x'] == bin_label]
            if sub_df.empty:
                continue
            n_points = sub_df['Count'].iloc[0]
            count = sub_df['Count'].iloc[0]

            if n_points == 1:
                y = [count / 2]
            else:
                y = np.linspace(0.5, count - 0.5, n_points)

            x = bin_pos[i] + np.random.uniform(-0.35, 0.35, n_points)

            palette_keys = ['orange', 'vert', 'bleu']
            BIN_COLORS = [PALETTE[k] for k in palette_keys]

            movies_list = sub_df['MoviesText'].iloc[0].split(', ')
            customdata = movies_list[:n_points]

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                marker=dict(
                    color=BIN_COLORS[i % len(BIN_COLORS)],
                    size=9,
                    opacity=0.85,
                    line=dict(width=0)
                ),
                customdata=customdata,
                hovertemplate='<b>%{customdata}</b><extra></extra>',
                showlegend=False
            ))

        fig.update_layout(
            xaxis_title='',
            yaxis_title='',
            height=400,
            margin=dict(l=40, r=40, t=40, b=40),
            bargap=0.13,
            barcornerradius=7,
            xaxis=dict(
                tickmode='array',
                tickvals=bin_pos,
                ticktext=bins,
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
            yaxis=dict(
                fixedrange=True
            )
        )

        fig.update_yaxes(tickfont=dict(size=14), title_font=dict(size=16))

        if reverse:
            fig.update_xaxes(autorange="reversed")

        return fig