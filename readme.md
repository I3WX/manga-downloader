
# Manga Downloader

```markdown

## Project Overview

The **Manga Downloader** is a Python script that allows users to download manga chapters from MangaDex and save them as PDF files. This script searches for a manga by its title, retrieves the chapters within a specified range, and compiles the chapter images into PDFs.

## Features

- **Search Manga by Title**: Search for manga on MangaDex by title.
- **Retrieve Chapters**: Retrieve chapters for the specified manga.
- **Download Images**: Download chapter images from MangaDex.
- **Save to PDF**: Save the downloaded images into PDF format.

## Requirements

Before running the script, ensure you have the following installed:

- Python 3.x
- `requests` module
- `pypdf` module
- `tqdm` module
- `Pillow` module

## Installation

To install the required Python packages, you can use the provided batch file:

1. Open a command prompt.
2. Navigate to the project directory.
3. Run the batch file to install dependencies:

   ```bash
   installModule.bat
   ```

Alternatively, you can manually install the required modules using pip:

```bash
pip install requests pypdf tqdm pillow
```

## Usage

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd manga-downloader
   ```

2. **Run the Script**:

   ```bash
   python try.py [title] -c [start_chapter] [end_chapter]
   ```

   - Replace `[title]` with the title of the manga enclosed in square brackets. For example, `[One Piece]`.
   - Replace `[start_chapter]` with the starting chapter number.
   - Replace `[end_chapter]` with the ending chapter number.

3. **Example**:

   ```bash
   python try.py "[Attack on Titan]" -c 1 5
   ```

   This command downloads chapters 1 to 5 of "Attack on Titan".

## Script Arguments

- `[title]`: The title of the manga to download, enclosed in square brackets.
- `-c`: Flag indicating the chapter range.
- `[start_chapter]`: The starting chapter number.
- `[end_chapter]`: The ending chapter number.

### Notes

- Ensure that the title is exactly as it appears on MangaDex.
- The chapter range must be valid and within the available chapters for the manga.

## Directory Structure

```
manga-downloader/
│
├── try.py               # Main script
├── installModule.bat    # Batch file to install dependencies
└── README.md            # This readme file
```

## Troubleshooting

If you encounter any issues or errors while using the script:

- Ensure you have an active internet connection.
- Verify the manga title is correct.
- Check if you have the required permissions to create files in the directory.

## Acknowledgments

This project is inspired by the [mangapark-dl](https://github.com/tohyongcheng/mangapark-dl.git) project. Special thanks to the developers of that project for their pioneering work.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Disclaimer

This tool is for educational purposes only. Please respect the terms of service of MangaDex and support the manga authors by purchasing official releases.
```

### Key Improvements:
- **Headers**: Used for each section for clear separation and hierarchy.
- **Code Blocks**: Used for commands to enhance readability.
- **Lists**: Used for features and requirements to present them clearly.
- **Example Section**: Added a practical example to illustrate usage.
- **Directory Structure**: Provided as a formatted tree for clarity.
- **Links**: Used for referring to other projects or files, improving navigation.

Replace `<repository-url>` with the URL of your GitHub repository. This format ensures the `README.md` is easy to follow and visually appealing when viewed on GitHub or other Markdown-supported platforms.
