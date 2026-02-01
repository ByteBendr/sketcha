# 🎨 Sketcha - AI Image Recognition App

A beautifully designed Flask web application that uses advanced AI to recognize objects in images! Features a hand-drawn, cartoonish UI with smooth animations, **fully functional dark mode**, and a clean, spacious layout.

### 🎨 Design Features
- **Hand-drawn Aesthetics** - Playful, cartoonish design with custom fonts
- **Dark Mode** - Beautiful dark theme with perfect contrast (saves your preference!)
- **Smooth Animations** - Bouncing logo, wiggling icons, sliding cards, sparkle effects
- **Smart Color System** - CSS variables for easy theming
- **Spacious Layout** - Generous padding and margins for comfortable viewing
- **Visual Feedback** - Hover effects, active states, and interactive elements

## 🚀 Features

- 🖼️ **Drag & Drop Upload** - Easy image uploading with visual feedback
- 🤖 **Advanced AI** - Uses Microsoft's ResNet-152 for highly accurate predictions
- 🌙 **Working Dark Mode** - Toggle between light and dark themes (preference saved!)
- 📊 **Visual Results** - Animated confidence bars and smart emoji matching
- 😊 **200+ Smart Emojis** - Intelligently matched to prediction categories
- 📱 **Fully Responsive** - Perfect experience on desktop, tablet, and mobile
- ✨ **Delightful Effects** - Sparkle trail, smooth transitions, micro-interactions
- ⚠️ **AI Disclaimer** - Clear warning about prediction accuracy

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download
Download all the files to a directory on your computer.

### Step 2: Install Dependencies
Open a terminal/command prompt in the project directory and run:

```bash
Requirements Installer (LAUNCH FIRST).py
```

**Note:** The first time you run the app, it will download the ResNet-152 AI model (~230MB). This may take a few minutes depending on your internet connection.

### Step 3: Run the Application
```bash
python app.py
```

The app will start on `http://localhost:5000`

## 🎮 How to Use

1. **Open your browser** and navigate to `http://localhost:5000`
2. **Toggle Dark Mode** by clicking the moon/sun button in the top-right corner (your preference is saved!)
3. **Upload an image** by either:
   - Dragging and dropping an image onto the drop zone
   - Clicking the drop zone or "Choose Image" button to browse files
4. **Click "Analyze Image!"** to start the AI recognition
5. **View the results** - The top 5 predictions appear with confidence scores and emojis

## 📁 Project Structure

```
sketcha/
│
├── app.py                   # Flask application with ResNet-152
├── requirements.txt         # Python dependencies
├── README.md                # This file
│
├── templates/
│   └── index.html           # Main HTML template
│   └── favicon
│       └── (favicon files)
├── static/
│   ├── css/
│   │   └── style.css        # All styles (organized with CSS variables)
│   └── js/
│       └── script.js        # Frontend JavaScript (dark mode, uploads, etc.)
│
└── uploads/                 # (auto-created) Temporary storage
```

## 🎨 Design System

### Color Palette
- **Primary Pink**: `#FF6B9D` - Main accent color
- **Teal**: `#4ECDC4` - Secondary accent
- **Yellow**: `#FEC84D` - Highlights
- **Purple**: `#B565D8` - Tertiary accent
- **Orange**: `#FF9A56` - Warnings

### Dark Mode Colors
- **Background**: `#1a1a2e` - Deep navy
- **Cards**: `#252538` - Slightly lighter navy
- **Text**: `#eaeaea` - Light gray
- **Borders**: `#4a4a6a` - Muted purple-gray

### Fonts
- **Bubblegum Sans** - Headings and logo
- **Grandstander** - Buttons and labels
- **Patrick Hand** - Body text

## 🤖 AI Model

- **Model**: Microsoft ResNet-152
- **Accuracy**: One of the most accurate image classification models
- **Categories**: 1000+ object categories from ImageNet
- **Predictions**: Top 5 results with confidence scores
- **Processing**: Runs locally (no API keys needed!)


## 🔧 Customization

### Change Colors
Edit CSS variables in `static/css/style.css`:

```css
:root {
    --color-primary: #FF6B9D;    /* Your primary color */
    --color-accent: #4ECDC4;     /* Your accent color */
    /* ... more colors ... */
}

body.dark-mode {
    --color-bg: #1a1a2e;         /* Dark background */
    /* ... dark mode colors ... */
}
```

### Add More Emojis
Edit the `emoji_map` in `app.py`:

```python
emoji_map = {
    'your_category': '🎯',
    # Add more mappings...
}
```

### Change AI Model
Edit the classifier in `app.py`:

```python
classifier = pipeline(
    "image-classification", 
    model="your-model-name",
    top_k=5
)
```

## 📷 Supported Image Formats
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

**Maximum file size**: 16MB

## 🐛 Troubleshooting

### Dark Mode Not Saving
- Clear browser cache and try again
- Make sure localStorage is enabled in your browser
- Some privacy modes may prevent localStorage

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5001)
```

### Model Download Issues
- Check your internet connection
- The model (~230MB) downloads on first run
- Try running the app again if it fails

### Slow Performance
- First prediction is slower (model loading)
- Subsequent predictions are faster
- Consider using a GPU for better performance

## 💡 Tips for Best Results

- Use clear, well-lit images
- Objects should be prominent in the frame
- Try various subjects: animals, objects, food, vehicles, nature
- Multiple objects may be detected
- Check all 5 predictions for interesting insights

## 🎉 Features Checklist

- ✅ Dark mode preference persistence
- ✅ Smooth animations and transitions
- ✅ Mobile responsive design
- ✅ Working notification system
- ✅ Drag and drop upload
- ✅ Image preview with remove option
- ✅ Loading states
- ✅ Empty states
- ✅ Error handling
- ✅ Advanced AI model
- ✅ Smart emoji matching

## 🤝 Contributing

Feel free to customize and enhance! Ideas:
- Add more emoji mappings
- Create additional themes
- Add image filters
- Support batch uploads
- Save prediction history
- Compare different models
- Add user accounts
- Implement image cropping

## 📜 License

Free to use and modify for personal and educational purposes.

## 🙏 Credits

- **AI Model**: Microsoft ResNet-152
- **Framework**: Flask
- **Fonts**: Google Fonts (Bubblegum Sans, Grandstander, Patrick Hand)
- **Design**: Custom hand-drawn aesthetic with modern functionality
- **Favicon**: Thanks to 'anilofex' from Flaticon for the favicon (<a href="https://www.flaticon.com/free-icons/computer-vision" title="computer vision icons">anilofex - Flaticon</a>)

---

**Made with 💖 and a sprinkle of AI magic! ✨**
