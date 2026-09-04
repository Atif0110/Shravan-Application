import os
from dotenv import load_dotenv
import requests
import json
from groq import Groq
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
import re
from collections import deque
from security import is_safe_external_url

load_dotenv()

class WebsiteScraper:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def get_rendered_html(self, url):
        if not is_safe_external_url(url):
            raise ValueError("Only public HTTP(S) URLs are allowed")
        chrome_options = Options()
        chrome_options.add_argument("--headless=chrome")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument("--log-level=3")

        # Enable Chrome's Network domain via performance logging so we can
        # capture background JSON responses without depending on the
        # abandoned selenium-wire package (which is incompatible with
        # modern versions of blinker/Flask).
        chrome_options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )

        # Prefer webdriver-manager so a matching driver is fetched
        # automatically instead of relying on a committed binary that goes
        # stale with every Chrome update.
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception:
            driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.execute_cdp_cmd("Network.enable", {})
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            json_responses = []
            seen_request_ids = set()

            for entry in driver.get_log("performance"):
                try:
                    message = json.loads(entry["message"])["message"]
                except (KeyError, json.JSONDecodeError):
                    continue

                if message.get("method") != "Network.responseReceived":
                    continue

                params = message.get("params", {})
                response = params.get("response", {})
                request_id = params.get("requestId")
                mime_type = response.get("mimeType", "")

                if not request_id or request_id in seen_request_ids:
                    continue
                if "json" not in mime_type:
                    continue

                seen_request_ids.add(request_id)

                try:
                    body_result = driver.execute_cdp_cmd(
                        "Network.getResponseBody", {"requestId": request_id}
                    )
                    data = json.loads(body_result.get("body", ""))
                    json_responses.append({
                        "url": response.get("url", ""),
                        "data": data
                    })
                except Exception:
                    # Response body may no longer be available (e.g. it was
                    # evicted from the cache) or may not be valid JSON.
                    pass

            html = driver.page_source
            return html, json_responses
        finally:
            driver.quit()

    def find_doctor_page_links(self, homepage_url, doctor_type, max_pages=5):
        """
        Enhanced method to crawl multiple pages and find doctor-related URLs with robust keyword matching
        """
        if not is_safe_external_url(homepage_url):
            return []

        visited_urls = set()
        all_found_urls = set()
        urls_to_visit = deque([homepage_url])
        base_domain = urlparse(homepage_url).netloc
        
        # Comprehensive keyword list for medical websites
        doctor_keywords = [
            # Basic terms
            'about-us', 'doctor', 'doctors', 'our doctors', doctor_type.lower(),
            'specialist', 'specialists', 'department', 'departments', 'our team',
            
            # Medical staff terms
            'medical team', 'healthcare team', 'medical staff', 'clinical team',
            'physicians', 'physician', 'consultants', 'cfonsultant', 'faculty',
            'medical faculty', 'clinical faculty', 'staff', 'medical professionals',
            
            # Department/Service terms
            'services', 'medical services', 'clinical services', 'specialties',
            'specialty', 'specialization', 'divisions', 'division', 'units',
            'medical units', 'clinical units', 'centers', 'centre', 'center',
            
            # About/Info terms
            'about', 'about us', 'team', 'our staff', 'meet our', 'meet the',
            'leadership', 'directory', 'staff directory', 'physician directory',
            'find a doctor', 'find doctor', 'search doctor', 'book appointment',
            
            # Medical specialties (add more as needed)
            'cardiology', 'neurology', 'orthopedic', 'pediatric', 'gynecology',
            'oncology', 'dermatology', 'psychiatry', 'radiology', 'surgery',
            'emergency', 'internal medicine', 'family medicine', 'pathology',
            
            # Common variations
            'dr.', 'dr', 'md', 'phd', 'profile', 'profiles', 'bio', 'biography',
            'credentials', 'experience', 'expertise', 'qualifications'
        ]
        
        # URL path keywords
        url_keywords = [
            'doctor', 'doctors', 'physician', 'staff', 'team', 'about',
            'department', 'service', 'specialty', 'faculty', 'profile',
            'bio', 'directory', 'find', 'search', 'meet', doctor_type.lower()
        ]
        
        pages_crawled = 0
        
        while urls_to_visit and pages_crawled < max_pages:
            current_url = urls_to_visit.popleft()
            
            if current_url in visited_urls:
                continue
                
            try:
                print(f"Crawling page {pages_crawled + 1}: {current_url}")
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()
                
                visited_urls.add(current_url)
                pages_crawled += 1
                
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    title = link.get('title', '').lower()
                    
                    # Skip empty or invalid links
                    if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                        continue
                    
                    # Convert relative URLs to absolute
                    full_url = urljoin(current_url, href)
                    parsed_url = urlparse(full_url)
                    
                    # Only process URLs from the same domain
                    if parsed_url.netloc != base_domain:
                        continue
                    
                    # Check if URL or text contains relevant keywords
                    is_relevant = False
                    
                    # Check text content
                    if text and any(keyword in text for keyword in doctor_keywords):
                        is_relevant = True
                    
                    # Check title attribute
                    if title and any(keyword in title for keyword in doctor_keywords):
                        is_relevant = True
                    
                    # Check URL path
                    url_path = parsed_url.path.lower()
                    if any(keyword in url_path for keyword in url_keywords):
                        is_relevant = True
                    
                    # Special patterns in URL
                    if re.search(r'/(doctor|physician|staff|team|about|department|specialty)s?/', url_path):
                        is_relevant = True
                    
                    if is_relevant:
                        all_found_urls.add(full_url)
                        
                        # Add to crawl queue if not visited (for next level crawling)
                        if full_url not in visited_urls and len(urls_to_visit) < 20:  # Limit queue size
                            urls_to_visit.append(full_url)
                
            except Exception as e:
                print(f"Error crawling {current_url}: {str(e)}")
                continue
        
        # Remove duplicates and sort by URL length (shorter URLs often more relevant)
        unique_urls = sorted(list(all_found_urls), key=lambda x: len(x))
        
        # Filter out obviously irrelevant URLs
        filtered_urls = []
        exclude_patterns = [
            'login', 'register', 'cart', 'checkout', 'payment', 'admin',
            'wp-admin', 'wp-content', 'privacy', 'terms', 'cookie',
            'newsletter', 'subscription', 'download', 'pdf', 'image',
            'photo', 'gallery', 'news', 'blog', 'event', 'calendar'
        ]
        
        for url in unique_urls:
            url_lower = url.lower()
            if not any(pattern in url_lower for pattern in exclude_patterns):
                filtered_urls.append(url)
        
        print(f"Found {len(filtered_urls)} potential doctor page URLs after crawling {pages_crawled} pages")
        return filtered_urls[:20]  # Return top 20 most relevant URLs

    def fetch_doctor_information(self, url, doctor_type):
        html, json_responses = self.get_rendered_html(url)
        
        json_text = json.dumps(json_responses, ensure_ascii=False)

        soup = BeautifulSoup(html, 'html.parser')
        body_text = soup.find("body").get_text(separator='\n', strip=True)

        prompt = f"""
        You are a medical website data extraction agent.

        From the following unstructured HTML text, extract structured doctor information. 
        Only include doctors related to "{doctor_type}". Each doctor should have:
        {{
            "Name": "Dr. John Doe",
            "Designation": "Senior Gynecologist",
            "Specialization": "Gynecology",
            "Contact": "john.doe@domain",
            "Doctor_Image": "http://example.com/image.jpg"
        }}

        Your response should be a just JSON array of objects, each representing a doctor. No other text should be included.  If you are unable to find a specified field then just return none
        if no doctors are found, return an empty array.
        HTML Text:
        '''{body_text[:6000]}'''
        """

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                "role": "system",
                "content": "You are an expert HTML medical page scraper. Extract structured doctor information from the provided text."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        try:
            response = chat_completion.choices[0].message.content
            if response == []:
                prompt = f"""
                    You are a medical website data extraction agent.

                    From the following structured json text, extract structured doctor information. 
                    Only include doctors related to "{doctor_type}". Each doctor should have:
                    {{
                        "Name": "Dr. John Doe",
                        "Designation": "Senior Gynecologist",
                        "Specialization": "Gynecology",
                        "Contact": "john.doe@domain",
                        "Doctor_Image": "http://example.com/image.jpg"
                    }}

                    Your response should be a just JSON array of objects, each representing a doctor. No other text should be included. If you are unable to find a specified field then just return none
                    if no doctors are found, return an empty array.
                    JSON Text:
                    '''{json_text[:6000]}'''
                """

                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                        "role": "system",
                        "content": "You are an expert JSON data extractor. Extract structured doctor information from the json data in text format provided text."
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                )
                response = chat_completion.choices[0].message.content
            return json.loads(response)
        except Exception as e:
            return f"Error: {str(e)}"
