"""
Medical Translator Mobile App - Mendy (Multi-Language Version)
A multilingual medical translation assistant supporting Chinese, Urdu, and Twi

Dependencies:
pip install flask google-generativeai python-dotenv

Setup:
1. Create a .env file with: GEMINI_API_KEY=your_key_here
2. Run: python app.py
3. Open browser to http://localhost:5001
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️ Gemini API key not found. Please set GEMINI_API_KEY in .env file")
model = genai.GenerativeModel("gemini-flash-latest")

# Language configurations
LANGUAGE_CONFIG = {
    'chinese': {
        'name': '中文',
        'english_name': 'Chinese',
        'realtime_title': '实时翻译 Realtime Translation',
        'preparation_title': '就医准备 Hospital Preparation',
        'input_placeholder': 'Type or paste text here... 在此输入或粘贴文字...',
        'symptom_placeholder': 'Describe your symptoms... 描述您的症状...',
        'translate_btn': '翻译 Translate',
        'advice_btn': '获取建议 Get Advice',
        'back_btn': '返回首页 Back to Home',
        'translating': '翻译中... Translating...',
        'analyzing': '分析中... Analyzing...',
        'target_lang': 'Chinese',
        'speaker': 'Chinese-speaking'
    },
    'urdu': {
        'name': 'اردو',
        'english_name': 'Urdu',
        'realtime_title': 'فوری ترجمہ Realtime Translation',
        'preparation_title': 'ہسپتال کی تیاری Hospital Preparation',
        'input_placeholder': 'Type or paste text here... یہاں متن لکھیں یا پیسٹ کریں...',
        'symptom_placeholder': 'Describe your symptoms... اپنی علامات بیان کریں...',
        'translate_btn': 'ترجمہ کریں Translate',
        'advice_btn': 'مشورہ حاصل کریں Get Advice',
        'back_btn': 'واپس جائیں Back to Home',
        'translating': 'ترجمہ ہو رہا ہے... Translating...',
        'analyzing': 'تجزیہ ہو رہا ہے... Analyzing...',
        'target_lang': 'Urdu',
        'speaker': 'Urdu-speaking'
    },
    'twi': {
        'name': 'Twi',
        'english_name': 'Twi',
        'realtime_title': 'Nkyerɛaseɛ Ntɛm Realtime Translation',
        'preparation_title': 'Ayaresabea Ho Nhyehyɛeɛ Hospital Preparation',
        'input_placeholder': 'Type or paste text here... Kyerɛw anaa fa nsɛm gu hɔ...',
        'symptom_placeholder': 'Describe your symptoms... Ka wo yadeɛ ho nsɛm...',
        'translate_btn': 'Kyerɛ Aseɛ Translate',
        'advice_btn': 'Nya Afotuo Get Advice',
        'back_btn': 'San Kɔ Mfiaseɛ Back to Home',
        'translating': 'Yɛrekyerɛ aseɛ... Translating...',
        'analyzing': 'Yɛrehwɛ mu... Analyzing...',
        'target_lang': 'Twi (Akan language from Ghana)',
        'speaker': 'Twi-speaking'
    }
}

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for realtime translation page
@app.route('/realtime')
def realtime():
    lang = request.args.get('lang', 'chinese')
    config = LANGUAGE_CONFIG.get(lang, LANGUAGE_CONFIG['chinese'])
    return render_template('realtime.html', language=lang, config=config)

# Route for hospital preparation page
@app.route('/preparation')
def preparation():
    lang = request.args.get('lang', 'chinese')
    config = LANGUAGE_CONFIG.get(lang, LANGUAGE_CONFIG['chinese'])
    return render_template('preparation.html', language=lang, config=config)

# Translation API endpoint
@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    lang = data.get('language', 'chinese')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    config = LANGUAGE_CONFIG.get(lang, LANGUAGE_CONFIG['chinese'])
    
    prompt = f"""You are a medical translator helping {config['speaker']} patients at an English-speaking hospital.

Translate this English medical phrase to {config['target_lang']} and provide helpful context:
"{text}"

Provide your response in this exact format:

TRANSLATION:
[Direct word-to-word {config['target_lang']} translation]

CONTEXT:
[In {config['target_lang']}: Explain the situation, where they likely are, and what the staff is asking for]

RESPONSES:
[In {config['target_lang']}: Provide 2-3 possible responses they can give, with English translations]


