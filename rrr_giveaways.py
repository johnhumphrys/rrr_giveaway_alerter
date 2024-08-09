import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_giveaways():
    url = "https://www.rrr.org.au/subscriber-giveaways"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        giveaways = []
        giveaway_items = soup.select('.list-view__item')
        for item in giveaway_items:
            title = item.select_one('.list-view__title span').text.strip()
            description = item.select_one('.list-view__summary p').text.strip()
            link = item.select_one('.list-view__anchor')['href']
            image = item.select_one('.list-view__image')['data-src']
            
            giveaways.append({
                'title': title,
                'description': description,
                'link': f"https://www.rrr.org.au{link}",
                'image': image
            })
        return giveaways
    else:
        raise Exception(f"Failed to retrieve content. Status code: {response.status_code}")

def save_giveaways(giveaways, filename='giveaways.json'):
    with open(filename, 'w') as file:
        json.dump(giveaways, file, indent=4)

def load_giveaways(filename='giveaways.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return []

def compare_giveaways(old_list, new_list):
    old_titles = {giveaway['title'] for giveaway in old_list}
    new_titles = {giveaway['title'] for giveaway in new_list}
    
    added = new_titles - old_titles
    removed = old_titles - new_titles
    
    return added, removed

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')

    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

def download_image(image_url, filename):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")

def send_discord_message(webhook_url, content, files=None):
    data = {"content": content}
    response = requests.post(webhook_url, data=data, files=files)
    
    if response.status_code not in [200, 204]:
        print(f"Failed to send message to Discord. Status code: {response.status_code}, Response: {response.text}")

def main():
    try:
        config = load_config()
        webhook_url = config.get("discord_webhook_url")
        
        new_giveaways = fetch_giveaways()
        old_giveaways = load_giveaways()
        
        if old_giveaways:
            added, _ = compare_giveaways(old_giveaways, new_giveaways)
            
            if added:
                print("New giveaways detected:")
                for item in new_giveaways:
                    if item['title'] in added:
                        print(f" - {item['title']}")
                        image_filename = f"{item['title'].replace(' ', '_')}.png"
                        try:
                            download_image(item['image'], image_filename)
                        except Exception as e:
                            print(f"Error downloading image: {e}")
                            continue
                        
                        with open(image_filename, 'rb') as img:
                            files = {"file": (image_filename, img)}
                            content = f"**{item['title']}**\n{item['description']}\n{item['link']}"
                            send_discord_message(webhook_url, content, files)
                        
                        os.remove(image_filename)
            else:
                print("No new giveaways detected.")
        else:
            print("No previous data to compare.")
        
        save_giveaways(new_giveaways)
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        send_discord_message(config.get("discord_webhook_url"), error_message)

if __name__ == "__main__":
    main()