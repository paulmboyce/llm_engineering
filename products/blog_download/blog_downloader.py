#!/usr/bin/env python3
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import html2text
import argparse
from pathlib import Path
import shutil
import time

class BlogDownloader:
    def __init__(self):
        # Create base articles directory
        self.base_dir = Path("./articles")
        self.base_dir.mkdir(exist_ok=True)
        
        # Initialize HTML to Markdown converter
        self.md_converter = html2text.HTML2Text()
        self.md_converter.ignore_links = False
        self.md_converter.ignore_images = False
        self.md_converter.ignore_emphasis = False
        self.md_converter.body_width = 0  # No wrapping
        
        # User agent to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def sanitize_filename(self, filename):
        """Convert a string to a valid filename."""
        # Replace spaces with underscores and remove invalid characters
        valid_filename = re.sub(r'[^\w\-.]', '_', filename)
        return valid_filename
    
    def get_base_url(self, url):
        """Extract base URL from a given URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def download_image(self, img_url, article_dir):
        """Download an image and save it to images directory."""
        try:
            # Create images directory if it doesn't exist
            images_dir = article_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Get image filename from URL
            img_filename = self.sanitize_filename(os.path.basename(urlparse(img_url).path))
            if not img_filename or img_filename == '':
                img_filename = f"image_{int(time.time() * 1000)}.jpg"
            
            # Download image
            response = requests.get(img_url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            # Save image
            img_path = images_dir / img_filename
            with open(img_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            
            return f"images/{img_filename}"
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")
            return img_url
    
    def process_article(self, article_url):
        """Process a single article."""
        try:
            print(f"Processing article: {article_url}")
            response = requests.get(article_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find the article title
            title = soup.find('h1')
            if title:
                title_text = title.get_text().strip()
            else:
                title_text = f"Article_{int(time.time())}"
            
            # Create a directory for the article
            article_dir_name = self.sanitize_filename(title_text)
            article_dir = self.base_dir / article_dir_name
            article_dir.mkdir(exist_ok=True)
            
            # Find the article content
            # This is a simplified approach and may need to be adjusted for specific blogs
            article_content = None
            content_selectors = [
                'article', 
                '.post-content', 
                '.entry-content', 
                '.content', 
                'main',
                '#content'
            ]
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    article_content = content
                    break
            
            if not article_content:
                article_content = soup.body
            
            # Process images in the article
            base_url = self.get_base_url(article_url)
            for img in article_content.find_all('img'):
                if img.get('src'):
                    img_url = img['src']
                    # Handle relative URLs
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(base_url, img_url)
                    
                    # Download the image and update the src attribute
                    local_path = self.download_image(img_url, article_dir)
                    img['src'] = local_path
            
            # Convert HTML to markdown
            markdown_content = self.md_converter.handle(str(article_content))
            
            # Add title at the top
            markdown_content = f"# {title_text}\n\n{markdown_content}"
            
            # Save the markdown content
            with open(article_dir / "article.md", "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            print(f"Successfully saved article: {title_text}")
            return True
        except Exception as e:
            print(f"Error processing article {article_url}: {e}")
            return False
    
    def find_all_articles(self, blog_url):
        """Find all article URLs from a blog homepage."""
        try:
            article_urls = set()
            visited_pages = set()  # Track pages we've already processed
            pages_to_visit = [blog_url]  # Queue of pages to visit
            base_url = self.get_base_url(blog_url)
            parsed_blog_url = urlparse(blog_url)
            blog_domain = parsed_blog_url.netloc
            
            # Process the main blog page and any pagination pages
            while pages_to_visit and len(visited_pages) < 30:  # Limit to 30 pages for safety
                current_page = pages_to_visit.pop(0)
                if current_page in visited_pages:
                    continue
                
                visited_pages.add(current_page)
                print(f"Scanning for articles on page: {current_page}")
                
                response = requests.get(current_page, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find pagination links first
                pagination_links = set()
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Handle relative URLs
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(base_url, href)
                    
                    # Only include URLs from the same domain
                    parsed_href = urlparse(href)
                    if parsed_href.netloc != blog_domain:
                        continue
                    
                    # Check for pagination patterns
                    pagination_patterns = ['/page/', '?page=', '?paged=', '&paged=', '&page=']
                    if any(pattern in href.lower() for pattern in pagination_patterns):
                        pagination_links.add(href)
                
                # Add new pagination links to our queue
                for link in pagination_links:
                    if link not in visited_pages and link not in pages_to_visit:
                        pages_to_visit.append(link)
                
                # Find article links on this page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Skip empty links, anchors, and javascript
                    if not href or href.startswith('#') or href.startswith('javascript:'):
                        continue
                    
                    # Handle relative URLs
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(base_url, href)
                    
                    # Only include URLs from the same domain
                    parsed_href = urlparse(href)
                    if parsed_href.netloc != blog_domain:
                        continue
                    
                    # Skip exact homepage and common non-article paths
                    if href == blog_url or href == base_url:
                        continue
                    
                    # Skip pagination pages
                    if any(pattern in href.lower() for pattern in pagination_patterns):
                        continue
                    
                    # Skip common non-article paths
                    if any(pattern in href.lower() for pattern in ['/tag/', '/category/', '/author/', 
                                                                     '/about/', '/contact/',
                                                                     '/feed/', '/rss/', '/wp-content/',
                                                                     '/wp-admin/', '/login/', '/sign-up/']):
                        continue
                    
                    # More inclusive article detection
                    is_article = False
                    
                    # For blogs with articles at root level (like popcornmetrics)
                    # Check if the URL has a path beyond the domain with a reasonable length
                    path_parts = parsed_href.path.strip('/').split('/')
                    if len(path_parts) == 1 and len(path_parts[0]) > 5:
                        is_article = True
                    
                    # Check URL patterns (expanded list)
                    if any(pattern in href.lower() for pattern in ['/post/', '/article/', '/blog/', '/20', '/entry/', 
                                                                     '/archive/', '?p=', '.html', '.php']):
                        is_article = True
                        
                    # Look at the link's context for article indicators
                    parent_classes = []
                    for parent in link.parents:
                        if parent.get('class'):
                            parent_classes.extend(parent.get('class'))
                            
                    article_container_indicators = ['post', 'article', 'entry', 'blog-item', 'story']
                    if any(indicator in ' '.join(parent_classes).lower() for indicator in article_container_indicators):
                        is_article = True
                        
                    # Link text often indicates an article (if it has substantial text, it's often a title)
                    link_text = link.get_text().strip()
                    if len(link_text) > 20:  # Likely a title
                        is_article = True
                        
                    if is_article:
                        article_urls.add(href)
                
                # Respect the server by adding a small delay
                time.sleep(1)
            
            print(f"Found {len(article_urls)} potential articles on domain {blog_domain} after scanning {len(visited_pages)} pages")
            return list(article_urls)
        except Exception as e:
            print(f"Error finding articles from {blog_url}: {e}")
            return []
    
    def run(self):
        """Run the blog downloader."""
        parser = argparse.ArgumentParser(description='Download blog content as markdown.')
        parser.add_argument('--url', help='URL to a specific article or blog homepage')
        args = parser.parse_args()
        
        if args.url:
            url = args.url
        else:
            choice = input("Enter '1' to download a single article or '2' to download an entire blog: ")
            if choice == '1':
                url = input("Enter the article URL: ")
                self.process_article(url)
            elif choice == '2':
                url = input("Enter the blog homepage URL: ")
                articles = self.find_all_articles(url)
                for article_url in articles:
                    self.process_article(article_url)
                    # Add a small delay to be respectful to the server
                    time.sleep(1)
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

if __name__ == "__main__":
    downloader = BlogDownloader()
    downloader.run() 