Do not include pronunciation. Keep it concise and practical for a hospital setting."""

    try:
        print(f"Translating to {lang}: {text}")
        response = model.generate_content(prompt)
        content = response.text
        
        print("=" * 50)
        print(f"GEMINI RESPONSE ({lang}):")
        print(content)
        print("=" * 50)
        
        # Parse the response
        try:
            parts = content.split('TRANSLATION:')[1].split('CONTEXT:')
            translation = parts[0].strip()
            
            parts2 = parts[1].split('RESPONSES:')
            context = parts2[0].strip()
            responses = parts2[1].strip()
        except (IndexError, AttributeError) as parse_error:
            print(f"Parsing error: {parse_error}")
            return jsonify({
                'translation': content,
                'context': 'Raw response (parsing failed)',
                'responses': 'See translation above'
            })
        
        return jsonify({
            'translation': translation,
            'context': context,
            'responses': responses
        })
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'{type(e).__name__}: {str(e)}'}), 500

# Hospital preparation advice API endpoint
@app.route('/api/advice', methods=['POST'])
def advice():
    data = request.json
    symptom = data.get('symptom', '')
    lang = data.get('language', 'chinese')
    
    if not symptom:
        return jsonify({'error': 'No symptom provided'}), 400
    
    config = LANGUAGE_CONFIG.get(lang, LANGUAGE_CONFIG['chinese'])
    
    prompt = f"""You are a medical advisor helping a {config['speaker']} person understand what United States hospital care they need.

The patient says: "{symptom}"

Provide advice in {config['target_lang']} about:
1. What type of doctor/department they should see
2. Whether they need an appointment
3. What to expect during the visit
4. What to bring (insurance, ID, etc.)
5. Any costs they might incur

