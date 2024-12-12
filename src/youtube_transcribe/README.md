# Youtube Transcribe

This module scrapes YouTube video metadata and downloads their transcripts. It also processes and labels the transcripts by querying our machine learning model and then uploads the labeled transcripts to our GCP bucket.

## Build Container

To build the container, run:

```bash
sh run_yt_transcript.sh
```

## Workflow

1. Scrape Youtube for videos based on a search string (keyword). Run it with the command:

```bash
python video_id_scraper.py --keyword
```

where you choose your own keyword.

2. Get the transcript of the Youtube videos based on the keyword search. To do this run the file:

```bash
python get_transcript.py
```

3. Level the transcript into one of our 5 language categories (A1, A2, B1, B2, C1) and upload it to our GCP bucket. To do this run the file:

```bash
python level_transcript.py
```
