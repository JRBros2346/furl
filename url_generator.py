import random,string,json,os

def generate_short_url(existing_urls, length=6):
    while True:
        short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if short_url not in existing_urls:
            return short_url

def save_url_to_json(long_url, username, title, json_file='urls.json'):
    if os.path.exists(json_file):
        if os.path.getsize(json_file) > 0:
            with open(json_file, 'r') as file:
                try:
                    url_data = json.load(file)
                except json.JSONDecodeError:
                    url_data = {}
        else:
            url_data = {}
    else:
        url_data = {}

    short_url = generate_short_url(url_data.keys())
    
    if username not in url_data:
        url_data[username] = {}
    
    url_data[username][short_url] = {"long_url": long_url, "title": title, "count": 0}
    
    with open(json_file, 'w') as file:
        json.dump(url_data, file, indent=4)
    
    return short_url

def load_user_urls(username, json_file='urls.json'):
    if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
        with open(json_file, 'r') as file:
            data = json.load(file)
            if username in data:
                return data[username]
    return {}
