import requests
from datetime import datetime, timedelta
from typing import List
from bs4 import BeautifulSoup
from .base import NewsSourceHandler, Article
import re
import json

class SECFilingsHandler(NewsSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__(
            source_name="SEC Filings",
            feed_url="https://data.sec.gov/submissions/CIK{}.json",
            max_articles=max_articles
        )
        self.company_feed_url = "https://www.sec.gov/files/company_tickers.json"

    def _get_10k_content(self, accession_number: str, cik: str, headers: dict) -> str:
        """Extract content from a 10-K filing"""
        try:
            # Get the filing document
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{accession_number}-index.htm"
            response = requests.get(filing_url, headers=headers)
            response.raise_for_status()
            
            # Parse the filing page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the 10-K document link (usually has '10-k' in the description)
            doc_link = None
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 4 and '10-k' in cols[3].text.lower():
                    doc_link = cols[2].find('a')['href'] if cols[2].find('a') else None
                    break
            
            if not doc_link:
                return "Could not find 10-K document"
                
            # Get the actual document
            doc_url = f"https://www.sec.gov{doc_link}"
            doc_response = requests.get(doc_url, headers=headers)
            doc_response.raise_for_status()
            
            # Parse the document
            doc_soup = BeautifulSoup(doc_response.content, 'html.parser')
            
            # Priority sections to extract (in order of importance)
            priority_items = [
                'Item 1. Business',
                'Item 1A. Risk Factors',
                'Item 2. Management\'s Discussion',
                'Item 7. Management\'s Discussion',
                'Item 7A. Quantitative and Qualitative Disclosures'
            ]
            
            content_sections = []
            current_section = None
            current_content = []
            
            # First pass: find section boundaries
            sections = {}
            for tag in doc_soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4']):
                text = tag.get_text(strip=True)
                
                # Check if this is a section header
                for item in priority_items:
                    if item.lower() in text.lower():
                        if current_section:
                            sections[current_section] = current_content
                        current_section = item
                        current_content = []
                        break
                
                if current_section and text:
                    # Only add non-empty, meaningful content
                    if len(text) > 10:  # Skip very short lines
                        current_content.append(text)
            
            if current_section:
                sections[current_section] = current_content
            
            # Build final content with size limits
            final_content = []
            max_section_chars = 3000  # Limit each section to ~3000 chars
            
            for item in priority_items:
                if item in sections:
                    section_content = sections[item]
                    content_text = ' '.join(section_content)
                    
                    # Truncate section if too long
                    if len(content_text) > max_section_chars:
                        content_text = content_text[:max_section_chars] + "..."
                    
                    final_content.append(f"{item}:\n{content_text}")
                    
                    # Break if we've collected enough content
                    if sum(len(s) for s in final_content) > 10000:  # Total limit ~10k chars
                        break
            
            return "\n\n".join(final_content)
            
        except Exception as e:
            print(f"Error extracting 10-K content: {str(e)}")
            return ""
        
    def fetch_articles(self) -> List[Article]:
        try:
            # Add SEC required headers
            headers = {
                'User-Agent': 'MKNewsCopilot francis@madkudu.com'
            }
            
            # First get list of companies
            response = requests.get(self.company_feed_url, headers=headers)
            response.raise_for_status()
            companies = response.json()
            
            articles = []
            processed = 0
            
            # Process each company until we hit max_articles
            for _, company_info in companies.items():
                if processed >= self.max_articles:
                    break
                    
                try:
                    # Handle CIK format - ensure it's a string and properly padded
                    if 'cik_str' in company_info:
                        cik = str(company_info['cik_str']).zfill(10)
                    else:
                        cik = str(company_info.get('cik', '')).zfill(10)
                        
                    if not cik or len(cik.strip('0')) == 0:
                        print(f"Invalid CIK for company {company_info.get('title', 'Unknown')}")
                        continue
                        
                    company_name = company_info.get('title', '')
                    if not company_name:
                        continue
                    
                    # Get company filings
                    filings_url = self.feed_url.format(cik)
                    response = requests.get(filings_url, headers=headers)
                    response.raise_for_status()
                    filings = response.json()
                    
                    # Look for recent 10-K filings
                    recent_filings = filings.get('filings', {}).get('recent', {})
                    if not recent_filings:
                        continue
                        
                    form_types = recent_filings.get('form', [])
                    filing_dates = recent_filings.get('filingDate', [])
                    accession_numbers = recent_filings.get('accessionNumber', [])
                    
                    if not form_types or not filing_dates or not accession_numbers:
                        continue
                    
                    # Find most recent 10-K
                    for i, form in enumerate(form_types):
                        if form == '10-K' and i < len(filing_dates) and i < len(accession_numbers):
                            # Get the full document content
                            content = self._get_10k_content(accession_numbers[i], cik.lstrip('0'), headers)
                            
                            if not content:
                                continue
                                
                            # Create article
                            article = Article(
                                title=f"{company_name} - Annual Report (10-K)",
                                url=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_numbers[i].replace('-', '')}/{accession_numbers[i]}-index.htm",
                                content=content,
                                published_at=datetime.strptime(filing_dates[i], '%Y-%m-%d'),
                                source=self.source_name,
                                companies=[company_name],
                                topics=['Financial Results'],
                                summary=""
                            )
                            articles.append(article)
                            processed += 1
                            print(f"Successfully processed 10-K for {company_name}")
                            break
                            
                except Exception as e:
                    print(f"Error processing company {company_info.get('title', 'Unknown')}: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error fetching SEC filings: {str(e)}")
            return []