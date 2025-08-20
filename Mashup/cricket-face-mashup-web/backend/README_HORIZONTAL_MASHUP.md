# Horizontal Face Mashup System

This is a new implementation of the face mashup system that creates horizontal transparency gradients instead of vertical ones. The system is designed to be highly configurable and includes Canny edge detection for background removal.

## Key Features

- **Horizontal Transparency Gradient**: First player's image is the background (eyes visible), second player's image is the foreground (mouth/neck visible)
- **Configurable Transition Points**: Easily adjust where and how the transparency transition occurs
- **Canny Edge Detection**: Automatically removes backgrounds and creates white backgrounds with edge outlines
- **Real-time Configuration**: Update parameters without restarting the server
- **Debug Output**: Save intermediate images for analysis and tuning

## How It Works

1. **Background Player (img1)**: Shows through the top portion of the image (eyes region)
2. **Foreground Player (img2)**: Shows through the bottom portion (mouth/neck region)
3. **Transparency Gradient**: Smooth transition between the two players in the middle section
4. **Edge Detection**: Final step applies Canny edge detection to create clean outlines on white background

## Configuration

The system uses `mashup_config.json` for all parameters. Here's what each section controls:

### Transition Settings
```json
{
  "transition": {
    "start_y_ratio": 0.0,        // Where transparency starts (0.0 = top)
    "end_y_ratio": 0.5,          // Where transparency ends (0.5 = middle)
    "blend_zone_ratio": 0.1,     // Size of transition zone (0.1 = 10% of height)
    "smoothness": 0.8            // How smooth the transition is (0.0 = sharp, 1.0 = very smooth)
  }
}
```

### Processing Settings
```json
{
  "processing": {
    "target_size": [350, 350],           // Output image dimensions
    "gaussian_blur_kernel": [5, 5],      // Blur kernel for smoothing
    "canny_edge_low": 50,                // Canny edge detection low threshold
    "canny_edge_high": 150,              // Canny edge detection high threshold
    "background_white_threshold": 200    // Threshold for white background
  }
}
```

### Output Settings
```json
{
  "output": {
    "save_debug_images": true,           // Save intermediate images
    "debug_output_dir": "../Output/debug" // Where to save debug images
  }
}
```

## Quick Configuration Examples

### Early Transition (Eyes to Mouth)
```json
{
  "transition": {
    "start_y_ratio": 0.0,
    "end_y_ratio": 0.3,
    "blend_zone_ratio": 0.05,
    "smoothness": 0.9
  }
}
```

### Late Transition (More Eyes, Less Mouth)
```json
{
  "transition": {
    "start_y_ratio": 0.0,
    "end_y_ratio": 0.7,
    "blend_zone_ratio": 0.15,
    "smoothness": 0.6
  }
}
```

### Sharp Transition (Clear Cut)
```json
{
  "transition": {
    "start_y_ratio": 0.0,
    "end_y_ratio": 0.5,
    "blend_zone_ratio": 0.02,
    "smoothness": 0.3
  }
}
```

### Gradual Transition (Smooth Blend)
```json
{
  "transition": {
    "start_y_ratio": 0.0,
    "end_y_ratio": 0.5,
    "blend_zone_ratio": 0.25,
    "smoothness": 0.95
  }
}
```

## Usage

### 1. Start the Server
```bash
cd backend
python horizontal_main.py
```

### 2. Create Random Mashup
```bash
curl -X POST http://localhost:8000/create-mashup
```

### 3. Create Custom Mashup
```bash
curl -X POST http://localhost:8000/create-mashup-custom \
  -H "Content-Type: application/json" \
  -d '{
    "player_names": ["Player1", "Player2"],
    "config_overrides": {
      "transition": {
        "end_y_ratio": 0.4,
        "smoothness": 0.7
      }
    }
  }'
```

### 4. Update Configuration
```bash
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "transition": {
      "end_y_ratio": 0.6,
      "blend_zone_ratio": 0.12
    }
  }'
```

### 5. Get Current Configuration
```bash
curl http://localhost:8000/config
```

## Testing

Run the test script to see different configurations in action:

```bash
cd backend
python test_horizontal_mashup.py
```

This will create test images showing:
- Basic mashup functionality
- Different transition configurations
- Edge detection pipeline
- Configuration management

## API Endpoints

- `GET /` - Root endpoint
- `GET /players` - List all preloaded players
- `GET /config` - Get current configuration
- `POST /config` - Update configuration
- `POST /create-mashup` - Create random mashup
- `POST /create-mashup-custom` - Create custom mashup with specific players/config
- `GET /health` - Health check

## Debug Output

When `save_debug_images` is enabled, the system saves:
- `{player1_name}_background.png` - Background player image
- `{player2_name}_foreground.png` - Foreground player image
- `alpha_mask.png` - Raw alpha mask
- `alpha_mask_visualization.png` - Color-coded alpha mask
- `mashup_before_canny.png` - Mashup before edge detection

## Troubleshooting

### Common Issues

1. **Face Detection Fails**: Check that images contain clear, front-facing faces
2. **Poor Transition Quality**: Adjust `blend_zone_ratio` and `smoothness` parameters
3. **Edge Detection Too Aggressive**: Lower `canny_edge_high` threshold
4. **Edge Detection Too Weak**: Increase `canny_edge_low` threshold

### Performance Tips

- Smaller `blend_zone_ratio` values create faster transitions
- Higher `smoothness` values create smoother but more computationally intensive transitions
- Disable debug image saving in production for better performance

## Migration from Vertical System

The main differences from the old vertical system:

1. **Gradient Direction**: Horizontal instead of vertical
2. **Player Order**: First player = background (eyes), second player = foreground (mouth/neck)
3. **Configurable**: All parameters are now in a JSON config file
4. **Edge Detection**: Automatic background removal with Canny edge detection
5. **Debug Output**: Save intermediate images for analysis

## Future Enhancements

- **Multiple Transition Points**: Support for more complex blending patterns
- **Adaptive Face Detection**: Automatic adjustment based on face features
- **Background Replacement**: Choose different background styles
- **Real-time Preview**: Live preview of configuration changes
