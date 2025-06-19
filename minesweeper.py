import pygame as pg
import os, zipfile, tempfile, json, sys

pg.init()

if getattr(sys, 'frozen', False):
    folder = os.path.dirname(sys.executable)
else:
    folder = os.path.dirname(os.path.abspath(__file__))

print("Looking for .mnsp files in:", folder)

mnsp_file = None
for f in os.listdir(folder):
    if f.lower().endswith('.mnsp'):
        mnsp_file = f
        break

if mnsp_file is None:
    raise NameError("Can't find .mnsp file.")

print("Trying to open:", mnsp_file)
with zipfile.ZipFile(mnsp_file, 'r') as archive:

    with archive.open("video.txt", "r") as f:
        content = f.read().decode().split("-\r\n")

    audio_data = archive.read("audio.mp3")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        tmp_audio.write(audio_data)
        tmp_audio_path = tmp_audio.name

    with archive.open("info.json") as data:
        json_bytes = data.read()
        json_text = json_bytes.decode('utf-8')
        info = json.loads(json_text)

pg.mixer.init()
pg.mixer.music.load(tmp_audio_path)
pg.mixer.music.set_volume(1)

gridx, gridy = info["WIDTH"], info["HEIGHT"]
screen = pg.display.set_mode((gridx * 16 + 20, gridy * 16 + 64))
clock = pg.time.Clock()
fps = info["FPS"]


pg.display.set_caption("Minesweeper")
isRunning = True

class CounterDisplay:
    def __init__(self, x, y, digit_width, digit_height, image_folder):
        self.x = x
        self.y = y
        self.digit_width = digit_width
        self.digit_height = digit_height
        self.image_folder = image_folder

        self.digits = {}
        for char in "-0123456789":
            img = pg.image.load(f"{image_folder}/counter{char}.png")
            self.digits[char] = pg.transform.scale(img, (digit_width, digit_height))

    def draw(self, surface, value):
        if value >= 999:
            value = 999
        try:
            value = int(float(value))
        except ValueError:
            value = 0

        value_str = str(value)
        value_str = value_str.rjust(3, '0')[-3:]

        for i, char in enumerate(value_str):
            img = self.digits.get(char, self.digits['-'])
            surface.blit(img, (self.x + i * self.digit_width, self.y))

cells, borders = [], []

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

icon = pg.image.load(resource_path('icon.png'))
pg.display.set_icon(icon)

border_dir = resource_path('assets/borders')
cell_dir = resource_path('assets/cells')

def load_images():
    for filename in sorted(os.listdir(cell_dir)):
        image = pg.image.load(os.path.join(cell_dir, filename))
        cells.append(image)

    for filename in sorted(os.listdir(border_dir)):
        image_path = os.path.join(border_dir, filename)
        image = pg.image.load(image_path)

        if filename in ['bottom.png', 'top.png']:
            border = pg.transform.scale(image, (gridx * 16, 10))
        elif filename in ['left.png', 'right.png']:
            border = pg.transform.scale(image, (10, screen.get_height()))
        else:
            border = pg.transform.scale(image, (10, 10))

        borders.append(border)
def game_borders():
    screen.blit(borders[1], (0, screen.get_height() - borders[1].get_height()))  # bottomleft
    screen.blit(borders[2], (screen.get_width() - borders[2].get_width(), screen.get_height() - borders[1].get_height()))  # bottomright
    screen.blit(borders[8], (0, 44))  # topleft
    screen.blit(borders[9], (screen.get_width() - borders[9].get_width(), 44))  # topright

    screen.blit(borders[0], (10, screen.get_height() - borders[0].get_height()))  # bottom
    screen.blit(borders[6], (screen.get_width() - borders[6].get_width(), screen.get_height() - borders[6].get_height() - 10))  # right
    screen.blit(borders[3], (0, screen.get_height() - borders[3].get_height() - 10))  # left
    screen.blit(borders[7], (10, 54 - borders[7].get_height()))  # top
    screen.blit(borders[7], (10, 0))  # top

    screen.blit(borders[8], (0, 0))  # topleft
    screen.blit(borders[9], (screen.get_width() - borders[9].get_width(), 0))  # topright

    screen.fill((195, 195, 195), (4, 47, screen.get_width() - 8, 5))
    screen.fill((195, 195, 195), (10, 10, screen.get_width() - 20, 34))

load_images()
game_borders()

timeCounter = CounterDisplay(15, 15, 13, 26, resource_path('assets/counter'))
bombCounter = CounterDisplay(screen.get_width() - 15 - 13 * 3, 15, 13, 26, resource_path('assets/counter'))
timeCounter.draw(screen, 0)
bombCounter.draw(screen, 0)

smile_face = pg.image.load(resource_path('assets/faces/smileface.png'))
smile_face_down = pg.image.load(resource_path('assets/faces/smilefacedown.png'))
click_face = pg.image.load(resource_path('assets/faces/clickface.png'))

screen.blit(smile_face, (screen.get_width() // 2 - 13, 15))

time, time_change = 0, 0
current, nextf = 0, 0
empty = 0
caption_index = 0
for y in range(gridy):
    for x in range(gridx):
        screen.blit(cells[10], (x * 16 + 10, y * 16 + 54))

while isRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            isRunning = False

        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            if 15 <= mouse_y <= 41 and screen.get_width() // 2 - 13 <= mouse_x <= screen.get_width() // 2 + 13:
                pg.display.set_caption("Minesweeper")
                screen.blit(smile_face_down, (screen.get_width() // 2 - 13, 15))
                pg.mixer.music.stop()
                pg.mixer.music.play()
                time = 0
                time_change = 1 / fps
                current = 0
                nextf = 1

        if event.type == pg.MOUSEBUTTONUP:
            screen.blit(smile_face, (screen.get_width() // 2 - 13, 15))


    if nextf == 1:
        frame = content[current].splitlines()
        empty = 0

        for y in range(len(frame)):
            for x in range(len(frame[y])):
                char = frame[y][x]
                if char == 'x':
                    index = 10
                else:
                    index = int(char)
                    empty += 1
                screen.blit(cells[index], (x * 16 + 10, y * 16 + 54))

    bombCounter.draw(screen, empty)
    timeCounter.draw(screen, time)

    # Unused captions system
    '''
    current_time = pg.mixer.music.get_pos()
    if caption_index < len(captions) and current_time >= captions[caption_index][0]:
        pg.display.set_caption(captions[caption_index][1])
        caption_index += 1
    '''

    if current + nextf < len(content):
        current += nextf
    else:
        current = 0
        nextf = 0
        time_change = 0

    time += time_change

    pg.display.update()
    clock.tick(fps)