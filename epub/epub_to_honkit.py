import ebooklib
from ebooklib import epub
import os
from bs4 import BeautifulSoup

def epub_to_honkit(epub_file):
    # Create a new directory for the Honkit project
    project_dir = os.path.splitext(os.path.basename(epub_file))[0]
    os.makedirs(project_dir, exist_ok=True)

    # Open the EPUB file
    book = epub.read_epub(epub_file)

    # Iterate over each HTML file in the EPUB
    chapters = []
    chapter_index = 0
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(item.get_content(), 'html.parser')

            # Find the chapter title (h1)
            chapter_title = soup.find('h1')
            if chapter_title:
                chapter_title = chapter_title.text.strip()
                chapter_dir = os.path.join(project_dir, f'chapter{chapter_index:02d}')
                os.makedirs(chapter_dir, exist_ok=True)

                # Find all sections (h2) in the chapter
                sections = soup.find_all('h2')
                section_index = 0

                # Iterate over all paragraphs in the chapter
                for paragraph in soup.find_all('p'):
                    # If we've reached a new section, create a new file
                    if section_index < len(sections) and paragraph.find_previous('h2') == sections[section_index]:
                        section_title = sections[section_index].text.strip()
                        section_index += 1
                        section_file = os.path.join(chapter_dir, f'{section_index-1:02d}.md')
                        with open(section_file, 'w') as f:
                            f.write(f'# {section_title}\n\n')

                    # Write the paragraph to the current section file
                    section_file = os.path.join(chapter_dir, f'{section_index-1:02d}.md' if section_index > 0 else f'00.md')
                    with open(section_file, 'a') as f:
                        f.write(paragraph.text.strip() + '\n\n')

                # If there are no sections, create a single file for the chapter
                if section_index == 0:
                    chapter_file = os.path.join(chapter_dir, '00.md')
                    with open(chapter_file, 'w') as f:
                        f.write(f'# {chapter_title}\n\n')
                        for paragraph in soup.find_all('p'):
                            f.write(paragraph.text.strip() + '\n\n')

                # Create a SUMMARY.md file for the chapter
                summary_file = os.path.join(chapter_dir, 'SUMMARY.md')
                with open(summary_file, 'w') as f:
                    f.write(f'# {chapter_title}\n\n')
                    f.write('------\n\n')
                    for i, section in enumerate(sections):
                        section_title = section.text.strip()
                        f.write(f'- [{section_title}]({i:02d}.md)\n')
                    if len(sections) == 0:
                        f.write(f'- [{chapter_title}](00.md)\n')

                chapters.append((chapter_title, chapter_dir, sections))
                chapter_index += 1

    # Create a master SUMMARY.md file at the project root
    master_summary_file = os.path.join(project_dir, 'SUMMARY.md')
    with open(master_summary_file, 'w') as f:
        f.write('# Summary\n\n')
        f.write('- [Intro](README.md)\n')
        f.write('- [About](gitbook/README.md)\n\n')
        f.write('## Content\n\n')
        for chapter_title, chapter_dir, sections in chapters:
            f.write(f'- [{chapter_title}](gitbook/markdown/zh/{os.path.basename(chapter_dir)}/SUMMARY.md)\n')
            for i, section in enumerate(sections):
                section_title = section.text.strip()
                f.write(f'    - [{section_title}](gitbook/markdown/zh/{os.path.basename(chapter_dir)}/{i:02d}.md)\n')
            if len(sections) == 0:
                f.write(f'    - [{chapter_title}](gitbook/markdown/zh/{os.path.basename(chapter_dir)}/00.md)\n')

def main():
    epub_file = input("Please enter the path to the EPUB file: ")
    if not os.path.exists(epub_file):
        print("The file does not exist.")
        return
    if not epub_file.endswith('.epub'):
        print("The file is not an EPUB file.")
        return
    epub_to_honkit(epub_file)
    print("Conversion complete.")

if __name__ == "__main__":
    main()
