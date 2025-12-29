# 🎨 Instagram Carousel Generator

A professional, AI-powered tool for creating stunning Instagram carousels with your brand theme.

![Carousel Generator](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![AI Powered](https://img.shields.io/badge/AI-Claude%20%2B%20OpenAI-00D4AA)
![Deploy](https://img.shields.io/badge/Deploy-Railway-0B0D0E)

## ✨ Features

- **🤖 AI Content Generation** - Enter an idea, get professional carousel content
- **🎨 Brand Theme Customization** - Colors, fonts, and styles that match your brand
- **👁️ Live Preview** - See your carousel before exporting
- **📱 Instagram Optimized** - Perfect 1080x1080 sizing
- **💾 Multiple Export Formats** - PNG images or PDF
- **🔄 Theme Persistence** - Save and reuse your brand settings

## 🚀 Quick Start

### Option 1: Use the Live Demo
Visit: **[Your Railway URL will go here]**

### Option 2: Run Locally
```bash
# Clone the repository
git clone https://github.com/EliteSystemsAI/instagram-carousel-generator.git
cd instagram-carousel-generator

# Install dependencies
pip install -r requirements.txt

# Add your API key (optional - works without it)
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the app
streamlit run carousel_generator.py
```

Open http://localhost:8501 in your browser.

## 🎯 How to Use

### 1. **AI Content Generation**
- Enter your content idea (e.g., "5 tips for Instagram growth")
- Choose number of slides (3-10)
- Click "Generate Content"
- AI creates professional carousel structure

### 2. **Customize Your Brand**
- Set primary, secondary, and accent colors
- Choose fonts
- Save your theme for future use

### 3. **Edit & Preview**
- Fine-tune text in the Manual Editor
- See live preview of all slides
- Navigate between slides with the slider

### 4. **Export**
- Download individual PNG images
- Export as single PDF
- Save to local folder

## 🎨 Brand Theme Examples

**Corporate Blue**
- Primary: #1E3A8A
- Secondary: #3B82F6  
- Accent: #60A5FA

**Vibrant Purple**
- Primary: #7C3AED
- Secondary: #A855F7
- Accent: #C084FC

**Professional Dark**
- Primary: #111827
- Secondary: #374151
- Accent: #6B7280

## 🤖 AI Features

The carousel generator uses AI to create:
- **Compelling hooks** for the first slide
- **Value-packed content** for middle slides  
- **Strong call-to-actions** for the final slide
- **Relevant hashtags** for Instagram
- **Engaging captions** for your posts

Works with:
- **Claude API** (recommended)
- **OpenAI API** (fallback)
- **Basic templates** (no API key needed)

## 📱 Perfect for Content Creators

- **Brand Strategists** - Create on-brand content quickly
- **Social Media Managers** - Streamline carousel production
- **Entrepreneurs** - Professional posts without design skills
- **Agencies** - Client-ready content at scale

## 🔧 Technical Details

- **Framework**: Streamlit
- **AI**: Claude (Anthropic) + OpenAI fallback
- **Image Processing**: Pillow (PIL)
- **Deployment**: Railway
- **Export Formats**: PNG, PDF

## 🚀 Deploy Your Own

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/EliteSystemsAI/instagram-carousel-generator)

1. Click the Railway button above
2. Add your `ANTHROPIC_API_KEY` environment variable
3. Deploy and share the URL

## 📄 License

MIT License - Use this for commercial projects, modify as needed.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes  
4. Push to the branch
5. Open a Pull Request

## 💡 Ideas & Support

- Create issues for feature requests
- Contribute templates and themes
- Share your carousel designs

---

**Made with ❤️ for Instagram content creators**

*Generate professional carousels in seconds, not hours.*