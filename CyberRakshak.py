# -----------------------------------------------------
# TEAM : SGVP International School
# -----------------------------------------------------


import hashlib
import random
import string
import urllib.request
import json
import os
import requests 
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

SIGHTENGINE_API_USER = "812724024"
SIGHTENGINE_API_SECRET = "H6WF6yHi2PtKiCYcMmvcM6GLrsfebGM6"

def make_password(length=16, use_upper=True, use_numbers=True, use_symbols=True):
    lower_chars = string.ascii_lowercase
    upper_chars = string.ascii_uppercase
    digit_chars = string.digits
    symbol_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    all_chars = lower_chars
    final_password = []

    if use_upper:
        all_chars += upper_chars
        final_password.append(random.choice(upper_chars))
    
    if use_numbers:
        all_chars += digit_chars
        final_password.append(random.choice(digit_chars))
        
    if use_symbols:
        all_chars += symbol_chars
        final_password.append(random.choice(symbol_chars))
    
    count_needed = length - len(final_password)
    for i in range(count_needed):
        final_password.append(random.choice(all_chars))
    
    random.shuffle(final_password)
    
    return "".join(final_password)

def get_strength(password):
    score = 0
    if not password: return 0, "", "bg-gray-800", "0%"
    
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    
    if any(c.isupper() for c in password): score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1

    if score < 3: return score, "Weak", "bg-red-500", "25%"
    elif score < 5: return score, "Medium", "bg-yellow-400", "50%"
    elif score < 6: return score, "Strong", "bg-cyan-400", "75%"
    else: return score, "Very Strong", "bg-emerald-400", "100%"

