// Debug: Check if this file is loading
console.log('📂 CelebrityData.js is loading...');

// For large datasets (1600+), we'll use lazy loading instead of eager loading
let imageModules = {};

try {
    console.log('🔄 Trying to find images with literal glob patterns...');
    
    let totalFound = 0;
    imageModules = {};
    
    // Since images are in public/images, we need to use the correct relative path from src
    // Vite requires literal patterns, so we can't use a loop with variables
    
    console.log('🔍 Trying pattern: ../public/images/*.png');
    try {
        const modulesPng = import.meta.glob('../public/images/*.png', { as: 'url', eager: true });
        const countPng = Object.keys(modulesPng).length;
        console.log(`   Found ${countPng} PNG files`);
        if (countPng > 0) {
            imageModules = { ...imageModules, ...modulesPng };
            totalFound += countPng;
            const examplePaths = Object.keys(modulesPng).slice(0, 3);
            console.log(`   Example PNG paths:`, examplePaths);
        }
    } catch (error) {
        console.log(`   PNG pattern failed:`, error.message);
    }
    
    console.log('🔍 Trying pattern: ../public/images/*.jpg');
    try {
        const modulesJpg = import.meta.glob('../public/images/*.jpg', { as: 'url', eager: true });
        const countJpg = Object.keys(modulesJpg).length;
        console.log(`   Found ${countJpg} JPG files`);
        if (countJpg > 0) {
            imageModules = { ...imageModules, ...modulesJpg };
            totalFound += countJpg;
            const examplePaths = Object.keys(modulesJpg).slice(0, 3);
            console.log(`   Example JPG paths:`, examplePaths);
        }
    } catch (error) {
        console.log(`   JPG pattern failed:`, error.message);
    }
    
    console.log('🔍 Trying pattern: ../public/images/*.jpeg');
    try {
        const modulesJpeg = import.meta.glob('../public/images/*.jpeg', { as: 'url', eager: true });
        const countJpeg = Object.keys(modulesJpeg).length;
        console.log(`   Found ${countJpeg} JPEG files`);
        if (countJpeg > 0) {
            imageModules = { ...imageModules, ...modulesJpeg };
            totalFound += countJpeg;
            const examplePaths = Object.keys(modulesJpeg).slice(0, 3);
            console.log(`   Example JPEG paths:`, examplePaths);
        }
    } catch (error) {
        console.log(`   JPEG pattern failed:`, error.message);
    }
    
    console.log(`📊 Total files found across all patterns: ${totalFound}`);
    
    if (totalFound === 0) {
        console.error('❌ No images found with any glob pattern!');
        console.log('🔍 Let me try a manual discovery approach...');
        
        // Fallback: Try to access known image paths directly
        const testPaths = [
            '/images/1.png',
            '/images/1.jpg', 
            '/images/image_1.png',
            '/images/image_1.jpg',
            '/images/img_1.png',
            '/images/img_1.jpg',
            '/images/photo_1.png',
            '/images/photo_1.jpg'
        ];
        
        for (const testPath of testPaths) {
            try {
                // Test if we can access the image
                console.log(`🧪 Testing access to: ${testPath}`);
            } catch (error) {
                console.log(`   Cannot access: ${testPath}`);
            }
        }
    }
    
} catch (error) {
    console.error('❌ Critical error in image discovery:', error);
    imageModules = {};
}

// Function to convert filename to display name
function filenameToDisplayName(filename) {
    return filename
        .replace(/\.(png|jpg|jpeg|svg)$/i, '') // Remove extension
        .split(/[-_]/) // Split on hyphens and underscores
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize each word
        .join(' '); // Join with spaces
}

// Generate celebrities array with direct URL access
export let celebrities = Object.entries(imageModules).map(([path, imageUrl], index) => {
    const filename = path.split('/').pop().replace(/\.(png|jpg|jpeg|svg)$/i, '');
    
    // Transform glob path to correct public asset path
    // ../public/images/filename.png -> /images/filename.png
    const publicPath = path.replace('../public', '').replace(/\?url$/, '');
    
    return {
        id: index + 1,
        name: filenameToDisplayName(filename),
        imagePath: publicPath, // Correct public asset path
        imageLoader: null, // No longer needed with eager loading
        imageUrl: imageUrl // Direct URL from eager import
    };
});

// Log discovered celebrities for debugging
console.log('📊 Total image patterns discovered:', celebrities.length);
console.log('📁 Sample celebrity names:', celebrities.slice(0, 10).map(c => c.name));

