import json
import os
import requests
from bs4 import BeautifulSoup

def generate_config(url: str, llm_mode_str: str) -> dict:
    """
    Connects to the specified LLM to analyze the URL and generate 
    a scraping configuration dictionary.
    """
    print(f"[llm_config] Analyzing {url} with {llm_mode_str}...")
    
    # 1. Fetch initial HTML to provide context to the LLM
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        html = res.text
    except Exception as e:
        print(f"[llm_config] Error fetching {url}: {e}")
        return None

    # Simplify HTML to save tokens (remove head, scripts, svgs, etc)
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "svg", "head", "iframe"]):
        tag.decompose()
        
    # Extract structural skeleton: keep div, nav, article, ul, li, a 
    # to let the LLM guess the layout. Limit length to ~10k chars.
    skeleton_html = str(soup)[:10000] 
    
    # 2. Prepare LiteLLM prompt
    # LLM String format: "local:ollama/llama3" or "api:openai:gpt-4o"
    try:
        import litellm
    except ImportError:
        print("[llm_config] litellm not installed. Please pip install litellm.")
        return fallback_config(url)
        
    parts = llm_mode_str.split(":", 1)
    if len(parts) > 1:
        model_name = parts[1]
    else:
        model_name = "gpt-3.5-turbo" # Default
        
    system_prompt = '''You are an expert web scraping architect. 
Given a snippet of an API documentation website's HTML, you must determine the optimal scraping configuration.
Output ONLY a valid JSON object with the following schema:
{
  "base_url": "The root matching URL path to consider for scraping",
  "link_selector": "The CSS selector to find all API sub-page links",
  "content_selector": "The CSS selector where the main API documentation content is located",
  "slug_pattern": "A regex or simple pattern to derive the slug from the URL",
  "exclude_patterns": ["List of CSS selectors to remove (e.g. nav, footer, scripts)"],
  "max_depth": 2
}'''

    user_prompt = f"Analyze this HTML snippet and generate the JSON config for {url}:\n\n```html\n{skeleton_html}\n```"

    try:
        response = litellm.completion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        config = json.loads(content)
        
        # Save to configs/
        os.makedirs("configs", exist_ok=True)
        config_path = f"configs/config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"[llm_config] Successfully generated config and saved to {config_path}")
        return config

    except Exception as e:
        print(f"[llm_config] Error calling LLM: {e}")
        return fallback_config(url)

def fallback_config(url: str) -> dict:
    print("[llm_config] Falling back to default config.")
    return {
        "base_url": url,
        "link_selector": "a[href]",
        "content_selector": "article",
        "slug_pattern": "slug",
        "exclude_patterns": ["nav", "footer", "script", "style"],
        "max_depth": 2
    }
