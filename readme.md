

# Manga Downloader

## Project Overview

The **Manga Downloader** is a Python script that allows users to download manga chapters from MangaDex and save them as PDF files. It searches for manga by title, retrieves specified chapters, and compiles the images into PDFs.

## Features

- Search for manga on MangaDex by title
- Retrieve and download chapter images
- Compile images into PDF format, one PDF per chapter
- Option to download lower resolution images to save space
- Organize downloads in manga-specific directories

## Requirements

- Python 3.x
- Required modules: `requests`, `pypdf`, `tqdm`, `Pillow`

## Installation

### Option 1: Using the Batch File (Windows)

1. Open a command prompt
2. Navigate to the project directory
3. Run:
   ```
   installModule.bat
   ```

### Option 2: Manual Installation

Use pip to install the required modules:

```bash
pip install requests pypdf tqdm pillow
```

Note: The batch file installs `requests`, `pypdf`, and `tqdm`. You may need to install `pillow` separately.

## Usage

1. Run the script:
   ```
   python manga_downloader.py
   ```

2. Follow the prompts:
   - Enter the manga title
   - Specify start and end chapter numbers
   - Choose resolution option (y/n for lower resolution)

Example interaction:
```
Enter title of manga: One Piece
Enter chapter number to start download: 1
Enter chapter number to end download: 5
Want lower resolution image(y/n): n
```

## Directory Structure

```
manga-downloader/
│
├── manga_downloader.py  # Main script
├── installModule.bat    # Installation batch file
└── README.md            # This file
```

## Troubleshooting

If you encounter issues:
- Ensure you have an active internet connection
- Verify the manga title exists on MangaDex
- Check for necessary file/directory creation permissions
- Confirm valid chapter number inputs

## Notes

- The script uses a personal client API key for MangaDex. Be aware of usage limitations.
- Lower resolution option halves image dimensions, saving storage space.
- Each manga download creates a new directory for organization.

## Disclaimer

This tool is for educational purposes only. Please respect MangaDex's terms of service and support manga authors by purchasing official releases.

## Acknowledgments

This project is inspired by the [mangapark-dl](https://github.com/tohyongcheng/mangapark-dl.git) project. Special thanks to the developers of that project for their pioneering work.
