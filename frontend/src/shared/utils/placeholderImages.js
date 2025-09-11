// Placeholder image utilities to generate SVG data URLs for mock images

/**
 * Generate a placeholder image as a data URL
 */
export const generatePlaceholder = (width, height, text, bgColor = '#8b7355', textColor = '#ffffff') => {
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="${bgColor}"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="${textColor}">
        ${text}
      </text>
    </svg>
  `;
  
  return `data:image/svg+xml;base64,${btoa(svg)}`;
};

/**
 * Generate placeholder images for different stages
 */
export const placeholders = {
  productImage: (name) => generatePlaceholder(400, 300, name || 'Product Image', '#8b7355', '#ffffff'),
  
  backgroundRemoved: (name) => generatePlaceholder(400, 300, `${name || 'Product'} No BG`, '#ffffff', '#000000'),
  
  model3D: (name) => generatePlaceholder(400, 300, `${name || 'Product'} 3D`, '#4a5568', '#ffffff'),
  
  productGrid: (name) => generatePlaceholder(200, 200, name || 'Product', '#e5e7eb', '#4b5563'),
  
  mask: () => generatePlaceholder(400, 300, 'Mask', '#000000', '#ffffff'),
};

/**
 * Get a placeholder avatar/icon
 */
export const getPlaceholderIcon = (letter = '?', bgColor = '#6366f1') => {
  const svg = `
    <svg width="40" height="40" xmlns="http://www.w3.org/2000/svg">
      <circle cx="20" cy="20" r="20" fill="${bgColor}"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="white">
        ${letter.toUpperCase()}
      </text>
    </svg>
  `;
  
  return `data:image/svg+xml;base64,${btoa(svg)}`;
};
