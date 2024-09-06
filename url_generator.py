import random, string, json, os


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
    
    # Store the data in the required format
    url_data[short_url] = {
        "username": username,
        "long_url": long_url,
        "title": title,
        "count": 0,
        "active": True,
    }
    
    with open(json_file, 'w') as file:
        json.dump(url_data, file, indent=4)
    
    return short_url

def load_user_urls(username, json_file='urls.json'):
    if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
        with open(json_file, 'r') as file:
            data = json.load(file)
            # Filter the URLs by the user's name
            user_urls = {short_url: info for short_url, info in data.items() if info["username"] == username}
            return user_urls
    return {}
