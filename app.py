from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import StringIO
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Read CSV file
            df = pd.read_csv(file)
            
            # Process data and generate plots
            graphs = {
                'reading_trends': create_reading_trends_plot(df),
                #'genre_distribution': create_genre_distribution_plot(df),
                'author_popularity': create_author_popularity_plot(df),
                'ratings_analysis': create_ratings_analysis_plot(df),
                'bookshelf_analysis': create_bookshelf_analysis_plot(df)
            }
            
            return render_template('results.html', graphs=graphs)
    
    return render_template('index.html')

def create_reading_trends_plot(df):
    # Filter and process data
    df_trends = df.dropna(subset=['Date Read']).copy()  # Use .copy() to create an explicit copy
    df_trends['Date Read'] = pd.to_datetime(df_trends['Date Read'], errors='coerce')

    # Extract year and month from 'Date Read' for grouping
    df_trends.loc[:, 'Year-Month'] = df_trends['Date Read'].dt.to_period('M')

    # Count the number of books read per year-month
    reading_trends = df_trends.groupby('Year-Month').size().reset_index(name='Books Read')

    # Convert 'Year-Month' to datetime for Plotly
    reading_trends['Year-Month'] = reading_trends['Year-Month'].dt.to_timestamp()
    
    # Create plot
    fig = px.bar(reading_trends, x='Year-Month', y='Books Read',
                 title='Number of Books Read by Month',
                 labels={'Year-Month': 'Month', 'Books Read': 'Number of Books'},
                 text='Books Read',  # Add text labels on bars
                 color='Books Read',  # Color the bars based on the number of books read
                 color_continuous_scale='Temps') 
    return fig_to_html(fig)


def create_author_popularity_plot(df):
    df_read_shelf = df[df['Exclusive Shelf'].str.strip().str.lower() == 'read'].copy()
    author_popularity_read_shelf = df_read_shelf['Author'].value_counts().reset_index()
    author_popularity_read_shelf.columns = ['Author', 'Count']
    
    fig = px.bar(author_popularity_read_shelf, x='Author', y='Count', 
                 title='Most Common Authors on the "Read" Shelf', 
                 labels={'Author': 'Author', 'Count': 'Number of Books'},
                 color='Count', color_continuous_scale='Temps')
    return fig_to_html(fig)

def create_ratings_analysis_plot(df):
    df_ratings = df[df['My Rating'] > 0].copy()
    fig = px.histogram(df_ratings, x='My Rating', nbins=5,
                       title='Distribution of Book Ratings', 
                       labels={'My Rating': 'Rating', 'count': 'Number of Books'},
                       color='My Rating',  # This will color bars based on the 'My Rating' values
                       color_discrete_sequence=px.colors.qualitative.Set1)
    return fig_to_html(fig)

def create_bookshelf_analysis_plot(df):
    df_shelves = df.dropna(subset=['Exclusive Shelf']).copy()
    df_shelves = df_shelves.assign(Shelf=df_shelves['Exclusive Shelf'].str.split(',')).explode('Shelf')
    df_shelves['Shelf'] = df_shelves['Shelf'].str.strip().str.lower()
    shelf_distribution = df_shelves['Shelf'].value_counts().reset_index()
    shelf_distribution.columns = ['Shelf', 'Count']
    
    fig = px.bar(shelf_distribution, x='Shelf', y='Count', 
                 title='Bookshelf Analysis', 
                 labels={'Shelf': 'Bookshelf', 'Count': 'Number of Books'})
    
    return fig_to_html(fig)

def fig_to_html(fig):
    fig_html = pio.to_html(fig, full_html=False)
    return fig_html

if __name__ == '__main__':
    app.run(debug=True)
