from flask import Flask, render_template

templates_path = '../templates'
app = Flask(__name__, template_folder=templates_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
def user_page():
    return render_template('profile.html')

@app.route('/equipment')
def shop_page():
    return render_template('equipment.html')

@app.route('/profile/cart')
def user_cart():
    return render_template('cart.html')

@app.route('/profile/order-history')
def user_order_history():
    return render_template('order_history.html')


if __name__ == '__main__':
    app.run(debug=True)
