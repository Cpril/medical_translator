"""
Medical Translator Mobile App - Mendy
A bilingual English-Chinese medical translation assistant

Dependencies:
pip install flask openai python-dotenv

Setup:
1. Create a .env file with: OPENAI_API_KEY=your_key_here
2. Run: python app.py
3. Open browser to http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
# client = OpenAI(api_key=os.getenv('GEMINI_API_KEY'))
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️ Gemini API key not found. Please set GEMINI_API_KEY as an environment variable.")
model = genai.GenerativeModel("gemini-flash-latest")

for m in genai.list_models():
    print(m.name, m.supported_generation_methods)

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for realtime translation page
@app.route('/realtime')
def realtime():
    return render_template('realtime.html')

# Route for hospital preparation page
@app.route('/preparation')
def preparation():
    return render_template('preparation.html')

# Translation API endpoint
@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    prompt = f"""You are a medical translator helping Chinese-speaking patients at an English-speaking hospital.

Translate this English medical phrase to Chinese and provide helpful context:
"{text}"

Provide your response in this exact format:

TRANSLATION:
[Direct word-to-word Chinese translation]

CONTEXT:
[In Chinese: Explain the situation, where they likely are, and what the staff is asking for]

RESPONSES:
[In Chinese: Provide 2-3 possible responses they can give, with English translations]"""

    try:
        print(f"Sending request to Gemini for: {text}")
        response = model.generate_content(prompt)
        print(f"Got response from Gemini")
        content = response.text
        
        # DEBUG: Print the raw response
        print("=" * 50)
        print("RAW GEMINI RESPONSE:")
        print(content)
        print("=" * 50)
        
        # Try to parse, but provide fallback
        try:
            parts = content.split('TRANSLATION:')[1].split('CONTEXT:')
            translation = parts[0].strip()
            
            parts2 = parts[1].split('RESPONSES:')
            context = parts2[0].strip()
            responses = parts2[1].strip()
        except (IndexError, AttributeError) as parse_error:
            # If parsing fails, return raw content
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
    
    if not symptom:
        return jsonify({'error': 'No symptom provided'}), 400
    
    prompt = f"""You are a medical advisor helping a Chinese-speaking person understand what type of hospital care they need.

The patient says: "{symptom}"

Provide advice in Chinese about:
1. What type of doctor/department they should see
2. Whether they need an appointment or can walk in
3. What to expect during the visit
4. What to bring (insurance, ID, etc.)

