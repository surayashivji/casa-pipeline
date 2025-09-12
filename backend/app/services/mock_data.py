"""
Mock data service that uses existing frontend mock data and saves to database
This bridges the frontend mock data with the backend database
"""

from app.models.product import Product
from app.models.processing_stage import ProcessingStage, ProductImage, Model3D, ModelLOD, BatchJob
from app.core.database import SessionLocal
from datetime import datetime, timedelta
import uuid
import random
import base64
from typing import List, Dict, Any, Optional

def generate_placeholder_image(width: int, height: int, text: str, bg_color: str = "#8b7355", text_color: str = "#ffffff") -> str:
    """Generate a placeholder image as a data URL"""
    svg = f'''
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="{bg_color}"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="{text_color}">
        {text}
      </text>
    </svg>
    '''
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"

# Import the existing frontend mock data
# We'll recreate the data structure here to avoid frontend dependencies
MOCK_PRODUCTS_DATA = [
    {
        "id": "prod_1",
        "url": "https://www.ikea.com/us/en/p/ektorp-sofa-lofallet-beige-s69220332/",
        "name": "EKTORP",
        "description": "Sofa, Lofallet beige",
        "brand": "IKEA",
        "price": 599.00,
        "retailer_id": "s69220332",
        "ikea_item_number": "692.203.32",
        "dimensions": {
            "width": 85.75,
            "height": 34.625,
            "depth": 35.375,
            "unit": "inches"
        },
        "weight": 125.5,
        "category": "seating",
        "room_type": "living_room",
        "style_tags": ["modern", "scandinavian", "minimal"],
        "placement_type": "floor",
        "assembly_required": True,
        "in_stock": True,
        "images": [
            generate_placeholder_image(400, 300, "EKTORP 1", "#8b7355", "#ffffff"),
            generate_placeholder_image(400, 300, "EKTORP 2", "#8b7355", "#ffffff"),
            generate_placeholder_image(400, 300, "EKTORP 3", "#8b7355", "#ffffff"),
            generate_placeholder_image(400, 300, "EKTORP 4", "#8b7355", "#ffffff"),
            generate_placeholder_image(400, 300, "EKTORP 5", "#8b7355", "#ffffff")
        ]
    },
    {
        "id": "prod_2",
        "url": "https://www.ikea.com/us/en/p/poaeng-armchair-birch-veneer-knisa-light-beige-s79305927/",
        "name": "POÄNG",
        "description": "Armchair, birch veneer/Knisa light beige",
        "brand": "IKEA",
        "price": 129.00,
        "retailer_id": "s79305927",
        "ikea_item_number": "793.059.27",
        "dimensions": {
            "width": 26.75,
            "height": 39.375,
            "depth": 32.25,
            "unit": "inches"
        },
        "weight": 36.5,
        "category": "seating",
        "room_type": "living_room",
        "style_tags": ["modern", "scandinavian"],
        "placement_type": "floor",
        "assembly_required": True,
        "in_stock": True,
        "images": [
            "https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0497130_pe628957_s5.jpg",
            "https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0497131_pe628958_s5.jpg",
            "https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0837447_pe628959_s5.jpg"
        ]
    },
    {
        "id": "prod_3",
        "url": "https://www.ikea.com/us/en/p/lack-coffee-table-black-brown-20449908/",
        "name": "LACK",
        "description": "Coffee table, black-brown",
        "brand": "IKEA",
        "price": 39.99,
        "retailer_id": "20449908",
        "ikea_item_number": "204.499.08",
        "dimensions": {
            "width": 35.375,
            "height": 17.75,
            "depth": 21.625,
            "unit": "inches"
        },
        "weight": 18.5,
        "category": "tables",
        "room_type": "living_room",
        "style_tags": ["minimal", "modern"],
        "placement_type": "floor",
        "assembly_required": True,
        "in_stock": True,
        "images": [
            "https://www.ikea.com/us/en/images/products/lack-coffee-table-black-brown__0836215_pe601418_s5.jpg",
            "https://www.ikea.com/us/en/images/products/lack-coffee-table-black-brown__0836216_pe601417_s5.jpg"
        ]
    },
    {
        "id": "prod_4",
        "url": "https://www.ikea.com/us/en/p/billy-bookcase-white-00263850/",
        "name": "BILLY",
        "description": "Bookcase, white",
        "brand": "IKEA",
        "price": 59.99,
        "retailer_id": "00263850",
        "ikea_item_number": "002.638.50",
        "dimensions": {
            "width": 31.5,
            "height": 79.5,
            "depth": 11,
            "unit": "inches"
        },
        "weight": 67,
        "category": "storage",
        "room_type": "any",
        "style_tags": ["minimal", "scandinavian"],
        "placement_type": "floor",
        "assembly_required": True,
        "in_stock": True,
        "images": [
            "https://www.ikea.com/us/en/images/products/billy-bookcase-white__0625599_pe692385_s5.jpg",
            "https://www.ikea.com/us/en/images/products/billy-bookcase-white__0644785_pe702937_s5.jpg"
        ]
    },
    {
        "id": "prod_5",
        "url": "https://www.ikea.com/us/en/p/flintan-office-chair-vissle-gray-s39384822/",
        "name": "FLINTAN",
        "description": "Office chair, Vissle gray",
        "brand": "IKEA",
        "price": 89.99,
        "retailer_id": "s39384822",
        "ikea_item_number": "393.848.22",
        "dimensions": {
            "width": 23.625,
            "height": 37.375,
            "depth": 23.625,
            "unit": "inches"
        },
        "weight": 28,
        "category": "seating",
        "room_type": "office",
        "style_tags": ["modern", "ergonomic"],
        "placement_type": "floor",
        "assembly_required": True,
        "in_stock": False,
        "images": [
            "https://www.ikea.com/us/en/images/products/flintan-office-chair-vissle-gray__1010901_pe828244_s5.jpg",
            "https://www.ikea.com/us/en/images/products/flintan-office-chair-vissle-gray__1010902_pe828245_s5.jpg"
        ]
    }
]

