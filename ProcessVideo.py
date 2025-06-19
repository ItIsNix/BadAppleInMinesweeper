import cv2, zipfile, os, json, sys
from moviepy import VideoFileClip
from tqdm import tqdm

video_path = sys.argv[1]
output_archive_path = f'{os.path.splitext(os.path.basename(video_path))[0]}.mnsp'

width, height = int(sys.argv[2]), int(sys.argv[3])

positions = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (-1, 1), (1, -1), (-1, -1)
]

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise Exception('Error opening the video file.')

processed_frames = []

with tqdm(total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), desc='Processing Video', unit='frame') as pbar:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        resized = cv2.resize(frame, (width, height))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                brightness = gray[y, x]
                row.append('x' if brightness < 128 else '0')
            grid.append(row)

        for y in range(height):
            for x in range(width):
                if grid[y][x] == '0':
                    count = 0
                    for dx, dy in positions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if grid[ny][nx] == 'x':
                                count += 1
                    grid[y][x] = str(count)

        frame_str = '\n'.join(''.join(row) for row in grid)
        processed_frames.append(frame_str)
        pbar.update(1)

cap.release()
cv2.destroyAllWindows()

video_clip = VideoFileClip(video_path)
audio_clip = video_clip.audio
audio_clip.write_audiofile('audio.mp3')

with open('video.txt', 'w') as file:
    file.write('-\n'.join(processed_frames))

with open("info.json", "w") as f:
    json.dump({"FPS": round(video_clip.fps), "WIDTH": width, "HEIGHT": height}, f, indent=4)

audio_clip.close()
video_clip.close()

with zipfile.ZipFile(output_archive_path, 'w') as arch:
    arch.write('audio.mp3')
    arch.write('video.txt')
    arch.write('info.json')

os.remove('audio.mp3')
os.remove('video.txt')
os.remove('info.json')