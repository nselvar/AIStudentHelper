import subprocess
import re
import os
import json
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import openai
from pytubefix import YouTube
import concurrent.futures
import time


class SourceConfig:
    def __init__(self, source_type="YouTube Video", source_url=""):
        self.type = source_type
        self.url = source_url
        self.use_youtube_captions = True
        self.language = "auto"
        self.transcription_method = "Cloud Whisper"

    def clean_youtube_url(self):
        """Removes timestamp from YouTube URLs."""
        self.url = re.sub(r'&t=\d+s?', '', self.url)


class Transcriber:
    """Handles video transcription and audio processing."""

    def __init__(self, source_config: SourceConfig):
        self.source_config = source_config
        self.transcription_text = ""
        self.transcript_file_name = ""

    def get_api_key(self):
        """Loads API key from environment variables."""
        try:
            from google.colab import userdata
            return userdata.get('OPENAI_API_KEY')
        except ImportError:
            load_dotenv()
            return os.getenv('OPENAI_API_KEY')

    def process_audio_file(self, input_path, output_path):
        """Converts audio to a lower quality format to reduce file size."""
        command_convert = [
            'ffmpeg', '-y', '-i', input_path,
            '-ar', str(8000),
            '-ac', str(1),
            '-b:a', '16k',
            output_path
        ]
        subprocess.run(command_convert, check=True)

    def download_youtube_audio_only(self):
        """Downloads audio from YouTube video."""
        yt = YouTube(self.source_config.url)
        audio_stream = yt.streams.get_audio_only()
        return audio_stream.download(output_path=".", skip_existing=True)

    def download_youtube_captions(self):
        """Fetches YouTube captions."""
        regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        video_id = re.search(regex, self.source_config.url).group(1)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except:
            for available_transcript in transcript_list:
                if available_transcript.is_translatable:
                    transcript = available_transcript.translate('en').fetch()
                    break

        self.transcription_text = ""
        for entry in transcript:
            start_time = self.seconds_to_time_format(entry['start'])
            self.transcription_text += f"{start_time} {entry['text'].strip()}\n"

        self.transcript_file_name = f"{video_id}_captions.md"

        with open(self.transcript_file_name, 'w', encoding='utf-8') as f:
            f.write(self.transcription_text)

    def transcribe(self):
        """Manages the transcription process."""
        if self.source_config.type == "YouTube Video":
            self.source_config.clean_youtube_url()

            if self.source_config.use_youtube_captions:
                self.download_youtube_captions()
            else:
                video_path = self.download_youtube_audio_only()
                processed_audio_path = os.path.splitext(video_path)[0] + '_processed.mp3'
                self.process_audio_file(video_path, processed_audio_path)
                return processed_audio_path

    @staticmethod
    def seconds_to_time_format(seconds):
        """Converts seconds into HH:MM:SS format."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


class Summarizer:
    """Handles text summarization using OpenAI API."""

    def __init__(self, transcriber: Transcriber, model="gpt-4o-mini"):
        self.transcriber = transcriber
        self.model = model
        self.client = openai.OpenAI(api_key=self.transcriber.get_api_key())
        self.parallel_api_calls = 30
        self.chunk_size = 100
        self.overlap_size = 20
        self.max_output_tokens = 4096
        self.final_summary = ""

    def summarize(self, prompt):
        """Sends request to OpenAI API for text summarization."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_summary_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_output_tokens
        )
        return completion.choices[0].message.content

    def process_and_summarize(self):
        """Processes transcription text and sends it for summarization."""
        texts = [self.transcriber.transcription_text[i:i+self.chunk_size]
                 for i in range(0, len(self.transcriber.transcription_text), self.chunk_size - self.overlap_size)]
        cleaned_texts, timestamp_ranges = self.extract_and_clean_timestamps(texts)

        summaries = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_api_calls) as executor:
            future_to_chunk = {executor.submit(self.summarize, text_chunk): idx for idx, text_chunk in enumerate(cleaned_texts)}

            for future in concurrent.futures.as_completed(future_to_chunk):
                idx = future_to_chunk[future]
                try:
                    summarized_chunk = future.result()
                    summary_piece = self.format_timestamp_link(timestamp_ranges[idx]) + "\n\n" + summarized_chunk
                    summaries.append((idx, summary_piece))
                except Exception as exc:
                    print(f'Chunk {idx} generated an exception: {exc}')
                    time.sleep(10)
                    future_to_chunk[executor.submit(self.summarize, texts[idx])] = idx

        summaries.sort()
        summary_file_path = self.transcriber.transcript_file_name.replace(".md", "_FINAL.md")
        self.final_summary = "\n\n".join([summary for _, summary in summaries])

        with open(self.transcriber.transcript_file_name.replace(".md", "_FINAL.md"), 'w') as f:
            f.write(self.final_summary)
        print(f"✅ Summary file saved at: {os.path.abspath(summary_file_path)}")

    @staticmethod
    def extract_and_clean_timestamps(text_chunks):
        """Removes timestamps and cleans text."""
        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2})')
        cleaned_texts, timestamp_ranges = [], []
        for chunk in text_chunks:
            timestamps = timestamp_pattern.findall(chunk)
            timestamp_ranges.append(timestamps[0] if timestamps else "")
            cleaned_texts.append(re.sub(timestamp_pattern, "", chunk).strip())
        return cleaned_texts, timestamp_ranges

    def format_timestamp_link(self, timestamp):
        """Formats timestamp links."""
        return f"{timestamp} - {self.transcriber.source_config.url}&t={timestamp}" if timestamp else ""

    @staticmethod
    def get_summary_prompt():
        """Fetches predefined summary prompts from a local JSON file."""
        try:
            with open(os.getcwd() +"/videosummarize/prompts.json", "r", encoding="utf-8") as file:
                print(os.getcwd() + "\n")
                data = json.load(file)
                return data.get("Summarization", "Default summarization prompt")
        except FileNotFoundError:
            print("⚠️ Error: prompts.json file not found. Using default prompt.")
            return "Summarize the text in a concise and informative way."
        except json.JSONDecodeError:
            print("⚠️ Error: Invalid JSON format in prompts.json. Using default prompt.")
            return "Summarize the text in a concise and informative way."