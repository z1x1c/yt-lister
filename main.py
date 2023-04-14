import os
import json
import requests
from bs4 import BeautifulSoup
import googleapiclient.discovery

def load_config(file_path):
    with open(file_path) as f:
        config = json.load(f)
    return config

def get_authenticated_service(api_key):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

    return youtube

def get_channel_id(api_key, custom_url):
    response = requests.get(custom_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    channel_id = soup.find('meta', itemprop='channelId')['content']
    return channel_id

def get_video_urls(api_key, channel_id, limit_pages, max_pages):
    youtube = get_authenticated_service(api_key)

    video_urls = []
    next_page_token = None
    page_count = 0

    while True:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=5,
            order="date",
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response["items"]:
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_urls.append(video_url)

        next_page_token = response.get("nextPageToken")

        page_count += 1
        if not next_page_token or (limit_pages and page_count >= max_pages):
            break

    return video_urls

def main():
    config = load_config("config.json")
    api_key = config["youtube_api_key"]

    custom_url = input("Please enter the channel custom URL: ")

    channel_id = get_channel_id(api_key, custom_url)

    if channel_id:
        print(f"Channel ID: {channel_id}")

        limit_pages_input = input("Do you want to limit the number of pages fetched? (y/n): ")
        limit_pages = limit_pages_input.lower() == "y"

        if limit_pages:
            max_pages = int(input("Enter the maximum number of pages to fetch: "))
        else:
            max_pages = 0

        video_urls = get_video_urls(api_key, channel_id, limit_pages, max_pages)

        print(f"Total videos: {len(video_urls)}")
        for url in video_urls:
            print(url)
    else:
        print("Channel not found.")

if __name__ == "__main__":
    main()
