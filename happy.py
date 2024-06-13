from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)
import yfinance as yf

class User:
    def __init__(self, id, username, password, cash):
        self.id = id
        self.username = username
        self.password = password
        self.cash = cash
        self.portfolio = {}
        self.lentry=[]


    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(id=1, username='Anthony', password='password', cash=10000))
users.append(User(id=2, username='Becca', password='secret', cash=10000))
users.append(User(id=3, username='Carlos', password='somethingsimple', cash=10000))

app = Flask(__name__, template_folder='template')
app.secret_key = 'somesecretkeythatonlyishouldknow'

stockslist = []

list_of_symbols = ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA', 'AMZN', 'GOOG', 'TSM', 'PFE', 'BABA', 'WMT']
for symbol in list_of_symbols:
    tickerSymbol = symbol
    tickerData = yf.Ticker(tickerSymbol)
    todayData = tickerData.history(period='1d')
    stockslist.append({'symbol': symbol,
                       'fullname': tickerData.info['longName'],
                       'price': float(tickerData.info['regularMarketPreviousClose']),
                       'currency': tickerData.info['currency'],
                       'country': tickerData.info['country'],
                       'sector': tickerData.info['sector'],
                       'website': tickerData.info['website'],
                       'lowprice': str(tickerData.info['regularMarketDayLow']),
                       'highprice': str(tickerData.info['regularMarketDayHigh']),
                       'volume': str(tickerData.info['volume'])})

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user_list = [x for x in users if x.id == session['user_id']]
        if user_list:
            g.user = user_list[0]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user_list = [x for x in users if x.username == username]
        if user_list:
            user = user_list[0]
            if user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_id = len(users) + 1
        new_user = User(id=user_id, username=username, password=password, cash=10000)
        users.append(new_user)

        # Redirect to login page
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/<string:stockname>')
def stockdetail(stockname):
    c = 0
    for i in range(len(stockslist)):
        if stockname == stockslist[i].get('symbol'):
            c = i
    return render_template('stocksdetail.html', infolist=stockslist[c])

@app.route('/stocks', methods=['GET', "POST"])
def stocks(templist=stockslist):
    kwd = ""
    if request.method == "POST":
        kwd = request.form['searchkwd']
        templist = []
        for stockdict in stockslist:
            namelist = stockdict.values()
            for nameid in namelist:
                if kwd in nameid and stockdict not in templist:
                    templist.append(stockdict)

        return render_template('stocks.html', stockslist=templist)

    return render_template('stocks.html', stockslist=templist)

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST' and 'addsymbol' in request.form:
        get_add_symbol = request.form['addsymbol']
        print(get_add_symbol)
        tickerSymbol = get_add_symbol
        tickerData = yf.Ticker(tickerSymbol)
        todayData = tickerData.history(period='1d')
        stockslist.append({'symbol': tickerData.info['symbol'],
                           'fullname': tickerData.info['longName'],
                           'price': str(tickerData.info['regularMarketPreviousClose']),
                           'currency': tickerData.info['currency'],
                           'country': tickerData.info['country'],
                           'sector': tickerData.info['sector'],
                           'website': tickerData.info['website'],
                           'lowprice': str(tickerData.info['regularMarketDayLow']),
                           'highprice': str(tickerData.info['regularMarketDayHigh']),
                           'volume': str(tickerData.info['volume'])})

    elif request.method == 'POST' and 'delete_stock' in request.form:
        get_remove_symbol = request.form.get('delete_stock')
        for stockdict in stockslist:
            namelist = stockdict.values()
            for nameid in namelist:
                if get_remove_symbol in nameid:
                    stockslist.remove(stockdict)

    return render_template('admin.html', stockslist=stockslist)


@app.route('/home')
def home():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/')
def landing():
    return redirect('/home')



@app.route('/sell/<string:symbol>', methods=['POST'])
def sell_stock(symbol):
    if not g.user:
        return redirect(url_for('login'))

    quantity = int(request.form['selling'])
    stock = next((item for item in stockslist if item["symbol"] == symbol), None)

    if stock and symbol in g.user.portfolio and g.user.portfolio[symbol] >= quantity:
        profit = stock['price'] * quantity
        g.user.cash += profit
        g.user.portfolio[symbol] -= quantity
        if g.user.portfolio[symbol] == 0:
            del g.user.portfolio[symbol]
            g.user.lentry.append(f'You sold {quantity} shares of {symbol} at a price {stock["price"]} per share')
    return redirect(url_for('profile'))

@app.route('/home2')
def home2():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('home2.html')

@app.route('/buy/<string:symbol>', methods=['POST'])
def buy_stock(symbol):
    if not g.user:
        return redirect(url_for('login'))

    quantity = int(request.form['quantity'])
    stock = next((item for item in stockslist if item["symbol"] == symbol), None)

    if stock:
        buycost = stock['price'] * quantity
        if g.user.cash >= buycost:
            g.user.cash -= buycost
            if symbol in g.user.portfolio:
                g.user.portfolio[symbol] += quantity
            else:
                g.user.portfolio[symbol] = quantity
                g.user.lentry.append(f'You bought {quantity} shares of {symbol} at a price {stock["price"]} per share')

            return redirect(url_for('profile'))

    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run()
