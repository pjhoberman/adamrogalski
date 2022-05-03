from reportlab.pdfgen.textobject import PDFTextObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER
import os
def draw():
    page_height, page_width = LETTER
    margin = .5 * inch  # .25" on each side
    card_buffer = .125 * inch  # .125" between cards

    card_width = (page_width - margin) / 3  # 4 wide
    card_height = (page_height - margin) / 4  # 3 high

    line_height = 20
    card_margin = 10

    image_width = 1.75 * inch

    starting_coords = [margin / 2, margin / 2]

    canvas = Canvas("hello.pdf", pagesize=(page_width, page_height))
    # canvas.setFillColorRGB(0, 255, 0)
    canvas.setStrokeColorRGB(0, 0, 0)
    # canvas.setLineWidth(10)

    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(starting_coords[0] + card_width/2, starting_coords[1] + card_height/2, "1")

    # draw a box
    canvas.setFillColorRGB(188/256, 123/256, 73/256)
    canvas.rect(starting_coords[0], starting_coords[1] + card_height - line_height * 4, card_width, line_height*2.5, stroke=0, fill=1)
    canvas.setFillColorRGB(0,0,0)
    # image
    canvas.drawInlineImage("senate/adriane-johnson.jpg",
                           x=starting_coords[0],
                           y=starting_coords[1],
                           height=card_height,
                           preserveAspectRatio=True)

    # State
    canvas.drawString(starting_coords[0] + card_margin + image_width, starting_coords[1] + card_height - line_height * 1, "Illinois")
    # side
    canvas.drawString(starting_coords[0] + card_margin + image_width, starting_coords[1] + card_height - line_height * 2, "Senate")
    # name
    canvas.drawString(starting_coords[0] + card_margin + image_width, starting_coords[1] + card_height - line_height * 3, "Bob Barker (D)")
    # District
    canvas.drawString(starting_coords[0] + card_margin + image_width, starting_coords[1] + card_height - line_height * 4, "123rd District")
    # Title
    canvas.drawString(starting_coords[0] + card_margin + image_width, starting_coords[1] + card_height - line_height * 5.5, "Chief of chief")




    starting_coords[0] += card_width + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "2")
    # State
    canvas.drawString(starting_coords[0] + card_margin, starting_coords[1] + card_height - line_height * 2, "Illinois")

    starting_coords[0] += card_width + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "3")

    starting_coords[0] = margin/2

    starting_coords[1] += card_height + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "4")

    starting_coords[0] += card_width + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "5")

    starting_coords[0] += card_width + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "6")

    starting_coords[0] = margin/2

    starting_coords[1] += card_height + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "7")

    starting_coords[0] += card_width + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "8")

    starting_coords[0] += card_width + card_buffer
    canvas.rect(*starting_coords, card_width, card_height, stroke=1)
    canvas.drawString(*starting_coords, "9", direction=-1)



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
