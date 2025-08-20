// Runtime image loader for large datasets
export class ImageLoader {
    constructor() {
        this.imageCache = new Set();
        this.loadedImages = [];
    }

    // Discover images by attempting to load them with sequential names or common patterns
    async discoverImages() {
        const images = [];
        const supportedExtensions = ['jpg', 'jpeg', 'png'];
        
        console.log('🔍 Discovering images in /images/ directory...');
        
        // Try to load a sample of images to estimate total count
        let foundCount = 0;
        let consecutiveMisses = 0;
        const maxMisses = 50; // Stop after 50 consecutive misses
        
        // Common naming patterns to try
        const patterns = [
            (i) => `image_${i}`,
            (i) => `img_${i}`,
            (i) => `photo_${i}`,
            (i) => `pic_${i}`,
            (i) => `${i}`,
            (i) => `person_${i}`,
            (i) => `celebrity_${i}`,
            (i) => String(i).padStart(4, '0'), // 0001, 0002, etc.
            (i) => String(i).padStart(3, '0'), // 001, 002, etc.
        ];
        
        for (let i = 1; i <= 2000 && consecutiveMisses < maxMisses; i++) {
            let found = false;
            
            for (const pattern of patterns) {
                for (const ext of supportedExtensions) {
                    const filename = `${pattern(i)}.${ext}`;
                    const imagePath = `/images/${filename}`;
                    
                    try {
                        const exists = await this.checkImageExists(imagePath);
                        if (exists) {
                            images.push({
                                id: foundCount + 1,
                                name: this.filenameToDisplayName(pattern(i)),
                                image: imagePath,
                                originalFilename: filename
                            });
                            foundCount++;
                            found = true;
                            consecutiveMisses = 0;
                            console.log(`✅ Found: ${filename}`);
                            break;
                        }
                    } catch (error) {
                        // Image doesn't exist, continue
                    }
                }
                if (found) break;
            }
            
            if (!found) {
                consecutiveMisses++;
            }
            
            // Log progress every 100 attempts
            if (i % 100 === 0) {
                console.log(`🔍 Checked ${i} possibilities, found ${foundCount} images`);
            }
        }
        
        console.log(`✅ Discovery complete: Found ${foundCount} images`);
        this.loadedImages = images;
        return images;
    }

    // Check if an image exists by attempting to load it
    async checkImageExists(imagePath) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = imagePath;
            
            // Timeout after 2 seconds
            setTimeout(() => resolve(false), 2000);
        });
    }

    // Convert filename to display name
    filenameToDisplayName(filename) {
        return filename
            .replace(/\.(png|jpg|jpeg|svg)$/i, '') // Remove extension
            .split(/[-_]/) // Split on hyphens and underscores
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize each word
            .join(' '); // Join with spaces
    }

    // Get random celebrities for the game
    getRandomCelebrities(excludeId = null, count = 4) {
        const available = this.loadedImages.filter(c => c.id !== excludeId);
        const shuffled = [...available].sort(() => Math.random() - 0.5);
        
        const actualCount = Math.min(count, available.length);
        return shuffled.slice(0, actualCount);
    }

    // Get celebrity by ID
    getCelebrityById(id) {
        return this.loadedImages.find(c => c.id === id);
    }
}