def check_database(password):
    encoded_pw = password.encode('utf-8')
    sha1_hash = hashlib.sha1(encoded_pw).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]
    
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    headers = {'User-Agent': 'SchoolProjectApp'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8')
        
        lines = data.splitlines()
        for line in lines:
            parts = line.split(':')
            if parts[0] == suffix:
                return int(parts[1])
        return 0
    except:
        return -1

def detect_ai_image(image_bytes):
    if not SIGHTENGINE_API_USER or not SIGHTENGINE_API_SECRET:
        import time
        time.sleep(1.5)
        
        mock_score = random.uniform(85, 99)
        mock_label = random.choice(["AI Generated", "Human / Real"])
        
        return {
            "label": mock_label,
            "score": round(mock_score, 1),
            "is_demo": True,
            "provider": "Sightengine (Simulated)"
        }

    params = {
        'models': 'genai',
        'api_user': SIGHTENGINE_API_USER,
        'api_secret': SIGHTENGINE_API_SECRET
    }
    files = {'media': image_bytes}

    try:
        r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
        output = r.json()
        
        if output.get('status') == 'success':
            ai_score = output['type']['ai_generated']
            
            if ai_score > 0.5:
                label = "AI Generated"
                confidence = ai_score * 100
            else:
                label = "Human / Real"
                confidence = (1 - ai_score) * 100
                
            return {
                "label": label,
                "score": round(confidence, 1),
                "is_demo": False
            }
        else:
            return {"error": f"API Error: {output.get('error', {}).get('message', 'Unknown error')}"}
            
    except Exception as e:
        return {"error": f"Connection Failed: {str(e)}"}

@app.route('/')
def home():
    return render_template_string(home_html)

@app.route('/toolkit')
def toolkit():
    return render_template_string(toolkit_html)

@app.route('/risk/finance')
def risk_finance():
    content = """
    <div class="space-y-6">
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
            <h3 class="text-white font-bold mb-2 text-lg">⚠️ The UPI QR Scam</h3>
            <p class="text-gray-400 text-sm">Scammers send a QR code on WhatsApp saying "Scan this to receive prize money".</p>
            <p class="text-red-400 font-bold text-sm mt-2">REALITY: Scanning a QR code is ONLY for sending money, never for receiving it.</p>
        </div>
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
            <h3 class="text-white font-bold mb-2 text-lg">🔗 Recent Trends</h3>
            <ul class="list-disc list-inside text-gray-400 text-sm space-y-2">
                <li>Fake 'Electricity Bill' SMS messages containing phishing links.</li>
                <li>'Part-time Job' offers on Telegram demanding a security deposit.</li>
                <li>Credit Card reward point expiry links.</li>
            </ul>
        </div>
        <div class="p-4 bg-green-900/20 border border-green-500/30 rounded-xl">
            <h3 class="text-green-400 font-bold mb-2">🛡️ Safety Tips</h3>
            <ul class="text-gray-300 text-sm space-y-2">
                <li>✅ Never share your UPI PIN with anyone.</li>
                <li>✅ Verify the VPA (UPI ID) before paying.</li>
                <li>✅ If you lose money, call 1930 immediately.</li>
            </ul>
        </div>
    </div>
    """
    return render_template_string(article_html, title="Financial Fraud", icon="💸", color="red", content=content)

@app.route('/risk/ai')
def risk_ai():
    content = """
    <div class="space-y-6">
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
            <h3 class="text-white font-bold mb-2 text-lg">🤖 Voice Cloning</h3>
            <p class="text-gray-400 text-sm">AI can now clone your voice from just 3 seconds of audio. Scammers use this to call your parents pretending to be you in an emergency.</p>
        </div>
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
            <h3 class="text-white font-bold mb-2 text-lg">🎭 Deepfake Video Calls</h3>
            <p class="text-gray-400 text-sm">Attackers use AI face-swapping in video calls to impersonate friends or officials. They might ask for urgent money transfers.</p>
        </div>
        <div class="p-4 bg-green-900/20 border border-green-500/30 rounded-xl">
            <h3 class="text-green-400 font-bold mb-2">🛡️ Safety Tips</h3>
            <ul class="text-gray-300 text-sm space-y-2">
                <li>✅ Establish a 'Secret Code Word' with your family.</li>
                <li>✅ Ask personal questions only they would know.</li>
                <li>✅ Use our AI Scanner tool to check suspicious images.</li>
            </ul>
        </div>
    </div>
    """
    return render_template_string(article_html, title="AI Deepfakes", icon="🤖", color="blue", content=content)

@app.route('/risk/arrest')
def risk_arrest():
    content = """
    <div class="space-y-6">
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
            <h3 class="text-white font-bold mb-2 text-lg">👮 What is 'Digital Arrest'?</h3>
            <p class="text-gray-400 text-sm">Criminals pose as Police, CBI, or Customs officers via video call (Skype/WhatsApp). They claim a parcel with drugs was found in your name and keep you on the call for hours (digital arrest) until you pay.</p>
        </div>
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
            <h3 class="text-white font-bold mb-2 text-lg">❌ The Law</h3>
            <p class="text-red-400 font-bold text-sm">Indian Police DO NOT conduct investigations or arrests via Video Call. There is no legal term called 'Digital Arrest'.</p>
        </div>
        <div class="p-4 bg-green-900/20 border border-green-500/30 rounded-xl">
            <h3 class="text-green-400 font-bold mb-2">🛡️ Safety Tips</h3>
            <ul class="text-gray-300 text-sm space-y-2">
                <li>✅ Do not panic. Disconnect the call.</li>
                <li>✅ Do not share your screen or bank details.</li>
                <li>✅ Report the number to cybercrime.gov.in.</li>
            </ul>
        </div>
    </div>
    """
    return render_template_string(article_html, title="Digital Arrest", icon="👮", color="yellow", content=content)

@app.route('/api/generate', methods=['POST'])
def generate_route():
    data = request.json
    pw = make_password(
        length=int(data.get('length', 16)),
        use_upper=data.get('upper', True),
        use_numbers=data.get('numbers', True),
        use_symbols=data.get('symbols', True)
    )
    return jsonify({'password': pw})

@app.route('/api/strength', methods=['POST'])
def strength_route():
    data = request.json
    s, t, c, w = get_strength(data.get('password', ''))
    return jsonify({'text': t, 'color': c, 'width': w})

@app.route('/api/pwned', methods=['POST'])
def pwned_route():
    data = request.json
    c = check_database(data.get('password', ''))
    return jsonify({'count': c})

@app.route('/api/scan-image', methods=['POST'])
def scan_image_route():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    try:
        image_bytes = file.read()
        result = detect_ai_image(image_bytes)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

article_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{ title }} - CyberRakshak</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        body { font-family: 'Outfit', sans-serif; background-color: #000; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none;  scrollbar-width: none; }
    </style>
</head>
<body class="bg-black text-white h-[100dvh] w-full flex justify-center overflow-hidden">
    <div class="w-full max-w-md h-full bg-gray-950 flex flex-col relative shadow-2xl border-x border-gray-900">
        
        <!-- Header -->
        <header class="p-5 bg-gray-900/80 backdrop-blur-md sticky top-0 z-20 border-b border-gray-800 flex items-center gap-4 shrink-0">
            <a href="/" class="p-2 rounded-full hover:bg-gray-800 transition-colors">
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
            </a>
            <h1 class="text-xl font-bold text-white">{{ title }}</h1>
        </header>

        <!-- Content -->
        <main class="flex-1 overflow-y-auto no-scrollbar p-6 pb-12">
            <div class="flex items-center gap-4 mb-6">
                <div class="w-16 h-16 bg-{{ color }}-500/20 rounded-2xl flex items-center justify-center text-4xl border border-{{ color }}-500/30">
                    {{ icon }}
                </div>
                <div>
                    <p class="text-xs text-{{ color }}-400 font-bold uppercase tracking-wider">AWARENESS GUIDE</p>
                    <h2 class="text-2xl font-bold text-white">{{ title }}</h2>
                </div>
            </div>
            
            <div class="prose prose-invert prose-sm">
                {{ content|safe }}
            </div>
            
            <a href="/toolkit" class="block w-full text-center bg-gray-800 hover:bg-gray-700 text-white font-bold py-4 rounded-xl mt-8 transition-colors">
                Open Security Tool
            </a>
        </main>
    </div>
</body>
</html>
"""

home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CyberRakshak</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        body { font-family: 'Outfit', sans-serif; background-color: #000; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none;  scrollbar-width: none; }
    </style>
</head>
<body class="bg-black text-white h-[100dvh] w-full flex justify-center overflow-hidden">

    <!-- Mobile Frame -->
    <div class="w-full max-w-md h-full bg-gray-950 flex flex-col relative shadow-2xl border-x border-gray-900">
        
        <!-- Status Bar Area (Simulated) -->
        <div class="h-6 w-full bg-gray-950 shrink-0"></div>

        <!-- Header -->
        <div class="px-6 py-4 flex justify-between items-center shrink-0">
            <div>
                <h1 class="text-4xl font-bold text-white tracking-tight">CyberRakshak</h1>
            </div>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto no-scrollbar px-6 pb-24">
            
            <!-- Hero Card -->
            <div class="mt-4 p-6 bg-purple-600 rounded-3xl relative overflow-hidden shadow-lg shadow-purple-900/40">
                <div class="relative z-10">
                    <h2 class="text-3xl font-bold mb-2">Secure Your<br>Digital Life.</h2>
                    <p class="text-purple-100 text-sm mb-6 opacity-90">UPI Fraud. Deepfakes. Identity Theft. Stay ahead of the threats.</p>
                    <a href="/toolkit" class="inline-block bg-white text-purple-700 px-6 py-3 rounded-full font-bold text-sm shadow-md active:scale-95 transition-transform">Use Tools</a>
                </div>
                <!-- Decorative Circle -->
                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-purple-500 rounded-full opacity-50"></div>
            </div>

            <!-- Section Title -->
            <h3 class="text-lg font-bold text-white mt-8 mb-4">Risk Awareness Feed</h3>

            <!-- Risk Cards (Clickable Links) -->
            <div class="space-y-4">
                <a href="/risk/finance" class="block p-5 bg-gray-900 rounded-2xl border border-gray-800 flex gap-4 items-center hover:bg-gray-800 transition-colors active:scale-95 transform duration-150">
                    <div class="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">💸</div>
                    <div>
                        <h4 class="font-bold text-white flex items-center gap-2">Financial Fraud <span class="text-xs text-red-400 bg-red-900/30 px-2 py-0.5 rounded">High Risk</span></h4>
                        <p class="text-xs text-gray-400 mt-1">UPI scams & QR codes drain accounts. Read more &rarr;</p>
                    </div>
                </a>

                <a href="/risk/ai" class="block p-5 bg-gray-900 rounded-2xl border border-gray-800 flex gap-4 items-center hover:bg-gray-800 transition-colors active:scale-95 transform duration-150">
                    <div class="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">🤖</div>
                    <div>
                        <h4 class="font-bold text-white">AI Deepfakes</h4>
                        <p class="text-xs text-gray-400 mt-1">Scammers use AI voice to impersonate family. Read more &rarr;</p>
                    </div>
                </a>

                <a href="/risk/arrest" class="block p-5 bg-gray-900 rounded-2xl border border-gray-800 flex gap-4 items-center hover:bg-gray-800 transition-colors active:scale-95 transform duration-150">
                    <div class="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">👮</div>
                    <div>
                        <h4 class="font-bold text-white">Digital Arrest</h4>
                        <p class="text-xs text-gray-400 mt-1">Fake police video calls threatening jail. Read more &rarr;</p>
                    </div>
                </a>
            </div>
            
            <p class="text-center text-gray-600 text-xs mt-8">SGVP International School</p>
        </div>

    </div>
</body>
</html>
"""

toolkit_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CyberRakshak Tool</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700&display=swap');
        body { font-family: 'Outfit', sans-serif; background-color: #000; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        
        .loader { border: 3px solid #333; border-radius: 50%; border-top: 3px solid #a855f7; width: 20px; height: 20px; -webkit-animation: spin 1s linear infinite; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Bottom Nav Styling */
        .nav-item.active svg { color: #a855f7; }
        .nav-item.active span { color: #a855f7; }
        .nav-item.active { background-color: rgba(168, 85, 247, 0.1); }
        
        .pb-safe { padding-bottom: env(safe-area-inset-bottom); }
    </style>
</head>
<body class="bg-black text-white h-[100dvh] w-full flex justify-center overflow-hidden">

    <div class="w-full max-w-md h-full bg-gray-950 flex flex-col relative shadow-2xl border-x border-gray-900">
        
        <header class="p-5 bg-gray-900/80 backdrop-blur-md sticky top-0 z-20 border-b border-gray-800 flex justify-between items-center shrink-0">
            <h1 class="text-xl font-bold text-white">CyberRakshak</h1>
            <a href="/" class="text-xs font-bold text-gray-500 bg-gray-800 px-3 py-1.5 rounded-full">HOME</a>
        </header>

        <main class="flex-1 overflow-y-auto no-scrollbar p-5 pb-32">
            
            <div id="quiz-panel" class="tab-panel">
                <h2 class="text-2xl font-bold text-white mb-6">Safety Quiz</h2>
                <div id="quiz-content" class="space-y-4"></div>
                <div id="quiz-feedback" class="mt-4 hidden p-5 rounded-2xl bg-gray-900 border border-gray-800"></div>
                <button id="quiz-next" onclick="nextQuestion()" class="mt-6 w-full py-4 bg-purple-600 text-white rounded-xl font-bold active:scale-95 transition-transform hidden">Next Question →</button>
            </div>

            <div id="detect-panel" class="tab-panel hidden space-y-6">
                <h2 class="text-2xl font-bold text-white">AI Scanner</h2>
                <p class="text-sm text-gray-400">Detect Deepfakes & AI Images</p>
                
                <div class="border-2 border-dashed border-gray-800 rounded-3xl h-48 flex flex-col items-center justify-center hover:border-blue-500 transition-colors bg-gray-900/50 cursor-pointer" id="drop-zone" onclick="document.getElementById('image-upload').click()">
                    <div class="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center mb-3">
                        <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    <p class="text-sm text-gray-400">Tap to upload image</p>
                    <input type="file" id="image-upload" accept="image/*" class="hidden" onchange="handleImageUpload()">
                </div>

                <div id="scan-area" class="hidden space-y-4">
                    <div class="flex items-center gap-4 bg-gray-900 p-3 rounded-xl border border-gray-800">
                        <img id="image-preview" class="w-12 h-12 object-cover rounded-lg bg-black" />
                        <div class="flex-1 min-w-0">
                            <p class="text-sm text-white font-medium truncate" id="file-name">filename.jpg</p>
                            <p class="text-xs text-gray-500">Ready</p>
                        </div>
                    </div>
                    
                    <button onclick="scanImage()" id="scan-btn" class="w-full py-4 bg-blue-600 text-white rounded-xl font-bold active:scale-95 transition-transform flex justify-center items-center gap-2">
                        <span>Scan Image</span>
                    </button>
                </div>

                <div id="scan-result" class="hidden p-5 rounded-2xl border border-gray-800"></div>
            </div>

            <div id="generator-panel" class="tab-panel hidden space-y-6">
                <h2 class="text-2xl font-bold text-white">Pass Generator</h2>
                <div class="flex space-x-2">
                    <input id="gen-out" readonly class="flex-1 p-4 bg-gray-900 border border-gray-800 rounded-xl text-green-400 font-mono text-lg focus:outline-none" placeholder="...">
                    <button onclick="copyToClipboard()" class="p-4 bg-gray-800 text-white rounded-xl font-bold active:scale-95 transition-transform">Copy</button>
                </div>
                <div class="grid grid-cols-2 gap-3 text-sm font-medium">
                    <label class="flex items-center gap-3 p-4 bg-gray-900 rounded-xl"><input type="checkbox" id="use-upper" checked class="w-5 h-5 rounded border-gray-700 bg-black text-green-600"> A-Z</label>
                    <label class="flex items-center gap-3 p-4 bg-gray-900 rounded-xl"><input type="checkbox" id="use-numbers" checked class="w-5 h-5 rounded border-gray-700 bg-black text-green-600"> 0-9</label>
                    <label class="flex items-center gap-3 p-4 bg-gray-900 rounded-xl"><input type="checkbox" id="use-symbols" checked class="w-5 h-5 rounded border-gray-700 bg-black text-green-600"> @#$</label>
                    <label class="flex items-center gap-3 p-4 bg-gray-900 rounded-xl"><span class="text-gray-500">Len:</span><input type="number" id="gen-len" value="16" min="8" max="32" class="bg-transparent w-full text-center text-white focus:outline-none font-bold"></label>
                </div>
                <button onclick="generatePassword()" class="w-full py-4 bg-green-600 text-white rounded-xl font-bold active:scale-95 transition-transform mt-2">Generate</button>
            </div>

            <div id="meter-panel" class="tab-panel hidden space-y-6">
                <h2 class="text-2xl font-bold text-white">Password Strength meter</h2>
                <div class="relative">
                    <input id="meter-in" type="password" class="w-full p-4 bg-gray-900 border border-gray-800 rounded-xl text-white focus:outline-none text-lg" placeholder="Type password...">
                </div>
                <div class="w-full bg-gray-900 rounded-full h-4 mt-4 overflow-hidden">
                    <div id="meter-bar" class="h-full rounded-full bg-gray-800 w-0 transition-all duration-500"></div>
                </div>
                <p id="meter-text" class="text-center font-bold text-lg mt-2 h-6"></p>

                <!-- SUGGESTIONS CHECKLIST -->
                <div class="bg-gray-900 rounded-xl p-4 border border-gray-800 mt-4">
                    <h3 class="text-gray-400 text-sm font-bold uppercase tracking-wider mb-3">Suggestions</h3>
                    <div class="grid grid-cols-1 gap-2 text-sm text-gray-500">
                        <div id="req-len8" class="flex items-center gap-2 transition-colors"><span class="w-2 h-2 rounded-full bg-gray-700"></span> At least 8 characters</div>
                        <div id="req-len12" class="flex items-center gap-2 transition-colors"><span class="w-2 h-2 rounded-full bg-gray-700"></span> 12+ characters (better)</div>
                        <div id="req-upper" class="flex items-center gap-2 transition-colors"><span class="w-2 h-2 rounded-full bg-gray-700"></span> Uppercase letter (A-Z)</div>
                        <div id="req-lower" class="flex items-center gap-2 transition-colors"><span class="w-2 h-2 rounded-full bg-gray-700"></span> Lowercase letter (a-z)</div>
                        <div id="req-num" class="flex items-center gap-2 transition-colors"><span class="w-2 h-2 rounded-full bg-gray-700"></span> Number (0-9)</div>
                        <div id="req-special" class="flex items-center gap-2 transition-colors"><span class="w-2 h-2 rounded-full bg-gray-700"></span> Special character (@#$)</div>
                    </div>
                </div>
            </div>

            <div id="pwned-panel" class="tab-panel hidden space-y-6">
                <h2 class="text-2xl font-bold text-white">Breach Detector</h2>
                <p class="text-sm text-gray-400">Has your password been leaked in a data breach?</p>
                <div class="flex space-x-2">
                    <input id="pwned-in" type="password" class="flex-1 p-4 bg-gray-900 border border-gray-800 rounded-xl text-white focus:outline-none" placeholder="Enter password...">
                    <button onclick="checkPwned()" class="p-4 bg-orange-600 text-white rounded-xl font-bold active:scale-95 transition-transform">Check</button>
                </div>
                <div id="pwned-result" class="hidden p-5 rounded-2xl mt-4"></div>
            </div>

            <div id="sos-panel" class="tab-panel hidden space-y-6">
                <h2 class="text-2xl font-bold text-red-500">Emergency SOS</h2>
                <div class="bg-red-900/20 border border-red-900/50 p-6 rounded-3xl text-center">
                    <div class="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center text-3xl mx-auto mb-4 animate-pulse">📞</div>
                    <h3 class="font-bold text-white text-xl">Cyber Helpline</h3>
                    <p class="text-red-200 text-sm mt-2 mb-6">Dial immediately if you lost money.</p>
                    <a href="tel:1930" class="block w-full bg-red-600 text-white font-bold py-4 rounded-xl active:scale-95 transition-transform">CALL 1930</a>
                </div>
                
                <h3 class="font-bold text-gray-400 mt-4 ml-1">Quick Guides</h3>
                <div class="p-4 bg-gray-900 rounded-2xl border border-gray-800 flex gap-4">
                    <div class="text-2xl">💰</div>
                    <div>
                        <h4 class="font-bold text-white">UPI Fraud</h4>
                        <p class="text-xs text-gray-400">Call 1930. Freeze Bank Account.</p>
                    </div>
                </div>
                <div class="p-4 bg-gray-900 rounded-2xl border border-gray-800 flex gap-4">
                    <div class="text-2xl">👮</div>
                    <div>
                        <h4 class="font-bold text-white">Fake Arrest</h4>
                        <p class="text-xs text-gray-400">Hang up. Do not pay. It's a scam.</p>
                    </div>
                </div>
            </div>

        </main>

        <nav class="absolute bottom-0 w-full bg-gray-950 border-t border-gray-900 flex overflow-x-auto pb-safe shrink-0">
            <button onclick="switchTab('quiz')" id="tab-quiz" class="nav-item flex-1 min-w-[70px] py-3 flex flex-col items-center justify-center gap-1 active transition-colors rounded-lg m-1">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span class="text-[10px] font-bold text-gray-500 uppercase">Quiz</span>
            </button>
            <button onclick="switchTab('detect')" id="tab-detect" class="nav-item flex-1 min-w-[70px] py-3 flex flex-col items-center justify-center gap-1 transition-colors rounded-lg m-1">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                <span class="text-[10px] font-bold text-gray-500 uppercase">Scan</span>
            </button>
            <button onclick="switchTab('generator')" id="tab-generator" class="nav-item flex-1 min-w-[70px] py-3 flex flex-col items-center justify-center gap-1 transition-colors rounded-lg m-1">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
                <span class="text-[10px] font-bold text-gray-500 uppercase">Gen</span>
            </button>
            <button onclick="switchTab('meter')" id="tab-meter" class="nav-item flex-1 min-w-[70px] py-3 flex flex-col items-center justify-center gap-1 transition-colors rounded-lg m-1">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                <span class="text-[10px] font-bold text-gray-500 uppercase">Meter</span>
            </button>
            <button onclick="switchTab('pwned')" id="tab-pwned" class="nav-item flex-1 min-w-[70px] py-3 flex flex-col items-center justify-center gap-1 transition-colors rounded-lg m-1">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                <span class="text-[10px] font-bold text-gray-500 uppercase">Check</span>
            </button>
            <button onclick="switchTab('sos')" id="tab-sos" class="nav-item flex-1 min-w-[70px] py-3 flex flex-col items-center justify-center gap-1 transition-colors rounded-lg m-1">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                <span class="text-[10px] font-bold text-gray-500 uppercase">SOS</span>
            </button>
        </nav>

    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-panel').forEach(el => el.classList.add('hidden'));
            document.getElementById(tabId + '-panel').classList.remove('hidden');
            
            document.querySelectorAll('.nav-item').forEach(el => {
                el.classList.remove('active');
            });

            document.getElementById('tab-' + tabId).classList.add('active');
        }

        switchTab('quiz');

        const questions = [
            {q: "SMS: 'SBI Account Blocked. Click link to update PAN'.", a: ["Click link", "Delete SMS", "Reply PAN", "Forward"], c: 1, expl: "Phishing! Banks never send KYC update links via SMS."},
            {q: "'Bank Manager' calls for OTP to cancel transaction.", a: ["Give OTP", "Ask Name", "Hang Up", "Wait"], c: 2, expl: "Scam. Bank employees NEVER ask for OTPs."},
            {q: "WhatsApp: 'You won ₹25 Lakhs KBC Lottery'.", a: ["Pay tax", "Call them", "Send Bank Details", "Block & Report"], c: 3, expl: "Fraud. Real lotteries don't message on WhatsApp."},
            {q: "Scan QR code to RECEIVE money?", a: ["Money comes", "Money goes", "Nothing", "Safe"], c: 1, expl: "Scam. You only scan QR to PAY money."},
            {q: "'Free Laptop Scheme - Pay ₹100 Fee'.", a: ["Pay ₹100", "Verify .gov.in", "Register", "Share"], c: 1, expl: "Fake. Government schemes are usually free."},
            {q: "Fake Income Tax site?", a: ["incometax.gov.in", ".nic.in", "tax-refund.com", "uidai.gov.in"], c: 2, expl: "Official sites use .gov.in. Commercial .com is suspicious."},
            {q: "Post Boarding Pass photo online?", a: ["Safe", "Dangerous", "Okay if cropped", "Yes"], c: 1, expl: "Dangerous. Barcodes contain private data."},
            {q: "Job asks for 'Security Deposit'.", a: ["Good job", "Standard", "Scam", "Government"], c: 2, expl: "Scam. Real jobs don't ask for money."},
            {q: "Lost phone with UPI. Priority?", a: ["Cry", "Block SIM", "Facebook post", "New phone"], c: 1, expl: "Block SIM immediately to stop OTPs."},
            {q: "Police video call for 'Digital Arrest'.", a: ["Pay", "Scam", "Real", "Lawyer"], c: 1, expl: "Scam. Police don't video call for arrests."}
        ];
        let qIdx = 0;
        let qScore = 0;

        function loadQuiz() {
            const content = document.getElementById('quiz-content');
            if(qIdx >= questions.length) {
                content.innerHTML = `<div class="text-center p-6 bg-gray-900 rounded-2xl border border-gray-800"><h3 class='text-purple-400 font-bold text-2xl'>Score: ${qScore}/${questions.length}</h3><button onclick="location.reload()" class="mt-4 text-sm text-gray-400 underline">Restart Quiz</button></div>`;
                document.getElementById('quiz-next').classList.add('hidden');
                return;
            }
            const q = questions[qIdx];
            let html = `<p class="font-medium text-lg text-white mb-4">Q${qIdx + 1}: ${q.q}</p><div class="grid gap-3">`;
            q.a.forEach((opt, i) => {
                html += `<button onclick="answer(${i})" class="quiz-opt w-full text-left p-4 bg-gray-900 active:bg-gray-800 border border-gray-800 rounded-xl text-gray-300 font-medium">${opt}</button>`;
            });
            html += `</div>`;
            content.innerHTML = html;
            document.getElementById('quiz-feedback').classList.add('hidden');
            document.getElementById('quiz-next').classList.add('hidden');
        }

        function answer(i) {
            const buttons = document.querySelectorAll('.quiz-opt');
            const q = questions[qIdx];
            
            buttons.forEach(btn => btn.disabled = true);
            
            buttons[q.c].classList.remove('bg-gray-900', 'active:bg-gray-800', 'border-gray-800');
            buttons[q.c].classList.add('bg-green-600', 'border-green-600', 'text-white');

            if (i === q.c) {
                qScore++;
                
                const feed = document.getElementById('quiz-feedback');
                feed.classList.remove('hidden');
                feed.innerHTML = `<span class="text-green-400 font-bold">Correct!</span> ${q.expl}`;
                feed.className = "mt-4 p-4 rounded-xl bg-green-900/20 border border-green-500/30 text-sm";
            } else {
                buttons[i].classList.remove('bg-gray-900', 'active:bg-gray-800', 'border-gray-800');
                buttons[i].classList.add('bg-red-600', 'border-red-600', 'text-white');
                
                const feed = document.getElementById('quiz-feedback');
                feed.classList.remove('hidden');
                feed.innerHTML = `<span class="text-red-400 font-bold">Wrong.</span> ${q.expl}`;
                feed.className = "mt-4 p-4 rounded-xl bg-red-900/20 border border-red-500/30 text-sm";
            }
            
            document.getElementById('quiz-next').classList.remove('hidden');
        }
        function nextQuestion() { qIdx++; loadQuiz(); }
        loadQuiz();

        function handleImageUpload() {
            const file = document.getElementById('image-upload').files[0];
            if (file) {
                document.getElementById('drop-zone').classList.add('hidden');
                document.getElementById('scan-area').classList.remove('hidden');
                document.getElementById('file-name').innerText = file.name;
                document.getElementById('image-preview').src = URL.createObjectURL(file);
                document.getElementById('scan-result').classList.add('hidden');
            }
        }

        async function scanImage() {
            const file = document.getElementById('image-upload').files[0];
            if (!file) return;

            const btn = document.getElementById('scan-btn');
            btn.innerHTML = '<div class="loader"></div> Scanning...';
            btn.disabled = true;

            const formData = new FormData();
            formData.append('image', file);

            try {
                const res = await fetch('/api/scan-image', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                
                const resultDiv = document.getElementById('scan-result');
                resultDiv.classList.remove('hidden');
                
                if (data.error) {
                    resultDiv.className = "p-5 rounded-2xl animate-fade-in border border-red-500/30 bg-red-900/20";
                    resultDiv.innerHTML = `<h3 class="text-red-400 font-bold">Error</h3><p class="text-gray-300 text-sm">${data.error}</p>`;
                } else {
                    const isArtificial = data.label.toLowerCase().includes('artificial') || data.label.toLowerCase().includes('ai') || data.label.toLowerCase().includes('fake');
                    const color = isArtificial ? "text-red-400" : "text-green-400";
                    const border = isArtificial ? "border-red-500/30 bg-red-900/20" : "border-green-500/30 bg-green-900/20";
                    
                    let disclaimer = "";
                    if (data.is_demo) {
                        disclaimer = "<p class='text-xs text-gray-500 mt-2 italic'>* Demo Mode: Result is simulated for school project demonstration as API key is missing.</p>";
                    }

                    resultDiv.className = `p-5 rounded-2xl animate-fade-in border ${border}`;
                    resultDiv.innerHTML = `<h3 class="${color} font-bold text-xl uppercase">${data.label}</h3>
                                           <p class="text-gray-200 mt-1">Confidence Score: <strong>${data.score}%</strong></p>
                                           ${disclaimer}`;
                }
            } catch (err) {
                console.error(err);
            } finally {
                btn.innerHTML = 'Scan Image';
                btn.disabled = false;
            }
        }

        async function generatePassword() {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    length: document.getElementById('gen-len').value,
                    upper: document.getElementById('use-upper').checked,
                    numbers: document.getElementById('use-numbers').checked,
                    symbols: document.getElementById('use-symbols').checked
                })
            });
            const data = await res.json();
            document.getElementById('gen-out').value = data.password;
        }

        function copyToClipboard() {
            const el = document.getElementById('gen-out');
            el.select();
            document.execCommand('copy');
        }

        document.getElementById('meter-in').addEventListener('input', async function() {
            const val = this.value;
            
            const setStatus = (id, valid) => {
                const el = document.getElementById(id);
                const dot = el.querySelector('span');
                if(valid) {
                    el.classList.remove('text-gray-500');
                    el.classList.add('text-green-400');
                    dot.classList.remove('bg-gray-700');
                    dot.classList.add('bg-green-500');
                } else {
                    el.classList.add('text-gray-500');
                    el.classList.remove('text-green-400');
                    dot.classList.add('bg-gray-700');
                    dot.classList.remove('bg-green-500');
                }
            };

            setStatus('req-len8', val.length >= 8);
            setStatus('req-len12', val.length >= 12);
            setStatus('req-upper', /[A-Z]/.test(val));
            setStatus('req-lower', /[a-z]/.test(val));
            setStatus('req-num', /[0-9]/.test(val));
            setStatus('req-special', /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(val));

            const res = await fetch('/api/strength', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: val})
            });
            const data = await res.json();
            const bar = document.getElementById('meter-bar');
            bar.style.width = data.width;
            bar.className = `h-full rounded-full ${data.color}`;
            document.getElementById('meter-text').innerText = data.text;
        });

        async function checkPwned() {
            const pw = document.getElementById('pwned-in').value;
            if(!pw) return;
            const box = document.getElementById('pwned-result');
            box.innerHTML = "Checking...";
            box.classList.remove('hidden');
            const res = await fetch('/api/pwned', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: pw})
            });
            const data = await res.json();
            if(data.count > 0) {
                box.className = "p-5 rounded-2xl mt-4 bg-red-900/30 border border-red-500/30";
                box.innerHTML = `<h4 class="font-bold text-red-400">Leaked!</h4> Seen ${data.count} times.`;
            } else {
                box.className = "p-5 rounded-2xl mt-4 bg-green-900/30 border border-green-500/30";
                box.innerHTML = `<h4 class="font-bold text-green-400">Safe</h4> Not found in database.`;
            }
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':

    app.run(debug=True)