Keep it practical, clear, and reassuring. Use simple Chinese."""

    try:
        response = model.generate_content(prompt)
        
        return jsonify({
            'advice': response.text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create index.html
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mendy - 医疗翻译助手</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
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
        
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 16px;
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
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        small {
            display: block;
            margin-top: 5px;
            font-weight: 400;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="avatar">🏥</div>
            <h1>Hi, I'm Mendy</h1>
            <p class="subtitle">你的医疗翻译助手<br>Your Medical Translator</p>
        </div>
        <a href="/realtime" class="btn">
            🔄 I'm at the hospital and need realtime translation<br>
            <small>我在医院需要实时翻译</small>
        </a>
        <a href="/preparation" class="btn btn-secondary">
            📋 I need to go to the hospital<br>
            <small>我需要去医院</small>
        </a>
    </div>
</body>
</html>''')
    
    # Create realtime.html
    with open('templates/realtime.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>实时翻译 - Mendy</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
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
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .quick-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-btn:hover {
            background: #e0e0e0;
        }
        
        .translate-btn {
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
        
        .translate-btn:hover {
            opacity: 0.9;
        }
        
        .translate-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            display: none;
        }
        
        .result-box.active {
            display: block;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .result-section {
            margin-bottom: 20px;
        }
        
        .result-section:last-child {
            margin-bottom: 0;
        }
        
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
            width: 100%;
            padding: 15px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            text-decoration: none;
            display: block;
            text-align: center;
        }
        
        .back-btn:hover {
            background: #5a6268;
        }
        
        .loading {
            text-align: center;
            color: #667eea;
            padding: 20px;
            display: none;
        }
        
        .loading.active {
            display: block;
        }
        
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
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }
        
        .error.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>实时翻译 Realtime Translation</h1>
        </div>
        
        <div class="input-group">
            <textarea id="inputText" placeholder="Type or paste text here... 在此输入或粘贴文字..."></textarea>
            <div class="quick-questions">
                <button class="quick-btn" onclick="setQuickQuestion('Do you have insurance?')">Do you have insurance?</button>
                <button class="quick-btn" onclick="setQuickQuestion('What brings you in today?')">What brings you in?</button>
                <button class="quick-btn" onclick="setQuickQuestion('Any allergies?')">Any allergies?</button>
                <button class="quick-btn" onclick="setQuickQuestion('When did the symptoms start?')">When did symptoms start?</button>
            </div>
            <button class="translate-btn" id="translateBtn" onclick="translateText()">翻译 Translate</button>
        </div>
        
        <div class="error" id="errorBox"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            翻译中... Translating...
        </div>
        
        <div id="resultBox" class="result-box">
            <div class="result-section">
                <div class="result-title">📝 逐字翻译 Word-to-Word Translation</div>
                <div class="result-content" id="translation"></div>
            </div>
            <div class="result-section">
                <div class="result-title">💡 解释和情境 Explanation & Context</div>
                <div class="result-content" id="context"></div>
            </div>
            <div class="result-section">
                <div class="result-title">💬 可能的回答 Possible Responses</div>
                <div class="result-content" id="responses"></div>
            </div>
        </div>
        
        <a href="/" class="back-btn">返回首页 Back to Home</a>
    </div>
    
    <script>
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
                    body: JSON.stringify({text: text})
                });
                
                if (!response.ok) {
                    throw new Error('Translation failed');
                }
                
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
    
    # Create preparation.html
    with open('templates/preparation.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>就医准备 - Mendy</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
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
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .quick-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-btn:hover {
            background: #e0e0e0;
        }
        
        .translate-btn {
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
        
        .translate-btn:hover {
            opacity: 0.9;
        }
        
        .translate-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            display: none;
        }
        
        .result-box.active {
            display: block;
            animation: fadeIn 0.3s ease-in;
        }
        
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
            width: 100%;
            padding: 15px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            text-decoration: none;
            display: block;
            text-align: center;
        }
        
        .back-btn:hover {
            background: #5a6268;
        }
        
        .loading {
            text-align: center;
            color: #667eea;
            padding: 20px;
            display: none;
        }
        
        .loading.active {
            display: block;
        }
        
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
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }
        
        .error.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>就医准备 Hospital Preparation</h1>
        </div>
        
        <div class="input-group">
            <textarea id="symptomText" placeholder="Describe your symptoms... 描述您的症状..."></textarea>
            <div class="quick-questions">
                <button class="quick-btn" onclick="setSymptom('我发烧了')">我发烧了 Fever</button>
                <button class="quick-btn" onclick="setSymptom('我肚子疼')">我肚子疼 Stomach pain</button>
                <button class="quick-btn" onclick="setSymptom('我头痛')">我头痛 Headache</button>
                <button class="quick-btn" onclick="setSymptom('我咳嗽')">我咳嗽 Cough</button>
            </div>
            <button class="translate-btn" id="adviceBtn" onclick="getAdvice()">获取建议 Get Advice</button>
        </div>
        
        <div class="error" id="errorBox"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            分析中... Analyzing...
        </div>
        
        <div id="adviceBox" class="result-box">
            <div class="result-content" id="advice"></div>
        </div>
        
        <a href="/" class="back-btn">返回首页 Back to Home</a>
    </div>
    
    <script>
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
                    body: JSON.stringify({symptom: text})
                });
                
                if (!response.ok) {
                    throw new Error('Advice request failed');
                }
                
                const data = await response.json();
                
                document.getElementById('advice').textContent = data.advice;
                
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
    print("📱 Open http://localhost:5000 in your browser")
    print("✅ Templates created successfully!")
    app.run(debug=True, host='0.0.0.0', port=5000)