from pathlib import Path
from PIL import ImageFont
from shapely.geometry import Polygon
import cv2
import os.path
import random
import subprocess
import json
from colorthief import ColorThief
import get_images


def draw_with_border(x, y, message, color_fill, color_border, font, draw):
    border_width = max((font.size // 25), 2)

    for i in range(1, border_width + 1):
        draw.text((x, y + i), message, fill=color_border, font=font)
        draw.text((x, y - i), message, fill=color_border, font=font)
        draw.text((x + i, y), message, fill=color_border, font=font)
        draw.text((x - i, y), message, fill=color_border, font=font)

        draw.text((x - i, y - i), message, fill=color_border, font=font)
        draw.text((x - i, y + i), message, fill=color_border, font=font)
        draw.text((x + i, y - i), message, fill=color_border, font=font)
        draw.text((x + i, y + i), message, fill=color_border, font=font)

    draw.text((x, y), message, fill=color_fill, font=font)

def set_font(image, message, font_name="fonts/Caveat-Bold.ttf"):
    # keep increasing font size until the font area is 1/5th the size of image
    font_size = 10
    font = ImageFont.truetype(font_name, size=font_size)
    image_area = image.size[0] * image.size[1]
    font_area = font.getsize(message)[0] * font.getsize(message)[1]
    while (image_area / 3) > font_area:
        font_size = font_size + 5
        font = ImageFont.truetype(font_name, size=font_size)
        font_area = font.getsize(message)[0] * font.getsize(message)[1]
    return font


def messages_multiline(text, font, image):
    image_size = image.size
    lines = []
    if image_size[0] > image_size[1]:
        # image_width is boxed width, if its too long, dont make text go all the way across
        image_width = image_size[0] / random.uniform(1, 1.5)
    else:
        image_width = image_size[0]
    if font.getsize(text)[0] <= image_width:
        # if it can fit in one line, don't do anything
        lines.append(text)
    else:
        words = text.split(" ")
        i = 0
        while i < len(words):
            line = ""
            while (
                i < len(words) and font.getsize(line + words[i] + " ")[0] <= image_width
            ):
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line.rstrip())
    return lines


def get_colors(file_name):
    color_thief = ColorThief(file_name)
    return color_thief.get_palette(color_count=2, quality=1)


def randomize_location(image, messages, font, faces):
    image_size = image.size
    x_coordinate = 0
    y_coordinate = 0
    for message in messages:
        font_area = font.getsize(message)
        # get widest line
        if font_area[0] > x_coordinate:
            x_coordinate = font_area[0]
        # get total line height
        y_coordinate = y_coordinate + font_area[1]
    # try to find a location for text that doesn't overflow
    # randomize locations that still fit
    placed = False
    tries = 0
    while placed is False and tries < 20:
        placed = True
        x = random.randrange(0, image_size[0] - x_coordinate)
        y = random.randrange(0, image_size[1] - y_coordinate)
        for face in faces:
            if is_intersected(face, (x, y, x + x_coordinate, y + y_coordinate)):
                placed = False
        tries = tries + 1
    get_images.logging.info("tried: %i" % tries)
    return (x, y, len(faces))


def is_intersected(face, text):
    face_polygon = Polygon(
        [(face[0], face[1]), (face[2], face[1]), (face[2], face[3]), (face[0], face[3])]
    )
    text_polygon = Polygon(
        [(text[0], text[1]), (text[2], text[1]), (text[2], text[3]), (text[0], text[3])]
    )
    return face_polygon.intersects(text_polygon)


def get_quote(p):
    with open(p, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        return random.choice(lines)

