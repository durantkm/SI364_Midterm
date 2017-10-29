from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import Required, AnyOf, Optional

import requests
import json
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdeomfnbp34t3tsocapmcsd6547djvsnosni45748t4t344nyhhh6555'
app.debug = False

class Users_State(FlaskForm):
	State = StringField('What state do you live in?', validators = [Required(), AnyOf(['alabama','alaska','arizona','arkansas','california','colorado','connecticut','delaware',
		'florida','georgia','hawaii','idaho','illinois','indiana','iowa','kansas','kentucky','louisiana','maine','maryland','massachusetts','michigan','minnesota','mississippi','missouri',
		'montana','nebraska','nevada','new hampshire','new jersey','new mexico','new york','north carolina','north dakota','ohio','oklahoma','oregon','pennsylvania','rhode island'
		,'south carolina','south dakota','tennessee','texas','utah','vermont','virginia','washington','west virginia','wisconsin','wyoming','district of columbia', 'puerto rico'])])
	New_Data_Request = StringField('Would you like to request today\'s data?', validators =[Optional(), AnyOf(['yes','no'])])
	submit = SubmitField('Submit')

@app.route('/')
def Home_Page():
	extra_info =[("https://www.cnbc.com/id/100450613", 'CNBC-How many stocks should you own at one time?'),
				 ("https://www.thestreet.com/story/13588155/1/this-is-why-how-many-shares-matters.html", 'TheStreet-How many shares should I buy?'),
				 ("https://www.gobankingrates.com/investing/10-stocks-beginners-try-2016/",'GoBankingRates-10 Stocks for Beginners to Try in 2017'),
				 ("https://www.gobankingrates.com/investing/9-safe-stocks-first-time-investors/", 'GoBankingRates-9 Safe Stocks for First-Time Investors'),
				 ("http://www.investopedia.com/articles/pf/07/budget-qs.asp?lgl=myfinance-layout-no-ads",'Investopedia-How much should I set aside for investments?'),
				 ("http://finance.zacks.com/percentage-should-set-stop-loss-investing-stock-market-4421.html", 'Zacks Finance-Stop Losses and where to set them')]
	#Will show a homepage that explains what the app is supposed to do, as well as
	#provide links with information related to the companies. Another link will 
	#direct the user to the actual form
	return render_template('Home_Page_Design.html', extra_info = extra_info)

@app.route('/Users_State_Form')
def Investment_App_Form():
	#Will show the WTForm asking for state and whether they'd like to update the information
	#on file. The cookie will hold the information related to whether they'd like to update

	Users_State_Form = Users_State()
	#return render_template('Users_State_Form.html', form = Users_State_Form)
	newdata_response= make_response(render_template('Users_State_Form.html', form = Users_State_Form))
	newdata_response.set_cookie('data_requested', 'no')
	return newdata_response

