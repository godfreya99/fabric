from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
from flask import send_from_directory
import os
from dotenv import load_dotenv
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

##################################################
##################################################
#
# ⚠️ CAUTION: This is an HTTP-only server!
#
# If you don't know what you're doing, don't run
#
##################################################
##################################################
load_dotenv(os.path.join(os.path.dirname(__file__), '../api/.env'))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/favicon.ico")
def favicon():
    """    Send the favicon.ico file from the static directory.

    Returns:
        Response object with the favicon.ico file

    Raises:
         -
    """

    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        login_data = {"username": username, "password": password}

        response = requests.post("http://127.0.0.1:13337/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("token")
            session["token"] = token
            return redirect(url_for("index"))
        else:
            flash("Login failed. Please check your username and password.", "error")
            return redirect(url_for("login"))
    
    return render_template("login.html")
@app.route("/", methods=["GET", "POST"])
def index():
    """    Process the POST request and send a request to the specified API endpoint.

    Returns:
        str: The rendered HTML template with the response data.
    """
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        prompt = request.form.get("prompt")
        endpoint = request.form.get("api")
        response = send_request(prompt=prompt, endpoint=endpoint)
        return render_template("index.html", response=response)
    return render_template("index.html", response=None)

def send_request(prompt, endpoint):
    """    Send a request to the specified endpoint of an HTTP-only server.

    Args:
        prompt (str): The input prompt for the request.
        endpoint (str): The endpoint to which the request will be sent.

    Returns:
        str: The response from the server.

    Raises:
        KeyError: If the response JSON does not contain the expected "response" key.
    """

    base_url = "http://127.0.0.1:13337"
    url = f"{base_url}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {session['token']}",
    }
    data = json.dumps({"input": prompt})
    response = requests.post(url, headers=headers, data=data, verify=False)

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # raises HTTPError if the response status isn't 200
    except requests.ConnectionError:
        return "Error: Unable to connect to the server."
    except requests.HTTPError as e:
        return f"Error: An HTTP error occurred: {str(e)}"

def main():
    app.run(host="0.0.0.0", port=13338, debug=True)

if __name__ == "__main__":
    main()