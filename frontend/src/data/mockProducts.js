// Mock IKEA products with realistic data
export const mockProducts = [
  {
    id: 'prod_1',
    url: 'https://www.ikea.com/us/en/p/ektorp-sofa-lofallet-beige-s69220332/',
    name: 'EKTORP',
    description: 'Sofa, Lofallet beige',
    brand: 'IKEA',
    price: 599.00,
    retailer_id: 's69220332',
    ikea_item_number: '692.203.32',
    dimensions: {
      width: 85.75,
      height: 34.625,
      depth: 35.375,
      unit: 'inches'
    },
    weight: 125.5,
    category: 'seating',
    room_type: 'living_room',
    style_tags: ['modern', 'scandinavian', 'minimal'],
    placement_type: 'floor',
    assembly_required: true,
    images: [
      'https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818567_pe774489_s5.jpg',
      'https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818568_pe774490_s5.jpg',
      'https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818569_pe774491_s5.jpg',
      'https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0818570_pe774492_s5.jpg',
      'https://www.ikea.com/us/en/images/products/ektorp-sofa-lofallet-beige__0950871_pe800739_s5.jpg'
    ]
  },
  {
    id: 'prod_2',
    url: 'https://www.ikea.com/us/en/p/poaeng-armchair-birch-veneer-knisa-light-beige-s79305927/',
    name: 'POÄNG',
    description: 'Armchair, birch veneer/Knisa light beige',
    brand: 'IKEA',
    price: 129.00,
    retailer_id: 's79305927',
    ikea_item_number: '793.059.27',
    dimensions: {
      width: 26.75,
      height: 39.375,
      depth: 32.25,
      unit: 'inches'
    },
    weight: 36.5,
    category: 'seating',
    room_type: 'living_room',
    style_tags: ['modern', 'scandinavian'],
    placement_type: 'floor',
    assembly_required: true,
    images: [
      'https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0497130_pe628957_s5.jpg',
      'https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0497131_pe628958_s5.jpg',
      'https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0837447_pe628959_s5.jpg'
    ]
  },
  {
    id: 'prod_3',
    url: 'https://www.ikea.com/us/en/p/lack-coffee-table-black-brown-20449908/',
    name: 'LACK',
    description: 'Coffee table, black-brown',
    brand: 'IKEA',
    price: 39.99,
    retailer_id: '20449908',
    ikea_item_number: '204.499.08',
    dimensions: {
      width: 35.375,
      height: 17.75,
      depth: 21.625,
      unit: 'inches'
    },
    weight: 18.5,
    category: 'tables',
    room_type: 'living_room',
    style_tags: ['minimal', 'modern'],
    placement_type: 'floor',
    assembly_required: true,
    images: [
      'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop&crop=center&auto=format&q=80&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      'https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400&h=300&fit=crop&crop=center&auto=format&q=80&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    ]
  },
  {
    id: 'prod_4',
    url: 'https://www.ikea.com/us/en/p/billy-bookcase-white-00263850/',
    name: 'BILLY',
    description: 'Bookcase, white',
    brand: 'IKEA',
    price: 59.99,
    retailer_id: '00263850',
    ikea_item_number: '002.638.50',
    dimensions: {
      width: 31.5,
      height: 79.5,
      depth: 11,
      unit: 'inches'
    },
    weight: 67,
    category: 'storage',
    room_type: 'any',
    style_tags: ['minimal', 'scandinavian'],
    placement_type: 'floor',
    assembly_required: true,
    images: [
      'https://www.ikea.com/us/en/images/products/billy-bookcase-white__0625599_pe692385_s5.jpg',
      'https://www.ikea.com/us/en/images/products/billy-bookcase-white__0644785_pe702937_s5.jpg'
    ]
  },
  {
    id: 'prod_5',
    url: 'https://www.ikea.com/us/en/p/flintan-office-chair-vissle-gray-s39384822/',
    name: 'FLINTAN',
    description: 'Office chair, Vissle gray',
    brand: 'IKEA',
    price: 89.99,
    retailer_id: 's39384822',
    ikea_item_number: '393.848.22',
    dimensions: {
      width: 23.625,
      height: 37.375,
      depth: 23.625,
      unit: 'inches'
    },
    weight: 28,
    category: 'seating',
    room_type: 'office',
    style_tags: ['modern', 'ergonomic'],
    placement_type: 'floor',
    assembly_required: true,
    images: [
      'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=300&fit=crop&crop=center&auto=format&q=80&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop&crop=center&auto=format&q=80&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    ]
  }
];
