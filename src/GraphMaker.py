import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Any, List
from plotly.subplots import make_subplots

class GraphMaker:
    
    def __init__(self):
        self.PALETTE = {
            'orange' : '#FF8C00',
            'vert' : '#00E054',
            'bleu' : '#40BCF4'
        }

    def general_metrics_div(self, metrics):
        # metrics = [(val, label, icon), ...]
        first_row = metrics[:3]
        second_row = metrics[3:5]
        palette = [self.PALETTE['orange'], self.PALETTE['vert'], self.PALETTE['bleu']]

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
        <div class="metrics-grid">
            <div class="metrics-title">You have watched...</div>
            <div class="metrics-row">
                {''.join(make_block(metric, palette[i % len(palette)]) for i, metric in enumerate(first_row))}
            </div>
            <div class="metrics-title">Your watchlist contains...</div>
            <div class="metrics-row">
                {''.join(make_block(metric, palette[(i+3) % len(palette)]) for i, metric in enumerate(second_row))}
            </div>
        </div>
        """
        return div_content

    def graph_genre(self, df) :

        genre_counts = df['Genre'].value_counts().sort_index().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        genre_counts = genre_counts.sort_values('Count', ascending=False)

        bins = genre_counts['Genre'].tolist()
        bin_pos = np.arange(len(bins))
        fig = go.Figure()

        # Barplot (fond, transparent)
        fig.add_trace(go.Bar(
            x=bin_pos,
            y=genre_counts['Count'],
            marker_color=self.PALETTE['orange'],
            opacity=0.10,
            width=0.95,
            showlegend=False,
            text=genre_counts['Count'],
            hovertemplate=None,
            hoverinfo='skip'
        ))

        for i, bin_label in enumerate(bins):
            sub_df = df[df['Genre'] == bin_label]
            if sub_df.empty:
                continue

            n_points = sub_df.shape[0]
            count = df[df['Genre'] == bin_label]['Genre'].count()
            # Étalement vertical des points sur toute la hauteur de la barre
            if n_points == 1:
                y = [count/2]
            else:
                y = np.linspace(0.5, count-0.5, n_points)
            # Jitter horizontal centré sur la barre
            x = bin_pos[i] + np.random.uniform(-0.35, 0.35, n_points)

            palette_keys = list(self.PALETTE.keys())
            BIN_COLORS = [self.PALETTE[k] for k in palette_keys]
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
                customdata=sub_df[['Name', 'Year']],
                hovertemplate='<b>%{customdata[0]} (%{customdata[1]})</b><extra></extra>',
                showlegend=False
            ))

        fig.update_layout(
            xaxis_title='',
            yaxis_title='Films count',
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

        return fig

    def graph_director(self, df):
        colors = [self.PALETTE['orange'], self.PALETTE['vert'], self.PALETTE['bleu']]
        color_seq = [colors[i % len(colors)] for i in range(len(df))]

        fig = px.bar(
            df,
            x='Director',
            y='Number of Movies',
            text='Number of Movies',
            color='Director',
            color_discrete_sequence=color_seq,
            labels={'Director': 'Director', 'Number of Movies': 'Number of Movies'},
        )

        fig.update_traces(
            textposition='inside',
            hovertemplate="<b>%{x}</b><br>%{y} films<extra></extra>"
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
            bargap=0.17,
            barcornerradius=8,
            showlegend=False,
        )

        return fig

    def graph_actor(self, df):

        nb_actor = df.sort_values("Number of Movies", ascending=False).reset_index(drop=True)
        colors = [self.PALETTE['orange'], self.PALETTE['vert'], self.PALETTE['bleu']]
        color_seq = [colors[i % len(colors)] for i in range(len(nb_actor))]

        fig = px.bar(
            nb_actor,
            x='Actors',
            y='Number of Movies',
            text='Number of Movies',
            color='Actors',
            color_discrete_sequence=color_seq,
            labels={'Actor': 'Actors', 'Number of Movies': 'Number of Movies'},
        )

        fig.update_traces(
            textposition='inside',
            hovertemplate="<b>%{x}</b><br>%{y} films<extra></extra>"
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
            bargap=0.17,
            barcornerradius=8,
            showlegend=False,
        )

        return fig

    def cinephile_graph(self, result):

        fig = go.Figure(go.Pie(
            labels=result['category'],
            values=result['number'],
            textinfo='label+percent',
            hole=0.7,
            marker=dict(colors=[self.PALETTE['orange'], self.PALETTE['vert'], self.PALETTE['bleu']]),
            textfont=dict(size=16),
            insidetextorientation='auto',
            pull=[0.3, 0.2, 0.1, 0],  # Pull the slices out a bit for emphasis
            rotation=90,
            sort=False
        ))

        fig.update_traces(
            showlegend=False,
            hovertemplate='<b>%{label}</b><br>%{value} films<extra></extra>'
        )

        fig.update_layout(
            margin=dict(t=20, b=20, r=20, l=20)
        )
        return fig

    def graph_decade(self, df):
        fig = px.bar(
            df,
            x='Number',
            y='FiveYearBin',
            text='Number',
            color='FiveYearBin',
            color_discrete_sequence=[self.PALETTE['orange'], self.PALETTE['vert'], self.PALETTE['bleu']],
            orientation='h'
        )

        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>',
            marker_line_color="#444",
            textfont_size=14,
            textposition="outside"
        )
        fig.update_layout(
            xaxis_title='',
            yaxis_title='Number of films',
            margin=dict(t=80, b=60),
            xaxis=dict(
                tickfont=dict(size=18),
                fixedrange=True,
                showgrid=True,
            ),
            yaxis=dict(
                title_font=dict(size=16),
                tickfont=dict(size=14),
                fixedrange=True,
                ticks='outside',
                tickmode='linear',
                dtick=1,
            ),
            barcornerradius=7,
            showlegend=False,
            bargap=0.2
        )
        
        return fig

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
            countrycolor="gray"
        )

        fig.update_layout(
            geo_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font=dict(color="white"),
            margin=dict(l=0, r=0, t=40, b=0)
        )

        return fig

    def graph_rating_director(self, df_plot, nb_films_par_director):
        fig = px.bar(
            nb_films_par_director,
            x='Director',
            y='Number of movie',
            title='Top 25 most viewed directors and their average rating',
            labels={'Director': 'Director', 'Number of movie': 'Number of movie'},
            text='Number of movie'
        )
        fig.add_scatter(x=df_plot['Director'],y=df_plot['Moyenne_Rating'], name='Mean Rating Letterboxd',mode='lines+markers')
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def graph_rating_actor(self, df):
        fig = px.bar(
            df,
            x='Actor',
            y='Nb_Films',
            title='Top 25 most viewed actors and their average rating',
            labels={'Director': 'Director', 'Nb_Films': 'Number of movie'},
            text='Nb_Films'
        )
        fig.add_scatter(x=df['Actor'],y=df['Moyenne_Rating'], name='Mean Rating Letterboxd',mode='lines+markers')
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def graph_genre_rating(self, df):
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df['Genre'],
            y=df['Nombre de films'],
            name='Number of movie',
            yaxis='y1',
            text=df['Nombre de films']
        ))

        fig.add_trace(go.Scatter(
            x=df['Genre'],
            y=df['Moyenne_Rating'],
            name='Mean rating',
            yaxis='y2',
            mode='lines+markers'
        ))

        fig.update_layout(
            title='Number of films and average rating by genre',
            xaxis=dict(title='Genre', tickangle=-45),
            yaxis=dict(
                title='Number of movie',
                side='left'
            ),
            yaxis2=dict(
                title='Mean rating',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[df['Moyenne_Rating'].min() - 0.5, df['Moyenne_Rating'].max() + 0.5]  # échelle personnalisée ici
            ),
            legend=dict(x=1.02, y=0.99),
            height=500
        )
        return fig

    def graph_comparaison_rating(self, df, rating_df):
        fig = px.bar(df, x='imdbRating', y='Number of movie', title="Breakdown of IMDB ratings and your own ratings",labels={'imdbRating': 'Rating', 'Number of movie': 'Number of movie'},text='Number of movie',)
        fig.data[0].name = "Rating IMDB"

        letterboxd_rate = rating_df.groupby('Rating').size().reset_index(name='Number of movie')
        
        fig.add_bar(x=letterboxd_rate['Rating'], y=letterboxd_rate['Number of movie'], name='Rating Letterboxd',text=letterboxd_rate['Number of movie'])
        fig.update_layout(barmode='group', showlegend=True)

        return fig

    def graph_generate_wordcloud(self, wc):
        fig, ax = plt.subplots(figsize = (20, 10),facecolor='k')
        ax.imshow(wc, interpolation = 'bilinear')
        plt.axis('off')
        return fig

    def graph_runtime_bar(self, df):
       # Comptage par bin pour les barres de fond
        runtime_counts = df['RuntimeBin'].value_counts().sort_index().reset_index()
        runtime_counts.columns = ['RuntimeBin', 'Count']

        bins = runtime_counts['RuntimeBin'].tolist()
        bin_pos = np.arange(len(bins))
        fig = go.Figure()

        # Barplot (fond, transparent)
        fig.add_trace(go.Bar(
            x=bin_pos,
            y=runtime_counts['Count'],
            marker_color=self.PALETTE['orange'],
            opacity=0.10,
            width=0.95,
            showlegend=False,
            hovertemplate=None,
            hoverinfo='skip'
        ))

        # Swarmplot pour chaque bin
        for i, bin_label in enumerate(bins):
            sub_df = df[df['RuntimeBin'] == bin_label]
            if sub_df.empty:
                continue

            n_points = sub_df.shape[0]
            count = runtime_counts.loc[i, 'Count']
            # Étalement vertical des points sur toute la hauteur de la barre
            if n_points == 1:
                y = [count/2]
            else:
                y = np.linspace(0.5, count-0.5, n_points)
            # Jitter horizontal centré sur la barre
            x = bin_pos[i] + np.random.uniform(-0.35, 0.35, n_points)

            palette_keys = list(self.PALETTE.keys())
            BIN_COLORS = [self.PALETTE[k] for k in palette_keys]
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
                customdata=sub_df[['Title', 'Year','Runtime']],
                hovertemplate='<b>%{customdata[0]} (%{customdata[1]})</b><br>%{customdata[2]} min<extra></extra>',
                showlegend=False
            ))

        fig.update_layout(
            xaxis_title='Runtime (minutes)',
            yaxis_title='Films count',
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

        return fig
    
    def movie_per_year(self, df):
        films_par_annee = df['Year'].value_counts().sort_index()

        df_par_annee = films_par_annee.reset_index()
        df_par_annee.columns = ['Year', 'Number of Movies']

        fig = px.line(df_par_annee, x='Year', y='Number of Movies', title='Number of movie per year')

        st.plotly_chart(fig)

    def graph_radar(self, radar_stats):

        scores_names = ['Consommateur', 'Explorateur', 'Consensuel', 'Éclectique', 'Actif']
        scores_names_display = ['Consumer', 'Explorer', 'Consensus', 'Eclectic', 'Active']
        scores_values = [radar_stats[score] for score in scores_names]

        markers = radar_stats['nb_films_vus'], radar_stats['ratio_peu_vus'], radar_stats['moyenne_diff_rating'], radar_stats['ratio_par_genre'], radar_stats['nb_interactions']

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores_values,  # Close the loop
            theta=scores_names_display,
            fill='toself',
            name='Your Profile',
            line=dict(color=self.PALETTE['orange'])
        ))
        fig.add_trace(go.Scatterpolar(
            r=[50, 50, 50, 50, 50],  # Close the loop
            theta=scores_names_display,
            fill='toself',
            name='Average Profile',
            line=dict(color=self.PALETTE['bleu'])
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]  # Adjust the range as needed
                )
            ),
            showlegend=True,
            title='Your Profile in the Radar',
            title_x=0.5,
            plot_bgcolor=self.PALETTE['blanc'],
            font=dict(color=self.PALETTE['bleu'])
        )
        return fig
    
    def two_div_four_films(self, first_list, second_list, first_word, second_word, final_text):

        first_imgs  = list(first_list['Poster'][:4]) if 'Poster' in first_list.columns else []
        second_imgs = list(second_list['Poster'][:4]) if 'Poster' in second_list.columns else []

        two_div = f"""
        <div class="two_div-flex">
        <div class="two_div-col">
            <div class="two_div-title">The 4 {first_word} films {final_text}</div>
            <div class="two_div-grid">
            {''.join([
                f'<div class="two_div-poster"><img src="{img}"><span class="two_div-tooltip">{title} ({year})</span></div>'
                if img else '<div class="two_div-poster"></div>'
                for img, title, year in zip(first_imgs, first_list["Title"][:4], first_list["Year"][:4])
            ])}
            </div>
        </div>
        <div class="two_div-col">
            <div class="two_div-title">The 4 {second_word} films {final_text}</div>
            <div class="two_div-grid">
            {''.join([
                f'<div class="two_div-poster"><img src="{img}"><span class="two_div-tooltip">{title} ({year})</span></div>'
                if img else '<div class="two_div-poster"></div>'
                for img, title, year in zip(second_imgs, second_list["Title"][:4], second_list["Year"][:4])
            ])}
            </div>
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
            <div class="two_div-five-title">The 10 films {final_text}</div>
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
            margin=dict(t=10, b=50),
            height=175,
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
            font={"size": 10, "color": "#9e9e9e"},
            showlegend=False,
        )
        return layout
    #TODO voir les couleurs de la palette
    #see https://github.com/brunorosilva/plotly-calplot/tree/main for more details (about the waffle plot)
    def waffle(self,df,month_pos,weekdays,weeknumber):
        GRAY = "#202831"
        GREEN=self.PALETTE['vert']
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
                    "%{customdata[0]} <br>Week=%{x} <br>%{customdata[1]}=%{z} "),
        customdata=np.stack((df['date'].astype(str), ["movie watched"] * df.shape[0]), axis=-1),
        )
        fig=self.create_month_lines(
            cplt=[fig],
            month_lines_color= self.PALETTE['bleu'],
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