"""
Instagram Carousel Generator with Streamlit Dashboard
Interactive tool for creating branded carousel posts with AI assistance
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import io
import base64
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Instagram Carousel Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple health check for Railway
if st.query_params.get("healthz"):
    st.write("OK")
    st.stop()

# Elite Systems AI Custom Styling
st.markdown("""
<style>
    /* Elite Systems AI Theme */
    .stApp {
        background: black !important;
        color: white !important;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #ff3b3b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        text-shadow: 0 0 30px rgba(37, 99, 235, 0.3);
    }
    
    .subtitle {
        color: #9ca3af;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb, .css-fg4pbf {
        background: rgba(0, 0, 0, 0.9) !important;
        color: white !important;
    }
    
    .css-1v3fvcr {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stSelectbox label {
        color: white !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        gap: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: #9ca3af !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border: 1px solid rgba(37, 99, 235, 0.5) !important;
    }
    
    /* Labels */
    .css-1cpxqw2, .css-16huue1, label {
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.2) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px !important;
        color: #10b981 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.2) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
        color: #ef4444 !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.2) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        color: #3b82f6 !important;
    }
    
    /* Preview styling */
    .preview-container {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin: 1rem 0 !important;
    }
    
    /* Color picker */
    .stColorPicker > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class BrandTheme:
    """Brand theme configuration"""
    name: str
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    accent_color: str = "#f093fb"
    background_color: str = "#ffffff"
    text_color: str = "#2d3436"
    font_family: str = "Arial"
    logo_path: Optional[str] = None

@dataclass
class CarouselSlide:
    """Individual carousel slide configuration"""
    slide_number: int
    title: str = ""
    subtitle: str = ""
    body_text: str = ""
    bullet_points: List[str] = None
    image_path: Optional[str] = None
    layout: str = "center"  # center, left, right, split
    background_style: str = "gradient"  # solid, gradient, image

