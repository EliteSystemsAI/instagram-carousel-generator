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
import logging
import re
import traceback
import time
import psutil
from dataclasses import asdict

# Load environment variables
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('carousel_generator.log', mode='a')  # File output
    ]
)

logger = logging.getLogger(__name__)

# Analytics and Performance Tracking
class EliteAnalytics:
    """Elite Systems AI Analytics Tracker"""
    
    def __init__(self):
        self.session_start = time.time()
        self.events = []
        self.performance_metrics = {}
        
    def track_event(self, event_type: str, event_data: dict = None):
        """Track user events and system performance"""
        timestamp = time.time()
        
        event = {
            'timestamp': timestamp,
            'event_type': event_type,
            'session_duration': timestamp - self.session_start,
            'system_info': self._get_system_info(),
            'data': event_data or {}
        }
        
        self.events.append(event)
        logger.info(f"Analytics: {event_type} - {event_data}")
        
    def _get_system_info(self):
        """Get current system performance metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2)
            }
        except:
            return {'cpu_percent': 0, 'memory_percent': 0, 'memory_available_gb': 0}
    
    def track_generation_performance(self, slides_count: int, generation_time: float, success: bool):
        """Track carousel generation performance"""
        self.track_event('carousel_generation', {
            'slides_count': slides_count,
            'generation_time_seconds': generation_time,
            'success': success,
            'avg_time_per_slide': generation_time / slides_count if slides_count > 0 else 0
        })
    
    def track_ai_usage(self, provider: str, success: bool, response_time: float = None):
        """Track AI API usage"""
        self.track_event('ai_api_usage', {
            'provider': provider,
            'success': success,
            'response_time_seconds': response_time
        })
    
    def track_export(self, format_type: str, slides_count: int):
        """Track export events"""
        self.track_event('export', {
            'format': format_type,
            'slides_count': slides_count
        })
    
    def get_session_summary(self):
        """Get analytics summary for the session"""
        total_events = len(self.events)
        session_duration = time.time() - self.session_start
        
        event_types = {}
        for event in self.events:
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'session_duration_minutes': round(session_duration / 60, 2),
            'total_events': total_events,
            'event_breakdown': event_types,
            'final_system_info': self._get_system_info()
        }

# Initialize analytics
if 'analytics' not in st.session_state:
    st.session_state.analytics = EliteAnalytics()

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

# Elite Systems AI Custom Styling - Cohesive Dark Theme
st.markdown("""
<style>
    /* ==========================================
       ELITE SYSTEMS AI - COHESIVE DARK THEME
       ========================================== */

    /* Base App Styling */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0d0d0d 100%) !important;
        color: #ffffff !important;
    }

    /* Main content area */
    .main .block-container {
        background: transparent !important;
        padding: 2rem 3rem 3rem 3rem !important;
        max-width: 1200px !important;
    }

    /* Improved padding for all containers */
    [data-testid="stVerticalBlock"] > div {
        padding: 0.25rem 0 !important;
    }

    /* Form elements spacing */
    .stTextInput, .stTextArea, .stSelectbox, .stSlider {
        margin-bottom: 0.75rem !important;
    }

    /* Better spacing for columns */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }

    /* Card-like containers */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* ==========================================
       SIDEBAR - COHESIVE STYLING
       ========================================== */

    /* Sidebar container - using data-testid for stability */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%) !important;
        border-right: 1px solid rgba(37, 99, 235, 0.3) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 1.5rem 1rem !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 1rem !important;
    }

    /* Sidebar content */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }

    /* Sidebar headers - LARGER TEXT */
    [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        border-bottom: 1px solid rgba(37, 99, 235, 0.3);
        padding-bottom: 0.75rem;
        margin-bottom: 1.25rem;
    }

    [data-testid="stSidebar"] h2 {
        color: #ffffff !important;
        font-size: 1.25rem !important;
        border-bottom: 1px solid rgba(37, 99, 235, 0.3);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        border-bottom: 1px solid rgba(37, 99, 235, 0.3);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Sidebar labels and text - LARGER & MORE READABLE */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: #e0e0e0 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.25rem !important;
    }

    [data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
        font-size: 0.9rem !important;
    }

    /* Sidebar inputs - LARGER & DARKER */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: rgba(20, 20, 30, 0.8) !important;
        border: 1px solid rgba(37, 99, 235, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        padding: 0.5rem !important;
    }

    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
        background: rgba(20, 20, 40, 0.9) !important;
    }

    /* Sidebar selectbox - LARGER */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(20, 20, 30, 0.8) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(20, 20, 30, 0.8) !important;
        border: 1px solid rgba(37, 99, 235, 0.4) !important;
        border-radius: 8px !important;
        min-height: 40px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] span {
        font-size: 0.95rem !important;
    }

    /* Sidebar color pickers - LARGER */
    [data-testid="stSidebar"] [data-testid="stColorPicker"] {
        background: rgba(20, 20, 30, 0.6) !important;
        padding: 10px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
    }

    [data-testid="stSidebar"] [data-testid="stColorPicker"] > div > div {
        width: 50px !important;
        height: 35px !important;
    }

    /* Sidebar sliders - BETTER VISIBILITY */
    [data-testid="stSidebar"] [data-testid="stSlider"] {
        padding: 0.75rem 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {
        background: rgba(37, 99, 235, 0.3) !important;
        height: 6px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #60a5fa !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }

    /* Sidebar metrics/stats boxes */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(37, 99, 235, 0.1) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #3b82f6 !important;
    }

    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(37, 99, 235, 0.3) !important;
        margin: 1.5rem 0 !important;
    }

    /* ==========================================
       MAIN CONTENT AREA
       ========================================== */

    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #ff3b3b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 1rem;
    }

    .subtitle {
        color: #9ca3af;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Headers in main area */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #ffffff !important;
    }

    /* ==========================================
       BUTTONS - MAIN AREA
       ========================================== */

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

    /* ==========================================
       INPUTS - MAIN AREA (DARK BACKGROUNDS)
       ========================================== */

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(15, 15, 25, 0.9) !important;
        border: 1px solid rgba(37, 99, 235, 0.4) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
        background: rgba(20, 20, 35, 0.95) !important;
    }

    /* Text area specific styling */
    .stTextArea > div > div > textarea {
        min-height: 120px !important;
    }

    .stSelectbox > div > div > div {
        background: rgba(15, 15, 25, 0.9) !important;
        border: 1px solid rgba(37, 99, 235, 0.4) !important;
        border-radius: 8px !important;
        color: white !important;
        min-height: 42px !important;
    }

    .stSelectbox > div > div > div:hover {
        border-color: #3b82f6 !important;
    }

    /* ==========================================
       TABS
       ========================================== */

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(37, 99, 235, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        gap: 8px !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: #9ca3af !important;
        font-weight: 600 !important;
        border: 1px solid transparent !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(37, 99, 235, 0.2) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border: 1px solid rgba(37, 99, 235, 0.5) !important;
    }

    /* ==========================================
       ALERTS & MESSAGES - HIGH CONTRAST
       ========================================== */

    .stSuccess, [data-testid="stAlert"][data-baseweb*="positive"] {
        background: rgba(16, 185, 129, 0.2) !important;
        border: 2px solid rgba(16, 185, 129, 0.6) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    .stSuccess p, [data-testid="stAlert"][data-baseweb*="positive"] p {
        color: #34d399 !important;
        font-size: 0.95rem !important;
    }

    .stError, [data-testid="stAlert"][data-baseweb*="negative"] {
        background: rgba(239, 68, 68, 0.2) !important;
        border: 2px solid rgba(239, 68, 68, 0.6) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    .stError p, [data-testid="stAlert"][data-baseweb*="negative"] p {
        color: #f87171 !important;
        font-size: 0.95rem !important;
    }

    .stInfo, [data-testid="stAlert"] {
        background: rgba(59, 130, 246, 0.2) !important;
        border: 2px solid rgba(59, 130, 246, 0.5) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    .stInfo p, [data-testid="stAlert"] p {
        color: #93c5fd !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stAlert"] li {
        color: #93c5fd !important;
        font-size: 0.9rem !important;
        margin: 0.25rem 0 !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.2) !important;
        border: 2px solid rgba(245, 158, 11, 0.6) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    .stWarning p {
        color: #fbbf24 !important;
        font-size: 0.95rem !important;
    }

    /* ==========================================
       PROGRESS BAR
       ========================================== */

    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #2563eb, #3b82f6, #ff3b3b) !important;
    }

    /* ==========================================
       SLIDERS - MAIN AREA
       ========================================== */

    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
    }

    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    }

    [data-testid="stThumbValue"] {
        color: #3b82f6 !important;
        font-weight: 600 !important;
    }

    /* ==========================================
       EXPANDERS
       ========================================== */

    .streamlit-expanderHeader {
        background: rgba(37, 99, 235, 0.1) !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }

    .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* ==========================================
       DATAFRAMES & TABLES
       ========================================== */

    .stDataFrame {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
        border-radius: 8px !important;
    }

    /* ==========================================
       CODE BLOCKS
       ========================================== */

    code {
        background: rgba(37, 99, 235, 0.2) !important;
        color: #60a5fa !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }

    /* ==========================================
       HIDE STREAMLIT BRANDING
       ========================================== */

    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}

    /* ==========================================
       CUSTOM SCROLLBAR
       ========================================== */

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
    }

    /* ==========================================
       ELITE BRANDING ELEMENTS
       ========================================== */

    .elite-badge {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .elite-card {
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .elite-stat {
        text-align: center;
        padding: 1rem;
    }

    .elite-stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #3b82f6;
    }

    .elite-stat-label {
        font-size: 0.9rem;
        color: #9ca3af;
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
    
    # Font cache for performance optimization
    _font_cache = {}
    
    def __init__(self, theme: BrandTheme):
        self.theme = theme
        self.slides = []
        
    def create_slide(self, slide: CarouselSlide, custom_sizes: Dict = None) -> Image.Image:
        """Create a single carousel slide with intelligent text positioning"""
        try:
            logger.info(f"Creating slide {slide.slide_number}: {slide.title[:50]}...")
            
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
                    fonts['title'], self.theme.text_color, align, 
                    max_width=self.SAFE_ZONE, add_shadow=True
                )
                current_y += title_height + self.SECTION_SPACING
                
            # Draw subtitle with improved contrast
            if optimized_slide.subtitle:
                # Choose subtitle color based on background for better contrast
                subtitle_color = self._get_contrast_color(slide.background_style, is_subtitle=True)
                subtitle_height = self._draw_text_with_effects(
                    draw, optimized_slide.subtitle, (x_offset, current_y),
                    fonts['subtitle'], subtitle_color, align, 
                    max_width=self.SAFE_ZONE, add_shadow=True
                )
                current_y += subtitle_height + self.SECTION_SPACING
                
            # Draw body text
            if optimized_slide.body_text:
                body_height = self._draw_text_with_effects(
                    draw, optimized_slide.body_text, (x_offset, current_y),
                    fonts['body'], self.theme.text_color, align, 
                    max_width=self.SAFE_ZONE, add_shadow=False
                )
                current_y += body_height + self.SECTION_SPACING
                
            # Draw bullet points with proper spacing
            if optimized_slide.bullet_points:
                for bullet in optimized_slide.bullet_points:
                    bullet_text = f"• {bullet}"
                    bullet_x = x_offset if optimized_slide.layout == "center" else x_offset + 20
                    bullet_align = "left" if optimized_slide.layout != "right" else "left"
                    bullet_height = self._draw_text_with_effects(
                        draw, bullet_text, (bullet_x, current_y),
                        fonts['bullet'], self.theme.text_color, bullet_align, 
                        max_width=self.SAFE_ZONE - 40, add_shadow=False
                    )
                    current_y += bullet_height + (self.SECTION_SPACING // 2)
                    
                    # Check if we're running out of space
                    if current_y > content_bottom - 50:
                        break
                
            # Add brand watermark
            self._add_watermark(draw)
            
            logger.info(f"Successfully created slide {slide.slide_number}")
            return img
            
        except Exception as e:
            logger.error(f"Failed to create slide {slide.slide_number}: {str(e)}")
            logger.error(f"Slide details: {slide}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            
            # Return a basic error slide
            error_img = Image.new('RGB', self.INSTAGRAM_SIZE, color='#ff0000')
            error_draw = ImageDraw.Draw(error_img)
            try:
                error_font = ImageFont.load_default()
                error_draw.text((50, 500), f"Error creating slide {slide.slide_number}", 
                              fill='white', font=error_font)
                error_draw.text((50, 550), f"Error: {str(e)[:100]}", 
                              fill='white', font=error_font)
            except:
                pass  # If even error rendering fails, return blank red image
            return error_img
    
    def _load_fonts_with_emoji_support(self, custom_sizes: Dict):
        """Load fonts with better emoji support for all platforms including Railway/Linux"""
        # Extended font options with full paths for Linux/Docker environments
        font_options = [
            # Linux/Docker paths (Railway uses Nixpacks/Docker)
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            # macOS fonts
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            # Windows fonts
            "C:/Windows/Fonts/arialuni.ttf",
            "C:/Windows/Fonts/seguiemj.ttf",
            # Generic font names (PIL will search system paths)
            "Arial Unicode MS",
            "DejaVu Sans",
            "Liberation Sans",
            "FreeSans",
            "Noto Sans",
            self.theme.font_family,
            "Arial",
        ]

        fonts = {}
        successful_font = None

        for font_type in ['title', 'subtitle', 'body', 'bullet']:
            size = custom_sizes[font_type]
            font_loaded = False

            # If we already found a working font, try it first
            if successful_font:
                try:
                    fonts[font_type] = ImageFont.truetype(successful_font, size)
                    font_loaded = True
                except (OSError, IOError):
                    pass

            if not font_loaded:
                for font_path in font_options:
                    try:
                        fonts[font_type] = ImageFont.truetype(font_path, size)
                        font_loaded = True
                        successful_font = font_path  # Remember this font works
                        logger.info(f"Loaded font: {font_path} for {font_type}")
                        break
                    except (OSError, IOError):
                        continue

            if not font_loaded:
                try:
                    # Try default with size (PIL 10.0+)
                    fonts[font_type] = ImageFont.load_default(size)
                    logger.warning(f"Using default font for {font_type}")
                except TypeError:
                    # Older PIL versions don't support size parameter
                    fonts[font_type] = ImageFont.load_default()
                    logger.warning(f"Using basic default font for {font_type}")

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
        """Get font with size adapted to text length - with caching for performance"""
        # Further reduce font size for very long text
        char_count = len(text)
        if char_count > 100:
            size_reduction = min(12, (char_count - 100) // 20)
            adjusted_size = max(self.MIN_FONT_SIZE, base_size - size_reduction)
        else:
            adjusted_size = base_size
        
        # Create cache key
        cache_key = f"{self.theme.font_family}_{adjusted_size}"
        
        # Check cache first
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
            
        # Load font and cache it
        try:
            font = ImageFont.truetype(self.theme.font_family, adjusted_size)
            self._font_cache[cache_key] = font
            return font
        except:
            # Cache the default font too
            default_font = ImageFont.load_default()
            self._font_cache[cache_key] = default_font
            return default_font
    
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

def sanitize_json_string(text: str) -> str:
    """Sanitize JSON string by removing invalid control characters"""
    if not text:
        return text

    # Remove control characters except tab, newline, and carriage return
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # Replace problematic quotes and ensure proper escaping
    sanitized = sanitized.replace('\u201c', '"').replace('\u201d', '"')
    sanitized = sanitized.replace('\u2018', "'").replace('\u2019', "'")

    # Remove any trailing commas before closing braces/brackets (common JSON error)
    sanitized = re.sub(r',\s*}', '}', sanitized)
    sanitized = re.sub(r',\s*]', ']', sanitized)

    # Fix escaped newlines in strings that might cause issues
    sanitized = sanitized.replace('\\n', ' ')

    return sanitized

def extract_json_from_text(text: str) -> Optional[Dict]:
    """Extract and parse JSON from potentially malformed text response"""
    logger.info(f"Attempting to extract JSON from response (length: {len(text)})")

    # First, try to find JSON block markers
    json_start_markers = ['```json', '```JSON', '```']
    json_end_markers = ['```']

    text_to_parse = text

    # Check for markdown code blocks
    for start_marker in json_start_markers:
        if start_marker in text:
            start_idx = text.find(start_marker) + len(start_marker)
            # Find the closing marker
            end_idx = text.find('```', start_idx)
            if end_idx > start_idx:
                text_to_parse = text[start_idx:end_idx].strip()
                logger.info(f"Found JSON in code block")
                break

    # If no code block found, look for raw JSON object
    if text_to_parse == text:
        # Find the first { and last } to extract JSON object
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace > first_brace:
            text_to_parse = text[first_brace:last_brace + 1]
            logger.info(f"Extracted JSON from braces")

    # Sanitize and try parsing
    try:
        sanitized = sanitize_json_string(text_to_parse)
        result = json.loads(sanitized)
        logger.info(f"Successfully parsed JSON with keys: {list(result.keys()) if isinstance(result, dict) else 'array'}")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        logger.debug(f"Failed text (first 500 chars): {text_to_parse[:500]}")

        # Try more aggressive cleaning
        try:
            # Remove any text before first { and after last }
            cleaned = text_to_parse.strip()
            if cleaned.startswith('{') and cleaned.endswith('}'):
                # Try replacing single quotes with double quotes
                cleaned = re.sub(r"'([^']*)':", r'"\1":', cleaned)
                sanitized = sanitize_json_string(cleaned)
                result = json.loads(sanitized)
                logger.info(f"Successfully parsed JSON after aggressive cleaning")
                return result
        except json.JSONDecodeError:
            pass

    logger.error(f"All JSON parsing attempts failed")
    return None

def validate_ai_response(response_data: Dict) -> bool:
    """Validate that AI response contains required fields"""
    required_fields = ['hook_slide', 'content_slides', 'cta_slide']
    
    for field in required_fields:
        if field not in response_data:
            return False
    
    # Validate hook_slide structure
    if not isinstance(response_data['hook_slide'], dict) or 'title' not in response_data['hook_slide']:
        return False
    
    # Validate content_slides structure
    if not isinstance(response_data['content_slides'], list) or len(response_data['content_slides']) == 0:
        return False
    
    # Validate cta_slide structure
    if not isinstance(response_data['cta_slide'], dict) or 'title' not in response_data['cta_slide']:
        return False
    
    return True

def get_ai_suggestions(content_idea: str, num_slides: int = 5) -> Dict:
    """Get AI-powered content suggestions for carousel"""
    start_time = time.time()
    logger.info(f"Getting AI suggestions for: {content_idea} ({num_slides} slides)")

    # Try Claude API first
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "YOUR_CLAUDE_API_KEY_HERE":
        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Calculate content slides (total - hook - CTA)
            content_slide_count = max(1, num_slides - 2)

            prompt = f"""Create an Instagram carousel post with {num_slides} slides about: {content_idea}

You MUST respond with ONLY a valid JSON object, no other text before or after. No markdown, no explanation.

The JSON must have this exact structure:
{{
    "hook_slide": {{
        "title": "Attention-grabbing hook title (max 8 words)",
        "subtitle": "Supporting subtitle that creates curiosity"
    }},
    "content_slides": [
        {{
            "title": "Slide title",
            "subtitle": "Brief subtitle",
            "bullet_points": ["Point 1", "Point 2", "Point 3"]
        }}
    ],
    "cta_slide": {{
        "title": "Strong call-to-action title",
        "subtitle": "What they should do next",
        "action_text": "Follow for more!"
    }},
    "hashtags": "#hashtag1 #hashtag2 #hashtag3",
    "caption": "Engaging Instagram caption with emojis and call to action."
}}

Requirements:
- hook_slide: Create a compelling hook that stops scrollers
- content_slides: Provide exactly {content_slide_count} content slides with valuable tips/insights
- cta_slide: Strong call-to-action encouraging engagement
- hashtags: 10-15 relevant hashtags as a single string
- caption: 150-200 word engaging caption with emojis

Topic: {content_idea}

Respond with ONLY the JSON object, nothing else."""

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2500,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response with enhanced error handling
            content = response.content[0].text
            
            try:
                # Use our improved JSON extraction
                parsed_response = extract_json_from_text(content)
                
                if parsed_response and validate_ai_response(parsed_response):
                    # Track successful AI usage
                    response_time = time.time() - start_time
                    if 'analytics' in st.session_state:
                        st.session_state.analytics.track_ai_usage('claude', True, response_time)
                    return parsed_response
                else:
                    st.warning("AI response validation failed. Using fallback content.")
                    if 'analytics' in st.session_state:
                        st.session_state.analytics.track_ai_usage('claude', False, time.time() - start_time)
                    return generate_fallback_content(content_idea, num_slides)
                    
            except Exception as parse_error:
                st.error(f"JSON parsing error: {str(parse_error)}")
                logging.error(f"Claude API JSON parsing failed: {parse_error}")
                logging.debug(f"Raw response content: {content[:500]}...")  # Log first 500 chars
                if 'analytics' in st.session_state:
                    st.session_state.analytics.track_ai_usage('claude', False, time.time() - start_time)
                return generate_fallback_content(content_idea, num_slides)
        except Exception as e:
            st.warning(f"Claude API failed: {e}")
            if 'analytics' in st.session_state:
                st.session_state.analytics.track_ai_usage('claude', False, time.time() - start_time)
            
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
            
            try:
                parsed_response = extract_json_from_text(content)
                if parsed_response and validate_ai_response(parsed_response):
                    return parsed_response
                else:
                    st.warning("OpenAI response validation failed. Using fallback content.")
                    return generate_fallback_content(content_idea, num_slides)
            except Exception as parse_error:
                st.error(f"OpenAI JSON parsing error: {str(parse_error)}")
                logging.error(f"OpenAI API JSON parsing failed: {parse_error}")
                return generate_fallback_content(content_idea, num_slides)
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

    st.divider()

    # ==========================================
    # ELITE BRAND STRATEGIST FEATURES
    # ==========================================
    st.subheader("🚀 Elite Brand Templates")

    # Pre-built brand templates
    template_options = {
        "Elite Systems AI": {
            "primary": "#2563eb",
            "secondary": "#3b82f6",
            "accent": "#ff3b3b",
            "bg": "#000000",
            "text": "#ffffff"
        },
        "Luxury Gold": {
            "primary": "#d4af37",
            "secondary": "#b8860b",
            "accent": "#ffd700",
            "bg": "#1a1a1a",
            "text": "#ffffff"
        },
        "Ocean Vibes": {
            "primary": "#0077b6",
            "secondary": "#00b4d8",
            "accent": "#90e0ef",
            "bg": "#03045e",
            "text": "#ffffff"
        },
        "Sunset Energy": {
            "primary": "#ff6b6b",
            "secondary": "#feca57",
            "accent": "#ff9ff3",
            "bg": "#2d3436",
            "text": "#ffffff"
        },
        "Nature Fresh": {
            "primary": "#00b894",
            "secondary": "#00cec9",
            "accent": "#55efc4",
            "bg": "#1e272e",
            "text": "#ffffff"
        },
        "Corporate Pro": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#3498db",
            "bg": "#ecf0f1",
            "text": "#2c3e50"
        }
    }

    selected_template = st.selectbox(
        "Quick Apply Template",
        ["Select a template..."] + list(template_options.keys())
    )

    if selected_template != "Select a template..." and st.button("🎨 Apply Template", use_container_width=True):
        template = template_options[selected_template]
        st.session_state.theme = BrandTheme(
            name=selected_template,
            primary_color=template["primary"],
            secondary_color=template["secondary"],
            accent_color=template["accent"],
            background_color=template["bg"],
            text_color=template["text"],
            font_family="Arial"
        )
        st.success(f"✅ Applied '{selected_template}' template!")
        st.rerun()

    st.divider()

    # Content Pillars for Brand Strategists
    st.subheader("📚 Content Pillars")
    st.markdown("""
    <div style="background: rgba(37, 99, 235, 0.1); padding: 12px; border-radius: 8px; border: 1px solid rgba(37, 99, 235, 0.3); margin-bottom: 10px;">
        <p style="color: #60a5fa; font-size: 0.85rem; margin: 0;">
        <strong>💡 Pro Tip:</strong> Rotate between these content types for maximum engagement:
        </p>
    </div>
    """, unsafe_allow_html=True)

    content_pillars = [
        "📖 Educational Tips",
        "🎯 Industry Insights",
        "💬 Behind the Scenes",
        "🏆 Client Success Stories",
        "❓ FAQ & Myth Busters",
        "🔥 Trending Topics"
    ]

    for pillar in content_pillars:
        st.markdown(f"<p style='color: #e0e0e0; margin: 4px 0; font-size: 0.9rem;'>• {pillar}</p>", unsafe_allow_html=True)

    st.divider()

    # Engagement Optimizer
    st.subheader("📈 Engagement Tips")

    engagement_tips = st.expander("Best Posting Practices", expanded=False)
    with engagement_tips:
        st.markdown("""
        **🕐 Best Times to Post:**
        - Weekdays: 11am-1pm, 7-9pm
        - Weekends: 10am-12pm

        **📱 Carousel Best Practices:**
        - 5-10 slides perform best
        - First slide = hook (stop the scroll!)
        - Last slide = strong CTA
        - Use consistent branding
        - Add text overlays for accessibility

        **#️⃣ Hashtag Strategy:**
        - Mix of popular + niche tags
        - 20-30 hashtags optimal
        - Save hashtag sets for reuse
        """)

    st.divider()

    # Elite Performance Dashboard
    st.subheader("📊 Elite Performance Dashboard")
    
    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CPU Usage", f"{cpu_percent:.1f}%")
            st.metric("Memory", f"{memory.percent:.1f}%")
        with col2:
            st.metric("Available RAM", f"{memory.available / (1024**3):.1f} GB")
            st.metric("Font Cache", f"{len(CarouselGenerator._font_cache)} fonts")
    except Exception:
        st.info("Performance metrics unavailable")
    
    # Session analytics summary
    if hasattr(st.session_state, 'analytics'):
        summary = st.session_state.analytics.get_session_summary()
        
        st.metric("Session Duration", f"{summary['session_duration_minutes']:.1f} min")
        st.metric("Total Events", summary['total_events'])
        
        if summary['event_breakdown']:
            st.write("**Activity Breakdown:**")
            for event_type, count in summary['event_breakdown'].items():
                st.write(f"• {event_type}: {count}")
    
    # Elite branding
    st.markdown("""
    ---
    **🚀 Elite Systems AI**
    
    *Professional-grade analytics and performance monitoring for enterprise-level content creation*
    """)

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
            progress_container = st.empty()
            status_container = st.empty()
            
            with st.spinner("Connecting to AI services..."):
                progress_container.progress(0)
                status_container.info("🔗 Initializing AI connection...")
                
                try:
                    suggestions = get_ai_suggestions(content_idea, num_slides)
                    progress_container.progress(1.0)
                    status_container.success("✅ Content generated successfully!")
                    
                    if suggestions:
                        # Create slides from AI suggestions
                        status_container.info("🎨 Creating carousel slides...")
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
                        
                        status_container.success("✅ Content generated! Check the Preview tab")
                        
                        # Display caption and hashtags
                        st.subheader("📝 Suggested Caption")
                        st.text_area("Caption", value=suggestions.get('caption', ''), height=150)
                        
                        st.subheader("#️⃣ Suggested Hashtags")
                        hashtags = suggestions.get('hashtags', [])
                        # Handle both string and list formats
                        if isinstance(hashtags, str):
                            st.code(hashtags)
                        else:
                            st.code(' '.join(hashtags))
                    else:
                        status_container.error("❌ Failed to generate content. Please try again.")
                        
                except Exception as e:
                    logger.error(f"Content generation failed: {str(e)}")
                    progress_container.empty()
                    status_container.error(f"❌ Content generation failed: {str(e)}")
                    st.error("Something went wrong with content generation. Please check your API keys and try again.")
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
            try:
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
                status_text = st.empty()
                
                logger.info(f"Starting generation of {len(st.session_state.slides)} slides")
                
                generation_start = time.time()
                successful_slides = 0
                
                for i, slide in enumerate(st.session_state.slides):
                    status_text.text(f"Generating slide {i + 1} of {len(st.session_state.slides)}: {slide.title[:30]}...")
                    
                    try:
                        img = generator.create_slide(slide, custom_sizes)
                        st.session_state.generated_images.append(img)
                        successful_slides += 1
                        progress_bar.progress((i + 1) / len(st.session_state.slides))
                        
                    except Exception as slide_error:
                        logger.error(f"Failed to generate slide {i + 1}: {str(slide_error)}")
                        status_text.error(f"Failed to generate slide {i + 1}: {str(slide_error)}")
                        continue
                
                generation_time = time.time() - generation_start
                generation_success = successful_slides == len(st.session_state.slides)
                
                # Track generation performance
                st.session_state.analytics.track_generation_performance(
                    len(st.session_state.slides), 
                    generation_time, 
                    generation_success
                )
                
                status_text.success("✅ Preview generated successfully!")
                logger.info(f"Successfully generated {successful_slides}/{len(st.session_state.slides)} slides in {generation_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Preview generation failed: {str(e)}")
                st.error(f"❌ Preview generation failed: {str(e)}")
                st.error("Please check the logs for detailed error information.")
        
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
                        use_container_width=True)
            
            # Export options
            st.divider()
            st.subheader("💾 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download individual images
                if st.button("📥 Download All Images", use_container_width=True):
                    st.session_state.analytics.track_export("individual_images", len(st.session_state.generated_images))
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
                    st.session_state.analytics.track_export("project_save", len(st.session_state.generated_images))
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
                        st.session_state.analytics.track_export("pdf", len(st.session_state.generated_images))
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