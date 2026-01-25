# holds functions for generating donut charts for cinephile data

import plotly.graph_objects as go

from src.constants import PALETTE
from src.utils import compute_categories, make_movies_text

def donut_chart(data_handler, view_name):
    df = data_handler.get_dataframe(view_name)
    ref = data_handler.get_dataframe("ALL_MOVIES")
    data = _donut_chart_data(ref, df)
    fig = _donut_chart_fig(data)
    return fig


def _donut_chart_data(ref, df):
    result = compute_categories(ref, df)
    result['Films'] = result['category'].apply(
        lambda x: df[df['category'] == x]['Title'].tolist()
    )
    result['MoviesText'] = result['Films'].apply(
        lambda x: make_movies_text(x, split=False)
    )
    return result


def _donut_chart_fig(data):

    fig = go.Figure(go.Pie(
        labels=data['category'],
        values=data['number'],
        textinfo='label+percent',
        hole=0.7,
        marker=dict(colors=[PALETTE['orange'], PALETTE['vert'], PALETTE['bleu']]),
        textfont=dict(size=16),
        insidetextorientation='auto',
        pull=[0.3, 0.2, 0.1, 0],
        rotation=90,
        sort=False,
        customdata=data['MoviesText'],
    ))

    fig.update_traces(
        showlegend=False,
        hovertemplate='<b>%{label}</b><br>%{customdata}<extra></extra>'
    )

    fig.update_layout(
        margin=dict(t=20, b=20, r=20, l=20)
    )
    
    return fig