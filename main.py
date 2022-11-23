import os
import requests
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

global finalImage, finalImageHolder


def processImage(image: Image) -> Image:
    """Processes the image to be used in the card, both a smaller version and a darker version"""
    height = image.height
    width = image.width
    if height > width:
        image = image.resize((960, int((960 / width) * height)))
        image = image.crop((0, int((image.height - 960) / 2), 960, int((image.height + 960) / 2)))
    else:
        image = image.resize((int((960 / height) * width), 960))
        image = image.crop((int((image.width - 960) / 2), 0, int((image.width + 960) / 2), 960))
    smallImage = image.copy()
    smallImage.thumbnail((340, 340))
    image = Image.eval(image, lambda x: x * 0.65)
    return image, smallImage


def drawImage(name: str, numLine: str, backImage: Image, smallImage: Image, img: Image, fonts: tuple) -> Image:
    """Draws the card to the image, along with the text"""
    helvetica, helveticaSmall, helveticaBold, majorMonoFront, majorMonoBack = fonts
    img.paste(backImage, (0, 0))
    draw = ImageDraw.Draw(img)
    img.paste(smallImage, (310, 255))
    draw.rectangle(((10, 10), (950, 950)), outline=(255, 255, 255), width=3)
    draw.rectangle(((310, 705), (650, 560)), fill=(255, 255, 255), outline=(255, 255, 255), width=0)
    draw.rectangle(((310, 705), (320, 255)), fill=(255, 255, 255), outline=(255, 255, 255), width=0)
    draw.rectangle(((640, 705), (650, 255)), fill=(255, 255, 255), outline=(255, 255, 255), width=0)
    draw.rectangle(((310, 264), (650, 255)), fill=(255, 255, 255), outline=(255, 255, 255), width=0)
    draw.text((336, 575), "PANTONE", font=helveticaBold, fill=(0, 0, 0))
    draw.text((515, 584), "©", font=helveticaSmall, fill=(122, 122, 122))
    draw.text((336, 618), numLine, font=helvetica, fill=(122, 122, 122))
    draw.text((336, 646), name, font=helvetica, fill=(122, 122, 122))
    num1, num2 = numLine.split(" - ")
    num2 = num2.split(" ")[0]
    textImage = Image.new('RGBA', (960, 960), color=(255, 255, 255, 0))
    textDraw = ImageDraw.Draw(textImage)
    textDraw.text(((960 - majorMonoBack.getlength(num1)) / 2, 335), num1, font=majorMonoBack, fill=(255, 255, 255, 115))
    textDraw.text(((960 - majorMonoBack.getlength(num1)) / 2 + 1, 335), num1, font=majorMonoBack, fill=(255, 255, 255, 115))
    textDraw.text(((960 - majorMonoBack.getlength(num1)) / 2 - 1, 335), num1, font=majorMonoBack, fill=(255, 255, 255, 115))
    textDraw.text(((960 - majorMonoFront.getlength(num2)) / 2, 375), num2, font=majorMonoFront, fill=(255, 255, 255, 255))
    textDraw.text(((960 - majorMonoFront.getlength(num2)) / 2 + 3, 375), num2, font=majorMonoFront, fill=(255, 255, 255, 255))
    textDraw.text(((960 - majorMonoFront.getlength(num2)) / 2 - 3, 375), num2, font=majorMonoFront, fill=(255, 255, 255, 255))
    img = img.convert("RGBA")
    textImage = textImage.convert("RGBA")
    img = Image.alpha_composite(img, textImage)
    return img


def createImage(name: str, numLine: str, image: Image) -> None:
    """Creates the image and displays it to the screen"""
    global finalImageHolder, finalImage
    helvetica = ImageFont.truetype("venv/fonts/helveticaneue.ttf", 24)
    helveticaSmall = ImageFont.truetype("venv/fonts/helveticaneue.ttf", 8)
    helveticaBold = ImageFont.truetype("venv/fonts/HelveticaNeue Bold.ttf", 36)
    majorMonoFront = ImageFont.truetype("venv/fonts/MajorMonoDisplay-Regular.ttf", 90)
    majorMonoBack = ImageFont.truetype("venv/fonts/MajorMonoDisplay-Regular.ttf", 160)
    backImage, smallImage = processImage(image)
    img = Image.new('RGB', (960, 960), color=(0, 0, 0))
    img = drawImage(name, numLine, backImage, smallImage, img, (helvetica, helveticaSmall, helveticaBold, majorMonoFront, majorMonoBack))
    finalImage = img
    phScaled = ImageTk.PhotoImage(img.resize((250, 250)))
    finalImageHolder.grid_forget()
    finalImageHolder = tk.Label(image=phScaled)
    finalImageHolder.grid(row=4, column=0, columnspan=2)
    finalImageHolder.image = phScaled


def createUI() -> None:
    """Creates the UI for the program"""
    global finalImageHolder
    root = tk.Tk()
    root.title("Spotify Album Cover Generator")
    root.geometry("255x345")
    root.resizable(False, False)
    tk.Label(root, text="Name").grid(row=0, column=0)
    tk.Label(root, text="Number Line").grid(row=1, column=0)
    tk.Label(root, text="Image URL").grid(row=2, column=0)
    name = tk.Entry(root)
    name.grid(row=0, column=1)
    numLine = tk.Entry(root)
    numLine.grid(row=1, column=1)
    url = tk.Entry(root)
    url.grid(row=2, column=1)
    tk.Button(root, text="Generate", command=lambda: createImage(name.get(), numLine.get(), Image.open(
        requests.get(url.get(), stream=True).raw))).grid(row=3, column=0)
    tk.Button(root, text="Save", command=lambda: saveImage(finalImage)).grid(row=3, column=1)

    def saveImage(img: Image) -> None:
        """Saves the image to a file in the users download folder"""
        global finalImageHolder
        img.save(os.path.expanduser(f"~/Downloads/{name.get()}.png"))
        name.delete(0, tk.END)
        numLine.delete(0, tk.END)
        url.delete(0, tk.END)
        finalImageHolder.grid_forget()
        finalImageHolder = tk.Label(image=phScaled)
        finalImageHolder.grid(row=4, column=0, columnspan=2)
        finalImageHolder.image = phScaled

    finalImageHolder = tk.Label()
    finalImageHolder.grid(row=4, column=0, columnspan=2)
    phScaled = ImageTk.PhotoImage(Image.new('RGB', (250, 250), color=(0, 0, 0)))
    finalImageHolder = tk.Label(image=phScaled)
    finalImageHolder.grid(row=4, column=0, columnspan=2)
    finalImageHolder.image = phScaled
    root.mainloop()


if __name__ == '__main__':
    createUI()
