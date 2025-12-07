# modules externes
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
from io import BytesIO

# modules internes

from src.utils import computeRuntime

class WrappedGenerator:
    def __init__(self,dataHandler):
        self.dataHandler = dataHandler #circular import avoided by importing here
    
    
    def ellipsis(self,text,max_len=20):
        text=str(text)
        return text if len(text) <= max_len else text[:max_len - 3] + "..."
    

    def generate_wrapped(self):
        # Image settings
        width, height = 1080 , 1920
        bg_color = (18, 18, 18)
        text_color = (235, 235, 235)
        muted = (170, 170, 170)

        left_header = "Top movies"
        right_header = "Top directors"

        #color
        orange=(255, 140, 0)
        vert=(0, 224, 84)
        bleu=(64, 188, 244)

        watched_df=self.dataHandler.get_watched_df()
        top_genre=self.dataHandler.mostCommonGenre()

        runtime=computeRuntime(watched_df)*60

        top5_titles=self.dataHandler.get_top5_titles()
        top5_directors=self.dataHandler.get_top5_directors()

        for title in top5_titles:
            url = self.dataHandler.get_url(title)
            if url is not None:
                response = requests.get(url)
                break
        # Create image
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if response is None:
            response = requests.get("https://m.media-amazon.com/images/M/MV5BNDIzNGUwZmYtODM0Yy00NjA3LTgxOGUtOTY0ZGM5MjBkM2I3XkEyXkFqcGc@._V1_SX300.jpg")

        cover = Image.open(BytesIO(response.content))
        cover_height = int(height * (4/8))
        w_orig, h_orig = cover.size
        ratio = w_orig / h_orig

        # Pour remplir toute la largeur, calculer la hauteur correspondante
        new_height = int(width / ratio)

        # Redimensionner l'image en largeur
        cover_resized = cover.resize((width, new_height), Image.LANCZOS)

        # Si la hauteur est plus grande que la zone cible, crop verticalement (centré)
        if new_height > cover_height:
            top = (new_height - cover_height) // 2
            cover_cropped = cover_resized.crop((0, top, width, top + cover_height))
        else:
            cover_cropped = cover_resized

        #cover = cover.resize((width, cover_height))
        img.paste(cover_cropped, (0, 0))
        y_offset = cover_height + 40
        # Load fonts (fallback to default if not available)
        def load_font(name="arial.ttf", size=40):
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                return ImageFont.load_default(size)

        font_header = load_font(size=50)
        font_row = load_font(size=55)
        font_small = load_font(size=75)

        # Column positions
        left_x = 70
        right_x = 650
        top_y = y_offset

        # Draw headers for both columns (right-aligned for header on right column)
        draw.text((left_x, top_y), left_header, font=font_header, fill=muted)
        draw.text((right_x, top_y), right_header, font=font_header, fill=muted)

        # Starting Y for rows (leave some space under headers)
        y = top_y + 70

        # Determine max number of rows between two columns
        max_rows = max(len(top5_titles), len(top5_directors))

        # Draw each row: left cell and right cell on same horizontal line
        for i in range(max_rows):
            # Left cell text (if exists)
            if i < len(top5_titles):
                left_text = top5_titles[i]
                # Wrap if too long to the column width (approx)
                wrapped = textwrap.fill(self.ellipsis(left_text), width=24)
                draw.text((left_x, y), wrapped, font=font_row, fill=orange)
            # Right cell text (if exists)
            if i < len(top5_directors):
                right_text = top5_directors[i]
                wrapped_r = textwrap.fill(self.ellipsis(right_text,14), width=24)
                draw.text((right_x, y), wrapped_r, font=font_row, fill=orange)
            y += 80  # move to next row

        y += 80 
        draw.text((left_x, y), "Minutes watched", font=font_header, fill=muted)

        draw.text((right_x, y), "Top genre", font=font_header, fill=muted)
        y += 80 
        draw.text((left_x, y), str(int(runtime)), font=font_small, fill=vert)

        draw.text((right_x, y), top_genre, font=font_small, fill=bleu)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()