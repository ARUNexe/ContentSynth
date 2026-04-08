from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
import random
import os
import time


class VideoEngine:

    job_id = ""



    def __init__(self, job_id):
        self.job_id = job_id
        mkdir_path = f"outputs/{self.job_id}/video"
        os.makedirs(mkdir_path, exist_ok=True)

    def create_video_clip(self, speaker1_timestamp, speaker2_timestamp, total_duration):

        start_time = time.time()
        print(f"Total video duration: {total_duration} seconds")
        print(f"Speaker 1 duration: {speaker1_timestamp} ms") 
        print(f"Speaker 2 duration: {speaker2_timestamp} ms")        

        video_pool_resource = "resources/videos/atla_0.mp4"


        video_pool_clip = VideoFileClip(video_pool_resource)
        video_pool_clip_duration = video_pool_clip.duration   # in seconds

        background_video_starttime = random.randint(0, max(0, int(video_pool_clip_duration - total_duration)))
        background_video_endtime = background_video_starttime + total_duration 

        final_video_clip = video_pool_clip.with_subclip(background_video_starttime, background_video_endtime)
        #final_video_clip = video_pool_clip.time_slice(background_video_starttime, background_video_endtime)
        final_audio_clip = AudioFileClip(f"outputs/{self.job_id}/audio/final_audio.wav")

        final_video_clip = final_video_clip.with_audio(final_audio_clip)
        # final_video_clip = final_video_clip.resized(height=360)

        speaker1_subtitle_path = f"outputs/{self.job_id}/subtitle/speaker1_sub.srt"
        speaker2_subtitle_path = f"outputs/{self.job_id}/subtitle/speaker2_sub.srt"


        speaker1_generator = lambda txt: TextClip(
            'resources/font/vendsans_Italic_variable.ttf',
            text=txt,
            color='white',
            stroke_color="black",
            stroke_width=9,
            method='caption',
            margin=(10, 10, 10, 10),
            font_size=50,
            size=(int(final_video_clip.w * 0.8), None),  # Convert to integer
        )

        speaker2_generator = lambda txt: TextClip(
            'resources/font/vendsans_variable.ttf',
            text=txt,
            color='orange',
            stroke_color="black",
            stroke_width=9,
            method='caption',
            margin=(10, 10, 10, 10),
            font_size=50,
            size=(int(final_video_clip.w * 0.8), None),  # Convert to integer
        )

        subtitle_speaker1 = SubtitlesClip(speaker1_subtitle_path, make_textclip=speaker1_generator).with_position(('center', final_video_clip.h * 0.8))
        subtitle_speaker2 = SubtitlesClip(speaker2_subtitle_path, make_textclip=speaker2_generator).with_position(('center', final_video_clip.h * 0.8))
        final_video_clip = CompositeVideoClip([final_video_clip, subtitle_speaker1, subtitle_speaker2])
        # final_video_clip = CompositeVideoClip([final_video_clip, subtitle_speaker2])
        # final_video_clip = final_video_clip.resized(height=360)
        
        final_video_outputpath = f"outputs/{self.job_id}/video/final_video.mp4"
        final_video_clip.write_videofile(final_video_outputpath, codec="libx264", audio_codec="aac",threads=15)
        end_time = time.time()
        print(f" \n\n Video generation and processing time: {end_time - start_time} seconds")