Keep it practical, clear, and reassuring. Use {config['target_lang']}, Do not show pronunciation."""

    try:
        print(f"Getting advice in {lang}: {symptom}")
        response = model.generate_content(prompt)
        
        return jsonify({
            'advice': response.text
        })
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'{type(e).__name__}: {str(e)}'}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create index.html (Home page with language selection)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mendy - Medical Translator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header { text-align: center; margin-bottom: 30px; }
        .avatar {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
        }
        h1 { color: #333; font-size: 24px; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 16px; margin-bottom: 30px; }
        .language-label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 15px;
            text-align: center;
            font-size: 14px;
        }
        .language-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin-bottom: 30px;
        }
        .lang-btn {
            padding: 15px 10px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            font-weight: 600;
            color: #666;
        }
        .lang-btn:hover { border-color: #667eea; transform: translateY(-2px); }
        .lang-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
        }
        .lang-flag { font-size: 24px; display: block; margin-bottom: 5px; }
        .action-buttons { display: none; }
        .action-buttons.active { display: block; animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .btn {
            width: 100%;
            padding: 18px;
            margin: 10px 0;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            display: block;
            text-align: center;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .btn-secondary { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        small { display: block; margin-top: 5px; font-weight: 400; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="avatar">🏥</div>
            <h1>Hi, I'm Mendy</h1>
            <p class="subtitle">Your Medical Translator</p>
        </div>
        
        <label class="language-label">Select Your Language / 选择语言 / اپنی زبان منتخب کریں / Paw wo kasa</label>
        <div class="language-buttons">
            <button class="lang-btn" onclick="selectLanguage('chinese')">
                <span class="lang-flag">🇨🇳</span>
                中文<br>Chinese
            </button>
            <button class="lang-btn" onclick="selectLanguage('urdu')">
                <span class="lang-flag">🇵🇰</span>
                اردو<br>Urdu
            </button>
            <button class="lang-btn" onclick="selectLanguage('twi')">
                <span class="lang-flag">🇬🇭</span>
                Twi<br>Akan
            </button>
        </div>
        
        <div id="chinese-actions" class="action-buttons">
            <a href="/realtime?lang=chinese" class="btn">
                🔄 I'm at the hospital and need realtime translation<br>
                <small>我在医院需要实时翻译</small>
            </a>
            <a href="/preparation?lang=chinese" class="btn btn-secondary">
                📋 I need to go to the hospital<br>
                <small>我需要去医院</small>
            </a>
        </div>
        
        <div id="urdu-actions" class="action-buttons">
            <a href="/realtime?lang=urdu" class="btn">
                🔄 I'm at the hospital and need realtime translation<br>
                <small>مجھے ہسپتال میں فوری ترجمہ کی ضرورت ہے</small>
            </a>
            <a href="/preparation?lang=urdu" class="btn btn-secondary">
                📋 I need to go to the hospital<br>
                <small>مجھے ہسپتال جانے کی ضرورت ہے</small>
            </a>
        </div>
        
        <div id="twi-actions" class="action-buttons">
            <a href="/realtime?lang=twi" class="btn">
                🔄 I'm at the hospital and need realtime translation<br>
                <small>Mewɔ ayaresabea na mehia nkyerɛaseɛ ntɛm</small>
            </a>
            <a href="/preparation?lang=twi" class="btn btn-secondary">
                📋 I need to go to the hospital<br>
                <small>Ɛsɛ sɛ mekɔ ayaresabea</small>
            </a>
        </div>
    </div>
    
    <script>
        function selectLanguage(lang) {
            document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
            event.target.closest('.lang-btn').classList.add('active');
            document.querySelectorAll('.action-buttons').forEach(div => div.classList.remove('active'));
            document.getElementById(lang + '-actions').classList.add('active');
        }
    </script>
</body>
</html>''')
    
    # Create realtime.html (Translation page)
    with open('templates/realtime.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.realtime_title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header { text-align: center; margin-bottom: 30px; }
        h1 { color: #333; font-size: 24px; margin-bottom: 10px; }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
        }
        textarea:focus { outline: none; border-color: #667eea; }
        .quick-questions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .quick-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover { background: #e0e0e0; }
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            display: none;
        }
        .result-box.active { display: block; animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-section { margin-bottom: 20px; }
        .result-section:last-child { margin-bottom: 0; }
        .result-title {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .result-content {
            color: #333;
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .back-btn {
            background: #6c757d;
            text-decoration: none;
            display: block;
            text-align: center;
            margin-top: 20px;
        }
        .back-btn:hover { background: #5a6268; }
        .loading { text-align: center; color: #667eea; padding: 20px; display: none; }
        .loading.active { display: block; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error { background: #fee; color: #c33; padding: 15px; border-radius: 8px; margin-top: 10px; display: none; }
        .error.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ config.realtime_title }}</h1>
        </div>
        
        <textarea id="inputText" placeholder="{{ config.input_placeholder }}"></textarea>
        <div class="quick-questions">
            <button class="quick-btn" onclick="setQuickQuestion('Do you have insurance?')">Do you have insurance?</button>
            <button class="quick-btn" onclick="setQuickQuestion('What brings you in today?')">What brings you in?</button>
            <button class="quick-btn" onclick="setQuickQuestion('Any allergies?')">Any allergies?</button>
            <button class="quick-btn" onclick="setQuickQuestion('When did the symptoms start?')">When did symptoms start?</button>
        </div>
        <button class="btn" id="translateBtn" onclick="translateText()">{{ config.translate_btn }}</button>
        
        <div class="error" id="errorBox"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            {{ config.translating }}
        </div>
        
        <div id="resultBox" class="result-box">
            <div class="result-section">
                <div class="result-title">📝 Translation</div>
                <div class="result-content" id="translation"></div>
            </div>
            <div class="result-section">
                <div class="result-title">💡 Context</div>
                <div class="result-content" id="context"></div>
            </div>
            <div class="result-section">
                <div class="result-title">💬 Possible Responses</div>
                <div class="result-content" id="responses"></div>
            </div>
        </div>
        
        <a href="/" class="btn back-btn">{{ config.back_btn }}</a>
    </div>
    
    <script>
        const currentLanguage = "{{ language }}";
        
        function setQuickQuestion(text) {
            document.getElementById('inputText').value = text;
        }
        
        async function translateText() {
            const text = document.getElementById('inputText').value;
            if (!text.trim()) {
                showError('Please enter some text to translate!');
                return;
            }
            
            const btn = document.getElementById('translateBtn');
            btn.disabled = true;
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('resultBox').classList.remove('active');
            document.getElementById('errorBox').classList.remove('active');
            
            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, language: currentLanguage})
                });
                
                if (!response.ok) throw new Error('Translation failed');
                
                const data = await response.json();
                
                document.getElementById('translation').textContent = data.translation;
                document.getElementById('context').textContent = data.context;
                document.getElementById('responses').textContent = data.responses;
                
                document.getElementById('loading').classList.remove('active');
                document.getElementById('resultBox').classList.add('active');
            } catch (error) {
                document.getElementById('loading').classList.remove('active');
                showError('Translation error. Please check your API key and try again.');
            } finally {
                btn.disabled = false;
            }
        }
        
        function showError(message) {
            const errorBox = document.getElementById('errorBox');
            errorBox.textContent = message;
            errorBox.classList.add('active');
        }
    </script>
</body>
</html>''')
    
# Create preparation.html (Hospital preparation page)
    with open('templates/preparation.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.preparation_title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header { text-align: center; margin-bottom: 30px; }
        h1 { color: #333; font-size: 24px; margin-bottom: 10px; }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
        }
        textarea:focus { outline: none; border-color: #667eea; }
        .quick-questions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .quick-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover { background: #e0e0e0; }
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            display: none;
        }
        .result-box.active { display: block; animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-content {
            color: #333;
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .back-btn {
            background: #6c757d;
            text-decoration: none;
            display: block;
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            color: white;
            border-radius: 12px;
            font-weight: 600;
        }
        .back-btn:hover { background: #5a6268; }
        .loading { text-align: center; color: #667eea; padding: 20px; display: none; }
        .loading.active { display: block; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error { background: #fee; color: #c33; padding: 15px; border-radius: 8px; margin-top: 10px; display: none; }
        .error.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ config.preparation_title }}</h1>
        </div>
        
        <textarea id="symptomText" placeholder="{{ config.symptom_placeholder }}"></textarea>
        <div class="quick-questions">
            {% if language == 'chinese' %}
            <button class="quick-btn" onclick="setSymptom('我发烧了')">我发烧了 Fever</button>
            <button class="quick-btn" onclick="setSymptom('我肚子疼')">我肚子疼 Stomach pain</button>
            <button class="quick-btn" onclick="setSymptom('我头痛')">我头痛 Headache</button>
            <button class="quick-btn" onclick="setSymptom('我咳嗽')">我咳嗽 Cough</button>
            {% elif language == 'urdu' %}
            <button class="quick-btn" onclick="setSymptom('مجھے بخار ہے')">مجھے بخار ہے Fever</button>
            <button class="quick-btn" onclick="setSymptom('میرے پیٹ میں درد ہے')">میرے پیٹ میں درد ہے Stomach pain</button>
            <button class="quick-btn" onclick="setSymptom('میرے سر میں درد ہے')">میرے سر میں درد ہے Headache</button>
            <button class="quick-btn" onclick="setSymptom('مجھے کھانسی ہے')">مجھے کھانسی ہے Cough</button>
            {% elif language == 'twi' %}
            <button class="quick-btn" onclick="setSymptom('Mewɔ atiridiì')">Mewɔ atiridiì Fever</button>
            <button class="quick-btn" onclick="setSymptom('Me yam ye me ya')">Me yam ye me ya Stomach pain</button>
            <button class="quick-btn" onclick="setSymptom('Me tire ye me ya')">Me tire ye me ya Headache</button>
            <button class="quick-btn" onclick="setSymptom('Meworɔ')">Meworɔ Cough</button>
            {% endif %}
        </div>
        <button class="btn" id="adviceBtn" onclick="getAdvice()">{{ config.advice_btn }}</button>
        
        <div class="error" id="errorBox"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            {{ config.analyzing }}
        </div>
        
        <div id="adviceBox" class="result-box">
            <div class="result-content" id="advice"></div>
        </div>
        
        <a href="/" class="btn back-btn">{{ config.back_btn }}</a>
    </div>
    
    <script>
        const currentLanguage = "{{ language }}";
        
        function setSymptom(text) {
            document.getElementById('symptomText').value = text;
        }
        
        async function getAdvice() {
            const text = document.getElementById('symptomText').value;
            if (!text.trim()) {
                showError('Please describe your symptoms!');
                return;
            }
            
            const btn = document.getElementById('adviceBtn');
            btn.disabled = true;
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('adviceBox').classList.remove('active');
            document.getElementById('errorBox').classList.remove('active');
            
            try {
                const response = await fetch('/api/advice', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symptom: text, language: currentLanguage})
                });
                
                if (!response.ok) throw new Error('Advice request failed');
                
                const data = await response.json();
                
                document.getElementById('advice').innerHTML = marked.parse(data.advice);
                document.getElementById('loading').classList.remove('active');
                document.getElementById('adviceBox').classList.add('active');
            } catch (error) {
                document.getElementById('loading').classList.remove('active');
                showError('Error getting advice. Please check your API key and try again.');
            } finally {
                btn.disabled = false;
            }
        }
        
        function showError(message) {
            const errorBox = document.getElementById('errorBox');
            errorBox.textContent = message;
            errorBox.classList.add('active');
        }
    </script>
</body>
</html>''')
        
    print("🏥 Starting Mendy Medical Translator...")
    print("📱 Open http://localhost:5001 in your browser")
    print("✅ Templates created successfully!")
    app.run(debug=True, host='0.0.0.0', port=5001)