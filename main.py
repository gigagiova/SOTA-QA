import pdfplumber
from pdfplumber.ctm import CTM

x_crop = .1
y_crop = .08

with pdfplumber.open("./transcript.pdf") as pdf:

    words: [dict] = []

    # Selects page and filters only for horizontal text
    start_height = 0
    for page in pdf.pages:
        filtered_page = page.crop((page.width * x_crop, page.height * y_crop,
                                   page.width * (1 - x_crop), page.height * (1 - y_crop)))
        filtered_page = filtered_page.filter(lambda char: char["object_type"] == "char" and CTM(*char["matrix"]).skew_x == 0)
        words.extend(filtered_page.extract_words())
        start_height += page.height

    paragraphs = [{"text": words[0]["text"], "size": words[0]["bottom"] - words[0]["top"]}]

    for w in range(1, len(words)):
        height = words[w]["bottom"] - words[w]["top"]
        # If there is a new line in the document, and it is distant enough to qualify as a new paragraph append it
        if words[w]["x0"] < words[w-1]["x0"] or words[w]["top"] > words[w-1]["bottom"]:
            # If we are on a new page do nothing
            if words[w]["top"] - words[w - 1]["bottom"] < 0:
                pass
            # Current text is bigger than previous line likely because is a title, so we add a new paragraph
            if words[w]["top"] - words[w-1]["bottom"] > 2 * height or height - paragraphs[-1]["size"] > 1:
                paragraphs.append({"text": "", "size": height})
            else:
                paragraphs[-1]["text"] += "\n"

        # Add the last word to the current paragraph
        paragraphs[-1]["text"] += " " + words[w]["text"]
        paragraphs[-1]["size"] = height

    # paragraphs = list(filter(lambda pg: not re.search(erase, pg["text"]) and len(pg) < 20, paragraphs))

    for p in paragraphs:
        print(f'[{(len(p["text"].split()))}] {p["text"]}')
        print("---------------")

