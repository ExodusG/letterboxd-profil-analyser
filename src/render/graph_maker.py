import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import src.utils as utils
from typing import Any, List
from wordcloud import WordCloud
import random
from plotly.subplots import make_subplots
from src.constants import PALETTE

class GraphMaker:
    
    def __init__(self):
        self.colors=list(PALETTE.values())

    def general_metrics_div(self, metrics):
        first_row = metrics[:3]
        second_row = metrics[3:5]
        palette = [PALETTE['orange'], PALETTE['vert'], PALETTE['bleu']]

        def make_block(metric, color):
            value, label, icon = metric
            return f"""
            <div class="metric-block" style="background:{color};">
                <span class="metric-icon">{icon}</span>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """

        div_content = f"""
        <h2 class="metrics-title">You have watched...</h2>
        <div class="metrics-grid">
            <div class="metrics-row">
                {''.join(make_block(metric, palette[i % len(palette)]) for i, metric in enumerate(first_row))}
            </div>
        </div>
        """
        div_content2 = f"""
        <h2 class="metrics-title">Your watchlist contains...</h2>
        <div class="metrics-grid">
            <div class="metrics-row">
                {''.join(make_block(metric, palette[(i+3) % len(palette)]) for i, metric in enumerate(second_row))}
            </div>
        </div>
        """

        div = f"""
        <div class="metrics-container">
            {div_content}
            {div_content2}
        </div>
        """

        return div

    def graph_mapW(self, df):
        
        custom_scale=["#40BCF4","#00E054","#FF8C00"]
        fig = go.Figure(go.Choropleth(
            locations=df["code"],
            z=df["count"],
            text=df["Country"],
            colorscale=custom_scale,
            showscale=False,
            hovertemplate="<b>%{text}</b><br>%{z} films<extra></extra>"
        ))

        fig.update_geos(
            showcoastlines=False,
            showland=True,
            landcolor="#0E1117",
            showocean=True,
            oceancolor="#0E1117",
            showframe=False,
            showcountries=True,
            countrycolor="gray",
            projection_type="natural earth"
        )

        fig.update_layout( 
            geo_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font=dict(color="white"),
            margin=dict(l=0, r=0, t=40, b=0)
        )

        return fig

    def graph_rating_director(self, df_plot):
        colors = [PALETTE['orange'], PALETTE['vert']]
        color_seq = [colors[i % len(colors)] for i in range(25)]
        fig = px.bar(
            df_plot,
            x='Director',
            y='Nb_Films',
            text='Nb_Films',
            color='Director',
            color_discrete_sequence=color_seq,
            custom_data="MoviesText"
        )
        for trace in fig.data:
            if trace.type == 'bar':
                trace.showlegend = False
        fig.update_traces(
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Films:<br>%{customdata[0]}<extra></extra>',
        )
        fig.update_layout(
            xaxis=dict(
                tickangle=-35,
                showgrid=False,
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
            yaxis=dict(
                title='Number of Movies',
                showgrid=True,
                tickmode='array',
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
            legend=dict(
                 yanchor="top",
                 xanchor="right"
            ),
            bargap=0.17,
            barcornerradius=8,
            # showlegend=False,
        )

        fig.add_scatter(x=df_plot['Director'],y=df_plot['Moyenne_Rating'], name='Mean Rating',mode='lines+markers',line=dict(color=PALETTE['bleu']), marker=dict(color=PALETTE['bleu']),showlegend=True)
        #fig.update_layout(xaxis_tickangle=-45)
        return fig

    def graph_rating_actor(self, df):
        colors = [PALETTE['orange'], PALETTE['bleu']]
        color_seq = [colors[i % len(colors)] for i in range(len(df))]
        fig = px.bar(
            df,
            x='Actor',
            y='Nb_Films',
            text='Nb_Films',
            color='Actor',
            color_discrete_sequence=color_seq,
            custom_data="MoviesText"
        )
        for trace in fig.data:
            if trace.type == 'bar':
                trace.showlegend = False
        fig.update_traces(
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Films:<br>%{customdata[0]}<extra></extra>',
        )
        fig.update_layout(
            xaxis=dict(
                tickangle=-35,
                showgrid=False,
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
            yaxis=dict(
                title='Number of Movies',
                showgrid=True,
                tickmode='array',
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
             legend=dict(
                 yanchor="top",
                 xanchor="right"
            ),
            bargap=0.17,
            barcornerradius=8,
            #showlegend=False,
        )
        fig.add_scatter(x=df['Actor'],y=df['Moyenne_Rating'], name='Mean Rating',mode='lines+markers',line=dict(color=PALETTE['vert']), marker=dict(color=PALETTE['vert']),showlegend=True)
        #fig.update_layout(xaxis_tickangle=-45)
        return fig

    def graph_genre_rating(self, df):
        fig = go.Figure()
        colors = [PALETTE['vert'], PALETTE['bleu']]
        color_seq = [colors[i % len(colors)] for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df['Genre'],
            y=df['Nombre de films'],
            name='Number of movie',
            yaxis='y1',
            text=df['Nombre de films'],
            marker_color=color_seq,
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=df['Genre'],
            y=df['Moyenne_Rating'],
            name='Mean rating',
            yaxis='y2',
            mode='lines+markers',
            marker_color=PALETTE['orange'],
            showlegend=True
        ))

        fig.update_layout(
            xaxis=dict(
                title='Genre',
                tickangle=-35,
                showgrid=False,
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True),
            yaxis=dict(
                title='Number of Movies',
                showgrid=True,
                tickmode='array',
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
            yaxis2=dict(
                title='Mean rating',
                overlaying='y',
                side='right',
                showgrid=False,
                fixedrange=True,
                range=[df['Moyenne_Rating'].min() - 0.5, df['Moyenne_Rating'].max() + 0.5]  # échelle personnalisée ici
            ),
            legend=dict(
                 yanchor="top",
                 xanchor="right"
            ),
            #legend=dict(x=1.02, y=0.99),
            #height=500
            bargap=0.17,
            barcornerradius=8,
            #showlegend=False,
        )
        return fig

    def graph_comparaison_rating(self, df, rating_df):
        fig = px.bar(df, x='imdbRating', y='Number of movie',labels={'imdbRating': 'Rating', 'Number of movie': 'Number of movie'},text='Number of movie',color_discrete_sequence=[PALETTE['vert']])
        fig.data[0].name = "Rating IMDB"
        fig.data[0].showlegend = True

        letterboxd_rate = rating_df.groupby('Rating').size().reset_index(name='Number of movie')
        
        fig.add_bar(x=letterboxd_rate['Rating'], y=letterboxd_rate['Number of movie'], name='Rating Letterboxd',text=letterboxd_rate['Number of movie'],marker=dict(color=PALETTE['bleu']))
        fig.update_layout(
            xaxis=dict(
                #tickangle=-35,
                showgrid=False,
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True,
                #tick0=0,      # point de départ
                #dtick=0.5,    # intervalle
                #range=[0, 10] 
            ),
            yaxis=dict(
                title='Number of Movies',
                showgrid=True,
                tickmode='array',
                tickfont=dict(size=14),
                title_font=dict(size=16),
                fixedrange=True
            ),
            legend=dict(
                 yanchor="top",
                 xanchor="right"
            ),
            bargap=0.17,
            barcornerradius=8,
            showlegend=True,
            barmode='group'
        )
        return fig

    def random_color_func(self,word, font_size, position, orientation, random_state=None, **kwargs):
        return random.choice([PALETTE['orange'], PALETTE['vert'], PALETTE['bleu']])

    def graph_generate_wordcloud(self, text, stopword):
        wordcloud = WordCloud(stopwords=stopword,width=800, height=400, background_color="#0e1117",max_words=120,color_func=self.random_color_func)
        wc=wordcloud.generate(text)
        fig, ax = plt.subplots(figsize = (20, 10),facecolor='k')
        ax.imshow(wc, interpolation = 'bilinear')
        plt.axis('off')
        return fig
    
    def movie_per_year(self, df):
        films_par_annee = df['Year'].value_counts().sort_index()

        df_par_annee = films_par_annee.reset_index()
        df_par_annee.columns = ['Year', 'Number of Movies']

        fig = px.line(df_par_annee, x='Year', y='Number of Movies', title='Number of movie per year')

        st.plotly_chart(fig)

    def graph_radar(self, scores_values, scores_names_display, hover_texts):

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores_values,
            theta=scores_names_display,
            fill='toself',
            line=dict(color=PALETTE['bleu']),
            line_width=0,
            name='Scores',
            hovertext=hover_texts,
            hoverinfo='text'
        ))

        fig.update_layout(
            polar=dict(
                bgcolor=PALETTE['gris'],
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=False,
                    ticks='',
                    gridcolor=PALETTE['blanc'],
                    showline=False
                ),
                angularaxis=dict(
                    tickfont=dict(
                        size=18,    
                        color=PALETTE['blanc']
                    ),
                    gridcolor=PALETTE['blanc']
                ),
            ),
            hoverlabel=dict(
                bgcolor=PALETTE['gris'],
                font_size=18,
                font_color='white',
                align='left'
            ),
            showlegend=False,
            margin=dict(t=30, b=30, l=20, r=20),
            height=550,
            dragmode=False
        )

        fig.update_traces(
            marker=dict(size=12, color=PALETTE['bleu']),
            selector=dict(type='scatterpolar')
        )

        return fig
    
    def two_div_four_films(self, first_list, second_list, first_word, second_word, final_text):

        first_imgs  = list(first_list['Poster'][:4]) if 'Poster' in first_list.columns else []
        second_imgs = list(second_list['Poster'][:4]) if 'Poster' in second_list.columns else []

        two_div = f"""
        <div class="two_div-flex">
        <div class="two_div-col">
            <div class="two_div-grid">
            {''.join([
                f'<div class="two_div-poster"><img src="{img}"><span class="two_div-tooltip">{title} ({year})</span></div>'
                if img else '<div class="two_div-poster"></div>'
                for img, title, year in zip(first_imgs, first_list["Title"][:4], first_list["Year"][:4])
            ])}
            </div>
            <div class="two_div-title">The 4 {first_word} films {final_text}</div>
        </div>
        <div class="two_div-col">
            <div class="two_div-grid">
            {''.join([
                f'<div class="two_div-poster"><img src="{img}"><span class="two_div-tooltip">{title} ({year})</span></div>'
                if img else '<div class="two_div-poster"></div>'
                for img, title, year in zip(second_imgs, second_list["Title"][:4], second_list["Year"][:4])
            ])}
            </div>
            <div class="two_div-title">The 4 {second_word} films {final_text}</div>
        </div>
        </div>
        """
        return two_div
    
    def two_div_five_films(self, first_list, second_list, final_text):

        first_imgs  = list(first_list['Poster'][:5]) if 'Poster' in first_list.columns else []
        second_imgs = list(second_list['Poster'][:5]) if 'Poster' in second_list.columns else []

        two_div = f"""
        <div class="two_div-five-flex">
        <div class="two_div-five-col">
            <div class="two_div-five-grid">
            {''.join([
                f'<div class="two_div-five-container"><div class="two_div-five-poster"><img src="{img}"><span class="two_div-five-tooltip">{title} ({year})</span></div>'
                f'<div>Your rating : {rating}</div> <div>IMDB rating : {imdb_rating}</div></div>'
                if img else '<div class="two_div-five-poster"></div>'
                for img, title, year,rating,imdb_rating in zip(first_imgs, first_list["Title"][:5], first_list["Year"][:5],first_list["Rating"][:5],first_list["imdbRating"][:5])
            ])}
            </div>
        </div>
        <div class="two_div-five-col">
           <div class="two_div-five-grid">
            {''.join([
                f'<div class="two_div-five-container"><div class="two_div-five-poster"><img src="{img}"><span class="two_div-five-tooltip">{title} ({year})</span></div>'
                f'<div>Your rating : {rating}</div> <div>IMDB rating : {imdb_rating}</div></div>'
                if img else '<div class="two_div-five-poster"></div>'
                for img, title, year,rating,imdb_rating in zip(second_imgs, second_list["Title"][:5], second_list["Year"][:5],second_list["Rating"][:5],second_list["imdbRating"][:5])
            ])}
            </div>
        </div>
        </div>
        """
        return two_div
    
    def one_div_four_films(self, first_list, final_text):

        first_imgs  = list(first_list['Poster'][:4]) if 'Poster' in first_list.columns else []

        two_div = f"""
        <div class="one_div-flex">
            <div class="one_div-col">
                <div class="one_div-title"> 4 films {final_text}</div>
                <div class="one_div-grid">
                {''.join([
                    f'<div class="one_div-poster"><img src="{img}"><span class="one_div-tooltip">{title} ({year})</span></div>'
                    if img else '<div class="one_div-poster"></div>'
                    for img, title, year in zip(first_imgs, first_list["Title"][:4], first_list["Year"][:4])
                ])}
                </div>
            </div>
        </div>
        """
        return two_div

    def update_plot_with_current_layout(
            self,
        fig: go.Figure,
        cplt: go.Figure,
        row: int,
        layout: go.Layout,
        years_as_columns: bool,
    ) -> go.Figure:
        fig.update_layout(layout)
        fig.update_xaxes(layout["xaxis"])
        fig.update_yaxes(layout["yaxis"])
        if years_as_columns:
            rows = [1] * len(cplt)
            cols = [(row + 1)] * len(cplt)
        else:
            rows = [(row + 1)] * len(cplt)
            cols = [1] * len(cplt)
        fig.add_traces(cplt, rows=rows, cols=cols)
        return fig

    def create_month_lines(
            self,
        cplt: List[go.Figure],
        month_lines_color: str,
        month_lines_width: int,
        data: pd.DataFrame,
        weekdays_in_year: List[float],
        weeknumber_of_dates: List[int],
    ) -> go.Figure:
        kwargs = dict(
            mode="lines",
            line=dict(color=month_lines_color, width=month_lines_width),
            hoverinfo="skip",
        )
        for date, dow, wkn in zip(data, weekdays_in_year, weeknumber_of_dates):
            if date.day == 1:
                cplt += [go.Scatter(x=[wkn - 0.5, wkn - 0.5], y=[dow - 0.5, 6.5], **kwargs)]
                if dow:
                    cplt += [
                        go.Scatter(
                            x=[wkn - 0.5, wkn + 0.5], y=[dow - 0.5, dow - 0.5], **kwargs
                        ),
                        go.Scatter(x=[wkn + 0.5, wkn + 0.5], y=[dow - 0.5, -0.5], **kwargs),
                    ]
        return cplt

    def decide_layout(
            self,
        title: str,
        month_names: List[str],
        month_positions: Any,
    ) -> go.Layout:
        layout = go.Layout(
            title=title,
            margin=dict(t=0, b=0),
            height=250,
            yaxis=dict(
                showline=False,
                showgrid=False,
                zeroline=False,
                tickmode="array",
                ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                tickvals=[0, 1, 2, 3, 4, 5, 6],
                autorange="reversed",
                fixedrange=True
            ),
            xaxis=dict(
                showline=False,
                showgrid=False,
                zeroline=False,
                tickmode="array",
                ticktext=month_names,
                tickvals=month_positions,
                side='top',
                ticks="",
                tickangle=0,
                fixedrange=True
            ),
            font={"size": 14, "color": PALETTE['blanc']},
            showlegend=False,
        )
        return layout
    
    #TODO voir les couleurs de la palette
    #see https://github.com/brunorosilva/plotly-calplot/tree/main for more details (about the waffle plot)
    def waffle(self,df,month_pos,weekdays,weeknumber):
        GRAY = "#202831"
        GREEN=PALETTE['vert']
        z_values = df['count']
        if np.all(z_values == 0):
            colorscale = [[0, GRAY], [1, GRAY]]
            zmax = 1  
        else:
            colorscale = [[0, GRAY]]
            steps = 10
            for i in range(1, steps + 1):
                value = i / steps
                opacity = min(0.2 + (value * 0.8), 1.0)
                green_rgba = f'rgba({int(GREEN[1:3], 16)}, {int(GREEN[3:5], 16)}, {int(GREEN[5:7], 16)}, {opacity})'
                colorscale.append([value, green_rgba])
            zmax = None  
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        layout = self.decide_layout("", month_names, month_pos)

        df['films_list'] = df['films_list'].apply(
            lambda x: '<br> • ' + x.replace(',', '<br> •') if x else ''
        )

        fig = go.Heatmap(
            x=weeknumber,
            y=weekdays,
            z=df['count'],
            colorbar=dict(title='Compteur'),
            xgap=1.5,
            ygap=1.5,
            showscale=False,
            colorscale=colorscale,
            zmin=0,
            zmax=zmax,
            name="",
            hovertemplate=(
            "<b>Date:</b> %{customdata[0]}<br>"
            "<b>Films watched:</b> %{z}"
            "%{customdata[1]}<extra></extra>"
            ),
            customdata=np.stack((df['date'].astype(str), df['films_list']), axis=-1),
        )
        fig=self.create_month_lines(
            cplt=[fig],
            month_lines_color= PALETTE['bleu'],
            month_lines_width=3,
            data=df['date'],
            weekdays_in_year=weekdays,
            weeknumber_of_dates=weeknumber
        )
        figTest = make_subplots(rows=1, cols=1)
        fig = self.update_plot_with_current_layout(
            fig=figTest,
            cplt=fig,
            row=0,
            layout=layout,
            years_as_columns=False
        )
        return fig