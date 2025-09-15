from typing import Dict, Any, List, Optional
import logging
import re
import asyncio
from urllib.parse import urljoin

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class IKEAScraper(BaseScraper):
    """Scraper for IKEA products and categories"""
    
    def can_handle(self, url: str) -> bool:
        """Check if this scraper can handle the URL"""
        return 'ikea.com' in url.lower()
    
    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape a single IKEA product page"""
        try:
            await self.initialize()
            await self.navigate_to_page(url)
            
            # Extract basic product data first
            product_data = {
                'url': url,
                'retailer': 'ikea',
                'retailer_id': self._extract_product_id(url),
                'name': await self._extract_name(),
                'brand': 'IKEA',
                'price': await self._extract_price(),
                'currency': 'USD',
                'images': await self._extract_images(),
            }
            
            # Extract description with section expansion
            await self._expand_product_details()
            product_data['description'] = await self._extract_description()
            
            # Extract remaining data
            product_data.update({
                'dimensions': await self._extract_dimensions(),
                'weight': await self._extract_weight(),
                'category': await self._extract_category(),
                'room_type': await self._extract_room_type(),
                'style_tags': await self._extract_style_tags(),
                'assembly_required': await self._check_assembly_required(),
                'ikea_item_number': await self._extract_item_number(),
            })
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping IKEA product {url}: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def _expand_product_details(self):
        """Expand product details section if collapsed"""
        try:
            await self.page.evaluate('''
                () => {
                    const allButtons = document.querySelectorAll('button, [role="button"]');
                    for (const btn of allButtons) {
                        if (btn.textContent && (
                            btn.textContent.includes('Product details') || 
                            btn.textContent.includes('Details') ||
                            btn.textContent.includes('Description')
                        )) {
                            if (btn.getAttribute('aria-expanded') !== 'true') {
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                }
            ''')
            await asyncio.sleep(2)
        except:
            pass  # Ignore errors in expansion

    async def _extract_name(self) -> str:
        """Extract product name"""
        try:
            selectors = [
                'h1[data-testid="product-title"]',
                'h1.pip-header-section__title--big',
                'h1.pip-header-section__title',
                'h1'
            ]
            
            for selector in selectors:
                name = await self.extract_text(selector)
                if name and name.strip():
                    return name.strip()
            
            return "Unknown Product"
        except:
            return "Unknown Product"
    
    async def _extract_price(self) -> float:
        """Extract product price"""
        try:
            selectors = [
                'span[data-testid="price-wrapper"]',
                '.pip-price__integer',
                '.pip-price',
                '[data-testid="price"]'
            ]
            
            for selector in selectors:
                price_text = await self.extract_text(selector)
                if price_text:
                    price_clean = re.sub(r'[^\d.]', '', price_text)
                    if price_clean:
                        return float(price_clean)
            
            return 0.0
        except:
            return 0.0
    
    async def _extract_description(self) -> str:
        """Extract product description/variant info"""
        try:
            description = await self.page.evaluate('''
                () => {
                    // Try the specific IKEA description selector first
                    const descriptionElement = document.querySelector('.pip-product-summary_description');
                    if (descriptionElement && descriptionElement.textContent && descriptionElement.textContent.trim()) {
                        return descriptionElement.textContent.trim();
                    }
                    
                    // Try other common selectors
                    const selectors = [
                        'div[data-testid="product-description"]',
                        '.pip-product-description',
                        '.pip-header-section__description',
                        '.pip-product-details__description',
                        '[data-testid*="description"]'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent && element.textContent.trim()) {
                            return element.textContent.trim();
                        }
                    }
                    
                    return null;
                }
            ''')
            
            if description and description.strip():
                return description.strip()
            
            return ""
        except:
            return ""
    
    async def _extract_images(self) -> List[str]:
        """Extract all product images"""
        try:
            images = await self.page.evaluate('''
                () => {
                    const images = new Set();
                    
                    const selectors = [
                        'img[data-testid*="image"]',
                        'img[src*="/images/products/"]',
                        '.pip-media-grid img',
                        '.pip-carousel img',
                        '.pip-product-media img',
                        '[data-testid="product-media"] img'
                    ];
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(img => {
                            if (img.src && img.src.includes('/images/products/')) {
                                images.add(img.src);
                            }
                        });
                    });
                    
                    return Array.from(images);
                }
            ''')
            
            processed_images = []
            for img_url in images:
                if '/images/products/' in img_url:
                    accessible_url = self._convert_to_high_res(img_url)
                    if accessible_url not in processed_images:
                        processed_images.append(accessible_url)
            
            return processed_images[:10]
        except:
            return []
    
    def _convert_to_high_res(self, img_url: str) -> str:
        """Convert IKEA image URL to accessible high resolution"""
        # IKEA image pattern: use the format that actually works
        # Keep _s5.jpg format and use ?f=xl parameter for best quality
        if '_s' in img_url:
            # Remove any existing parameters
            base_url = img_url.split('?')[0]
            # Ensure we have _s5.jpg format and add ?f=xl parameter
            processed_url = re.sub(r'_s\d+\.', '_s5.', base_url)
            return f"{processed_url}?f=xl"
        return img_url
    
    async def _extract_dimensions(self) -> Dict[str, Any]:
        """Extract product dimensions from IKEA's measurements section"""
        try:
            if not self.page or self.page.is_closed():
                return {'width': 0, 'height': 0, 'depth': 0, 'unit': 'inches'}
            
            # Try to find and click the "Measurements" section
            await self.page.evaluate('''
                () => {
                    const allButtons = document.querySelectorAll('button, [role="button"], .pip-header-section__title');
                    for (const btn of allButtons) {
                        if (btn.textContent && btn.textContent.includes('Measurements')) {
                            btn.click();
                            return true;
                        }
                    }
                    
                    const expandableButtons = document.querySelectorAll('button[aria-expanded="false"]');
                    for (const btn of expandableButtons) {
                        if (btn.textContent && btn.textContent.toLowerCase().includes('measure')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            ''')
            
            await asyncio.sleep(2)
            
            dimensions_data = await self.page.evaluate('''
                () => {
                    const selectors = [
                        '[data-testid*="measurements"]',
                        '[data-testid*="dimensions"]',
                        '.pip-product-dimensions',
                        '.pip-product-details',
                        '.pip-measurements'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent) {
                            const text = element.textContent;
                            if (text.includes('Width:') && text.includes('Height:')) {
                                return text;
                            }
                        }
                    }
                    
                    const allText = document.body.textContent;
                    const patterns = [
                        /Width:\\s*([\\d\\s/]+)"\\s*Height:\\s*([\\d\\s/]+)"\\s*Seat depth:\\s*([\\d\\s/]+)"\\s*Seat height:\\s*([\\d\\s/]+)"\\s*Seat width:\\s*([\\d\\s/]+)"\\s*Depth:\\s*([\\d\\s/]+)"/,
                        /Width:\\s*([\\d\\s/]+)"\\s*Height:\\s*([\\d\\s/]+)"\\s*Depth:\\s*([\\d\\s/]+)"/,
                        /Depth:\\s*([\\d\\s/]+)"\\s*Height:\\s*([\\d\\s/]+)"\\s*Seat depth:\\s*([\\d\\s/]+)"/,
                    ];
                    
                    for (const pattern of patterns) {
                        const match = allText.match(pattern);
                        if (match) {
                            return match[0];
                        }
                    }
                    
                    const dimensionLines = allText.split('\\n').filter(line => 
                        line.includes('Width:') || line.includes('Height:') || line.includes('Depth:')
                    );
                    
                    if (dimensionLines.length > 0) {
                        return dimensionLines.join(' ');
                    }
                    
                    return null;
                }
            ''')
            
            if dimensions_data:
                dimensions = {}
                dimension_patterns = [
                    (r'Width:\s*([\d\s/]+)"', 'width'),
                    (r'Height:\s*([\d\s/]+)"', 'height'),
                    (r'Depth:\s*([\d\s/]+)"', 'depth'),
                    (r'Seat width:\s*([\d\s/]+)"', 'width'),
                    (r'Seat depth:\s*([\d\s/]+)"', 'depth'),
                ]
                
                for pattern, dimension_key in dimension_patterns:
                    match = re.search(pattern, dimensions_data)
                    if match and dimension_key not in dimensions:
                        parsed_value = self._parse_measurement(match.group(1))
                        dimensions[dimension_key] = parsed_value
                
                if dimensions:
                    dimensions['unit'] = 'inches'
                    for key in ['width', 'height', 'depth']:
                        if key not in dimensions:
                            dimensions[key] = 0
                    return dimensions
                
        except:
            pass
        
        return {'width': 0, 'height': 0, 'depth': 0, 'unit': 'inches'}
    
    def _parse_measurement(self, text: str) -> float:
        """Parse IKEA measurement format (e.g., '85 3/4' to 85.75)"""
        try:
            text = text.strip()
            # Check for fraction
            if '/' in text:
                parts = text.split()
                if len(parts) == 2:
                    # Format: "85 3/4"
                    whole = float(parts[0])
                    fraction_parts = parts[1].split('/')
                    fraction = float(fraction_parts[0]) / float(fraction_parts[1])
                    return whole + fraction
                else:
                    # Format: "3/4"
                    fraction_parts = text.split('/')
                    return float(fraction_parts[0]) / float(fraction_parts[1])
            else:
                return float(text)
        except:
            return 0.0
    
    async def _extract_weight(self) -> float:
        """Extract product weight"""
        try:
            if not self.page or self.page.is_closed():
                return 0.0
                
            weight_text = await self.page.evaluate('''
                () => {
                    const allText = document.body.textContent;
                    const weightMatch = allText.match(/Weight:\\s*([\\d.]+)\\s*lb/);
                    if (weightMatch) {
                        return weightMatch[0];
                    }
                    return null;
                }
            ''')
            
            if weight_text:
                weight_match = re.search(r'Weight:\s*([\d.]+)\s*lb', weight_text)
                if weight_match:
                    pounds = float(weight_match.group(1))
                    return pounds * 0.453592
        except:
            pass
        
        return 0.0
    
    
    async def _extract_category(self) -> str:
        """Extract product category from breadcrumbs"""
        try:
            breadcrumb_selectors = [
                'nav[aria-label="Breadcrumbs"] ol li:nth-last-child(2) a',
                'nav[aria-label="Breadcrumbs"] ol li:nth-last-child(3) a',
                '.pip-breadcrumb a:nth-last-child(2)',
                'nav ol li:nth-last-child(2) a'
            ]
            
            for selector in breadcrumb_selectors:
                category = await self.extract_text(selector)
                if category and category.strip() and category.strip().lower() not in ['products', 'ikea']:
                    return category.strip()
            
            if '/cat/' in self.page.url:
                match = re.search(r'/cat/([^/]+)', self.page.url)
                if match:
                    return match.group(1).replace('-', ' ')
            
            product_name = await self._extract_name()
            if 'chair' in product_name.lower():
                return 'Chairs'
            elif 'sofa' in product_name.lower():
                return 'Sofas'
            elif 'table' in product_name.lower():
                return 'Tables'
            elif 'bed' in product_name.lower():
                return 'Beds'
            
            return 'Furniture'
        except:
            return 'Furniture'
    
    async def _extract_room_type(self) -> str:
        """Extract room type"""
        try:
            category = await self._extract_category()
            if 'chair' in category.lower() or 'sofa' in category.lower():
                return 'living'
            elif 'bed' in category.lower():
                return 'bedroom'
            elif 'table' in category.lower():
                return 'dining'
            else:
                return 'living'
        except:
            return 'living'
    
    async def _extract_style_tags(self) -> List[str]:
        """Extract style tags"""
        try:
            name = await self._extract_name()
            tags = []
            
            if 'swivel' in name.lower():
                tags.append('swivel')
            if 'modern' in name.lower():
                tags.append('modern')
            if 'vintage' in name.lower():
                tags.append('vintage')
            
            return tags if tags else ['contemporary']
        except:
            return ['contemporary']
    
    async def _check_assembly_required(self) -> bool:
        """Check if assembly is required"""
        try:
            assembly_text = await self.extract_text('body')
            if assembly_text:
                return 'assembly' in assembly_text.lower()
            return True
        except:
            return True
    
    async def _extract_item_number(self) -> str:
        """Extract IKEA item number"""
        try:
            item_number = await self.page.evaluate('''
                () => {
                    const testIdElement = document.querySelector('[data-testid="product-article-number"]');
                    if (testIdElement && testIdElement.textContent) {
                        return testIdElement.textContent.trim();
                    }
                    
                    const allText = document.body.textContent;
                    const articleMatch = allText.match(/Article Number\\s*([\\d.]+)/);
                    if (articleMatch) {
                        return articleMatch[1].trim();
                    }
                    
                    const elements = document.querySelectorAll('*');
                    for (const element of elements) {
                        const text = element.textContent;
                        if (text && text.includes('Article Number')) {
                            const match = text.match(/Article Number\\s*([\\d.]+)/);
                            if (match) {
                                return match[1].trim();
                            }
                        }
                    }
                    
                    const articleNumberMatch = allText.match(/\\b(\\d{3}\\.\\d{3}\\.\\d{2})\\b/);
                    if (articleNumberMatch) {
                        return articleNumberMatch[1].trim();
                    }
                    
                    return null;
                }
            ''')
            
            if item_number and item_number.strip():
                return item_number.strip()
            
            url_id = self._extract_product_id(self.page.url)
            if url_id:
                return url_id
            
            return ""
        except:
            return ""
    
    def _extract_product_id(self, url: str) -> str:
        """Extract IKEA product ID from URL"""
        # Pattern: 40581921 or similar
        match = re.search(r'-(\d{8,})', url)
        if match:
            return match.group(1)
        return ""
    
    async def scrape_category(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape products from IKEA category page (not implemented)"""
        # This method is required by the abstract base class but not used in the API
        # Return empty list to avoid breaking the interface
        return []
    
