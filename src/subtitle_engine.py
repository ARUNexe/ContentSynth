from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from faster_whisper import WhisperModel
from pydub import AudioSegment
import os



def format_time(seconds):
        seconds = (seconds)
        print("Formatting time for seconds:", seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"\


def create_transcription_withoffset(job_id,audio_filepath,srt_filename,max_sentence_words_length,second_offset):
        model_size = "tiny.en"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_filepath, word_timestamps=True)

        print("SEGMENT INFO:", info)

        subtitle_folder = f"outputs/{job_id}/subtitle"
        os.makedirs(subtitle_folder, exist_ok=True)


        # writer = get_writer("srt", subtitle_folder)
        # writer_options = {
        #     "max_words_per_line": max_sentence_words_length,
        #     "max_line_count": 1
        # } 

        # writer(segments, audio_filepath, writer_options)

        with open(srt_filename, 'w', encoding='utf-8') as srt_file:
            word_count = 0
            srt_line_list = []
            previous_end_time = 0
            for segment in segments:
                print("\n Processing segment:", segment)
                for word_info in segment.words:
                    print(f"Word: {word_info.word}, start: {word_info.start}, end: {word_info.end}")
                    if len(srt_line_list) == max_sentence_words_length:
                        print("Max words reached, writing line to SRT")
                        print("SRT LINE LIST:", srt_line_list)
                        start_time = srt_line_list[0].start
                        if(start_time - previous_end_time) > 0.5:
                            start_time = previous_end_time + 0.1
                        previous_end_time = srt_line_list[-1].end
                        end_time = srt_line_list[-1].end
                        texts = " ".join([w.word for w in srt_line_list])
                        line_out = f"{word_count + 1}\n{format_time(start_time + second_offset)} --> {format_time(end_time + second_offset)}\n{texts}\n\n"
                        srt_file.write(line_out)
                        srt_file.flush()
                        srt_line_list.clear()
                        word_count += 1
                    
                    srt_line_list.append(word_info)
            if len(srt_line_list) > 0:
                start_time = srt_line_list[0].start
                end_time = srt_line_list[-1].end
                previous_end_time = srt_line_list[-1].end
                texts = " ".join([w.word for w in srt_line_list])
                line_out = f"{word_count + 1}\n{format_time(start_time + second_offset)} --> {format_time(end_time + second_offset)}\n{texts}\n\n"
                srt_file.write(line_out)
                srt_file.flush()
                srt_line_list.clear()
            
            return previous_end_time

                # end_time = format_time(segment.end + second_offset)
                # text = segment.text
                # segment_id = segment.id + 1
                # line_out = f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
                # # print(line_out)
                # srt_file.write(f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n")
                # srt_file.flush() 




def create_collective_transcription(job_id,speaker1_audio_path,speaker2_audio_path):
        speaker1_transcription_srt_path = f"outputs/{job_id}/subtitle/speaker1_sub.srt"
        speaker2_transcription_srt_path = f"outputs/{job_id}/subtitle/speaker2_sub.srt" 

        speaker1_audio_clip = AudioSegment.from_wav(speaker1_audio_path)
        speaker2_audio_clip = AudioSegment.from_wav(speaker2_audio_path)

        speaker1_audio_clip = speaker1_audio_clip.apply_gain(-speaker1_audio_clip.max_dBFS)
        speaker2_audio_clip = speaker2_audio_clip.apply_gain(-speaker2_audio_clip.max_dBFS)

        speaker1_audio_duration = len(speaker1_audio_clip) // 1000 # in seconds
        speaker2_audio_duration = len(speaker2_audio_clip) // 1000 # in seconds

        max_sentence_words_length = 4  # in seconds


        end_time = create_transcription_withoffset(job_id,speaker1_audio_path,speaker1_transcription_srt_path,max_sentence_words_length,0)
        end_time = create_transcription_withoffset(job_id,speaker2_audio_path,speaker2_transcription_srt_path,max_sentence_words_length,end_time+0.2)



    
    


   



        