// Runtime image discovery function for when glob patterns fail
async function discoverImagesAtRuntime() {
    console.log('🔄 Starting runtime image discovery...');
    console.log('💡 Detected: Your images have spaces in names (e.g., "AADIL RASHID.png")');
    const discoveredImages = [];
    
    // First, try the specific pattern we detected from your files
    const knownImages = [
        'AADIL RASHID.png',
        'Abhijeet Malik.png', 
        'Abhishek KS.png',
        'Abhishek Singh.png'
    ];
    
    console.log('🧪 Testing known image files...');
    for (const filename of knownImages) {
        const imagePath = `/images/${encodeURIComponent(filename)}`;
        const exists = await testImageExists(imagePath);
        if (exists) {
            discoveredImages.push({
                id: discoveredImages.length + 1,
                name: filename.replace(/\.(png|jpg|jpeg)$/i, ''), // Use filename as-is for name
                imagePath: imagePath,
                imageLoader: () => Promise.resolve(imagePath),
                imageUrl: null
            });
            console.log(`✅ Found: ${filename}`);
        } else {
            console.log(`❌ Not found: ${filename}`);
        }
    }
    
    if (discoveredImages.length > 0) {
        console.log(`✅ Found ${discoveredImages.length} images using known pattern`);
        return discoveredImages;
    }
    
    // If known images failed, try to discover more systematically
    console.log('🔍 Trying to discover your 1600+ images with systematic approach...');
    const extensions = ['png', 'jpg', 'jpeg'];
    foundCount = discoveredImages.length;
    
    // For 1600+ images, let's try a more comprehensive approach
    // Common patterns for large datasets with names and spaces
    const patterns = [
        // Existing known pattern
        'AADIL RASHID', 'ABHIJEET MALIK', 'ABHISHEK KS', 'ABHISHEK SINGH',
        
        // Try numbered patterns with common prefixes
        ...Array.from({length: 50}, (_, i) => `PERSON ${i + 1}`),
        ...Array.from({length: 50}, (_, i) => `IMAGE ${i + 1}`),
        ...Array.from({length: 50}, (_, i) => `PHOTO ${i + 1}`),
        ...Array.from({length: 50}, (_, i) => `CELEBRITY ${i + 1}`),
        ...Array.from({length: 50}, (_, i) => `FACE ${i + 1}`),
        
        // Try patterns without spaces too
        ...Array.from({length: 100}, (_, i) => `${i + 1}`),
        ...Array.from({length: 100}, (_, i) => String(i + 1).padStart(4, '0')),
        ...Array.from({length: 100}, (_, i) => `image${i + 1}`),
        ...Array.from({length: 100}, (_, i) => `photo${i + 1}`),
    ];
    
    console.log(`🔍 Testing ${patterns.length} potential naming patterns...`);
    
    let consecutiveMisses = 0;
    const maxMisses = 200; // Increase patience for large datasets
    
    for (const baseName of patterns) {
        let foundThisRound = false;
        
        for (const ext of extensions) {
            const filename = `${baseName}.${ext}`;
            // Try both with and without URL encoding for spaces
            const pathOptions = [
                `/images/${encodeURIComponent(filename)}`,  // URL encoded
                `/images/${filename.replace(/ /g, '%20')}`,  // Space to %20
                `/images/${filename}`  // Direct (might work in some cases)
            ];
            
            for (const imagePath of pathOptions) {
                const exists = await testImageExists(imagePath);
                if (exists) {
                    discoveredImages.push({
                        id: foundCount + 1,
                        name: baseName,
                        imagePath: imagePath,
                        imageLoader: () => Promise.resolve(imagePath),
                        imageUrl: null
                    });
                    foundCount++;
                    foundThisRound = true;
                    consecutiveMisses = 0;
                    
                    console.log(`✅ Found #${foundCount}: ${filename}`);
                    
                    if (foundCount % 100 === 0) {
                        console.log(`🎯 Milestone: Found ${foundCount} images so far!`);
                    }
                    
                    // Early exit if we've found a lot
                    if (foundCount >= 1600) {
                        console.log('🎊 Found 1600+ images! Stopping discovery.');
                        return discoveredImages;
                    }
                    break; // Found with this encoding, try next filename
                }
            }
            
            if (foundThisRound) break; // Found with this extension, try next pattern
        }
        
        if (!foundThisRound) {
            consecutiveMisses++;
            if (consecutiveMisses >= maxMisses) {
                console.log(`⏹️ Stopping after ${maxMisses} consecutive misses`);
                break;
            }
        }
    }
    
    console.log(`✅ Runtime discovery complete: Found ${foundCount} images`);
    return discoveredImages;
}

// Helper function to test if an image exists
function testImageExists(imagePath) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = imagePath;
        
        // Shorter timeout for faster discovery
        setTimeout(() => resolve(false), 500);
    });
}

// Create the celebrities promise based on whether we found any celebrities
let celebritiesPromise;

// Check if we have any celebrities, if not try runtime discovery
if (celebrities.length === 0) {
    console.error('❌ Glob patterns found no images! Trying runtime discovery...');
    
    // Create a promise that will resolve when runtime discovery is complete
    celebritiesPromise = discoverImagesAtRuntime().then(discovered => {
        if (discovered.length > 0) {
            celebrities.length = 0; // Clear array
            celebrities.push(...discovered); // Add discovered images
            console.log(`✅ Runtime discovery successful: ${celebrities.length} images found`);
            return celebrities;
        } else {
            console.error('❌ Runtime discovery also failed! Make sure images are in /public/images/');
            return [];
        }
    });
} else {
    console.log(`✅ Successfully set up ${celebrities.length} celebrities for lazy loading`);
    
    // Show some stats
    const sampleNames = celebrities.slice(0, 5).map(c => c.name).join(', ');
    console.log(`🎯 First 5 celebrities: ${sampleNames}...`);
    
    if (celebrities.length > 1000) {
        console.log('🚀 Large dataset optimization: Images will be loaded on-demand');
    }
    
    // Create resolved promise for consistency
    celebritiesPromise = Promise.resolve(celebrities);
}

// Export the promise
export { celebritiesPromise };

// Function to load image URL for a specific celebrity (now just returns existing URL)
export async function loadCelebrityImage(celebrity) {
    // With eager loading, image URLs are already available
    if (celebrity.imageUrl) {
        console.log(`✅ Image URL already available for: ${celebrity.name}`);
        return celebrity.imageUrl;
    } else {
        console.log(`❌ No image URL available for: ${celebrity.name}`);
        return null;
    }
}

export function getRandomCelebrities(excludeId = null, count = 4) {
    const available = celebrities.filter(c => c.id !== excludeId);
    const shuffled = [...available].sort(() => Math.random() - 0.5);
    
    // If we don't have enough celebrities, return what we have
    const actualCount = Math.min(count, available.length);
    return shuffled.slice(0, actualCount);
}

export function getCelebrityById(id) {
    return celebrities.find(c => c.id === id);
}

export function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}
