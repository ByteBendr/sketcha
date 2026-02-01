from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
import numpy as np

from transformers import pipeline

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the image classification pipeline with advanced model
classifier = None

def get_classifier():
    global classifier
    if classifier is None:
        # Using ResNet-152 for better accuracy
        classifier = pipeline(
            "image-classification", 
            model="microsoft/resnet-152",
            top_k=5
        )
    return classifier

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_emoji_for_label(label):
    """Map labels to appropriate emojis with comprehensive coverage"""
    label_lower = label.lower()
    
    # Extensive emoji mapping
    emoji_map = {
        # Animals
        'dog': '🐕', 'puppy': '🐶', 'hound': '🐕‍🦺', 'retriever': '🦮', 'poodle': '🐩',
        'cat': '🐈', 'kitten': '🐱', 'tabby': '🐈‍⬛',
        'bird': '🐦', 'eagle': '🦅', 'owl': '🦉', 'duck': '🦆', 'chicken': '🐔', 'rooster': '🐓',
        'fish': '🐠', 'goldfish': '🐟', 'shark': '🦈', 'whale': '🐋', 'dolphin': '🐬',
        'horse': '🐴', 'zebra': '🦓', 'unicorn': '🦄',
        'cow': '🐄', 'bull': '🐂', 'ox': '🦬',
        'pig': '🐷', 'boar': '🐗',
        'sheep': '🐑', 'goat': '🐐', 'ram': '🐏',
        'elephant': '🐘', 'rhino': '🦏', 'hippo': '🦛',
        'lion': '🦁', 'tiger': '🐯', 'leopard': '🐆', 'cheetah': '🐆',
        'bear': '🐻', 'panda': '🐼', 'koala': '🐨',
        'monkey': '🐵', 'gorilla': '🦍', 'orangutan': '🦧',
        'rabbit': '🐰', 'hare': '🐇',
        'mouse': '🐭', 'rat': '🐀', 'hamster': '🐹',
        'fox': '🦊', 'wolf': '🐺',
        'deer': '🦌', 'moose': '🫎',
        'giraffe': '🦒', 'camel': '🐪', 'llama': '🦙',
        'penguin': '🐧', 'flamingo': '🦩', 'peacock': '🦚',
        'frog': '🐸', 'turtle': '🐢', 'lizard': '🦎', 'snake': '🐍', 'crocodile': '🐊',
        'butterfly': '🦋', 'bee': '🐝', 'ladybug': '🐞', 'spider': '🕷️', 'scorpion': '🦂',
        'octopus': '🐙', 'squid': '🦑', 'crab': '🦀', 'lobster': '🦞', 'shrimp': '🦐',
        
        # Vehicles
        'car': '🚗', 'automobile': '🚙', 'sports car': '🏎️', 'racing car': '🏁',
        'truck': '🚚', 'pickup': '🛻', 'delivery': '🚐',
        'bus': '🚌', 'minibus': '🚐', 'trolleybus': '🚎',
        'train': '🚂', 'locomotive': '🚂', 'railway': '🚃', 'subway': '🚇',
        'airplane': '✈️', 'aircraft': '🛩️', 'helicopter': '🚁', 'rocket': '🚀',
        'boat': '⛵', 'ship': '🚢', 'sailboat': '⛵', 'yacht': '🛥️',
        'bicycle': '🚲', 'bike': '🚴', 'motorcycle': '🏍️', 'scooter': '🛴',
        'ambulance': '🚑', 'fire truck': '🚒', 'police': '🚓', 'taxi': '🚕',
        'tractor': '🚜', 'bulldozer': '🚜',
        
        # Food & Drinks
        'pizza': '🍕', 'burger': '🍔', 'hamburger': '🍔', 'sandwich': '🥪',
        'hot dog': '🌭', 'taco': '🌮', 'burrito': '🌯',
        'bread': '🍞', 'baguette': '🥖', 'pretzel': '🥨',
        'cheese': '🧀', 'meat': '🥩', 'bacon': '🥓', 'poultry': '🍗',
        'egg': '🥚', 'fried egg': '🍳',
        'salad': '🥗', 'broccoli': '🥦', 'carrot': '🥕', 'corn': '🌽',
        'mushroom': '🍄', 'peanut': '🥜',
        'apple': '🍎', 'banana': '🍌', 'orange': '🍊', 'lemon': '🍋',
        'watermelon': '🍉', 'grapes': '🍇', 'strawberry': '🍓', 'cherry': '🍒',
        'peach': '🍑', 'pear': '🍐', 'pineapple': '🍍', 'coconut': '🥥',
        'tomato': '🍅', 'eggplant': '🍆', 'potato': '🥔', 'sweet potato': '🍠',
        'cake': '🍰', 'cupcake': '🧁', 'pie': '🥧', 'doughnut': '🍩', 'cookie': '🍪',
        'chocolate': '🍫', 'candy': '🍬', 'lollipop': '🍭', 'ice cream': '🍦',
        'coffee': '☕', 'tea': '🍵', 'wine': '🍷', 'beer': '🍺', 'cocktail': '🍹',
        'milk': '🥛', 'bottle': '🍼',
        
        # Nature & Plants
        'tree': '🌳', 'palm tree': '🌴', 'evergreen': '🌲', 'deciduous': '🌳',
        'flower': '🌸', 'blossom': '🌺', 'rose': '🌹', 'tulip': '🌷', 'sunflower': '🌻',
        'plant': '🌿', 'herb': '🌿', 'shamrock': '☘️', 'clover': '🍀',
        'cactus': '🌵', 'succulent': '🪴',
        'mushroom': '🍄',
        'leaf': '🍃', 'fallen leaf': '🍂', 'maple': '🍁',
        
        # Weather & Sky
        'sun': '☀️', 'cloud': '☁️', 'rain': '🌧️', 'snow': '❄️', 'thunder': '⚡',
        'rainbow': '🌈', 'star': '⭐', 'moon': '🌙',
        
        # Objects & Items
        'ball': '⚽', 'soccer': '⚽', 'basketball': '🏀', 'football': '🏈', 'baseball': '⚾',
        'tennis': '🎾', 'volleyball': '🏐',
        'book': '📚', 'notebook': '📓', 'newspaper': '📰',
        'phone': '📱', 'computer': '💻', 'laptop': '💻', 'keyboard': '⌨️', 'mouse': '🖱️',
        'camera': '📷', 'video': '📹',
        'watch': '⌚', 'clock': '🕐', 'alarm': '⏰',
        'light': '💡', 'candle': '🕯️', 'lamp': '🪔',
        'door': '🚪', 'window': '🪟', 'bed': '🛏️', 'couch': '🛋️', 'chair': '🪑',
        'toilet': '🚽', 'shower': '🚿', 'bathtub': '🛁',
        'umbrella': '☂️', 'glasses': '👓', 'sunglasses': '🕶️',
        'bag': '💼', 'backpack': '🎒', 'handbag': '👜',
        'shoe': '👞', 'boot': '👢', 'sandal': '👡', 'sneaker': '👟',
        'hat': '🎩', 'cap': '🧢', 'crown': '👑',
        'ring': '💍', 'gem': '💎',
        'key': '🔑', 'lock': '🔒',
        'hammer': '🔨', 'wrench': '🔧', 'screwdriver': '🪛',
        'scissors': '✂️', 'knife': '🔪',
        'guitar': '🎸', 'piano': '🎹', 'drum': '🥁', 'trumpet': '🎺', 'violin': '🎻',
        'microphone': '🎤', 'headphones': '🎧',
        'paint': '🎨', 'brush': '🖌️',
        'gift': '🎁', 'balloon': '🎈', 'party': '🎉',
        'trophy': '🏆', 'medal': '🥇',
        
        # Buildings & Places
        'house': '🏠', 'home': '🏡', 'building': '🏢', 'office': '🏢',
        'hospital': '🏥', 'school': '🏫', 'bank': '🏦', 'hotel': '🏨',
        'church': '⛪', 'mosque': '🕌', 'temple': '🛕',
        'castle': '🏰', 'palace': '🏰',
        'mountain': '⛰️', 'volcano': '🌋', 'desert': '🏜️', 'beach': '🏖️', 'island': '🏝️',
        'bridge': '🌉', 'fountain': '⛲', 'statue': '🗿',
        
        # People & Body
        'person': '👤', 'people': '👥', 'man': '👨', 'woman': '👩',
        'baby': '👶', 'child': '🧒',
        'face': '😊', 'smile': '😊', 'happy': '😄',
        'hand': '✋', 'finger': '👆', 'fist': '✊',
        'foot': '🦶', 'leg': '🦵', 'arm': '💪',
        'eye': '👁️', 'ear': '👂', 'nose': '👃', 'mouth': '👄',
        'heart': '❤️', 'brain': '🧠', 'bone': '🦴',
        
        # Symbols & Misc
        'flag': '🏁', 'fire': '🔥', 'water': '💧', 'lightning': '⚡',
        'diamond': '💎', 'crystal': '🔮',
        'money': '💰', 'coin': '🪙', 'dollar': '💵',
        'medical': '⚕️', 'pill': '💊', 'syringe': '💉',
        'science': '🔬', 'test tube': '🧪', 'dna': '🧬',
        'magnet': '🧲', 'battery': '🔋',
        'radioactive': '☢️', 'biohazard': '☣️',
    }
    
    for key, emoji in emoji_map.items():
        if key in label_lower:
            return emoji
    
    for key, emoji in emoji_map.items():
        if any(word in label_lower for word in key.split()):
            return emoji
    
    if any(word in label_lower for word in ['dog', 'cat', 'animal', 'pet']):
        return '🐾'
    elif any(word in label_lower for word in ['car', 'vehicle', 'transport']):
        return '🚗'
    elif any(word in label_lower for word in ['food', 'eat', 'meal']):
        return '🍽️'
    elif any(word in label_lower for word in ['plant', 'vegetation']):
        return '🌱'
    elif any(word in label_lower for word in ['building', 'structure', 'architecture']):
        return '🏛️'
    elif any(word in label_lower for word in ['sport', 'game', 'play']):
        return '⚽'
    elif any(word in label_lower for word in ['electronic', 'device', 'technology']):
        return '📱'
    elif any(word in label_lower for word in ['furniture', 'home']):
        return '🛋️'
    elif any(word in label_lower for word in ['clothing', 'wear', 'apparel']):
        return '👕'
    elif any(word in label_lower for word in ['tool', 'equipment']):
        return '🔧'
    elif any(word in label_lower for word in ['music', 'instrument', 'sound']):
        return '🎵'
    elif any(word in label_lower for word in ['art', 'painting', 'drawing']):
        return '🎨'
    
    return '✨'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image (PNG, JPG, JPEG, GIF, or WEBP)'}), 400
        

        image = Image.open(file.stream).convert('RGB')
        

        clf = get_classifier()
        predictions = clf(image)
        
        predictions = sorted(predictions, key=lambda x: x['score'], reverse=True)[:5]
        
        results = []
        for pred in predictions:
            label = pred['label']
            confidence = pred['score'] * 100
            
            emoji = get_emoji_for_label(label)
            
            clean_label = label.replace('_', ' ').replace('-', ' ').title()
            
            results.append({
                'label': clean_label,
                'confidence': round(confidence, 2),
                'emoji': emoji
            })
        
        return jsonify({
            'success': True,
            'predictions': results
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)