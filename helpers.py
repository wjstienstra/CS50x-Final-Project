import os
from dotenv import load_dotenv
import requests
import google.generativeai as genai
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, timedelta

load_dotenv()

genai_api_key = os.getenv("GENAI_API_KEY")
finnhub_api_key = os.getenv("FINNHUB_API_KEY")

if not genai_api_key or not finnhub_api_key:
    raise ValueError("Api Key environment variable not set.")


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def company_list():
    """Look up available companies"""

    # API request
    api_key = finnhub_api_key
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={api_key}"

    # Query API
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        print(f"Error while retreiving data: {error}")
        return None

def retrieve_news(company_symbol):
    """Lookup company news"""

    # API request
    api_key = finnhub_api_key
    # Define last seven days for Finnhubs from en to date
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')

    url = (f"https://finnhub.io/api/v1/company-news?symbol={company_symbol}&from={from_date}&to={to_date}&token={api_key}")

    # Query API
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        print(f"Error while retrieving data: {error}")
        return None

def get_quote(symbol):
    """Gets the latest price quote for a given stock symbol using Finnhub."""
    try:
        api_key = finnhub_api_key
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"

        response = requests.get(url)
        response.raise_for_status()

        # The API returns a dictionary with price info
        # 'c' is current price, 'd' is change, 'dp' is percent change
        return response.json()

    except requests.RequestException as error:
        print(f"Fout bij het ophalen van de quote voor {symbol}: {error}")
        return None

def get_company_profile(symbol):
    """Gets company profile data, including the logo, from Finnhub."""
    try:
        api_key = finnhub_api_key
        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"

        response = requests.get(url)
        response.raise_for_status()

        # The API returns a dictionary with price info
        return response.json()

    except requests.RequestException as error:
        print(f"Fout bij het ophalen van de quote voor {symbol}: {error}")
        return None

def summarize(articles):
    """Call Gemini to summarize recent news"""

    try:
        genai.configure(api_key = genai_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Use the following articles about a company to write a short summary of the latest news. Don't mention any individual articles. Focus on information that relates to the company and is relevant for the individual retail investor.

        Article:
        {articles}
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as error:
        print(f"Error while retrieving data: {error}")
        return None

