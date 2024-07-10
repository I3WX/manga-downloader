import os
import requests
from pypdf import PdfWriter, PdfReader
from PIL import Image
import io
import sys
from tqdm import tqdm

# Constants
MANGADEX_API = "https://api.mangadex.org"
API_KEY = "personal-client-376e5621-9f8e-4282-ae1e-a7960bbecba5-ca646298"


# Function to search for manga by title
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
def get_available_chapters(manga_id):
    url = f"{MANGADEX_API}/manga/{manga_id}/aggregate"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "translatedLanguage[]": ["en"],
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        print("Raw API response:")
        print(data)

        all_chapters = []

        for volume_id, volume_data in data["volumes"].items():
            print(f"Volume {volume_id}:")
            for chapter_id, chapter_data in volume_data["chapters"].items():
                print(
                    f"  Chapter {chapter_data['chapter']}: {chapter_data.get('title', 'No Title')}"
                )
                all_chapters.append(
                    {
                        "id": chapter_data["id"],
                        "attributes": {
                            "chapter": chapter_data["chapter"],
                            "title": chapter_data.get("title", "No Title"),
                        },
                    }
                )

        return all_chapters

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return []


# Function to retrieve image URLs of a chapter by chapter ID
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


# Function to save images to PDF
def save_images_to_pdf(images, pdf_path, title, progress_bar, low_resolution=False):
    pdf_writer = PdfWriter()

    # Create directory if it does not exist
    if not os.path.exists(title):
        os.makedirs(title)

    pdf_path = os.path.join(title, f"{pdf_path}.pdf")

    for url in images:
        try:
            response = requests.get(url)
            response.raise_for_status()

            # Open the image and ensure it's valid
            image = Image.open(io.BytesIO(response.content))

            # Convert image to RGB mode if it's not
            if image.mode != "RGB":
                image = image.convert("RGB")

            if low_resolution:
                width, height = image.size
                width = width // 2
                height = height // 2
                resized_image = image.resize((int(width), int(height)))
                image = resized_image

            # Save the image to a PDF in memory
            image_pdf = io.BytesIO()
            image.save(image_pdf, format="PDF")
            image_pdf.seek(0)

            # Read the PDF from memory and merge with the PdfWriter
            image_reader = PdfReader(image_pdf)
            page = image_reader.pages[0]
            pdf_writer.add_page(page)

            progress_bar.update(1)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    with open(pdf_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)


# Function to get available chapters for a manga
def get_available_chapters(manga_id):
    url = f"{MANGADEX_API}/manga/{manga_id}/feed"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "translatedLanguage[]": ["en"],  # Use array format
        "order[chapter]": "asc",  # Order by chapter ascending
        "limit": 500,  # Limit to avoid pagination issues
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        chapters = data["data"]
        unique_chapters = {}  # To store unique chapters

        for chapter in chapters:
            chapter_num = chapter["attributes"]["chapter"]
            if chapter_num not in unique_chapters:
                unique_chapters[chapter_num] = chapter

        for chapter_num, chapter in sorted(
            unique_chapters.items(), key=lambda x: float(x[0])
        ):
            print(
                f"Chapter {chapter['attributes']['chapter']}: {chapter['attributes']['title']}"
            )

        return list(unique_chapters.values())
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# Function to parse command-line arguments and validate input
def getData():
    title = str(input("Enter title of manga: "))
    mangaId = search_manga(title)

    if not mangaId:
        print(f"Manga '{title}' not found.")
        sys.exit(1)

    chapters = get_available_chapters(mangaId)

    startChapter = int(input("Enter chapter number to start download: "))
    endChapter = int(input("Enter chapter number to end download: "))

    resolution = input("Want lower resolution image(y/n): ").lower()

    if resolution == "y":
        lower_resolution = True
    elif resolution == "n":
        lower_resolution = False
    else:
        print("Choose resolution only between y/n.")
        sys.exit(1)

    return title, mangaId, startChapter, endChapter, lower_resolution, chapters


# Main function to orchestrate the download process
def main():
    title, manga_id, start_chapter, end_chapter, lower_resolution, chapters = getData()

    if not chapters:
        print(f"No chapters found for '{title}'.")
        return

    start_index = next(
        (
            i
            for i, ch in enumerate(chapters)
            if float(ch["attributes"]["chapter"]) >= start_chapter
        ),
        None,
    )
    end_index = next(
        (
            i
            for i, ch in enumerate(chapters)
            if float(ch["attributes"]["chapter"]) > end_chapter
        ),
        len(chapters),
    )

    if start_index is None or start_index >= len(chapters):
        print("Invalid start chapter.")
        return

    for chapter in chapters[start_index:end_index]:
        chapter_num = chapter["attributes"]["chapter"]
        chapter_id = chapter["id"]
        print(f"Downloading Chapter {chapter_num}...")
        images = get_images(chapter_id)
        progress_bar = tqdm(
            total=len(images), desc=f"Chapter {chapter_num}", unit="image"
        )
        save_images_to_pdf(
            images, f"Chapter_{chapter_num}", title, progress_bar, lower_resolution
        )
        progress_bar.close()
        print(f"Chapter {chapter_num} saved as PDF.")


main()
