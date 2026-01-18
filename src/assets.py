# load css and html files
import streamlit as st

CSS_DIR = 'static/styles/'
HTML_DIR = 'static/html/'

CSS_FILES = [
    'main_interface.css',
    'general_metrics.css',
    'graph.css',
    'background.css',
    'example.css'
]

HTML_FILES = [
    'bottom_bar',
    'main_title_and_instructions'
]

@st.cache_resource
def load_css():
    css = ""
    for file in CSS_FILES:
        with open(CSS_DIR + file, 'r', encoding='utf-8') as f:
            css += f.read() + "\n"
    return css

@st.cache_resource
def load_html():
    html_content = {}
    for file in HTML_FILES:
        with open(HTML_DIR + file + '.html', 'r', encoding='utf-8') as f:
            html_content[file] = f.read()
    return html_content