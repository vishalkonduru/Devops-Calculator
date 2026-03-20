from flask import Flask, render_template, request
import redis
import os
import time

app = Flask(__name__)

# Connect to Redis (for caching)
try:
    cache = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=6379,
        decode_responses=True
    )
    cache.ping()
    print("✅ Connected to Redis")
except:
    cache = None
    print("⚠️  Redis not available")

def calculate(num1, num2, operation):
    """Perform calculation"""
    if operation == 'add':
        return num1 + num2
    elif operation == 'subtract':
        return num1 - num2
    elif operation == 'multiply':
        return num1 * num2
    elif operation == 'divide':
        return num1 / num2 if num2 != 0 else 'Error: Division by zero'
    return 'Invalid operation'

@app.route('/')
def home():
    """Home page - calculator form"""
    return render_template('calculator.html', result=None)

@app.route('/calculate', methods=['POST'])
def calculate_route():
    """Handle calculation"""
    try:
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        operation = request.form['operation']
        
        # Create cache key
        cache_key = f"{num1}:{num2}:{operation}"
        
        # Check cache first
        if cache and cache.exists(cache_key):
            result = cache.get(cache_key)
            print(f"✅ Cache hit for {cache_key}")
        else:
            # Perform calculation
            result = calculate(num1, num2, operation)
            # Store in cache for 1 hour
            if cache and isinstance(result, (int, float)):
                cache.setex(cache_key, 3600, str(result))
                print(f"📦 Cached result for {cache_key}")
        
        return render_template('calculator.html', result=result)
    
    except ValueError:
        return render_template('calculator.html', result='Error: Invalid input')
    except Exception as e:
        return render_template('calculator.html', result=f'Error: {str(e)}')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'redis': 'connected' if cache and cache.ping() else 'disconnected'
    }
    return status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)