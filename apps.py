import streamlit as st
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Set page configuration for Streamlit layout and title
st.set_page_config(page_title="News Clustering", layout="wide")

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
# Define a function to display clusters, called when the button is pressed
def display_clusters():
    articles = scrape_bbc_news()
    clusters = cluster_articles(articles, n_clusters=5)  # Adjust the number of clusters here if needed

    for cluster_id, cluster_info in clusters.items():
        # Create a container for each cluster
        with st.container():
            # Use markdown to create the cluster box with a border and padding
            st.markdown(f"<div style='border: 1px solid #ccc; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown(f"## Cluster {cluster_id}", unsafe_allow_html=True)
            st.markdown(f"**Top terms:** {cluster_info['terms']}")
            # Display article titles as links
            for article in cluster_info['articles']:
                st.markdown(f"[{article['title']}]({article['link']})", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Main app UI
def main():
    # Main landing page text
    st.title("News Clustering Application")
    st.write("Welcome to the News Clustering App. Click the button below to fetch and cluster the latest news articles.")

    # Button to display clusters
    if st.button('Show Clusters'):
        display_clusters()

    # Set the background color for the app
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f0f2f6;
            color: #262730;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        .stButton>button {
            width: 100%;
            padding: 0.75em 1em;
            border-radius: 5px;
            border: none;
            color: white;
            background-color: #FF4B4B;
            font-size: 1.25em;
            font-weight: 500;
        }
        h1 {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
