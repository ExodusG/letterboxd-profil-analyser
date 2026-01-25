def poster_maker(data_handler, key, metric, layout, n_posters, ascending=True, ratings=False):
    """
    Generate a poster display based on specified criteria.

    :param layout: layout type {grid or flex}
    :param n_posters: number of posters to display
    :param ascending: sorting order
    """
    if ratings:
        df = data_handler.get_dataframe("RATING_MG")
    else:  
        df = data_handler.get_dataframe(f"{key.upper()}_MG")
    data = _poster_data(df, metric, n_posters, ascending)
    html_content = _poster_html(data, layout, ratings)
    return html_content

def _poster_data(df, metric, n_posters, ascending):
    sorted_df = df.sort_values(by=metric, ascending=ascending).head(n_posters)
    return sorted_df

def _poster_html(data, layout, ratings):
    layout_prefix = layout.lower()
    imgs = list(data['Poster']) if 'Poster' in data.columns else []
    years = data["Year"] if "Year" in data.columns else []
    titles = data["Title"] if "Title" in data.columns else []
    user_ratings = data["Rating"]/2 if "Rating" in data.columns and not data["Rating"].isnull().all() else [None] * len(data)
    imdb_ratings = data["Rating"] - data["diff_rating"] if "diff_rating" in data.columns and not data["diff_rating"].isnull().all() else [None] * len(data)
    html_posters = ''

    for img, title, year, user_rating, imdb_rating in zip(imgs, titles, years, user_ratings, imdb_ratings):
        rating_html = ''
        if ratings:
            rating_html = f"Your Rating: {user_rating:.1f} stars<br/>IMDB Rating: {imdb_rating:.1f}/10"
        poster_html = f"""
        <div class="{layout_prefix}-poster">
            <div class="{layout_prefix}-tooltip">
                <div class="{layout_prefix}-title">{title} ({year})</div>
                {rating_html}
            </div>
            <img src="{img}" alt="{title} Poster" class="{layout_prefix}-poster-img"/>
        </div>
        """
        html_posters += poster_html

    if layout == "flex":
        html_content = f"""
        <div class="{layout_prefix}-flex">
            {html_posters}
        </div>
        """
    elif layout == "grid":
        html_content = f"""
        <div class="{layout_prefix}-grid">
            {html_posters}
        </div>
        """
    else:
        raise ValueError("Invalid layout type. Use 'flex' or 'grid'.")

    return html_content
