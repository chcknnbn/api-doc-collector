import os
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import yaml

def run_collector(config: dict) -> str:
    """
    Executes the crawling and scraping based on the LLM generated config.
    Returns the path to the directory containing the markdown files.
    """
    base_url = config.get("base_url")
    link_selector = config.get("link_selector", "a[href]")
    content_selector = config.get("content_selector", "body")
    exclude_patterns = config.get("exclude_patterns", ["nav", "footer", "script", "style"])
    slug_pattern = config.get("slug_pattern", "slug") # Not deeply implemented for simplicity, we will split by /
    max_depth = config.get("max_depth", 1) # Support depth 1 first

    print(f"[collector] Starting scraper for {base_url}...")
    
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    # 1. Fetch initial index to find links
    try:
        res = requests.get(base_url, headers=headers, timeout=10)
        res.raise_for_status()
        index_soup = BeautifulSoup(res.text, 'html.parser')
    except Exception as e:
        print(f"[collector] Failed to fetch index {base_url}: {e}")
        return docs_dir

    # Extract matching links
    target_links = set()
    base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
    
    for a_tag in index_soup.select(link_selector):
        href = a_tag.get('href')
        if not href:
            continue
        full_url = urljoin(base_url, href)
        # Simple domain filter
        if full_url.startswith(base_domain):
            target_links.add(full_url)
            
    print(f"[collector] Found {len(target_links)} links matching '{link_selector}'")

    # 2. Scrape each target link
    for i, link in enumerate(target_links):
        print(f"[collector] [{i+1}/{len(target_links)}] Fetching {link}...")
        try:
            page_res = requests.get(link, headers=headers, timeout=10)
            page_res.raise_for_status()
            page_soup = BeautifulSoup(page_res.text, 'html.parser')
            
            # Extract Main Content
            main_content = page_soup.select_one(content_selector)
            if not main_content:
                main_content = page_soup.find('body')
                
            if not main_content:
                continue
                
            # Exclude noise elements
            for exclude in exclude_patterns:
                for noise_tag in main_content.select(exclude):
                    noise_tag.decompose()
                    
            html_content = str(main_content)
            
            # Markdownify
            markdown_content = md(html_content, heading_style="ATX").strip()
            
            # Title extraction
            title_tag = page_soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"
            
            # Generate Slug
            slug = link.strip('/').split('/')[-1]
            if not slug or slug.endswith('.html') or slug.endswith('.php'):
                slug = slug.split('.')[0] if '.' in slug else slug
            if not slug:
                slug = f"page_{i}"
                
            # YAML Frontmatter
            frontmatter = {
                "title": title,
                "url": link,
            }
            frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
            final_md = f"---\n{frontmatter_str}---\n\n{markdown_content}"
            
            # Save file
            file_path = os.path.join(docs_dir, f"{slug}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_md)
                
            # Polite delay
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[collector] Error fetching {link}: {e}")
            
    print(f"[collector] Finished scraping. Saved to {docs_dir}/")
    return docs_dir
