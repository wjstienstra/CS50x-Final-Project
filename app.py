from flask import Flask, jsonify, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta


from helpers import apology, login_required, company_list, retrieve_news, get_quote, get_company_profile, summarize

#configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure connection to SQLite database
db = SQL("sqlite:///database.db")

# Prevent cashed responses, but server versions always
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# RETREIVE LIST OF COMPANIES FOR SEARCH
print("Retreiving data...")
COMPANIES = company_list()

if COMPANIES:
    print(f"Succes {len(COMPANIES)} retreived")
else:
    print("Failed to retrieve the list")

#---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    # Get the user search
    query = request.args.get("q")
    if not query:
        return jsonify([]) # Return an empty list

    # Filter companies list, searching for symbols or names that start with the user query, limiting search results to 10
    results = [
        company for company in COMPANIES
        if query.lower() in company.get("symbol", "").lower() or
           query.lower() in company.get("description", "").lower()
    ][:5]
    return jsonify(results)

@app.route("/subscribe", methods=["POST"])
@login_required
# Symbol is retreived from the search form.
def subscribe():
    symbol = request.form.get("symbol")
    name = request.form.get("name")
    id = session["user_id"]
    # Retreive user followed companies and check whether it isn't in the database yet.
    rows = db.execute("SELECT * FROM subscriptions where user_id = ? AND company_symbol = ? ", id, symbol)
    if len(rows)> 0:
        return apology("You already follow this company!", 400)
    else:
        db.execute("INSERT INTO subscriptions (user_id, company_symbol, company_name) VALUES(?, ?, ?)", id, symbol, name)
        return redirect("/dashboard")

@app.route("/unsubscribe", methods=["POST"])
@login_required
# Symbol is retreived from the search form.
def unsubscribe():
    symbol = request.form.get("symbol")
    id = session["user_id"]

    # Double check whether company is followed, maybe not necessary. Can remove later
    rows = db.execute("SELECT * FROM subscriptions where user_id = ? AND company_symbol = ? ", id, symbol)
    if len(rows) == 0:
        return apology("You don't follow this company!", 400)
    else:
        db.execute("DELETE FROM subscriptions WHERE user_id = ? AND company_symbol = ?", id, symbol)
        return redirect("/dashboard")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Query database to ensure username does not exist
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            return apology("username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted and
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Check if passwords match
        elif (request.form.get("password") != request.form.get("confirmation")):
            return apology("passwords don't match", 400)

        # Check email was submitted
        elif not request.form.get("email"):
            return apology("must provide an email adress", 400)

        # Enter new user and hashed password in the database
        db.execute("INSERT INTO users (username, hash, email) VALUES(?, ?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")), request.form.get("email"))

        id = db.execute("SELECT id FROM users WHERE (username IS (?))",
                        request.form.get("username"))

        session["user_id"] = id[0]["id"]

        # Redirect user to dashboard
        return redirect("/dashboard")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        id = rows[0]["id"]
        session["user_id"] = id

        # Redirect user to dashboard
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    """Access Dashboard"""

    # Retrieve user id and subscriptions to display correct followed companies in dashboard
    id = session["user_id"]
    subscriptions = db.execute("SELECT id, company_name, company_symbol, ai_summary, summary_updated_at FROM subscriptions WHERE user_id = ?", id)

    dashboard_data = [] # This list will hold the final data for the template

    # Go over all subscriptions and retrieve updates
    for sub in subscriptions:
        company_symbol = sub["company_symbol"]
        summary_is_old = True # Assume summary needs update

        # Check to see if a summary exists and is recent (less then 1 hour)
        if sub["summary_updated_at"]:
            last_updated = datetime.strptime(sub["summary_updated_at"], '%Y-%m-%d %H:%M:%S')
            if (datetime.now() - last_updated) < timedelta(hours=1):
                summary_is_old = False
                ai_summary = sub["ai_summary"]

        # If summary is old or doesn't exist, generate a new one
        if summary_is_old:
            print(f"Generating new summary for {company_symbol}...")
            news_items = retrieve_news(company_symbol)
            ai_summary = "Could not generate AI-Summary."

            if news_items:
                news_context = ""
                for article in news_items[:10]:
                    headline = article.get('headline', '')
                    summary = article.get('summary', '')
                    if headline and summary:
                        news_context += f"Headline: {headline}\nSummary: {summary}\n\n"

                if news_context:
                    generated_summary = summarize(news_context)
                    if generated_summary:
                        ai_summary = generated_summary
                        # Format timestring before saving to DB to prevent formatting clashes
                        current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        # Saving to database..
                        db.execute("UPDATE subscriptions SET ai_summary = ?, summary_updated_at = ? WHERE id = ?", ai_summary, current_time_str, sub["id"])

                        # Update local dict with the new timestamp
                        sub["summary_updated_at"] = current_time_str

            sub["ai_summary"] = ai_summary # Update local dictionary
        else:
            print(f"Using cached summary for {company_symbol}.")

        # --- Data formatting for the templat ---

        # Format the update time
        formatted_time = "Not yet summarized." # fallback
        if sub["summary_updated_at"]:
            last_updated_at = datetime.strptime(sub["summary_updated_at"], '%Y-%m-%d %H:%M:%S')
            formatted_time = last_updated_at.strftime('%b %d %Y at %I:%M %p')

        # Get Company profile for Logo
        profile = get_company_profile(company_symbol)
        if profile:
            # Add the logo URL to the subscription dictionary
            sub['logo'] = profile.get('logo', '') # Empty string as fallback
        else:
            sub['logo'] = '' # Ensure the key always exists

        # Get latest quotes
        quote = get_quote(company_symbol)
        if quote:
            sub['current_price'] = quote.get('c', 0)
            sub['price_change'] = quote.get('d', 0)
            sub['percent_change'] = quote.get('dp', 0)

        dashboard_data.append({
            "symbol": company_symbol,
            "name": sub["company_name"],
            "logo": sub["logo"],
            "summary": ai_summary,
            "updated_at": formatted_time
        })

    return render_template("dashboard.html", dashboard_data=dashboard_data, subscriptions=subscriptions)


