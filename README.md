# Type to Video

This Python desktop application converts a XML, IDFX or TXT file containing keystroke and input data (from keyboard activity in Microsoft Word) into a video that visually replays the exact typing on a blank background.

## Features
- Parse files with keystroke data
- Render text as it would be typed, including timing
- Output a video showing the typing process
- Simple desktop GUI for file selection and video generation

## Requirements
- Python 3.8+
- moviepy
- Pillow
- lxml
- tkinter (usually included with Python)
- docx
- PIL
- ijson

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python main.py`
3. Use the GUI to select your XML file and generate the video. 

## Notes
1. Since there are many packages needed to be installed for this program, it is best to create a virtual environment so as to not conflict with the pre-installed packages.
    Starting a Virtual Environment:
    1. In Terminal, write:
    python -m venv myenv
    source myenv/bin/activate  
The exact way to activate the venv may differ based on the system.