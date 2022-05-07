import csv

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.textobject import PDFTextObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER
import os

# todo
#  - cut lines between cards
#  - extra long strings
#  - fonts


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



def draw():
    page_height, page_width = LETTER

    margin = .5 * inch  # .25" on each side
    x_margin = .41 * inch
    y_margin = .61 * inch
    card_buffer = .125 * inch  # .125" between cards
    y_card_buffer = .15 * inch
    x_card_buffer = .15 * inch
    card_width = page_width / 3 - x_margin  # 3 wide
    card_height = (page_height - y_margin*2 - y_card_buffer*4) / 4  # 4 high

    line_height = 20
    card_margin = 10

    image_width = 1 * inch
    image_height = 1.5 * inch



    # canvas = Canvas("hello.pdf", pagesize=(page_width, page_height))
    # # canvas.setFillColorRGB(0, 255, 0)
    # canvas.setStrokeColorRGB(0, 0, 0)
    # canvas.setLineWidth(10)


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
        # try:
        #     canvas.save()
        # except NameError:
        #     pass

        # canvas.setFillColorRGB(0, 255, 0)

        if not first_page:
            canvas.showPage()
            page += 1
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
                # print(starting_coords)
                # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
                # canvas.drawString(starting_coords[0] + card_width/2, starting_coords[1] + card_height/2, "1")

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
                else:
                    canvas.setFillColorRGB(37/256, 46/256, 190/256)  # D 37	46	190
                canvas.rect(starting_coords[0], starting_coords[1] + card_height - line_height * 3.25,
                            card_width, line_height*2, stroke=0, fill=1)
                canvas.setFillColorRGB(0,0,0)
                # if person.get("name").startswith("Norine"):
                #     image = "house/aaron-m-ortiz.jpg"
                # else:
                #     image = person.get("saved_image")
                # image
                try:
                    # todo: uncomment
                    # pass
                    img = ImageReader(person.get("saved_image"))
                    canvas.drawImage(img,
                                     x=round(starting_coords[0] + inch * .5, 4),
                                     y=round(starting_coords[1] + y_card_buffer/2, 4),
                                     height=image_height,
                                     width=image_width,)
                except OSError:
                    pass

                # State
                canvas.drawString(starting_coords[0] + card_margin + image_width + inch * .5,
                                  starting_coords[1] + card_height - line_height * 1, "Illinois")
                # side
                canvas.drawString(starting_coords[0] + card_margin + image_width + inch * .5,
                                  starting_coords[1] + card_height - line_height * 2, person.get("side"))
                # name
                canvas.drawString(starting_coords[0] + card_margin + image_width + inch * .5,
                                  starting_coords[1] + card_height - line_height * 3,
                                  f"{person.get('name')} ({person.get('party')})")
                # District
                canvas.drawString(starting_coords[0] + card_margin + image_width + inch * .5,
                                  starting_coords[1] + card_height - line_height * 4,
                                  f"{make_ordinal(person.get('district'))} District")
                # Title
                canvas.drawString(starting_coords[0] + card_margin + image_width + inch * .5,
                                  starting_coords[1] + card_height - line_height * 5.25, person.get("title"))




    # starting_coords[0] += card_width + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "2")
    # # State
    # canvas.drawString(starting_coords[0] + card_margin, starting_coords[1] + card_height - line_height * 2, "Illinois")
    #
    # starting_coords[0] += card_width + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "3")
    #
    # starting_coords[0] = margin/2
    #
    # starting_coords[1] += card_height + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "4")
    #
    # starting_coords[0] += card_width + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "5")
    #
    # starting_coords[0] += card_width + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "6")
    #
    # starting_coords[0] = margin/2
    #
    # starting_coords[1] += card_height + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "7")
    #
    # starting_coords[0] += card_width + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "8")
    #
    # starting_coords[0] += card_width + card_buffer
    # canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    # canvas.drawString(*starting_coords, "9", direction=-1)



    # canvas.rect(1*inch, 1*inch, 5*inch, 5*inch, fill=1)  # from bottom
    # textobject = PDFTextObject(canvas=canvas)
    # textobject.setTextOrigin(8*inch, 10*inch)
    # textobject.setTextTransform(1,1,1,1,1,1)
    # textobject.textOut("test")
    # canvas.drawText(textobject)
    canvas.save()
    # canvas.drawString(10, 10, "direction = 1", direction=1)
    # canvas.drawString(20, 20, "direction = -1", direction=-1)

if __name__ == '__main__':
    draw()