class MockDataService:
    """Service that uses existing frontend mock data and saves to database"""
    
    @staticmethod
    def get_mock_products(limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get mock products from existing frontend data"""
        products = MOCK_PRODUCTS_DATA[:limit]
        
        if status:
            # Filter by status if needed
            products = [p for p in products if p.get('status', 'scraped') == status]
        
        return products
    
    @staticmethod
    def get_mock_product(url: str) -> Optional[Dict[str, Any]]:
        """Get a specific mock product by URL"""
        for product in MOCK_PRODUCTS_DATA:
            if product['url'] == url:
                return product
        return None
    
    @staticmethod
    def create_mock_product_in_db(url: str, db: SessionLocal) -> Product:
        """Create a mock product in the database using existing frontend data"""
        
        # Try to find existing product by URL
        existing_product = db.query(Product).filter(Product.url == url).first()
        if existing_product:
            return existing_product
        
        # Find matching mock data
        mock_data = MockDataService.get_mock_product(url)
        if not mock_data:
            # Generate a new mock product if not found
            mock_data = MockDataService._generate_mock_product(url)
        
        # Create database product
        product = Product(
            url=mock_data['url'],
            name=mock_data['name'],
            brand=mock_data['brand'],
            variant_info=mock_data.get('description', ''),
            price=mock_data['price'],
            width_inches=mock_data['dimensions']['width'],
            height_inches=mock_data['dimensions']['height'],
            depth_inches=mock_data['dimensions']['depth'],
            weight_kg=mock_data['weight'],
            category=mock_data['category'],
            room_type=mock_data['room_type'],
            style_tags=mock_data['style_tags'],
            placement_type=mock_data['placement_type'],
            retailer_id=mock_data['retailer_id'],
            ikea_item_number=mock_data['ikea_item_number'],
            assembly_required=mock_data['assembly_required'],
            in_stock=mock_data['in_stock'],
            status="scraped",
            processing_mode="single"
        )
        
        db.add(product)
        db.flush()  # Get the ID
        
        # Create mock images
        for i, image_url in enumerate(mock_data['images']):
            img = ProductImage(
                product_id=product.id,
                image_type="original",
                image_order=i,
                s3_url=image_url,
                width_pixels=1024,
                height_pixels=1024,
                format="jpg",
                is_primary=(i == 0)
            )
            db.add(img)
        
        # Create initial processing stage
        stage = ProcessingStage(
            product_id=product.id,
            stage_name="scraping",
            stage_order=1,
            status="completed",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            processing_time_seconds=2.5,
            cost_usd=0.05,
            input_data={"url": url},
            output_data={"images_found": len(mock_data['images'])},
            stage_metadata={"retailer": "ikea", "mock": True}
        )
        db.add(stage)
        
        db.commit()
        return product
    
    @staticmethod
    def _generate_mock_product(url: str) -> Dict[str, Any]:
        """Generate a new mock product if not found in existing data"""
        product_names = ["EKTORP", "POÄNG", "LACK", "BILLY", "FLINTAN", "HEMNES", "MALM", "KALLAX"]
        categories = ["seating", "tables", "storage", "decor"]
        room_types = ["living_room", "bedroom", "office", "kitchen"]
        styles = [["modern", "scandinavian"], ["minimal", "contemporary"], ["rustic", "industrial"]]
        
        return {
            "id": f"prod_{uuid.uuid4().hex[:8]}",
            "url": url,
            "name": random.choice(product_names),
            "description": f"{random.choice(['Sofa', 'Chair', 'Table', 'Bookcase'])} in {random.choice(['beige', 'gray', 'white', 'black'])}",
            "brand": "IKEA",
            "price": round(random.uniform(29.99, 599.99), 2),
            "retailer_id": f"s{random.randint(10000000, 99999999)}",
            "ikea_item_number": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(10, 99)}",
            "dimensions": {
                "width": round(random.uniform(20, 90), 2),
                "height": round(random.uniform(15, 80), 2),
                "depth": round(random.uniform(15, 40), 2),
                "unit": "inches"
            },
            "weight": round(random.uniform(5, 150), 1),
            "category": random.choice(categories),
            "room_type": random.choice(room_types),
            "style_tags": random.choice(styles),
            "placement_type": "floor",
            "assembly_required": random.choice([True, False]),
            "in_stock": random.choice([True, False]),
            "images": [
                generate_placeholder_image(400, 300, f"Product {i}", "#8b7355", "#ffffff")
                for i in range(1, random.randint(3, 6))
            ]
        }
    
    @staticmethod
    def create_processing_stage(product_id: uuid.UUID, stage_name: str, 
                               input_data: Dict[str, Any], output_data: Dict[str, Any], 
                               db: SessionLocal) -> ProcessingStage:
        """Create a processing stage record"""
        
        stage = ProcessingStage(
            product_id=product_id,
            stage_name=stage_name,
            stage_order=MockDataService._get_stage_order(stage_name),
            status="completed",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            processing_time_seconds=random.uniform(1, 5),
            cost_usd=MockDataService._get_stage_cost(stage_name),
            input_data=input_data,
            output_data=output_data,
            stage_metadata={"mock": True}
        )
        
        db.add(stage)
        db.commit()
        return stage
    
    @staticmethod
    def _get_stage_order(stage_name: str) -> int:
        """Get stage order number"""
        order_map = {
            "scraping": 1,
            "image_selection": 2,
            "background_removal": 3,
            "image_approval": 4,
            "model_generation": 5,
            "optimization": 6,
            "saving": 7
        }
        return order_map.get(stage_name, 1)
    
    @staticmethod
    def _get_stage_cost(stage_name: str) -> float:
        """Get realistic stage cost"""
        cost_map = {
            "scraping": 0.05,
            "image_selection": 0.0,
            "background_removal": 0.15,
            "image_approval": 0.0,
            "model_generation": 0.50,
            "optimization": 0.10,
            "saving": 0.01
        }
        return cost_map.get(stage_name, 0.0)
    
    @staticmethod
    def create_mock_batch_job(product_ids: List[str], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock batch job"""
        return {
            "id": f"batch_{uuid.uuid4().hex[:8]}",
            "product_ids": product_ids,
            "status": "processing",
            "total_products": len(product_ids),
            "processed_products": 0,
            "successful_products": 0,
            "failed_products": 0,
            "settings": settings,
            "created_at": datetime.now().isoformat()
        }

# Create singleton instance
mock_data = MockDataService()