class CarouselGenerator:
    """Generate Instagram carousel images with brand styling"""
    
    INSTAGRAM_SIZE = (1080, 1080)
    SAFE_ZONE = 950  # Instagram safe zone for text
    TEXT_PADDING = 80  # Padding around text areas
    SECTION_SPACING = 60  # Increased spacing between text sections
    LINE_SPACING_MULTIPLIER = 1.2  # Space between lines
    MIN_FONT_SIZE = 24
    MAX_FONT_SIZE = 80
    
    def __init__(self, theme: BrandTheme):
        self.theme = theme
        self.slides = []
        
    def create_slide(self, slide: CarouselSlide, custom_sizes: Dict = None) -> Image.Image:
        """Create a single carousel slide with intelligent text positioning"""
        # Create base image
        img = Image.new('RGB', self.INSTAGRAM_SIZE, color='white')
        draw = ImageDraw.Draw(img)
        
        # Apply background
        if slide.background_style == "gradient":
            self._apply_gradient(img, self.theme.primary_color, self.theme.secondary_color)
        elif slide.background_style == "solid":
            img = Image.new('RGB', self.INSTAGRAM_SIZE, self.theme.background_color)
            draw = ImageDraw.Draw(img)
            
        # Calculate available content area (excluding indicators and watermark)
        content_top = self.TEXT_PADDING
        content_bottom = self.INSTAGRAM_SIZE[1] - 120  # Leave space for indicators
        available_height = content_bottom - content_top
        
        # Calculate layout parameters
        layout_info = self._calculate_layout_parameters(slide, available_height)
        
        if slide.layout == "center":
            x_offset = self.INSTAGRAM_SIZE[0] // 2
            align = "center"
        elif slide.layout == "left":
            x_offset = self.TEXT_PADDING + 20
            align = "left"
        else:
            x_offset = self.INSTAGRAM_SIZE[0] - self.TEXT_PADDING - 20
            align = "right"
        
        # Optimize content for available space
        optimized_slide = self._optimize_content_for_space(slide)
        
        # Start positioning from calculated top
        current_y = content_top + layout_info['top_margin']
        
        # Draw slide number indicator
        self._draw_slide_indicator(draw, slide.slide_number)
        
        # Get fonts with custom sizes if provided
        if custom_sizes:
            fonts = self._load_fonts_with_emoji_support(custom_sizes)
        else:
            fonts = {
                'title': self._get_adaptive_font(optimized_slide.title or "", layout_info['title_font_size']),
                'subtitle': self._get_adaptive_font(optimized_slide.subtitle or "", layout_info['subtitle_font_size']),
                'body': self._get_adaptive_font(optimized_slide.body_text or "", layout_info['body_font_size']),
                'bullet': self._get_adaptive_font("", layout_info['bullet_font_size'])
            }
        
        # Draw title with dynamic font sizing and effects
        if optimized_slide.title:
            title_height = self._draw_text_with_effects(
                draw, optimized_slide.title, (x_offset, current_y),
                title_font, self.theme.text_color, align, 
                max_width=self.SAFE_ZONE, add_shadow=True
            )
            current_y += title_height + self.SECTION_SPACING
            
        # Draw subtitle with improved contrast
        if optimized_slide.subtitle:
            subtitle_font = self._get_adaptive_font(optimized_slide.subtitle, layout_info['subtitle_font_size'])
            # Choose subtitle color based on background for better contrast
            subtitle_color = self._get_contrast_color(slide.background_style, is_subtitle=True)
            subtitle_height = self._draw_text_with_effects(
                draw, optimized_slide.subtitle, (x_offset, current_y),
                subtitle_font, subtitle_color, align, 
                max_width=self.SAFE_ZONE, add_shadow=True
            )
            current_y += subtitle_height + self.SECTION_SPACING
            
        # Draw body text
        if optimized_slide.body_text:
            body_font = self._get_adaptive_font(optimized_slide.body_text, layout_info['body_font_size'])
            body_height = self._draw_text_with_effects(
                draw, optimized_slide.body_text, (x_offset, current_y),
                body_font, self.theme.text_color, align, 
                max_width=self.SAFE_ZONE, add_shadow=False
            )
            current_y += body_height + self.SECTION_SPACING
            
        # Draw bullet points with proper spacing
        if optimized_slide.bullet_points:
            bullet_font = self._get_adaptive_font("• Sample bullet point", layout_info['bullet_font_size'])
            for bullet in optimized_slide.bullet_points:
                bullet_text = f"• {bullet}"
                bullet_x = x_offset if optimized_slide.layout == "center" else x_offset + 20
                bullet_align = "left" if optimized_slide.layout != "right" else "left"
                bullet_height = self._draw_text_with_effects(
                    draw, bullet_text, (bullet_x, current_y),
                    bullet_font, self.theme.text_color, bullet_align, 
                    max_width=self.SAFE_ZONE - 40, add_shadow=False
                )
                current_y += bullet_height + (self.SECTION_SPACING // 2)
                
                # Check if we're running out of space
                if current_y > content_bottom - 50:
                    break
                
        # Add brand watermark
        self._add_watermark(draw)
        
        return img
    
    def _load_fonts_with_emoji_support(self, custom_sizes: Dict):
        """Load fonts with better emoji support"""
        # Try emoji-compatible fonts first
        font_options = [
            "Arial Unicode MS",   # Good emoji support
            "Segoe UI Emoji",     # Windows emoji font  
            "Apple Color Emoji",  # macOS emoji font
            "Noto Color Emoji",   # Google emoji font
            self.theme.font_family,  # User's chosen font
            "Arial",              # Standard fallback
            "DejaVu Sans"         # Final fallback
        ]
        
        fonts = {}
        for font_type in ['title', 'subtitle', 'body', 'bullet']:
            size = custom_sizes[font_type]
            font_loaded = False
            
            for font_name in font_options:
                try:
                    fonts[font_type] = ImageFont.truetype(font_name, size)
                    font_loaded = True
                    break
                except (OSError, IOError):
                    continue
            
            if not font_loaded:
                try:
                    # Try default with size
                    fonts[font_type] = ImageFont.load_default(size)
                except:
                    # Ultimate fallback
                    fonts[font_type] = ImageFont.load_default()
        
        return fonts
    
    def _get_contrast_color(self, background_style: str, is_subtitle: bool = False) -> str:
        """Get appropriate text color based on background for better contrast"""
        if background_style == "gradient":
            # For gradients, use high contrast colors with thick outlines
            if is_subtitle:
                return "#ffffff"  # Pure white for maximum contrast
            else:
                return "#ffffff"  # Pure white for main text
        elif background_style == "solid":
            # For solid backgrounds, ensure high contrast
            if self.theme.background_color == "#000000":
                return "#ffffff"  # White on black
            else:
                return "#000000"  # Black on light backgrounds
        else:
            # Default to high contrast
            return "#ffffff"
        
    def _apply_gradient(self, img: Image.Image, color1: str, color2: str):
        """Apply gradient background"""
        width, height = img.size
        
        # Convert hex to RGB
        c1 = tuple(int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        c2 = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Create gradient
        for y in range(height):
            ratio = y / height
            r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
            g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
            b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
            
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
            
    def _calculate_layout_parameters(self, slide: CarouselSlide, available_height: int) -> Dict:
        """Calculate optimal font sizes and spacing for the slide content"""
        # Count content elements
        elements = []
        if slide.title: elements.append(('title', slide.title))
        if slide.subtitle: elements.append(('subtitle', slide.subtitle))
        if slide.body_text: elements.append(('body', slide.body_text))
        if slide.bullet_points: 
            for bullet in slide.bullet_points:
                elements.append(('bullet', bullet))
        
        # Base font sizes
        base_sizes = {
            'title': 72,
            'subtitle': 48, 
            'body': 36,
            'bullet': 32
        }
        
        # Calculate total estimated height with base sizes
        estimated_height = 0
        for element_type, content in elements:
            # Estimate lines needed
            char_count = len(content)
            estimated_lines = max(1, char_count // 50)  # Rough estimate
            line_height = base_sizes[element_type] * self.LINE_SPACING_MULTIPLIER
            estimated_height += estimated_lines * line_height + self.SECTION_SPACING
        
        # Scale fonts if content doesn't fit
        scale_factor = 1.0
        if estimated_height > available_height * 0.8:  # Use 80% of available height
            scale_factor = (available_height * 0.8) / estimated_height
            scale_factor = max(0.6, min(1.0, scale_factor))  # Limit scaling
        
        # Apply scaling and constraints
        final_sizes = {}
        for element_type, base_size in base_sizes.items():
            scaled_size = int(base_size * scale_factor)
            final_sizes[f'{element_type}_font_size'] = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, scaled_size))
        
        # Calculate top margin for vertical centering
        final_estimated_height = estimated_height * scale_factor
        top_margin = max(0, (available_height - final_estimated_height) // 2)
        final_sizes['top_margin'] = top_margin
        
        return final_sizes
    
    def _get_adaptive_font(self, text: str, base_size: int) -> ImageFont.ImageFont:
        """Get font with size adapted to text length"""
        # Further reduce font size for very long text
        char_count = len(text)
        if char_count > 100:
            size_reduction = min(12, (char_count - 100) // 20)
            adjusted_size = max(self.MIN_FONT_SIZE, base_size - size_reduction)
        else:
            adjusted_size = base_size
            
        try:
            return ImageFont.truetype(self.theme.font_family, adjusted_size)
        except:
            return ImageFont.load_default()
    
    def _measure_text_height(self, draw, text: str, font: ImageFont.ImageFont, max_width: int) -> int:
        """Measure the total height needed for wrapped text"""
        lines = self._wrap_text(text, draw, font, max_width)
        if not lines:
            return 0
            
        # Get line height from font metrics
        sample_bbox = draw.textbbox((0, 0), "Ay", font=font)
        line_height = sample_bbox[3] - sample_bbox[1]
        
        total_height = len(lines) * line_height
        if len(lines) > 1:
            total_height += (len(lines) - 1) * (line_height * 0.2)  # Add line spacing
            
        return total_height
    
    def _wrap_text(self, text: str, draw, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width, returning list of lines"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, force break
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def _draw_text_with_effects(self, draw, text: str, position: Tuple[int, int], 
                               font: ImageFont.ImageFont, color: str, align: str = "left", 
                               max_width: int = 900, add_shadow: bool = False) -> int:
        """Draw text with optional shadow/outline effects and return height used"""
        lines = self._wrap_text(text, draw, font, max_width)
        if not lines:
            return 0
            
        # Get line height
        sample_bbox = draw.textbbox((0, 0), "Ay", font=font)
        line_height = sample_bbox[3] - sample_bbox[1]
        line_spacing = int(line_height * 0.2)
        
        y = position[1]
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            
            # Calculate x position based on alignment
            if align == "center":
                x = position[0] - line_width // 2
            elif align == "right":
                x = position[0] - line_width
            else:
                x = position[0]
            
            # Always add strong outline for maximum readability on gradients
            outline_color = "#000000"
            outline_thickness = 4 if font.size > 50 else 3
            
            # Draw thick black outline for maximum contrast
            for dx in range(-outline_thickness, outline_thickness + 1):
                for dy in range(-outline_thickness, outline_thickness + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, fill=outline_color, font=font)
            
            # Add additional shadow for extra depth if requested
            if add_shadow:
                shadow_offset = 6
                draw.text((x + shadow_offset, y + shadow_offset), line, fill="#000000", font=font)
            
            # Draw main white text on top for maximum contrast
            draw.text((x, y), line, fill="#ffffff", font=font)
            y += line_height + line_spacing
            
        return len(lines) * line_height + (len(lines) - 1) * line_spacing
            
    def _draw_slide_indicator(self, draw, slide_number):
        """Draw slide number indicator"""
        indicator_size = 30
        margin = 40
        y = self.INSTAGRAM_SIZE[1] - margin - indicator_size
        
        for i in range(10):  # Max 10 slides
            x = margin + i * (indicator_size + 10)
            if i < slide_number:
                color = self.theme.primary_color
            else:
                color = "#e0e0e0"
            draw.ellipse([x, y, x + indicator_size, y + indicator_size], fill=color)
            
    def _truncate_text_intelligently(self, text: str, max_length: int) -> str:
        """Intelligently truncate text while preserving meaning"""
        if len(text) <= max_length:
            return text
            
        # Try to break at sentence boundaries first
        sentences = text.split('. ')
        if len(sentences) > 1:
            result = sentences[0]
            for sentence in sentences[1:]:
                if len(result + '. ' + sentence) <= max_length - 3:
                    result += '. ' + sentence
                else:
                    break
            if len(result) < max_length - 3:
                return result + '...'
                
        # Fall back to word boundaries
        words = text.split()
        result = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + len(result) <= max_length - 3:
                result.append(word)
                current_length += len(word)
            else:
                break
                
        return ' '.join(result) + '...' if result else text[:max_length-3] + '...'
    
    def _add_text_outline(self, draw, text: str, position: Tuple[int, int], 
                         font: ImageFont.ImageFont, text_color: str, outline_color: str = "#000000"):
        """Add outline effect to text for better readability"""
        x, y = position
        # Draw outline by drawing text in multiple positions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:  # Skip the center position
                    draw.text((x + dx, y + dy), text, fill=outline_color, font=font)
        # Draw the main text on top
        draw.text((x, y), text, fill=text_color, font=font)
    
    def _optimize_content_for_space(self, slide: CarouselSlide) -> CarouselSlide:
        """Optimize slide content to fit available space better"""
        optimized_slide = CarouselSlide(
            slide_number=slide.slide_number,
            title=slide.title,
            subtitle=slide.subtitle,
            body_text=slide.body_text,
            bullet_points=slide.bullet_points.copy() if slide.bullet_points else None,
            image_path=slide.image_path,
            layout=slide.layout,
            background_style=slide.background_style
        )
        
        # Intelligent title optimization
        if optimized_slide.title and len(optimized_slide.title) > 60:
            optimized_slide.title = self._truncate_text_intelligently(optimized_slide.title, 60)
            
        # Subtitle optimization
        if optimized_slide.subtitle and len(optimized_slide.subtitle) > 80:
            optimized_slide.subtitle = self._truncate_text_intelligently(optimized_slide.subtitle, 80)
            
        # Body text optimization
        if optimized_slide.body_text and len(optimized_slide.body_text) > 200:
            optimized_slide.body_text = self._truncate_text_intelligently(optimized_slide.body_text, 200)
            
        # Bullet points optimization
        if optimized_slide.bullet_points:
            optimized_bullets = []
            for bullet in optimized_slide.bullet_points[:6]:  # Limit to 6 bullets
                if len(bullet) > 60:
                    bullet = self._truncate_text_intelligently(bullet, 60)
                optimized_bullets.append(bullet)
            optimized_slide.bullet_points = optimized_bullets
            
        return optimized_slide
    
    def _add_watermark(self, draw):
        """Add brand watermark with improved styling"""
        try:
            font = ImageFont.truetype(self.theme.font_family, 18)
        except:
            font = ImageFont.load_default()
            
        text = f"@{self.theme.name}"
        bbox = draw.textbbox((0, 0), text, font=font)
        x = self.INSTAGRAM_SIZE[0] - bbox[2] - 30
        y = self.INSTAGRAM_SIZE[1] - bbox[3] - 30
        
        # Add subtle background for watermark
        padding = 8
        bg_coords = [
            x - padding, y - padding,
            x + bbox[2] + padding, y + bbox[3] + padding
        ]
        
        # Semi-transparent background
        draw.rounded_rectangle(bg_coords, radius=5, 
                             fill=(*tuple(int(self.theme.background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)), 128))
        
        draw.text((x, y), text, fill=self.theme.text_color, font=font)

def get_ai_suggestions(content_idea: str, num_slides: int = 5) -> Dict:
    """Get AI-powered content suggestions for carousel"""
    # Try Claude API first
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "YOUR_CLAUDE_API_KEY_HERE":
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            prompt = f"""Create an Instagram carousel post with {num_slides} slides about: {content_idea}
            
            Return a JSON structure with:
            - hook_slide: Compelling first slide with title and subtitle
            - content_slides: Array of {num_slides-2} value-providing slides with title, subtitle, and 3-4 bullet points each
            - cta_slide: Call-to-action final slide with title, subtitle, and action text
            - hashtags: 10-15 relevant hashtags
            - caption: Engaging Instagram caption (150-200 words)
            
            Make it educational, valuable, and engaging for Instagram audience."""
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            content = response.content[0].text
            try:
                return json.loads(content)
            except:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
                # Fallback structure if JSON parsing fails
                return generate_fallback_content(content_idea, num_slides)
        except Exception as e:
            st.warning(f"Claude API failed: {e}")
            
    # Try OpenAI API as fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai
            openai.api_key = openai_key
            
            prompt = f"""Create an Instagram carousel post with {num_slides} slides about: {content_idea}
            
            Return ONLY a valid JSON structure with:
            - hook_slide: Object with 'title' and 'subtitle'
            - content_slides: Array of {num_slides-2} objects with 'title', 'subtitle', and 'bullet_points' array
            - cta_slide: Object with 'title', 'subtitle', and 'action_text'
            - hashtags: Array of 10-15 hashtags
            - caption: String with engaging Instagram caption"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            st.warning(f"OpenAI API also failed: {e}")
            
    # Final fallback - generate basic structure
    st.info("Using basic template. To enable AI generation, add your API key to the .env file")
    return generate_fallback_content(content_idea, num_slides)

def generate_fallback_content(content_idea: str, num_slides: int) -> Dict:
    """Generate basic carousel structure without AI"""
    return {
        "hook_slide": {
            "title": content_idea[:50],
            "subtitle": "Swipe to learn more →"
        },
        "content_slides": [
            {
                "title": f"Point {i+1}",
                "subtitle": "Key insight",
                "bullet_points": [
                    f"Detail {j+1} about this point" 
                    for j in range(3)
                ]
            } 
            for i in range(num_slides-2)
        ],
        "cta_slide": {
            "title": "Want more tips?",
            "subtitle": "Follow for daily insights",
            "action_text": "Drop a 💙 if this helped!"
        },
        "hashtags": [
            "#instagram", "#contentcreation", "#socialmedia",
            "#marketing", "#business", "#entrepreneur",
            "#tips", "#growth", "#success", "#motivation"
        ],
        "caption": f"📍 {content_idea}\n\nSwipe through to discover actionable insights that will transform your approach.\n\nWhich tip resonated most with you? Let me know in the comments! 👇\n\nFollow for more daily tips and strategies."
    }

# Initialize session state
if 'slides' not in st.session_state:
    st.session_state.slides = []
if 'theme' not in st.session_state:
    st.session_state.theme = BrandTheme(
        name="Elite Systems AI",
        primary_color="#2563eb",
        secondary_color="#3b82f6", 
        accent_color="#ff3b3b",
        background_color="#000000",
        text_color="#ffffff",
        font_family="Arial"
    )
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# Main UI with Elite Systems AI branding
st.markdown('''
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 class="main-header">🎨 Instagram Carousel Generator</h1>
    <p class="subtitle">Powered by <strong>Elite Systems AI</strong> | Professional carousel creation with AI intelligence</p>
</div>
''', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Brand Theme Settings
    st.subheader("🎨 Brand Theme")
    brand_name = st.text_input("Brand Name", value=st.session_state.theme.name)
    
    col1, col2 = st.columns(2)
    with col1:
        primary_color = st.color_picker("Primary Color", value=st.session_state.theme.primary_color)
        accent_color = st.color_picker("Accent Color", value=st.session_state.theme.accent_color)
    with col2:
        secondary_color = st.color_picker("Secondary Color", value=st.session_state.theme.secondary_color)
        text_color = st.color_picker("Text Color", value=st.session_state.theme.text_color)
    
    background_color = st.color_picker("Background Color", value=st.session_state.theme.background_color)
    
    font_family = st.selectbox(
        "Font Family",
        ["Arial", "Helvetica", "Times", "Georgia", "Futura", "Impact"],
        index=0
    )
    
    # Font Size Controls
    st.subheader("📝 Typography")
    title_size = st.slider("Title Font Size", min_value=40, max_value=100, value=68, step=4)
    subtitle_size = st.slider("Subtitle Font Size", min_value=30, max_value=80, value=48, step=4)
    body_size = st.slider("Body Font Size", min_value=24, max_value=60, value=36, step=2)
    bullet_size = st.slider("Bullet Font Size", min_value=20, max_value=50, value=32, step=2)
    
    # Update theme
    st.session_state.theme = BrandTheme(
        name=brand_name,
        primary_color=primary_color,
        secondary_color=secondary_color,
        accent_color=accent_color,
        background_color=background_color,
        text_color=text_color,
        font_family=font_family
    )
    
    st.divider()
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    if st.button("💾 Save Theme", use_container_width=True):
        theme_file = Path("brand_theme.json")
        try:
            with open(theme_file, "w") as f:
                json.dump({
                    "name": st.session_state.theme.name,
                    "primary_color": st.session_state.theme.primary_color,
                    "secondary_color": st.session_state.theme.secondary_color,
                    "accent_color": st.session_state.theme.accent_color,
                    "background_color": st.session_state.theme.background_color,
                    "text_color": st.session_state.theme.text_color,
                    "font_family": st.session_state.theme.font_family
                }, f, indent=2)
            st.success("✅ Theme saved successfully!")
        except Exception as e:
            st.error(f"Failed to save theme: {e}")
    
    if st.button("📂 Load Theme", use_container_width=True):
        theme_file = Path("brand_theme.json")
        if theme_file.exists():
            try:
                with open(theme_file, "r") as f:
                    theme_data = json.load(f)
                    st.session_state.theme = BrandTheme(**theme_data)
                st.success("✅ Theme loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load theme: {e}")
        else:
            st.error("No saved theme found. Save a theme first!")

# Main content area
tab1, tab2, tab3 = st.tabs(["✨ AI Content Generator", "✏️ Manual Editor", "👁️ Preview & Export"])

with tab1:
    st.header("AI-Powered Content Generation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        content_idea = st.text_area(
            "Content Idea",
            placeholder="E.g., '5 tips for better Instagram engagement' or 'How to grow your business with social media'",
            height=100
        )
        
        num_slides = st.slider("Number of Slides", min_value=3, max_value=10, value=5)
        
    with col2:
        st.info("💡 The AI will generate:\n- Compelling hook\n- Value-packed content\n- Strong CTA\n- Hashtags\n- Caption")
    
    if st.button("🤖 Generate Content", type="primary", use_container_width=True):
        if content_idea:
            with st.spinner("Generating AI content..."):
                suggestions = get_ai_suggestions(content_idea, num_slides)
                
                if suggestions:
                    # Create slides from AI suggestions
                    st.session_state.slides = []
                    
                    # Hook slide
                    st.session_state.slides.append(CarouselSlide(
                        slide_number=1,
                        title=suggestions['hook_slide']['title'],
                        subtitle=suggestions['hook_slide'].get('subtitle', ''),
                        layout="center",
                        background_style="gradient"
                    ))
                    
                    # Content slides
                    for i, slide_data in enumerate(suggestions['content_slides'], start=2):
                        st.session_state.slides.append(CarouselSlide(
                            slide_number=i,
                            title=slide_data.get('title', f'Slide {i}'),
                            subtitle=slide_data.get('subtitle', ''),
                            bullet_points=slide_data.get('bullet_points', []),
                            layout="left",
                            background_style="gradient"
                        ))
                    
                    # CTA slide
                    st.session_state.slides.append(CarouselSlide(
                        slide_number=num_slides,
                        title=suggestions['cta_slide']['title'],
                        subtitle=suggestions['cta_slide'].get('subtitle', ''),
                        body_text=suggestions['cta_slide'].get('action_text', ''),
                        layout="center",
                        background_style="gradient"
                    ))
                    
                    st.success("✅ Content generated! Check the Preview tab")
                    
                    # Display caption and hashtags
                    st.subheader("📝 Suggested Caption")
                    st.text_area("Caption", value=suggestions.get('caption', ''), height=150)
                    
                    st.subheader("#️⃣ Suggested Hashtags")
                    st.code(' '.join(suggestions.get('hashtags', [])))
        else:
            st.warning("Please enter a content idea")

with tab2:
    st.header("Manual Slide Editor")
    
    # Select slide to edit
    if st.session_state.slides:
        slide_to_edit = st.selectbox(
            "Select Slide to Edit",
            options=range(len(st.session_state.slides)),
            format_func=lambda x: f"Slide {x+1}: {st.session_state.slides[x].title[:30]}..."
        )
        
        current_slide = st.session_state.slides[slide_to_edit]
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_slide.title = st.text_input("Title", value=current_slide.title)
            current_slide.subtitle = st.text_input("Subtitle", value=current_slide.subtitle)
            current_slide.body_text = st.text_area("Body Text", value=current_slide.body_text, height=100)
            
        with col2:
            current_slide.layout = st.selectbox("Layout", ["center", "left", "right"], 
                                               index=["center", "left", "right"].index(current_slide.layout))
            current_slide.background_style = st.selectbox("Background", ["gradient", "solid"],
                                                         index=["gradient", "solid"].index(current_slide.background_style))
            
            # Bullet points editor
            st.write("Bullet Points")
            if current_slide.bullet_points is None:
                current_slide.bullet_points = []
            
            num_bullets = st.number_input("Number of bullets", min_value=0, max_value=6, 
                                         value=len(current_slide.bullet_points))
            
            # Adjust bullet points list size
            while len(current_slide.bullet_points) < num_bullets:
                current_slide.bullet_points.append("")
            while len(current_slide.bullet_points) > num_bullets:
                current_slide.bullet_points.pop()
            
            for i in range(num_bullets):
                current_slide.bullet_points[i] = st.text_input(f"Bullet {i+1}", 
                                                              value=current_slide.bullet_points[i],
                                                              key=f"bullet_{slide_to_edit}_{i}")
        
        # Update slide
        st.session_state.slides[slide_to_edit] = current_slide
        
        # Add/Remove slides
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add Slide", use_container_width=True):
                new_slide = CarouselSlide(
                    slide_number=len(st.session_state.slides) + 1,
                    title="New Slide",
                    layout="center",
                    background_style="gradient"
                )
                st.session_state.slides.append(new_slide)
                st.rerun()
        
        with col2:
            if st.button("🗑️ Remove Current", use_container_width=True) and len(st.session_state.slides) > 1:
                st.session_state.slides.pop(slide_to_edit)
                # Renumber slides
                for i, slide in enumerate(st.session_state.slides):
                    slide.slide_number = i + 1
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset All", use_container_width=True):
                st.session_state.slides = []
                st.rerun()
    else:
        st.info("No slides yet. Use the AI Generator or add slides manually.")
        if st.button("➕ Add First Slide"):
            st.session_state.slides.append(CarouselSlide(
                slide_number=1,
                title="Welcome",
                subtitle="Swipe for more →",
                layout="center",
                background_style="gradient"
            ))
            st.rerun()

with tab3:
    st.header("Preview & Export")
    
    if st.session_state.slides:
        # Generate preview
        if st.button("🎨 Generate Preview", type="primary", use_container_width=True):
            generator = CarouselGenerator(st.session_state.theme)
            st.session_state.generated_images = []
            
            # Get custom font sizes from sidebar
            custom_sizes = {
                'title': title_size,
                'subtitle': subtitle_size, 
                'body': body_size,
                'bullet': bullet_size
            }
            
            progress_bar = st.progress(0)
            for i, slide in enumerate(st.session_state.slides):
                img = generator.create_slide(slide, custom_sizes)
                st.session_state.generated_images.append(img)
                progress_bar.progress((i + 1) / len(st.session_state.slides))
            
            st.success("✅ Preview generated!")
        
        # Display preview
        if st.session_state.generated_images:
            st.subheader("📱 Carousel Preview")
            
            # Slider for navigation
            current_slide = st.select_slider(
                "Navigate Slides",
                options=range(len(st.session_state.generated_images)),
                format_func=lambda x: f"Slide {x+1}"
            )
            
            # Display current slide
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(st.session_state.generated_images[current_slide], 
                        caption=f"Slide {current_slide + 1} of {len(st.session_state.generated_images)}",
                        use_column_width=True)
            
            # Export options
            st.divider()
            st.subheader("💾 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download individual images
                if st.button("📥 Download All Images", use_container_width=True):
                    for i, img in enumerate(st.session_state.generated_images):
                        buffer = io.BytesIO()
                        img.save(buffer, format='PNG', quality=100)
                        buffer.seek(0)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"carousel_{timestamp}_slide_{i+1}.png"
                        
                        st.download_button(
                            label=f"Download Slide {i+1}",
                            data=buffer,
                            file_name=filename,
                            mime="image/png",
                            key=f"download_{i}"
                        )
            
            with col2:
                # Save to project folder
                if st.button("💾 Save to Project", use_container_width=True):
                    output_dir = Path("carousel_output")
                    output_dir.mkdir(exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    for i, img in enumerate(st.session_state.generated_images):
                        filename = output_dir / f"carousel_{timestamp}_slide_{i+1}.png"
                        img.save(filename, quality=100)
                    
                    st.success(f"✅ Saved {len(st.session_state.generated_images)} images to carousel_output/")
            
            with col3:
                # Generate PDF
                if st.button("📄 Export as PDF", use_container_width=True):
                    if st.session_state.generated_images:
                        pdf_buffer = io.BytesIO()
                        st.session_state.generated_images[0].save(
                            pdf_buffer,
                            "PDF",
                            save_all=True,
                            append_images=st.session_state.generated_images[1:]
                        )
                        pdf_buffer.seek(0)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="Download PDF",
                            data=pdf_buffer,
                            file_name=f"carousel_{timestamp}.pdf",
                            mime="application/pdf"
                        )
            
            # Quick share info
            st.info("💡 **Pro Tips:**\n"
                   "- Images are optimized for Instagram (1080x1080)\n"
                   "- Upload in order from Slide 1 to last\n"
                   "- Use consistent hashtags across carousel posts\n"
                   "- Post at peak engagement times for your audience")
    else:
        st.warning("No slides to preview. Create content first!")

# Elite Systems AI Footer
st.divider()
st.markdown('''
<div class="footer">
    <p>Made with ❤️ by <strong>Elite Systems AI</strong></p>
    <p>Professional AI-powered content creation tools for modern businesses</p>
    <p><a href="https://elitesystemsai.com" target="_blank">Visit Elite Systems AI</a></p>
</div>
''', unsafe_allow_html=True)