

# from flask import Flask, render_template_string
# import requests
# from bs4 import BeautifulSoup
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# import numpy as np

# app = Flask(__name__)

# # HTML Template as a Python string
# HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>News Clusters</title>
# </head>
# <body>
#     <h1>Clustered News Articles</h1>
#     {% for cluster_id, cluster_info in clusters.items() %}
#         <h2>Cluster {{ cluster_id }}</h2>
#         <h3>Top terms: {{ cluster_info['keywords']|join(', ') }}</h3>
#         <ul>
#             {% for article in cluster_info['articles'] %}
#                 <li><a href="{{ article['link'] }}">{{ article['title'] }}</a></li>
#             {% endfor %}
#         </ul>
#     {% endfor %}
# </body>
# </html>
# """

# # Function to scrape BBC news
# def scrape_bbc_news():
#     # The URL of the BBC news page you want to scrape
#     url = 'https://www.bbc.com/news'
    
#     # Send a request to the BBC news page
#     response = requests.get(url)
    
#     # Parse the page content with BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     # Find all article elements - Adjust the selector based on the actual website structure
#     article_tags = soup.select('a.gs-c-promo-heading')
    
#     # Extract the title and link of each article
#     articles = []
#     for tag in article_tags:
#         title = tag.get_text()
#         link = tag.get('href')
        
#         # Ensure that link is absolute
#         if not link.startswith('http'):
#             link = f'https://www.bbc.com{link}'
        
#         articles.append({'title': title, 'link': link})
    
#     return articles

# # Function to cluster articles and determine top terms for each cluster
# def cluster_articles(articles, n_clusters=3):
#     if len(articles) < n_clusters:
#         n_clusters = len(articles)  # Ensure we do not have more clusters than samples

#     vectorizer = TfidfVectorizer(stop_words='english')
#     X = vectorizer.fit_transform([article['title'] for article in articles])
    
#     kmeans = KMeans(n_clusters=n_clusters, random_state=42)
#     kmeans.fit(X)
    
#     order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
#     terms = vectorizer.get_feature_names_out()
    
#     clusters = {}
#     for i in range(n_clusters):
#         cluster_articles = [articles[j] for j in range(len(articles)) if kmeans.labels_[j] == i]
#         top_terms = [terms[ind] for ind in order_centroids[i, :10]]  # Adjust 10 to get more or fewer terms
#         clusters[i] = {'keywords': top_terms, 'articles': cluster_articles}
        
#     return clusters

# @app.route('/')
# def show_clusters():
#     articles = scrape_bbc_news()  # Replace with actual scraping function
#     clusters = cluster_articles(articles, n_clusters=5)
#     return render_template_string(HTML_TEMPLATE, clusters=clusters)

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

app = Flask(__name__)

# HTML Template with basic CSS styling and spacing
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>News Clusters</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f0f0f0; }
        .container { width: 80%; margin: auto; }
        h1 { text-align: center; }
        .cluster { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .cluster h2 { color: #333; }
        .article { margin-bottom: 10px; }
        .article a { text-decoration: none; color: #0078D7; }
        .article a:hover { text-decoration: underline; }
        .terms { margin-top: 10px; font-size: 0.9em; color: #555; }
        .article-number { font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Clustered News Articles</h1>
        {% for cluster_id, cluster_info in clusters.items() %}
            <div class="cluster">
                <h2>Cluster {{ cluster_id }}</h2>
                <div class="terms">Top terms: {{ cluster_info['terms'] }}</div>
                <div style="margin-top: 20px;">
                    {% for article in cluster_info['articles'] %}
                        <div class="article">
                            <span class="article-number">Article {{ loop.index }}:</span>
                            <a href="{{ article['link'] }}">{{ article['title'] }}</a>
                        </div>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# Function to scrape BBC News
def scrape_bbc_news():
    url = 'https://www.bbc.co.uk/news'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_tags = soup.find_all('a', {'class': 'gs-c-promo-heading'})
    
    articles = []
    for tag in article_tags:
        title = tag.text.strip()
        link = tag['href']
        if not link.startswith('http'):
            link = f'https://www.bbc.co.uk{link}'
        articles.append({'title': title, 'link': link})
    
    return articles

# Function to cluster articles and get top terms for each cluster
# Function to cluster articles and get top terms for each cluster
def cluster_articles(articles, n_clusters=3):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([article['title'] for article in articles])

    if X.shape[0] < n_clusters:
        n_clusters = X.shape[0]  # Ensure we do not have more clusters than samples
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)
    
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    
    clusters = {}
    for i in range(n_clusters):
        cluster_terms = [terms[ind] for ind in order_centroids[i, :10]]  # Top-10 terms per cluster
        clusters[i] = {'articles': [], 'terms': ', '.join(cluster_terms)}
        
    for i, label in enumerate(kmeans.labels_):
        clusters[label]['articles'].append(articles[i])
        
    return clusters

@app.route('/')
def show_clusters():
    articles = scrape_bbc_news()  # Make sure this function is defined and scraping correctly
    clusters = cluster_articles(articles, n_clusters=5)
    return render_template_string(HTML_TEMPLATE, clusters=clusters)

if __name__ == '__main__':
    app.run(debug=True)