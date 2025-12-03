# XML to Video of Texxt

This Python desktop application converts an XML file containing keystroke and input data (from keyboard activity in Microsoft Word) into a video that visually replays the exact typing on a blank background.

## Features
- Parse XML files with keystroke data
- Render text as it would be typed, including timing
- Output a video showing the typing process
- Simple desktop GUI for file selection and video generation

## Requirements
- Python 3.8+
- moviepy
- Pillow
- lxml
- tkinter (usually included with Python)

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python main.py`
3. Use the GUI to select your XML file and generate the video. 