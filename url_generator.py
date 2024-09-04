import random,string,json,os

def generate_short_url(existing_urls, length=6):
    while True:
        short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if short_url not in existing_urls:
            return short_url

def save_url_to_json(long_url, username, json_file='urls.json'):
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            url_data = json.load(file)
    else:
        url_data = {}

    short_url = generate_short_url(url_data.keys())
    
    url_data[short_url] = {"long_url": long_url, "username": username}
    
    with open(json_file, 'w') as file:
        json.dump(url_data, file, indent=4)
    
    return short_url


