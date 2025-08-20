// Simple script to create placeholder test images
// Run with: node scripts/create-test-images.js

import fs from 'fs';
import path from 'path';

const celebrities = [
    "leonardo-dicaprio",
    "emma-watson", 
    "ryan-reynolds",
    "scarlett-johansson",
    "chris-hemsworth",
    "jennifer-lawrence"
];

// Create simple SVG placeholder images
celebrities.forEach((name, index) => {
    const color = `hsl(${index * 60}, 70%, 50%)`;
    const initials = name.split('-').map(n => n[0].toUpperCase()).join('');
    
    const svg = `
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <rect width="400" height="400" fill="${color}"/>
    <circle cx="150" cy="120" r="15" fill="white"/>
    <circle cx="250" cy="120" r="15" fill="white"/>
    <path d="M 120 100 Q 150 80 180 100" stroke="white" stroke-width="3" fill="none"/>
    <path d="M 220 100 Q 250 80 280 100" stroke="white" stroke-width="3" fill="none"/>
    <ellipse cx="200" cy="180" rx="8" ry="12" fill="white"/>
    <path d="M 160 220 Q 200 240 240 220" stroke="white" stroke-width="3" fill="none"/>
    <text x="200" y="320" text-anchor="middle" fill="white" font-size="24" font-weight="bold">${initials}</text>
    <text x="200" y="350" text-anchor="middle" fill="white" font-size="16">${name.replace('-', ' ')}</text>
</svg>`.trim();

    const imagePath = path.join('public', 'images', `${name}.svg`);
    
    // Ensure directory exists
    fs.mkdirSync(path.dirname(imagePath), { recursive: true });
    
    // Write SVG file
    fs.writeFileSync(imagePath, svg);
    
    console.log(`Created placeholder image: ${imagePath}`);
});

console.log('\nPlaceholder images created!');
console.log('Note: These are simple SVG placeholders.');
console.log('For best results, replace with actual celebrity photos in JPG format.');
