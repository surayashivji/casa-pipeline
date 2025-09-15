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
        logger.info(f"Scraping IKEA product: {url}")
        
        try:
            await self.initialize()
            
            # Navigate to product page
            await self.navigate_to_page(url)
            
            # Extract ALL data while browser is still open
            logger.info("Extracting all product data...")
            
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
            
            # Extract description
            logger.info("Extracting description...")
            # Try to expand product details section first (like we do for measurements)
            await self.page.evaluate('''
                () => {
                    // Look for buttons containing "Product details" or similar
                    const allButtons = document.querySelectorAll('button, [role="button"]');
                    let productDetailsBtn = null;
                    
                    for (const btn of allButtons) {
                        if (btn.textContent && (
                            btn.textContent.includes('Product details') || 
                            btn.textContent.includes('Details') ||
                            btn.textContent.includes('Description')
                        )) {
                            productDetailsBtn = btn;
                            break;
                        }
                    }
                    
                    // Click the product details button if found and collapsed
                    if (productDetailsBtn && productDetailsBtn.getAttribute('aria-expanded') !== 'true') {
                        productDetailsBtn.click();
                        console.log('Clicked Product details button');
                        return true;
                    }
                    
                    return false;
                }
            ''')
            
            # Wait for the content to expand
            await asyncio.sleep(2)
            product_data['description'] = await self._extract_description()
            
            # Extract dimensions (most important)
            logger.info("Extracting dimensions...")
            product_data['dimensions'] = await self._extract_dimensions()
            
            # Extract remaining data
            product_data.update({
                'weight': await self._extract_weight(),
                'category': await self._extract_category(),
                'room_type': await self._extract_room_type(),
                'style_tags': await self._extract_style_tags(),
                'assembly_required': await self._check_assembly_required(),
                'ikea_item_number': await self._extract_item_number(),
                'variants': await self._extract_variants()
            })
            
            logger.info(f"Successfully scraped: {product_data['name']}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping IKEA product {url}: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def _extract_name(self) -> str:
        """Extract product name"""
        try:
            # Try multiple selectors for product name
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
            
        except Exception as e:
            logger.error(f"Failed to extract product name: {e}")
            return "Unknown Product"
    
    async def _extract_price(self) -> float:
        """Extract product price"""
        try:
            # Try multiple selectors for price
            selectors = [
                'span[data-testid="price-wrapper"]',
                '.pip-price__integer',
                '.pip-price',
                '[data-testid="price"]'
            ]
            
            for selector in selectors:
                price_text = await self.extract_text(selector)
                if price_text:
                    # Remove currency symbols and convert to float
                    price_clean = re.sub(r'[^\d.]', '', price_text)
                    if price_clean:
                        return float(price_clean)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to extract price: {e}")
            return 0.0
    
    async def _extract_description(self) -> str:
        """Extract product description/variant info"""
        try:
            # First try to expand product details section (like measurements)
            await self.page.evaluate('''
                () => {
                    // Look for buttons containing "Product details" or similar
                    const allButtons = document.querySelectorAll('button, [role="button"]');
                    let productDetailsBtn = null;
                    
                    for (const btn of allButtons) {
                        if (btn.textContent && (
                            btn.textContent.includes('Product details') || 
                            btn.textContent.includes('Details') ||
                            btn.textContent.includes('Description')
                        )) {
                            productDetailsBtn = btn;
                            break;
                        }
                    }
                    
                    // Click the product details button if found and collapsed
                    if (productDetailsBtn && productDetailsBtn.getAttribute('aria-expanded') !== 'true') {
                        productDetailsBtn.click();
                        console.log('Clicked Product details button');
                        return true;
                    }
                    
                    return false;
                }
            ''')
            
            # Wait for the content to expand
            await asyncio.sleep(1)
            
            # Try the specific selector first, then fallback to text search
            description = await self.page.evaluate('''
                () => {
                    // Try the specific IKEA description selector first (note: single underscore)
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
                    
                    // Fallback: search for MILA description in all text
                    const allText = document.body.textContent;
                    if (allText.includes('MILA swivel easy chair')) {
                        const match = allText.match(/MILA swivel easy chair[^.]*\\.[^.]*\\.[^.]*\\./);
                        if (match) {
                            return match[0].trim();
                        }
                    }
                    
                    return null;
                }
            ''')
            
            if description and description.strip():
                logger.info(f"✅ Extracted description: {description[:100]}...")
                return description.strip()
            
            # No fallback - if we can't find a real description, return empty
            logger.warning("No specific description found")
            return ""
            
        except Exception as e:
            logger.error(f"Failed to extract description: {e}")
            return ""
    
    async def _extract_images(self) -> List[str]:
        """Extract all product images"""
        try:
            images = await self.page.evaluate('''
                () => {
                    const images = new Set();
                    
                    // Try multiple selectors for product images
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
            
            # Process and convert to accessible format
            processed_images = []
            for img_url in images:
                if '/images/products/' in img_url:
                    accessible_url = self._convert_to_high_res(img_url)
                    if accessible_url not in processed_images:
                        processed_images.append(accessible_url)
            
            # Limit to 10 images
            return processed_images[:10]
            
        except Exception as e:
            logger.error(f"Failed to extract images: {e}")
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
            # Check if browser is still open
            if not self.page or self.page.is_closed():
                logger.error("Browser page is closed, cannot extract dimensions")
                return {'width': 0, 'height': 0, 'depth': 0, 'unit': 'inches'}
            # Try to find and click the "Measurements" section
            await self.page.evaluate('''
                () => {
                    // Look for buttons containing "Measurements"
                    const allButtons = document.querySelectorAll('button, [role="button"], .pip-header-section__title');
                    let measurementsBtn = null;
                    
                    for (const btn of allButtons) {
                        if (btn.textContent && btn.textContent.includes('Measurements')) {
                            measurementsBtn = btn;
                            break;
                        }
                    }
                    
                    // Click the measurements button if found
                    if (measurementsBtn) {
                        measurementsBtn.click();
                        console.log('Clicked Measurements button');
                        return true;
                    }
                    
                    // Also try clicking any expandable sections
                    const expandableButtons = document.querySelectorAll('button[aria-expanded="false"]');
                    for (const btn of expandableButtons) {
                        if (btn.textContent && btn.textContent.toLowerCase().includes('measure')) {
                            btn.click();
                            console.log('Clicked expandable measurements section');
                            return true;
                        }
                    }
                    
                    return false;
                }
            ''')
            
            # Wait for the measurements to load
            await asyncio.sleep(2)
            
            # Now extract the dimensions
            dimensions_data = await self.page.evaluate('''
                () => {
                    // Look for the measurements content in various places
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
                    
                    // If not found in specific sections, search the entire page
                    const allText = document.body.textContent;
                    
                    // Look for the exact IKEA format
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
                    
                    // Fallback: look for any dimension-like text
                    const dimensionLines = allText.split('\\n').filter(line => 
                        line.includes('Width:') || line.includes('Height:') || line.includes('Depth:')
                    );
                    
                    if (dimensionLines.length > 0) {
                        return dimensionLines.join(' ');
                    }
                    
                    return null;
                }
            ''')
            
            logger.info(f"Dimensions data found: {dimensions_data[:200] if dimensions_data else 'None'}")
            
            if dimensions_data:
                dimensions = {}
                
                # Extract dimensions using the specific IKEA format
                dimension_patterns = [
                    (r'Width:\s*([\d\s/]+)"', 'width'),
                    (r'Height:\s*([\d\s/]+)"', 'height'),
                    (r'Depth:\s*([\d\s/]+)"', 'depth'),
                    (r'Seat width:\s*([\d\s/]+)"', 'width'),  # Use seat width as width if no main width
                    (r'Seat depth:\s*([\d\s/]+)"', 'depth'),  # Use seat depth as depth if no main depth
                ]
                
                for pattern, dimension_key in dimension_patterns:
                    match = re.search(pattern, dimensions_data)
                    if match and dimension_key not in dimensions:  # Don't overwrite if we already have a value
                        parsed_value = self._parse_measurement(match.group(1))
                        dimensions[dimension_key] = parsed_value
                        logger.info(f"Extracted {dimension_key}: {parsed_value}")
                
                # If we found at least one dimension, return what we have
                if dimensions:
                    dimensions['unit'] = 'inches'
                    # Fill in missing dimensions with 0
                    for key in ['width', 'height', 'depth']:
                        if key not in dimensions:
                            dimensions[key] = 0
                    return dimensions
                
        except Exception as e:
            logger.error(f"Failed to extract dimensions: {e}")
        
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
            # Check if browser is still open
            if not self.page or self.page.is_closed():
                logger.error("Browser page is closed, cannot extract weight")
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
                    # Convert pounds to kg
                    pounds = float(weight_match.group(1))
                    return pounds * 0.453592
            
        except Exception as e:
            logger.error(f"Failed to extract weight: {e}")
        
        return 0.0
    
    
    async def _extract_category(self) -> str:
        """Extract product category from breadcrumbs"""
        try:
            # Try to get category from breadcrumbs with multiple selectors
            breadcrumb_selectors = [
                'nav[aria-label="Breadcrumbs"] ol li:nth-last-child(2) a',
                'nav[aria-label="Breadcrumbs"] ol li:nth-last-child(3) a',  # Sometimes the category is 3rd from last
                '.pip-breadcrumb a:nth-last-child(2)',
                'nav ol li:nth-last-child(2) a'
            ]
            
            for selector in breadcrumb_selectors:
                category = await self.extract_text(selector)
                if category and category.strip() and category.strip().lower() not in ['products', 'ikea']:
                    return category.strip()
            
            # Fallback: extract from URL
            if '/cat/' in self.page.url:
                match = re.search(r'/cat/([^/]+)', self.page.url)
                if match:
                    return match.group(1).replace('-', ' ')
            
            # Try to infer from product name
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
            
        except Exception as e:
            logger.error(f"Failed to extract category: {e}")
            return 'Furniture'
    
    async def _extract_room_type(self) -> str:
        """Extract room type"""
        try:
            # This would need more sophisticated logic based on category
            category = await self._extract_category()
            if 'chair' in category.lower() or 'sofa' in category.lower():
                return 'living'
            elif 'bed' in category.lower():
                return 'bedroom'
            elif 'table' in category.lower():
                return 'dining'
            else:
                return 'living'
                
        except Exception as e:
            logger.error(f"Failed to extract room type: {e}")
            return 'living'
    
    async def _extract_style_tags(self) -> List[str]:
        """Extract style tags"""
        # For now, return default tags based on product name
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
            
        except Exception as e:
            logger.error(f"Failed to extract style tags: {e}")
            return ['contemporary']
    
    async def _check_assembly_required(self) -> bool:
        """Check if assembly is required"""
        try:
            assembly_text = await self.extract_text('body')
            if assembly_text:
                return 'assembly' in assembly_text.lower()
            return True
            
        except Exception as e:
            logger.error(f"Failed to check assembly requirement: {e}")
            return True
    
    async def _extract_item_number(self) -> str:
        """Extract IKEA item number"""
        try:
            # Try multiple approaches to find the Article Number
            item_number = await self.page.evaluate('''
                () => {
                    // Method 1: Look for specific data-testid
                    const testIdElement = document.querySelector('[data-testid="product-article-number"]');
                    if (testIdElement && testIdElement.textContent) {
                        return testIdElement.textContent.trim();
                    }
                    
                    // Method 2: Look for text containing "Article Number"
                    const allText = document.body.textContent;
                    const articleMatch = allText.match(/Article Number\\s*([\\d.]+)/);
                    if (articleMatch) {
                        return articleMatch[1].trim();
                    }
                    
                    // Method 3: Look for elements containing article number pattern
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
                    
                    // Method 4: Look for any text that looks like an IKEA article number (XXX.XXX.XX format)
                    const articleNumberMatch = allText.match(/\\b(\\d{3}\\.\\d{3}\\.\\d{2})\\b/);
                    if (articleNumberMatch) {
                        return articleNumberMatch[1].trim();
                    }
                    
                    return null;
                }
            ''')
            
            if item_number and item_number.strip():
                logger.info(f"✅ Extracted IKEA item number: {item_number}")
                return item_number.strip()
            
            # Fallback: Extract from URL
            url_id = self._extract_product_id(self.page.url)
            if url_id:
                logger.info(f"Using URL fallback for item number: {url_id}")
                return url_id
            
            logger.warning("No IKEA item number found")
            return ""
            
        except Exception as e:
            logger.error(f"Failed to extract item number: {e}")
            return ""
    
    def _extract_product_id(self, url: str) -> str:
        """Extract IKEA product ID from URL"""
        # Pattern: 40581921 or similar
        match = re.search(r'-(\d{8,})', url)
        if match:
            return match.group(1)
        return ""
    
    async def _extract_variants(self) -> List[Dict[str, Any]]:
        """Extract product variants (colors, materials, etc.)"""
        try:
            # Check if browser is still open
            if not self.page or self.page.is_closed():
                logger.error("Browser page is closed, cannot extract variants")
                return []
            
            variants = await self.page.evaluate('''
                () => {
                    const variants = [];
                    
                    // Look for IKEA product variants - focus on actual product options
                    // Strategy 1: Look for buttons that contain the product name pattern
                    const allButtons = document.querySelectorAll('button');
                    allButtons.forEach(btn => {
                        const text = btn.textContent?.trim();
                        if (text && text.length > 10 && text.length < 100) {
                            // Check if this looks like a product variant (contains product name + variant)
                            const lowerText = text.toLowerCase();
                            
                            // Skip obvious UI elements
                            if (!lowerText.includes('search') && 
                                !lowerText.includes('clear') && 
                                !lowerText.includes('products') &&
                                !lowerText.includes('rooms') &&
                                !lowerText.includes('deals') &&
                                !lowerText.includes('home accessories') &&
                                !lowerText.includes('ideas') &&
                                !lowerText.includes('design') &&
                                !lowerText.includes('business') &&
                                !lowerText.includes('services') &&
                                !lowerText.includes('support') &&
                                !lowerText.includes('play') &&
                                !lowerText.includes('in store') &&
                                !lowerText.includes('what\'s included') &&
                                !lowerText.includes('materials') &&
                                !lowerText.includes('assembly') &&
                                !lowerText.includes('packaging') &&
                                !lowerText.includes('show all') &&
                                !lowerText.includes('switch between') &&
                                !lowerText.includes('english') &&
                                !lowerText.includes('select') && 
                                !lowerText.includes('choose') &&
                                !lowerText.includes('add to bag') &&
                                !lowerText.includes('buy') &&
                                !lowerText.includes('view') &&
                                !lowerText.includes('all media') &&
                                !lowerText.includes('measurements') &&
                                !lowerText.includes('details') &&
                                !lowerText.includes('change') &&
                                !lowerText.includes('delivery') &&
                                !lowerText.includes('pickup') &&
                                !lowerText.includes('check availability') &&
                                !lowerText.includes('(14)') &&
                                !lowerText.includes('en') &&
                                !lowerText.includes('us')) {
                                
                                // Check if this looks like a product variant
                                // Should contain the main product name + variant description
                                if (text.includes('STOCKHOLM') || 
                                    text.includes('sofa') || 
                                    text.includes('chair') ||
                                    text.includes('table') ||
                                    text.includes('bed') ||
                                    text.includes('desk') ||
                                    text.includes('shelf') ||
                                    text.includes('cabinet') ||
                                    text.includes('dresser') ||
                                    text.includes('nightstand')) {
                                    
                                    variants.push({
                                        name: text,
                                        available: !btn.disabled && !btn.classList.contains('disabled')
                                    });
                                }
                            }
                        }
                    });
                    
                    // Strategy 2: Look for buttons near "Choose cover" text (more targeted)
                    const chooseCoverElements = document.querySelectorAll('*');
                    chooseCoverElements.forEach(el => {
                        if (el.textContent && el.textContent.includes('Choose cover')) {
                            // Find the parent container that holds the cover options
                            const container = el.closest('div, section, article, [class*="pip"]') || el.parentElement;
                            if (container) {
                                // Look for buttons that contain variant names
                                const buttons = container.querySelectorAll('button');
                                buttons.forEach(btn => {
                                    const text = btn.textContent?.trim();
                                    if (text && text.length > 5 && text.length < 100) {
                                        // Check if this looks like a variant name (not UI text)
                                        const lowerText = text.toLowerCase();
                                        if (!lowerText.includes('choose') &&
                                            !lowerText.includes('cover') &&
                                            !lowerText.includes('select') &&
                                            !lowerText.includes('search') &&
                                            !lowerText.includes('clear') &&
                                            !lowerText.includes('products') &&
                                            !lowerText.includes('rooms') &&
                                            !lowerText.includes('deals') &&
                                            !lowerText.includes('home accessories') &&
                                            !lowerText.includes('ideas') &&
                                            !lowerText.includes('design') &&
                                            !lowerText.includes('business') &&
                                            !lowerText.includes('services') &&
                                            !lowerText.includes('support') &&
                                            !lowerText.includes('play') &&
                                            !lowerText.includes('in store') &&
                                            !lowerText.includes('what\'s included') &&
                                            !lowerText.includes('materials') &&
                                            !lowerText.includes('assembly') &&
                                            !lowerText.includes('packaging') &&
                                            !lowerText.includes('show all') &&
                                            !lowerText.includes('switch between') &&
                                            !lowerText.includes('english') &&
                                            !lowerText.includes('check availability') &&
                                            !lowerText.includes('(14)') &&
                                            !lowerText.includes('en') &&
                                            !lowerText.includes('us')) {
                                            
                                            // Check if this looks like a variant name
                                            if (text.includes('Alhamn') || 
                                                text.includes('Djurmo') || 
                                                text.includes('Vissle') ||
                                                text.includes('Orrsta') ||
                                                text.includes('Kelinge') ||
                                                text.includes('beige') ||
                                                text.includes('brown') ||
                                                text.includes('turquoise') ||
                                                text.includes('gray') ||
                                                text.includes('white') ||
                                                text.includes('black') ||
                                                text.includes('blue') ||
                                                text.includes('red') ||
                                                text.includes('green')) {
                                                
                                                variants.push({
                                                    name: text,
                                                    available: !btn.disabled && !btn.classList.contains('disabled')
                                                });
                                            }
                                        }
                                    }
                                });
                            }
                        }
                    });
                    
                    // Remove duplicates
                    const uniqueVariants = [];
                    const seen = new Set();
                    variants.forEach(variant => {
                        if (!seen.has(variant.name)) {
                            seen.add(variant.name);
                            uniqueVariants.push(variant);
                        }
                    });
                    
                    return uniqueVariants;
                }
            ''')
            
            logger.info(f"Found {len(variants)} variants: {[v['name'] for v in variants]}")
            return variants
            
        except Exception as e:
            logger.error(f"Failed to extract variants: {e}")
            return []
    
    async def scrape_category(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape products from IKEA category page"""
        logger.info(f"Scraping IKEA category: {url}")
        
        try:
            await self.initialize()
            
            # Navigate to category page
            await self.navigate_to_page(url)
            
            products = []
            
            # Scroll to load more products (IKEA uses lazy loading)
            logger.info("Scrolling to load more products...")
            await self.scroll_to_load_content(scrolls=3)
            
            # Extract product data from the page
            product_data = await self.page.evaluate('''
                () => {
                    const products = [];
                    
                    // Try different selectors for product cards
                    const selectors = [
                        '[data-testid="plp-product-card"]',
                        '.plp-product',
                        '.pip-product',
                        '[data-product-id]'
                    ];
                    
                    let productElements = [];
                    for (const selector of selectors) {
                        productElements = document.querySelectorAll(selector);
                        if (productElements.length > 0) {
                            console.log(`Found ${productElements.length} products with selector: ${selector}`);
                            break;
                        }
                    }
                    
                    productElements.forEach((card, index) => {
                        try {
                            // Try to find the product link
                            const linkElement = card.querySelector('a[href*="/p/"]') || 
                                              card.querySelector('a') ||
                                              card.closest('a');
                            
                            if (!linkElement) return;
                            
                            const productUrl = linkElement.href;
                            if (!productUrl.includes('/p/')) return; // Skip if not a product URL
                            
                            // Try to extract product name
                            const nameSelectors = [
                                '.pip-product-compact__name',
                                '.plp-product__name',
                                'h3',
                                'h2',
                                '[data-testid*="name"]',
                                '.pip-header-section__title'
                            ];
                            
                            let productName = '';
                            for (const nameSelector of nameSelectors) {
                                const nameElement = card.querySelector(nameSelector);
                                if (nameElement && nameElement.textContent.trim()) {
                                    productName = nameElement.textContent.trim();
                                    break;
                                }
                            }
                            
                            // Try to extract price
                            const priceSelectors = [
                                '.pip-price__integer',
                                '.plp-price',
                                '[data-testid*="price"]',
                                '.price'
                            ];
                            
                            let priceText = '';
                            for (const priceSelector of priceSelectors) {
                                const priceElement = card.querySelector(priceSelector);
                                if (priceElement && priceElement.textContent.trim()) {
                                    priceText = priceElement.textContent.trim();
                                    break;
                                }
                            }
                            
                            // Try to extract image
                            const imgElement = card.querySelector('img');
                            const imageUrl = imgElement ? imgElement.src : '';
                            
                            if (productName && productUrl) {
                                products.push({
                                    url: productUrl,
                                    name: productName,
                                    price: priceText,
                                    image: imageUrl,
                                    index: index
                                });
                            }
                        } catch (e) {
                            console.log(`Error processing product card ${index}:`, e);
                        }
                    });
                    
                    return products;
                }
            ''')
            
            logger.info(f"Found {len(product_data)} products on page")
            
            # Limit results and format
            product_data = product_data[:limit]
            
            for item in product_data:
                try:
                    # Parse price
                    price = 0.0
                    if item['price']:
                        price_clean = re.sub(r'[^\d.]', '', item['price'])
                        if price_clean:
                            price = float(price_clean)
                    
                    products.append({
                        'url': item['url'],
                        'name': item['name'],
                        'price': price,
                        'images': [item['image']] if item['image'] else [],
                        'retailer': 'ikea',
                        'category': self._extract_category_from_url(url),
                        'retailer_id': self._extract_product_id(item['url'])
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing product {item.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(products)} products from category")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping IKEA category {url}: {e}")
            raise
        finally:
            await self.cleanup()
    
    def _extract_category_from_url(self, url: str) -> str:
        """Extract category name from URL"""
        try:
            match = re.search(r'/cat/([^/]+)', url)
            if match:
                category = match.group(1).replace('-', ' ')
                return category.title()
            return 'Furniture'
        except:
            return 'Furniture'
