from flask import Flask, render_template, request, redirect, url_for
import random
import threading
import time
from datetime import datetime
import pytz

app = Flask(__name__)

# West Africa Timezone
WAT = pytz.timezone('Africa/Lagos')

# Signal storage
signals = []
history = []
signals_today = []
bot_started = False

# Pairs and base prices
pair_prices = {
    'XAUUSD': 2300.0,
    'GBPUSD': 1.2800,
    'EURUSD': 1.1000,
    'USDJPY': 145.00,
    'GBPJPY': 185.00,
    'EURGBP': 0.8600,
    'USDCHF': 0.8800,
    'EURJPY': 160.00,
    'GBPCHF': 1.1300
}

def generate_signal():
    pair = random.choice(list(pair_prices.keys()))
    direction = random.choice(['Buy', 'Sell'])
    base_price = pair_prices[pair]
    entry = round(base_price + random.uniform(-0.005, 0.005) * base_price, 4)

    if direction == 'Buy':
        sl = round(entry - abs(entry * 0.002), 4)
        tp = round(entry + abs((entry - sl) * 2), 4)
    else:
        sl = round(entry + abs(entry * 0.002), 4)
        tp = round(entry - abs((sl - entry) * 2), 4)

    rr = "1:2"
    timestamp = datetime.now(WAT).strftime("%Y-%m-%d %H:%M:%S")

    new_signal = {
        'pair': pair,
        'direction': direction,
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'rr': rr,
        'time': timestamp
    }

    signals.append(new_signal)
    history.append(new_signal)

    today_str = datetime.now(WAT).strftime("%Y-%m-%d")
    global signals_today
    signals_today = [s for s in history if s['time'].startswith(today_str)]

def bot_loop():
    while True:
        generate_signal()
        time.sleep(20)  # quick testing

def start_bot():
    global bot_started
    if not bot_started:
        bot_started = True
        threading.Thread(target=bot_loop, daemon=True).start()

start_bot()

@app.route('/')
def home():
    return render_template('dashboard.html', signals=signals_today, history=history)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_signal = {
            'pair': request.form['pair'],
            'direction': request.form['direction'],
            'entry': float(request.form['entry']),
            'sl': float(request.form['sl']),
            'tp': float(request.form['tp']),
            'rr': request.form['rr'],
            'time': datetime.now(WAT).strftime("%Y-%m-%d %H:%M:%S")
        }
        signals.append(new_signal)
        history.append(new_signal)
        return redirect(url_for('home'))
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
