# Email GIF Creator

Transform your long demo videos into short, engaging GIFs perfect for email campaigns and presentations.

## What This Tool Does

This tool takes your MP4 video files and converts them into lightweight GIF animations that:
- Load quickly in emails
- Play automatically without clicking
- Show your entire demo in just a few seconds
- Maintain professional quality while keeping file sizes small

### Usage Usage

To convert your entire video into a 5-second GIF:

```
python gif_creator.py product_demo.mp4 email_demo.gif 5
```
This will:
- Take your entire video (even if it's several minutes long)
- Speed it up to fit in 5 seconds
- Create a GIF that's email-friendly (under 1.5 MB)

**Extract a specific segment:**
```
python python gif_creator.py video.mp4 output.gif 5 --start 45 --stop 105
```
Shows only the one-minute segment from 0:45 to 1:45

## Tips for Best Results

1. **Keep it Short**: 3-5 seconds is ideal for emails. Recipients get the message without waiting.

2. **Focus on Action**: Use segments that show movement, clicks, or transitions for more engaging GIFs.

3. **Test in Email**: Always send a test email to yourself to ensure the GIF displays properly.

4. **Multiple Versions**: Create different GIFs for different parts of your demo:
   - Overview GIF: Full demo compressed
   - Feature GIFs: Specific segments highlighting individual features
   - Problem/Solution GIF: Show the problem (first 30s) then solution (last 30s)

## Troubleshooting

**GIF is too large for email?**
- Reduce the duration (try 3 seconds instead of 5)
- Reduce the width (try 400px instead of 500px)
- Use a specific segment instead of the whole video

**GIF looks too fast?**
- Your video might be very long. Consider using just a portion with --start and --stop
- Increase the GIF duration to slow it down

**GIF quality looks poor?**
- Increase the width parameter for better resolution
- Increase the fps parameter for smoother motion

## Installation

```
pip install -r requirements.txt
```

## Script Overview

```python
from gif_creator import VideoToGifConverter

# Initialize converter
converter = VideoToGifConverter('video.mp4')

# Get video information
info = converter.get_video_info()
print(f"Duration: {info['duration']}s")

# Create GIF with default settings
converter.create_gif('output.gif')

# Create GIF with custom parameters
converter.create_gif(
    'output.gif',
    duration=5.0,      # GIF duration in seconds
    width=500,         # Maximum width (maintains aspect ratio)
    fps=10,            # Output frame rate
    start_time=30,     # Start at 30 seconds
    stop_time=90,      # End at 90 seconds
    optimize=True      # Enable PIL optimization
)
```
