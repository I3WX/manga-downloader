import requests
from pypdf import PdfWriter, PdfReader, PageObject
from PIL import Image
import io
import sys
import re

MANGADEX_API = "https://api.mangadex.org"
API_KEY = "personal-client-376e5621-9f8e-4282-ae1e-a7960bbecba5-ca646298"


def search_manga(title):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"title": title}
    try:
        response = requests.get(f"{MANGADEX_API}/manga", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        manga_id = data["data"][0]["id"] if data["data"] else None
        return manga_id
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


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


def save_images_to_pdf(images, pdf_name):
    pdf_writer = PdfWriter()

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

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    with open(pdf_name + ".pdf", "wb") as output_pdf:
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
        save_images_to_pdf(images, f"Chapter_{i}")
        print(f"Chapter {i} saved as PDF.")


if __name__ == "__main__":
    main()
