import audio_engine
import video_engine
import os
import uuid
import random
import time
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, db
from instagram_api_handler import create_media_container
from moviepy import VideoFileClip

load_dotenv()

db_reference = None

if not os.path.exists("secrets/firebase_cred_secret.json"):
    raise FileNotFoundError(
        "Firebase credentials file not found at secrets/firebase_cred_secret.json. "
        "Please run: ./tools/decrypt_firebase_cred.sh or set FIREBASE_SECRET_PASSPHRASE in .env"
    )
cred = credentials.Certificate("secrets/firebase_cred_secret.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
})


class ContentCreator:
    job_id = ""

    speaker1_characters = ["zukko"]
    speaker2_characters = ["iroh"]

    

    def __init__(self):
        self.job_id = uuid.uuid4()
        #self.job_id = "0ed8d23f-846a-4bf3-afa1-75c9c5194117"
        print(f"Job ID: {self.job_id}")

    def db_get_conversation(self):
        ref = db.reference("/conversations/control")
        current_index = ref.child("current_index").get()
        total_quotes = ref.child("total_quotes").get()
        print(f"Current Index: {current_index}, Total Quotes: {total_quotes}")
        if current_index >= total_quotes:
            print("All quotes have been processed.")
            return None
        ref = db.reference("/conversations/source")
        print("ref initialized = ", ref)
        dialogue1 = ref.child(str(current_index)).child("dialogue1").get()
        dialogue2 = ref.child(str(current_index)).child("dialogue2").get()
        print(f"Fetched conversation data: {dialogue1} | {dialogue2}")
        return dialogue1, dialogue2
    

    def db_increment_currentindex(self):
        ref = db.reference("/conversations/control")
        current_index = ref.child("current_index").get()
        ref.update({
            "current_index": current_index + 1
        })
        print(f"Incremented current index to {current_index + 1}")


    def create_mediacontent(self, char1_dialogue, char2_dialogue):
        
        audio_engine_instance = audio_engine.AudioEngine(str(self.job_id))

        char1_speaker = self.speaker1_characters[random.randint(0, len(self.speaker1_characters)-1)]
        char2_speaker = self.speaker2_characters[random.randint(0, len(self.speaker2_characters)-1)]

        audio_engine_instance.create_audio_file(char1_speaker,char1_dialogue,char2_speaker, char2_dialogue)
        print(f"Final audio created at: outputs/{self.job_id}/audio/final_audio.wav")

        speaker1_duration = audio_engine_instance.final_audio_c1_length
        speaker2_duration = audio_engine_instance.final_audio_c2_length
        total_duration = audio_engine_instance.final_audio_length

        video_engine_instance = video_engine.VideoEngine(str(self.job_id))
        video_engine_instance.create_video_clip(speaker1_duration,speaker2_duration,total_duration)
        print(f"Final video created at: outputs/{self.job_id}/video/final_video.mp4")

        
    

if __name__ == "__main__":

    while(True):
        content_creator = ContentCreator()
        start_time = time.time()
        char1_dialogue, char2_dialogue = content_creator.db_get_conversation()
        if char1_dialogue and char2_dialogue:
            print(f"Creating media content for dialogues:\n1: {char1_dialogue}\n2: {char2_dialogue} \n")
        else:
            print("No more conversations to process. Exiting loop.")
            break
        
        if char1_dialogue and char2_dialogue:
            content_creator.db_increment_currentindex()
            content_creator.create_mediacontent(char1_dialogue, char2_dialogue)
        else:
            print("No more conversations to process.")

        create_media_container(content_creator.job_id,"outputs/{}/video/final_video.mp4".format(content_creator.job_id), f"Follow for more amazing content! \n\n Zukko : {char1_dialogue} \n\n Iroh : {char2_dialogue} \n\n #animatedreel #animateddialogue #zukko #iroh #contentcreator #foryou #fyp #viralvideo #trendingreel #explorepage #Advice #Life #Anime #Quotes #LifeAdvice #AnimeQuotes #Motivation #Inspiration #DailyQuotes #PositiveVibes #LifeLessons #JapaneseAnime #Wisdom #Mindfulness #SelfImprovement #Empowerment #AnimeLife #ThoughtOfTheDay #PersonalGrowth")

        end_time = time.time()
        print(f"Total processing time: {end_time - start_time} seconds \n\n\n")
        break