@app.route('/User_Investment_Suggestions', methods = ['GET', 'POST'])
def Investment_App_Suggestions():
	#Uses cookie and requests to figure out suggestions and then shows them
	CACHE_FNAME = "Investment_App_Data.json"
	Company_Total_Info = []
	Investment_App_Suggestions_results = []
	Did_we_update = ''
	Companies = [('Verizon', 'VZ', 'Communications','https://en.wikipedia.org/wiki/Verizon_Communications'),('Chevron Corp.', 'CVX', 'Energy','https://en.wikipedia.org/wiki/Chevron_Corporation'),('Caterpillar Inc.', 'CAT', 'Construction','https://en.wikipedia.org/wiki/Caterpillar_Inc.'),
				 ('International Business Machines Corp.', 'IBM', 'Technology','https://en.wikipedia.org/wiki/IBM'),('ExxonMobil Corp.','XOM', 'Energy','https://en.wikipedia.org/wiki/ExxonMobil'),
				 ('Pfizer Inc.','PFE', 'Medicine','https://en.wikipedia.org/wiki/Pfizer'),('Merck & Co. Inc.', 'MRK', 'Medicine','https://en.wikipedia.org/wiki/Merck_%26_Co.'),('Proctor & Gamble Co.', 'PG', 'Consumer Goods','https://en.wikipedia.org/wiki/Procter_%26_Gamble'),
				 ('Wal-Mart Stores, Inc.', 'WMT', 'Retail','https://en.wikipedia.org/wiki/Walmart'),('Cisco Systems Inc.', 'CSCO', 'technology','https://en.wikipedia.org/wiki/Cisco_Systems'),
				 ('Microsoft', 'MSFT','Technology','https://en.wikipedia.org/wiki/Microsoft'),('PepsiCo','PEP','Consumer Goods','https://en.wikipedia.org/wiki/PepsiCo'),
				 ('3M', 'MMM','Industrial_Goods','https://en.wikipedia.org/wiki/3M'),('Dover', 'DOV', 'Industrial Goods','https://en.wikipedia.org/wiki/Dover_Corporation'),
				 ('MasterCard','MA','Financial','https://en.wikipedia.org/wiki/MasterCard'),('Starwood Property Trust','STWD','Financial', 'https://en.wikipedia.org/wiki/Starwood_Capital_Group'),
				 ('Apple', 'AAPL', 'Consumer Goods','https://en.wikipedia.org/wiki/Apple_Inc.')]
	

	def get_quandl_data(searchterm):
		base_url ="https://www.quandl.com/api/v3/datasets/WIKI/{}.json?".format(searchterm)
		param_d = {}
		param_d["api_key"] ="ZwHoW63KRFgak7tG9rGM"


		if searchterm in CACHE_DICTION:
			quandl_data = CACHE_DICTION[searchterm]
			return(quandl_data)
		else:
			quandl_response = requests.get(base_url, params = param_d)
			quandl_data = json.loads(quandl_response.text)
			CACHE_DICTION[searchterm] = quandl_data
			f = open(CACHE_FNAME, 'w')
			f.write(json.dumps(CACHE_DICTION))
			f.close()
			return(quandl_data)

	def Get_Company_Stock_Info(Stock_Symbol):
		#Insert call to quandl and returns the info I need specifically.
		company_data = get_quandl_data(Stock_Symbol)
		stock_close_recent = company_data["dataset"]["data"][0][4]
		stock_close_dayb4 = company_data["dataset"]["data"][1][4]
		return(int(stock_close_recent),int(stock_close_dayb4))

	def Calculate_amount_to_invest_per_month(state):
		#Gives the amount to be invested per month from the net income
		State_Incomes={'alabama': 44765,'alaska': 73355,'arizona': 51492,'arkansas': 41995,'california': 64500,'colorado': 63909,'connecticut': 71346,
					'delaware': 61255,'florida': 49426,'georgia': 51244,'hawaii': 73486,'idaho': 48275,'illinois':59588,'indiana': 50532,'iowa': 54736,
					'kansas': 53906,'kentucky': 45215,'louisiana': 45727,'maine': 51494,'maryland': 75847,'massachusetts': 70628,'michigan': 51084,
					'minnesota': 63488,'mississippi': 63488,'missouri': 50238,'montana': 49509,'nebraska': 54996,'nevada': 52431,'new hampshire': 70303,
					'new jersey': 72222,'new mexico': 45382,'new york': 60850,'north carolina': 47830,'north dakota': 60557,'ohio': 51075,'oklahoma': 48568,
					'oregon': 54148,'pennsylvania': 55702,'rhode island': 58073,'south carolina': 47238,'south dakota': 53017,'tennessee': 47275,'texas': 55653,
					'utah': 62912,'vermont': 56990,'virginia': 66262,'washington': 64129,'west virginia': 42019,'wisconsin': 55638,'wyoming': 60214,'district of columbia': 75628, 'puerto rico': 18626}
		Max_Money_Risk_per_month_forfive_shares = State_Incomes[state]/60
		return(int(Max_Money_Risk_per_month_forfive_shares))

	def calculate_stop_loss(stock_prices):
			stoploss = stock_prices[0] - stock_prices[1]
			if stoploss == 0:
				stoploss = stock_prices[0]
				return(stoploss)
			elif stoploss < 0:
				stoploss = stock_prices[0]
				return(stoploss)
			else:
				return(stoploss)

	def calculate_number_of_stocks_to_buy(Investing_Money, stock_prices):
		stoploss = calculate_stop_loss(stock_prices)
		number_of_stocks_bought = int(Investing_Money/stoploss)
		return(number_of_stocks_bought)

	form = Users_State(request.form)
	if request.method == 'POST' and form.validate_on_submit():
		State = form.State.data
		Are_we_updating = form.New_Data_Request.data
		if Are_we_updating == '':
			Are_we_updating = request.cookies.get('data_requested')

		print(Are_we_updating)
		if Are_we_updating == 'no':
			try:
				cache_file = open(CACHE_FNAME,'r')
				cache_contents = cache_file.read()
				cache_file.close()
				CACHE_DICTION = json.loads(cache_contents)
				Did_we_update ='No'

			except:
				CACHE_DICTION = {}
				Did_we_update ='HadTo'
		else:
			CACHE_DICTION = {}
			Did_we_update = 'Yes'

		for company in Companies:
												#company name, company stock symbol, industry, link
			Company_Total_Info.append((company[0],Get_Company_Stock_Info(company[1]),company[2],company[3]))
		Investing_Money = Calculate_amount_to_invest_per_month(State)
		#roughly middle ground value
		if Investing_Money >= 967:
			Company_Total_Info_sorted = sorted(Company_Total_Info, key = lambda x: x[1][0], reverse = True)
			for company_info in Company_Total_Info_sorted:
				#appends to a list name of company, number of stocks bought, current price, industry, link
				company = company_info[0]
				number_of_stocks_bought = calculate_number_of_stocks_to_buy(Investing_Money,company_info[1])
				current_price = company_info[1][0]
				industry =  company_info[2]
				link_to_comp_info = company_info[3]
				Investment_App_Suggestions_results.append((company, number_of_stocks_bought,current_price,industry,link_to_comp_info))
		else:
			Company_Total_Info_sorted = sorted(Company_Total_Info, key = lambda x: x[1][0])
			for company_info in Company_Total_Info_sorted:
				#appends to a list name of company, number of stocks bought, current price, industry, link
				company = company_info[0]
				number_of_stocks_bought = calculate_number_of_stocks_to_buy(Investing_Money,company_info[1])
				current_price = company_info[1][0]
				industry =  company_info[2]
				link_to_comp_info = company_info[3]
				Investment_App_Suggestions_results.append((company, number_of_stocks_bought,current_price,industry,link_to_comp_info))
		return(render_template('Investment_Suggestions.html', result = (Investment_App_Suggestions_results[:9], Did_we_update)))
	flash('All fields required and All entries must be lowercase!')
	return(redirect(url_for('Investment_App_Form')))

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def Internal_Server_Error(e):
	extra_info =[("https://www.cnbc.com/id/100450613", 'CNBC-How many stocks should you own at one time?'),
				 ("https://www.thestreet.com/story/13588155/1/this-is-why-how-many-shares-matters.html", 'TheStreet-How many shares should I buy?'),
				 ("https://www.gobankingrates.com/investing/10-stocks-beginners-try-2016/",'GoBankingRates-10 Stocks for Beginners to Try in 2017'),
				 ("https://www.gobankingrates.com/investing/9-safe-stocks-first-time-investors/", 'GoBankingRates-9 Safe Stocks for First-Time Investors'),
				 ("http://www.investopedia.com/articles/pf/07/budget-qs.asp?lgl=myfinance-layout-no-ads",'Investopedia-How much should I set aside for investments?'),
				 ("http://finance.zacks.com/percentage-should-set-stop-loss-investing-stock-market-4421.html", 'Zacks Finance-Stop Losses and where to set them')]
	return render_template('500.html',extra_info = extra_info), 500

if __name__== '__main__':
	app.run()