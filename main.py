import os
import requests
from pypdf import PdfWriter, PdfReader, PageObject
from PIL import Image
import io
import sys
import re
from tqdm import tqdm

# Constants
MANGADEX_API = "https://api.mangadex.org"
API_KEY = "personal-client-376e5621-9f8e-4282-ae1e-a7960bbecba5-ca646298"


# Function to search for manga by title
def search_manga(title):
    """
    Search for manga on MangaDex by title.

    Args:
        title (str): The title of the manga to search for.

    Returns:
        str: Manga ID if found, None otherwise.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"title": title}
    try:
        response = requests.get(f"{MANGADEX_API}/manga", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()["data"]

        for manga in data:
            manga_id = manga["id"]
            manga_titles = manga["attributes"]["title"]

            for lang, manga_title in manga_titles.items():
                if manga_title.lower().strip() == title.lower().strip():
                    return manga_id

        print(f"Manga '{title}' not found.")
        return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None


# Function to retrieve manga title by manga ID
def get_manga_title(manga_id):
    """
    Retrieve manga title from MangaDex API using manga ID.

    Args:
        manga_id (str): The ID of the manga.

    Returns:
        str: Title of the manga if found, otherwise an error message.
    """
    endpoint = f"{MANGADEX_API}/manga/{manga_id}"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()

        manga_data = response.json()

        if "data" in manga_data and "attributes" in manga_data["data"]:
            title = manga_data["data"]["attributes"]["title"]["en"]
            return title
        else:
            return "Title not found in the response"

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# Function to retrieve chapters of a manga by manga ID
def get_chapters(manga_id):
    """
    Retrieve chapters of a manga from MangaDex API using manga ID.

    Args:
        manga_id (str): The ID of the manga.

    Returns:
        list: List of chapters data if successful, None otherwise.
    """
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        params = {"manga": manga_id, "translatedLanguage[]": "en"}
        response = requests.get(
            f"{MANGADEX_API}/chapter", headers=headers, params=params
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# Function to retrieve image URLs of a chapter by chapter ID
def get_images(chapter_id):
    """
    Retrieve image URLs of a chapter from MangaDex API using chapter ID.

    Args:
        chapter_id (str): The ID of the chapter.

    Returns:
        list: List of image URLs if successful, None otherwise.
    """
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(
            f"{MANGADEX_API}/at-home/server/{chapter_id}", headers=headers
        )
        response.raise_for_status()
        base_url = response.json()["baseUrl"]
        chapter_hash = response.json()["chapter"]["hash"]
        images = response.json()["chapter"]["data"]
        image_urls = [f"{base_url}/data/{chapter_hash}/{image}" for image in images]
        return image_urls
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# Function to save images to PDF
def save_images_to_pdf(images, pdf_path, title, progress_bar):
    """
    Save images from URLs to a PDF file.

    Args:
        images (list): List of image URLs.
        pdf_path (str): Path to save the PDF file.
        title (str): Title of the manga.
        progress_bar (tqdm): Progress bar instance for tracking progress.
    """
    pdf_writer = PdfWriter()

    if not os.path.exists(title):
        os.makedirs(title)

    pdf_path = os.path.join(title, f"{pdf_path}.pdf")

    for url in images:
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))

            width, height = image.size

            page = PageObject.create_blank_page(width=width, height=height)
            page.merge_page(PdfReader(io.BytesIO(image.tobytes())).pages[0])

            pdf_writer.add_page(page)

            progress_bar.update(1)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    with open(pdf_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)


# Function to parse command-line arguments and validate input
def getData():
    """
    Parse command-line arguments and validate input.

    Returns:
        tuple: Tuple containing title (str), startChapter (int), and endChapter (int).
    """
    if len(sys.argv) < 2:
        print("Usage: python try.py [title] [-c num1 num2]")
        sys.exit(1)

    if sys.argv[1] == "-h":
        print("Usage: python try.py [title] [-c num1 num2]")
        print("-h: Display this help message")
        sys.exit(0)

    if len(sys.argv) >= 5:
        title_arg = sys.argv[1]
        flag = sys.argv[2] if len(sys.argv) > 2 else None
        startChapter = sys.argv[3] if len(sys.argv) > 3 else 1
        endChapter = sys.argv[4] if len(sys.argv) > 4 else ""

        if flag != "-c":
            print("Invalid flag! Use '-c'.")
            sys.exit(1)

    title_pattern = r"^\[(.+)\]$"
    match = re.match(title_pattern, title_arg)
    if not match:
        print("Title should be enclosed in square brackets, e.g., [title].")
        sys.exit(1)

    title = match.group(1)

    try:
        startChapter = int(startChapter)
        endChapter = int(endChapter)
    except ValueError:
        print("start and end of chapter should be integers.")
        sys.exit(1)

    return title, startChapter, endChapter


# Main function to orchestrate the download process
def main():
    """
    Main function to orchestrate the manga download process.
    """
    title, start_chapter, end_chapter = getData()
    manga_id = search_manga(title)
    if manga_id is None:
        print(f"Could not find manga with title '{title}'.")
        return
    chapter_ids = get_chapters(manga_id)

    if not chapter_ids:
        print(f"No chapters found for in database '{title}'.")
        return

    if (
        start_chapter < 1
        or end_chapter < start_chapter
        or end_chapter > len(chapter_ids)
    ):
        print("Invalid chapter range.")
        return

    for i in range(start_chapter, end_chapter + 1):
        chapter_id = chapter_ids[i - 1]["id"]
        print(f"Downloading Chapter {i}...")
        images = get_images(chapter_id)
        progress_bar = tqdm(total=len(images), desc=f"Chapter {i}", unit="image")  # type: ignore
        save_images_to_pdf(images, f"Chapter_{i}", title, progress_bar)
        progress_bar.close()
        print(f"Chapter {i} saved as PDF.")


if __name__ == "__main__":
    main()
