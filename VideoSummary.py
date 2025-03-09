from videosummarize.VideoSummarizer import SourceConfig, Transcriber, Summarizer


class VideoSummary:
    def __init__(self, source_url_path):
        print("🔍 Starting Youtube Video Analysis...")
        sourceConfig = SourceConfig(source_type="YouTube Video",source_url=source_url_path)
        transcriber = Transcriber(sourceConfig)
        transcriber.transcribe()
        summarizer = Summarizer(transcriber)
        summarizer.process_and_summarize()
        print("📊  End Youtube Video Analysis...")