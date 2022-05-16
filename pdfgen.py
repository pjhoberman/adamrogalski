import csv
import re

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

# pdfmetrics.registerFont(TTFont("Consola-regular", "CONSOLA.TTF"))  # todo: make sure the file exists
pdfmetrics.registerFont(TTFont("DIN", "DIN Alternate Bold.ttf"))
FONT = "DIN"  # or TimesNewRoman
# todo
#  - cut lines on right column - make sure all the cards are the same
#  - page cut lines


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


FONT_SIZE = 10
CAP_FONT_SIZE = 12


def write_special_text(c: Canvas, words: str, x: [int, float], y: [int, float], party=None):
    text = c.beginText()
    text.setTextOrigin(x, y)
    font_size = FONT_SIZE
    cap_font_size = CAP_FONT_SIZE
    # if party and len(words) + len(party) > 20:
    #     font_size = 6
    #     cap_font_size = 10
    # print(words, party, len(words) + (len(party) if party else 0), font_size)
    for letter in words:
        if letter.isupper():
            text.setFont(FONT, cap_font_size)
            text.textOut(letter)
        else:
            text.setFont(FONT, font_size)
            text.textOut(letter.upper())

    if party:
        text.setFont(FONT, cap_font_size)
        text.textOut(f" {party}")
    return text


def write_text(c: Canvas, words: str, x: [int, float], y: [int, float]):
    text = c.beginText()
    text.setTextOrigin(x, y)
    text.setFont(FONT, FONT_SIZE)
    if len(words) > 26:
        words = words.replace("/", " / ")
        words = iter(words.split())
        line1 = ""
        # line2 = ""
        while True:
            next_word = next(words)
            test = line1 + next_word + " "
            if len(test) > 26:
                break
            else:
                line1 = test
            # line1 += next(words) + " "
        line2 = next_word
        while True:
            try:
                line2 += " " + next(words)
            except StopIteration:
                break
        text.textLine(line1)
        text.textLine(line2)

    else:
        text.textOut(words)
    return text


def draw():
    page_height, page_width = LETTER
    # todo: make cards bigger, lower margin as well
    # margin = .5 * inch  # .25" on each side
    # x_margin = .41 * inch
    x_margin = 36

    # y_margin = .61 * inch
    y_margin = 36



    # card_buffer = .125 * inch  # .125" between cards
    y_card_buffer = .15 * inch * 0
    x_card_buffer = .15 * inch * 0
    # card_width = page_width / 3 - x_margin  # 3 wide
    card_width = 3.5 * inch

    # card_height = (page_height - y_margin*2 - y_card_buffer*4) / 4  # 4 high
    card_height = 2 * inch

    line_height = 20
    card_margin = 10

    image_width = 1.166 * inch
    image_height = 1.75 * inch

    people = []
    reds = []
    blues = []
    with open("output.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("party") == "D":
                blues.append(row)
            else:
                reds.append(row)
            # people.append(row)

    # people = iter(people)
    reds = iter(reds)
    blues = iter(blues)


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

    starting_coords = [x_margin/2, y_margin/2]
    first_page = True
    page = 1
    canvas = Canvas(f"output{page}.pdf", pagesize=(page_width, page_height))
    canvas.setStrokeColorRGB(0, 0, 0)

    on_reds = True
    current_list = reds
    while True:
        if not first_page:
            canvas.showPage()
        else:
            first_page = False
        page += 1
        print(f"page: {page}\n")
        # set_up_page(canvas)  # commenting out until we know proper lines
        for i in range(3):  # rows
            starting_coords[0] = x_margin/2 + (card_width + x_card_buffer) * i + x_card_buffer/2
            for j in range(4):  # columns
                try:
                    if on_reds:
                        person = next(reds)
                    else:
                        person = next(blues)
                except StopIteration:
                    if on_reds:
                        canvas.showPage()
                        on_reds = False
                        continue
                    else:
                        canvas.save()
                        return
                # print(person)
                starting_coords[1] = y_margin/2 + (card_height + y_card_buffer) * j + y_card_buffer/2

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
                if i == 0:
                    width_adjustment = 11
                else:
                    width_adjustment = 0
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
                            canvas.line(starting_coords[0] + card_width - 5 + width_adjustment*0,
                                        starting_coords[1] + card_height,
                                        starting_coords[0] + card_width + 5 + width_adjustment*0,
                                        starting_coords[1] + card_height)

                            canvas.line(starting_coords[0] + card_width + width_adjustment*0,
                                        starting_coords[1] + card_height - 5,
                                        starting_coords[0] + card_width + width_adjustment*0,
                                        starting_coords[1] + card_height + 5)

                    elif cut == "|":  # position 3
                        if position == 3:
                            canvas.line(starting_coords[0] + card_width + width_adjustment,
                                        starting_coords[1],
                                        starting_coords[0] + card_width + width_adjustment,
                                        starting_coords[1] - 10)
                        elif position == 2:
                            canvas.line(starting_coords[0] + card_width + width_adjustment,
                                        starting_coords[1] + card_height,
                                        starting_coords[0] + card_width + width_adjustment,
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
                            card_width + 12, line_height*2, stroke=0, fill=1)
                canvas.setFillColorRGB(0,0,0)
                try:
                    if person.get("saved_image") == "error":
                        img = ImageReader("no-image.jpg")
                    else:
                        img = ImageReader(person.get("saved_image"))
                    canvas.drawImage(img,
                                     x=round(starting_coords[0] + .35 * inch, 4),
                                     y=round(starting_coords[1] + .15*inch, 4),
                                     height=image_height,
                                     width=image_width,)
                except OSError:
                    pass

                x_alignment = starting_coords[0] + card_margin + image_width + inch * .3

                # State
                text = write_special_text(canvas, "Illinois",
                                          x=x_alignment,
                                          y=starting_coords[1] + card_height - line_height * 1)
                canvas.drawText(text)

                canvas.setFillColorRGB(1, 1, 1)
                # if person.get("party") == "D":
                #     canvas.setFillColorRGB(1, 1, 1)
                # else:
                #     canvas.setFillColorRGB(0, 0, 0)

                # side
                if person.get("side") == "Senate":
                    _side = "Senator"
                else:
                    _side = "Representative"
                text = write_special_text(canvas, _side, x=x_alignment,
                                          y=starting_coords[1] + card_height - line_height * 2)
                canvas.drawText(text)

                # name
                # drop middle name
                try:
                    name = " ".join(re.match(r"(.*)\s\w\.\s(.*)", person.get('name', '')).groups())
                except AttributeError:
                    name = person.get("name", "")
                text = write_special_text(canvas, name,
                                          x=x_alignment,
                                          y=starting_coords[1] + card_height - line_height * 2.75,
                                          party=f"({person.get('party')})")
                canvas.drawText(text)

                canvas.setFillColorRGB(0, 0, 0)

                # District
                text = write_text(canvas, f"{make_ordinal(person.get('district'))} District",
                                  x=x_alignment,
                                  y=starting_coords[1] + card_height - line_height * 4)
                canvas.drawText(text)

                if person.get("title") and person.get("title") != "":
                    text = write_text(canvas, person.get("title"),
                                      x=x_alignment,
                                      y=starting_coords[1] + card_height - line_height * 4.75)
                    canvas.drawText(text)

                img = ImageReader("RCMlogo-widegray.jpg")
                canvas.drawImage(img,
                                 x=x_alignment,
                                 y=starting_coords[1] + 11, #+ card_height - line_height * 6,
                                 height=11,
                                 width=54,)

    canvas.save()


if __name__ == '__main__':
    draw()
