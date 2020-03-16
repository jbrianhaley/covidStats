# Program to pull COVID-19 statistics from https://corona.help and display on Waveshare 2.9in black/red eInk display
# Code scrapes data from website by finding certain hand-picked tags in HTML.  Adding and changing countries would mean
# looking at the order of the HTML again.  I just got the eInk display connected this morning and rushed to get it working tonight.
# Output is seen in terminal and two .bmp images are created for epd display
# epd2in9b is required library from display manufacturer Waveshare

import argparse
import subprocess, datetime
from PIL import Image, ImageDraw, ImageFont
try:
    import epd2in9b
    eInk = True
except:
    eInk = False


parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument(
    '--epd', action='store_false', default=True,
    help='Force no output to eInk display')
args = parser.parse_args()

if eInk:
    if not args.epd:
        eInk = False

process = subprocess.run(['curl', 'https://corona.help/'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
process

headings = ["Worldwide Infected: ", "Worldwide Deaths: ", "US Infected: ","Switzerland Infected: ","US Deaths: ","Switzerland Deaths: "]

def getData():
    text = process.stdout
    text = text[text.index('<h5 class="mt-0 mb-4 text-white-50 font-16">'):]  #tag used for total numbers
    text = text[text.index('<h1>')+4:]
    headings[0]+=(text[:text.index('</h1>')])
    text = text[text.index('<h5 class="mt-0 mb-4 text-white-50 font-16">'):]  #tag used for total numbers
    text = text[text.index('<h1>')+4:]
    headings[1]+=(text[:text.index('</h1>')])

    for i in range(2):
        text = text[text.index('<a href="//corona.help/country/us">'):]  #United States
        text = text[text.index('<td class="text-right">')+23:]
        headings[2*i+2]+=(text[:text.index('</td>')])
        text = text[text.index('<a href="//corona.help/country/switzerland">'):]  #Switzerland
        text = text[text.index('<td class="text-right">')+23:]
        headings[2*i+3]+=(text[:text.index('</td>')])

getData()
headings.sort(reverse=True)

for i in range(2):
    headings.append(datetime.datetime.strftime(datetime.datetime.now(),'%A %m.%d.%y %H:%M:%S'))  #Timestamp twice to keep things even

font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf',18)
margin = offset = 5

blackimage = Image.new("RGB",(296,128),(255,255,255))
redimage = Image.new("RGB",(296,128),(255,255,255))
drawred = ImageDraw.Draw(redimage)
drawblack = ImageDraw.Draw(blackimage)

drawblack.rectangle((margin/2,offset/2,296-128-margin/2,128-offset/2),fill=(255,255,255),outline=(0,0,0))
drawred.rectangle((margin/2-1,offset/2-1,296-128-margin/2+1,128-offset/2+1),fill=(255,255,255),outline=(0,0,0))

print("-=-=-=-=-=-= ~ =-=-=-=-=-=-")
for item in headings:
    if headings.index(item)%2 == 1:
        drawred.text((margin,offset),item,fill=(0,0,0))
    else:
        drawblack.text((margin,offset),item,fill=(0,0,0))
    print(item)
    offset += font.getsize(headings[headings.index(item)])[1]
print("-=-=-=-=-=-= ~ =-=-=-=-=-=-")

redimage = redimage.rotate(-90,expand=1)
blackimage = blackimage.rotate(-90,expand=1)

redimage.save("redtext.bmp")
blackimage.save("blacktext.bmp")

redimage.close()
blackimage.close()

def display():
    print("Initializing epd")
    epd = epd2in9b.EPD()
    epd.init()

    frame_black = epd.get_frame_buffer(Image.open('blacktext.bmp'))
    frame_red = epd.get_frame_buffer(Image.open('redtext.bmp'))
    epd.display_frame(frame_black, frame_red)
    print("DONE")

display()
