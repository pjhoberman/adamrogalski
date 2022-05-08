import csv

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.textobject import PDFTextObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER
import os

# pdfmetrics.registerFont(TTFont("Consola-regular", "CONSOLA.TTF"))  # todo: make sure the file exists
pdfmetrics.registerFont(TTFont("TimesNewRoman", "Times New Roman.ttf"))
FONT = "Times-Roman"  # or TimesNewRoman
# todo
#  - extra long strings


def make_ordinal(n):
    """
    https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    """
    n = int(n)
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def write_special_text(c: Canvas, words: str, x: [int, float], y: [int, float], party=None):
    text = c.beginText()
    text.setTextOrigin(x, y)
    for letter in words:
        if letter.isupper():
            text.setFont(FONT, 10)
            text.textOut(letter)
        else:
            text.setFont(FONT, 6)
            text.textOut(letter.upper())

    if party:
        text.setFont(FONT, 10)
        text.textOut(f" {party}")
    return text


def write_text(c: Canvas, words: str, x: [int, float], y: [int, float]):
    text = c.beginText()
    text.setTextOrigin(x, y)
    text.setFont(FONT, 8)
    text.textOut(words)
    return text


def draw():
    page_height, page_width = LETTER

    # margin = .5 * inch  # .25" on each side
    x_margin = .41 * inch
    y_margin = .61 * inch
    # card_buffer = .125 * inch  # .125" between cards
    y_card_buffer = .15 * inch
    x_card_buffer = .15 * inch
    card_width = page_width / 3 - x_margin  # 3 wide
    card_height = (page_height - y_margin*2 - y_card_buffer*4) / 4  # 4 high

    line_height = 20
    card_margin = 10

    image_width = 1 * inch
    image_height = 1.5 * inch

    people = []
    with open("output.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            people.append(row)

    people = iter(people)

    def set_up_page(c):
        # draw page markers
        # bottom left
        c.line(x_margin/2, y_margin, x_margin - 2, y_margin)  # horizontal
        c.line(x_margin, y_margin/2, x_margin, y_margin - 2)  # vertical

        # top left
        c.line(x_margin/2, page_height - y_margin, x_margin - 2, page_height - y_margin)  # horizontal
        c.line(x_margin, page_height - y_margin/2, x_margin, page_height - y_margin + 2)  # vertical

        # top right
        c.line(page_width - x_margin/2, page_height - y_margin, page_width - x_margin + 2, page_height - y_margin)  # horizontal
        c.line(page_width - x_margin, page_height - y_margin/2, page_width - x_margin, page_height - y_margin + 2)  # vertical

        # bottom right
        c.line(page_width - x_margin/2, y_margin, page_width - x_margin + 2, y_margin)  # horizontal
        c.line(page_width - x_margin, y_margin/2, page_width - x_margin, y_margin - 2)  # vertical

    starting_coords = [x_margin, y_margin]
    first_page = True
    page = 1
    canvas = Canvas(f"output{page}.pdf", pagesize=(page_width, page_height))
    canvas.setStrokeColorRGB(0, 0, 0)

    while True:
        if not first_page:
            canvas.showPage()
        else:
            first_page = False
        page += 1
        print(f"page: {page}\n")
        set_up_page(canvas)
        for i in range(3):  # rows
            starting_coords[0] = x_margin + (card_width + x_card_buffer) * i + x_card_buffer/2
            for j in range(4):  # columns
                try:
                    person = next(people)
                except StopIteration:
                    canvas.save()
                    return
                # print(person)
                starting_coords[1] = y_margin + (card_height + y_card_buffer) * j + y_card_buffer/2

                cut_lines = {
                    0: {
                        0: {0: "bottom left", 1: "-", 2: "+", 3: "|"},
                        1: {1: "-", 2: "+"},
                        2: {1: "-", 2: "+"},
                        3: {1: "top left", 2: "|"},
                    },
                    2: {
                        0: {0: "|", 1: "+", 2: "-", 3: "bottom right"},
                        1: {1: "+", 2: "-"},
                        2: {1: "+", 2: "-"},
                        3: {1: "|", 2: "top right"},
                    },
                }

                # cut lines
                cuts = cut_lines.get(i, {}).get(j, {})
                for position, cut in cuts.items():
                    if cut == "bottom left":
                        canvas.line(starting_coords[0], starting_coords[1], starting_coords[0] - 10, starting_coords[1])
                        canvas.line(starting_coords[0], starting_coords[1], starting_coords[0], starting_coords[1]-10)
                    elif cut == "top left":
                        canvas.line(starting_coords[0], starting_coords[1] + card_height, starting_coords[0] - 10, starting_coords[1] + card_height)
                        canvas.line(starting_coords[0], starting_coords[1] + card_height, starting_coords[0], starting_coords[1]+10 + card_height)
                    elif cut == "top right":
                        canvas.line(starting_coords[0] + card_width, starting_coords[1] + card_height, starting_coords[0] + card_width + 10, starting_coords[1] + card_height)
                        canvas.line(starting_coords[0] + card_width, starting_coords[1] + card_height, starting_coords[0] + card_width, starting_coords[1]+10 + card_height)
                    elif cut == "bottom right":
                        canvas.line(starting_coords[0] + card_width, starting_coords[1], starting_coords[0] + card_width + 10, starting_coords[1])
                        canvas.line(starting_coords[0] + card_width, starting_coords[1], starting_coords[0] + card_width, starting_coords[1]-10)
                    elif cut == "-":  # position 1
                        if position == 1:
                            canvas.line(starting_coords[0],
                                        starting_coords[1] + card_height,
                                        starting_coords[0] - 10,
                                        starting_coords[1] + card_height)
                        elif position == 2:
                            canvas.line(starting_coords[0] + card_width,
                                        starting_coords[1] + card_height,
                                        starting_coords[0] + card_width - 10,
                                        starting_coords[1] + card_height)
                    elif cut == "+":  # position 2
                        if position == 1:
                            canvas.line(starting_coords[0] - 5,
                                        starting_coords[1] + card_height,
                                        starting_coords[0] + 5,
                                        starting_coords[1] + card_height)

                            canvas.line(starting_coords[0],
                                        starting_coords[1] + card_height - 5,
                                        starting_coords[0],
                                        starting_coords[1] + card_height + 5)
                        elif position == 2:
                            canvas.line(starting_coords[0] + card_width - 5,
                                        starting_coords[1] + card_height,
                                        starting_coords[0] + card_width + 5,
                                        starting_coords[1] + card_height)

                            canvas.line(starting_coords[0] + card_width,
                                        starting_coords[1] + card_height - 5,
                                        starting_coords[0] + card_width,
                                        starting_coords[1] + card_height + 5)

                    elif cut == "|":  # position 3
                        if position == 3:
                            canvas.line(starting_coords[0] + card_width,
                                        starting_coords[1],
                                        starting_coords[0] + card_width,
                                        starting_coords[1] - 10)
                        elif position == 2:
                            canvas.line(starting_coords[0] + card_width,
                                        starting_coords[1] + card_height,
                                        starting_coords[0] + card_width,
                                        starting_coords[1] + card_height - 10)
                        elif position == 1:
                            canvas.line(starting_coords[0],
                                        starting_coords[1] + card_height,
                                        starting_coords[0],
                                        starting_coords[1] + card_height - 10)
                        elif position == 0:
                            canvas.line(starting_coords[0],
                                        starting_coords[1],
                                        starting_coords[0],
                                        starting_coords[1] - 10)

                # draw a box
                if person.get("party") == "R":
                    canvas.setFillColorRGB(154/256, 35/256, 35/256)  # R 154	35	35
                    # canvas.setStrokeColorRGB(0, 0, 0)
                else:
                    canvas.setFillColorRGB(37/256, 46/256, 190/256)  # D 37	46	190
                    # canvas.setStrokeColorRGB(1, 1, 1)
                canvas.rect(starting_coords[0], starting_coords[1] + card_height - line_height * 3.25,
                            card_width, line_height*2, stroke=0, fill=1)
                canvas.setFillColorRGB(0,0,0)
                try:
                    img = ImageReader(person.get("saved_image"))
                    canvas.drawImage(img,
                                     x=round(starting_coords[0] + inch * .5, 4),
                                     y=round(starting_coords[1] + y_card_buffer/2, 4),
                                     height=image_height,
                                     width=image_width,)
                except OSError:
                    pass

                # State
                text = write_special_text(canvas, "Illinois",
                                          x=starting_coords[0] + card_margin + image_width + inch * .5,
                                          y=starting_coords[1] + card_height - line_height * 1)
                canvas.drawText(text)

                if person.get("party") == "D":
                    canvas.setFillColorRGB(1, 1, 1)
                else:
                    canvas.setFillColorRGB(0, 0, 0)

                # side
                if person.get("side") == "senate":
                    _side = "Senator"
                else:
                    _side = "Representative"
                text = write_special_text(canvas, _side, x=starting_coords[0] + card_margin + image_width + inch * .5,
                                          y=starting_coords[1] + card_height - line_height * 2)
                canvas.drawText(text)

                # name
                text = write_special_text(canvas, person.get('name'),
                                          x=starting_coords[0] + card_margin + image_width + inch * .5,
                                          y=starting_coords[1] + card_height - line_height * 3,
                                          party=f"({person.get('party')})")
                canvas.drawText(text)

                canvas.setFillColorRGB(0, 0, 0)

                # District
                text = write_text(canvas, f"{make_ordinal(person.get('district'))} District",
                                  x=starting_coords[0] + card_margin + image_width + inch * .5,
                                  y=starting_coords[1] + card_height - line_height * 4)
                canvas.drawText(text)

                if person.get("title") and person.get("title") != "":
                    text = write_text(canvas, person.get("title"),
                                      x=starting_coords[0] + card_margin + image_width + inch * .5,
                                      y=starting_coords[1] + card_height - line_height * 5.25)
                    canvas.drawText(text)

    canvas.save()


if __name__ == '__main__':
    draw()
