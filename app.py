from flask import Flask, render_template, request,json,redirect
from url_generator import save_url_to_json

app = Flask(__name__)
host="http://127.0.0.1:2006/"

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        url_received = request.form["lurl"]
        short_url=save_url_to_json(url_received,'user123')
        print(host+short_url)
        return host+short_url
       
        
    else:
        return render_template("home.html")

@app.route('/<short_url>', methods=['GET'])
def redirecting(short_url):
    with open('urls.json','r') as file:
        data=json.load(file)
        if short_url in data:
            l_url=data[short_url].get('long_url')
            print(f"long url : {l_url}")
            return redirect(short_url)
        else:
            abort(404,description="Short URL not found")


if __name__ == '__main__':
    app.run(debug=True,port=2006)
