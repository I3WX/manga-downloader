import os
from tkinter.ttk import Progressbar
import requests
from pypdf import PdfWriter, PdfReader, PageObject
from PIL import Image
import io
import sys
import re
from tqdm import tqdm

MANGADEX_API = "https://api.mangadex.org"
API_KEY = "personal-client-376e5621-9f8e-4282-ae1e-a7960bbecba5-ca646298"


def search_manga(title):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"title": title}
    try:
        response = requests.get(f"{MANGADEX_API}/manga", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()["data"]

        for manga in data:
            manga_id = manga["id"]
            manga_titles = manga["attributes"]["title"]

            # Compare the provided title with all available titles in different languages
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


def get_manga_title(manga_id):

    # Endpoint for getting manga details
    endpoint = f"{MANGADEX_API}/manga/{manga_id}"

    try:
        # Make a GET request to the MangaDex API
        response = requests.get(endpoint)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the JSON response
        manga_data = response.json()

        # Extract the title from the response
        if "data" in manga_data and "attributes" in manga_data["data"]:
            title = manga_data["data"]["attributes"]["title"]["en"]
            return title
        else:
            return "Title not found in the response"

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


def get_chapters(manga_id):
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


def get_images(chapter_id):
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


def save_images_to_pdf(images, pdf_path, title, progress_bar):
    pdf_writer = PdfWriter()

    if not os.path.exists(title):
        os.makedirs(title)

    pdf_path = os.path.join(title, f"{pdf_path}.pdf")

    for url in images:
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))

            # Get the dimensions of the image
            width, height = image.size

            # Create a page with the same size as the image
            page = PageObject.create_blank_page(width=width, height=height)

            # Convert image to PDF and read it
            image_pdf = io.BytesIO()
            image.save(image_pdf, format="PDF")
            image_pdf.seek(0)
            image_reader = PdfReader(image_pdf)

            # Merge the image PDF onto the blank page
            page.merge_page(image_reader.pages[0])

            # Add the page to the writer
            pdf_writer.add_page(page)

            progress_bar.update(1)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    with open(pdf_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)


def getData():
    if len(sys.argv) < 2:
        print("Usage: python try.py [title] [-c num1 num2]")
        sys.exit(1)

    if sys.argv[1] == "-h":
        print("Usage: python try.py [title] [-c num1 num2]")
        print("-h: Display this help message")
        sys.exit(0)

    if len(sys.argv) >= 5:
        title_arg = sys.argv[1]  # Title (e.g., '[I want to eat your pancreas]')
        flag = sys.argv[2] if len(sys.argv) > 2 else None  # The flag (should be '-c')
        startChapter = sys.argv[3] if len(sys.argv) > 3 else 1  # First number (e.g., 1)
        endChapter = (
            sys.argv[4] if len(sys.argv) > 4 else ""
        )  # Second number (e.g., 25)

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


def main():
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
