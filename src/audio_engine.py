from faster_whisper import WhisperModel
from pydub import AudioSegment
from f5_tts.api import F5TTS
import os
import time


from subtitle_engine import create_collective_transcription


class AudioEngine:

    final_audio_length = 0
    final_audio_c1_length = 0 # person 1
    final_audio_c2_length = 0 # person 2

    job_id = ""

    def __init__(self, job_id):
        self.job_id = job_id
        mkdir_path = f"outputs/{self.job_id}/audio"
        os.makedirs(mkdir_path, exist_ok=True)



    def create_audio_file(self, person1_character, person1_dialogue, person2_character, person2_dialogue):
        start_time = time.time()
        person1_reference_audiopath = f"resources/reference/{person1_character}/reference_{person1_character}_1.wav"
        person2_reference_audiopath = f"resources/reference/{person2_character}/reference_{person2_character}_1.wav"
        person1_reference_textpath = f"resources/reference/{person1_character}/reference_{person1_character}_1.txt"
        person2_reference_textpath = f"resources/reference/{person2_character}/reference_{person2_character}_1.txt"
        person1_reference_text = open(person1_reference_textpath, 'r').read()
        person2_reference_text = open(person2_reference_textpath, 'r').read()

        print("Person 1 Reference Text: ", person1_reference_text)
        print("Person 2 Reference Text: ", person2_reference_text)

        person1_output_wavpath = f"outputs/{self.job_id}/audio/speaker1_wav.wav"
        person2_output_wavpath = f"outputs/{self.job_id}/audio/speaker2_wav.wav"
        final_output_wavpath = f"outputs/{self.job_id}/audio/final_audio.wav"

        f5tts = F5TTS()
        wav, sr, spec = f5tts.infer(
            ref_file=person1_reference_audiopath,
            ref_text=person1_reference_text,
            gen_text=person1_dialogue,
            file_wave=person1_output_wavpath,
            file_spec=None,
            seed=None,
            speed=0.8
        )
        wav, sr, spec = f5tts.infer(
            ref_file=person2_reference_audiopath,
            ref_text=person2_reference_text,
            gen_text=person2_dialogue,
            file_wave=person2_output_wavpath,
            file_spec=None,
            seed=None,
            speed=0.9
        )


        audioSegment_wav1 = AudioSegment.from_wav(person1_output_wavpath)
        audioSegment_wav2 = AudioSegment.from_wav(person2_output_wavpath)
        self.final_audio_c1_length = len(audioSegment_wav1) // 1000 # in seconds
        self.final_audio_c2_length = len(audioSegment_wav2) // 1000 # in seconds

        speaker1_transcription_srt_path = f"outputs/{self.job_id}/audio/speaker1_sub.srt"
        speaker2_transcription_srt_path = f"outputs/{self.job_id}/audio/speaker2_sub.srt"

        # self.create_transcription(person1_output_wavpath,speaker1_transcription_srt_path)
        # self.create_transcription(person2_output_wavpath,speaker2_transcription_srt_path)

        create_collective_transcription(self.job_id,person1_output_wavpath,person2_output_wavpath)

        # Normalize individual audio segments before merging
        audioSegment_wav1 = audioSegment_wav1.apply_gain(-audioSegment_wav1.max_dBFS)
        audioSegment_wav2 = audioSegment_wav2.apply_gain(-audioSegment_wav2.max_dBFS)

        mergedAudioSegment = audioSegment_wav1 + audioSegment_wav2

        # Add background music to merged audio
        background_music_path = "resources/audio/avatar_love.wav"
        background_music = AudioSegment.from_wav(background_music_path)
        background_music = background_music.apply_gain(-background_music.max_dBFS) # Normalize background music
        background_music = background_music  # Reduce volume by 20 dB

        if len(background_music) < len(mergedAudioSegment):
            # Loop the background music if it's shorter than the merged audio
            loops = len(mergedAudioSegment) // len(background_music) + 1
            background_music = background_music * loops
        background_music = background_music[:len(mergedAudioSegment)]
        mergedAudioSegment = mergedAudioSegment.overlay(background_music)

        # add 3 seconds of silence at the end
        silence = AudioSegment.silent(duration=3000)  # 3 seconds of silence
        mergedAudioSegment += silence
        


        mergedAudioSegment.export(final_output_wavpath, format="wav")
        self.final_audio_length = len(mergedAudioSegment) // 1000  # in seconds

        print(f"Final audio length (ms): {self.final_audio_length}")
        print(f"Person 1 audio length (ms): {self.final_audio_c1_length}")
        print(f"Person 2 audio length (ms): {self.final_audio_c2_length}")
    
        end_time = time.time()
        print(f"\n\n Audio generation and processing time: {end_time - start_time} seconds")

        return final_output_wavpath
    

    