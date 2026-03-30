import requests
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import json
import os
from dotenv import load_dotenv

import time
from time import sleep

# Load environment variables from .env file
load_dotenv()

LONG_LIVED_TOKEN = os.getenv("INSTAGRAM_LONG_LIVED_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

if not LONG_LIVED_TOKEN or not IG_USER_ID:
    raise ValueError("INSTAGRAM_LONG_LIVED_TOKEN and IG_USER_ID environment variables must be set")
def url_getter():
    url = "https://freeimage.host/api/1/upload"
    api_key = os.getenv("FREEIMAGE_API_KEY")
    
    if not api_key:
        raise ValueError("FREEIMAGE_API_KEY environment variable not set")

    payload = {"key": api_key}
    files = {"source": open("new.jpeg", "rb")}

    res = requests.post(url, data=payload, files=files)
    print(res.json())
    return res.json()['image']['url']





def create_media_container(job_id,video_path, caption):

    catbox_api_endpoint = "https://catbox.moe/user/api.php"
    userhash = os.getenv("CATBOX_USERHASH")
    
    if not userhash:
        raise ValueError("CATBOX_USERHASH environment variable not set")
    
    with open(video_path, 'rb') as video_file:
        payload = {
            "reqtype": "fileupload",
            "userhash": userhash
        }

        response = requests.post(catbox_api_endpoint, data=payload, files={"fileToUpload": video_file})
        print("Catbox response: ", response.text)
    




    payload = {
        "media_type":   "REELS",
        "video_url":    response.text,
        "caption":      caption,
        "share_to_feed":True,
        "access_token": LONG_LIVED_TOKEN
    }

    post_url = 'https://graph.facebook.com/v16.0/{}/media'.format(IG_USER_ID)


    r = requests.post(post_url, data=payload)
    print(r.text)

    results = json.loads(r.text)
    print("results = ",results)
    container_id = creation_id = results['id']


    # check media status
    media_status_url = 'https://graph.facebook.com/v16.0/{}'.format(container_id)
    payload_status = {
        'fields': 'status_code,status',
        'access_token': LONG_LIVED_TOKEN
    }

    r = requests.get(media_status_url, params=payload_status)
    print("status check = ",r.text)

    status_result = json.loads(r.text)
    while status_result['status_code'] != 'FINISHED':
        print("Media is still processing, waiting for 5 seconds...")
        sleep(5)
        r = requests.get(media_status_url, params=payload_status)
        status_result = json.loads(r.text)
        print("status check = ",r.text)

    print("media upload successful")

    if 'id' in results:
        creation_id = results['id']
        second_url = 'https://graph.facebook.com/v23.0/{}/media_publish'.format(IG_USER_ID)
        seccond_payload = {
            'creation id': creation_id,
            'access_token': LONG_LIVED_TOKEN
        }
        r = requests.post(second_url, data=seccond_payload)
        print(r.text)
        print("video successfully posted")
    else:
        print("error bitch")


def publish_video(video_path, caption):
    video_url = url_getter()
    discription = "Like , Share and Follow                                      #art #positivity #thoughts #instadaily #photography #quotesdaily #writersofinstagram #photooftheday #quotesaboutlife #motivational #writer #sad #followforfollowback #detik #quotesoftheday #likeforlikes #entrepreneur #fitness #quotesindonesia #shayari #inspire #literasi #smile #beautiful #words #successquotes #selfcare #writing #explore #nature "


    post_url = 'https://graph.facebook.com/v16.0/{}/media'.format(IG_USER_ID)
    payload = {
        'image_url': image_url,
        'caption': discription,
        'access_token': LONG_LIVED_TOKEN
    }
    r = requests.post(post_url, data=payload)
    print(r.text)
    print("media upload successful")
    results = json.loads(r.text)
    if 'id' in results:
        creation_id = results['id']
        second_url = 'https://graph.facebook.com/v16.0/{}/media_publish'.format(IG_USER_ID)
        seccond_payload = {
            'creation id': creation_id,
            'access_token': LONG_LIVED_TOKEN
        }
        r = requests.post(second_url, data=seccond_payload)
        print(r.text)
        print("image successfully posted")
    else:
        print("error bitch")