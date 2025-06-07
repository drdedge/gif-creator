#!/usr/bin/env python3
"""
Email GIF Creator - Convert videos to email-friendly GIFs

A command-line tool for creating optimized GIF animations from video files,
perfect for email campaigns, documentation, and presentations.
"""

import click
import cv2
import numpy as np
import imageio
import os
import sys
from pathlib import Path
from typing import Optional, Tuple


class VideoToGifConverter:
    """Handles video to GIF conversion with various optimization options."""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.total_frames / self.fps
    
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
    
    def get_video_info(self) -> dict:
        """Return video information as a dictionary."""
        return {
            'duration': self.duration,
            'fps': self.fps,
            'resolution': f"{self.width}x{self.height}",
            'total_frames': self.total_frames
        }
    
    def create_gif(self, output_path: str, duration: float = 5.0,
                   width: Optional[int] = None, fps: int = 10,
                   start_time: float = 0, stop_time: Optional[float] = None,
                   optimize: bool = True) -> str:
        """
        Create a GIF from the video with specified parameters.
        
        Returns the path to the created GIF.
        """
        # Validate and adjust time parameters
        if stop_time is None:
            stop_time = self.duration
        
        stop_time = min(stop_time, self.duration)
        if start_time >= stop_time:
            raise ValueError(f"start_time ({start_time}) must be less than stop_time ({stop_time})")
        
        effective_duration = stop_time - start_time
        start_frame = int(start_time * self.fps)
        end_frame = int(stop_time * self.fps)
        effective_frames = end_frame - start_frame
        
        # Calculate resize parameters
        if width and width < self.width:
            scale_factor = width / self.width
            new_width = width
            new_height = int(self.height * scale_factor)
        else:
            scale_factor = 1.0
            new_width = self.width
            new_height = self.height
        
        # Calculate frame sampling
        output_frames_count = int(duration * fps)
        frame_interval = effective_frames / output_frames_count
        
        # Collect frames
        frames = []
        frame_indices = [start_frame + min(int(i * frame_interval), effective_frames - 1) 
                        for i in range(output_frames_count)]
        
        with click.progressbar(frame_indices, label='Processing frames') as indices:
            for frame_idx in indices:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()
                
                if not ret:
                    continue
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize if needed
                if scale_factor != 1.0:
                    frame_rgb = cv2.resize(frame_rgb, (new_width, new_height), 
                                         interpolation=cv2.INTER_AREA)
                
                frames.append(frame_rgb)
        
        # Create GIF
        click.echo("Creating GIF...")
        frame_duration = 1.0 / fps
        
        if optimize and self._check_pil_available():
            self._save_optimized_gif(frames, output_path, frame_duration)
        else:
            imageio.mimsave(output_path, frames, duration=frame_duration, loop=0)
        
        return output_path
    
    def _check_pil_available(self) -> bool:
        """Check if PIL is available for optimization."""
        try:
            import PIL
            return True
        except ImportError:
            return False
    
    def _save_optimized_gif(self, frames: list, output_path: str, frame_duration: float):
        """Save GIF with PIL optimization."""
        from PIL import Image
        
        # Convert numpy arrays to PIL Images
        pil_frames = [Image.fromarray(frame) for frame in frames]
        
        # Save with optimization
        pil_frames[0].save(
            output_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=frame_duration * 1000,  # PIL uses milliseconds
            loop=0,
            optimize=True,
            quality=85
        )


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_video_file(ctx, param, value):
    """Validate that the input file exists and is a video."""
    if not value:
        return value
    
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"File not found: {value}")
    
    if path.suffix.lower() not in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        raise click.BadParameter(f"File must be a video (mp4, avi, mov, mkv, webm)")
    
    return str(path)


@click.command()
@click.argument('video_file', callback=validate_video_file)
@click.argument('output_file', required=False)
@click.option('-d', '--duration', default=5.0, help='Duration of output GIF in seconds')
@click.option('-w', '--width', type=int, help='Maximum width (maintains aspect ratio)')
@click.option('-f', '--fps', default=10, help='Frames per second for output GIF')
@click.option('--start', 'start_time', default=0.0, help='Start time in seconds')
@click.option('--stop', 'stop_time', type=float, help='Stop time in seconds')
@click.option('--no-optimize', is_flag=True, help='Disable GIF optimization')
@click.option('--info', is_flag=True, help='Show video info and exit')
def create_gif(video_file, output_file, duration, width, fps, start_time, 
               stop_time, no_optimize, info):
    """
    Convert video to email-friendly GIF.
    
    Examples:
    
        # Convert entire video to 5-second GIF
        email-gif video.mp4
        
        # Create 3-second GIF from first minute only
        email-gif video.mp4 output.gif -d 3 --stop 60
        
        # Extract specific segment
        email-gif video.mp4 demo.gif --start 30 --stop 90
        
        # Optimize for email signature
        email-gif video.mp4 sig.gif -d 3 -w 300
    """
    try:
        converter = VideoToGifConverter(video_file)
        
        # Show info and exit if requested
        if info:
            info_dict = converter.get_video_info()
            click.echo(f"\nVideo Information:")
            click.echo(f"  File: {video_file}")
            click.echo(f"  Duration: {info_dict['duration']:.1f} seconds")
            click.echo(f"  Resolution: {info_dict['resolution']}")
            click.echo(f"  FPS: {info_dict['fps']:.1f}")
            click.echo(f"  Total frames: {info_dict['total_frames']:,}")
            return
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(video_file)
            output_file = str(input_path.with_suffix('.gif'))
        
        # Show conversion plan
        video_info = converter.get_video_info()
        effective_stop = stop_time if stop_time else video_info['duration']
        segment_duration = effective_stop - start_time
        speed_factor = segment_duration / duration
        
        click.echo(f"\nConversion Plan:")
        click.echo(f"  Input: {video_file}")
        click.echo(f"  Segment: {start_time:.1f}s to {effective_stop:.1f}s ({segment_duration:.1f}s)")
        click.echo(f"  Output: {output_file}")
        click.echo(f"  GIF Duration: {duration}s")
        click.echo(f"  Speed: {speed_factor:.1f}x")
        if width:
            click.echo(f"  Max Width: {width}px")
        click.echo(f"  FPS: {fps}")
        click.echo()
        
        # Create GIF
        output_path = converter.create_gif(
            output_file,
            duration=duration,
            width=width,
            fps=fps,
            start_time=start_time,
            stop_time=stop_time,
            optimize=not no_optimize
        )
        
        # Report results
        file_size = os.path.getsize(output_path)
        click.echo(f"\n✓ Success! GIF created: {output_path}")
        click.echo(f"  File size: {format_size(file_size)}")
        
        # Provide optimization tips if file is large
        if file_size > 2 * 1024 * 1024:  # 2MB
            click.echo("\n💡 Tips to reduce file size:")
            if not width or width > 400:
                click.echo("  • Try --width 400 or --width 300")
            if fps > 8:
                click.echo("  • Try --fps 8 or --fps 5")
            if duration > 3:
                click.echo("  • Try --duration 3")
            if segment_duration > 60:
                click.echo("  • Use --start and --stop to select a shorter segment")
    
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    create_gif()