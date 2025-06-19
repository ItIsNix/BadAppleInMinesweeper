# Bad apple!! in Minesweeper
Minesweeper recreation that plays videos, mainly the Bad Apple!! MV.

You can run Minesweeper.exe and click on the smiling face icon to start playing the video.

## Make Your Own `.mnsp` File
The video is stored in a completely original, totally-not-a-ZIP archive with the `.mnsp` extension.
To create your own `.mnsp` file run this command in the release or the source code directory:
```bash
py ProcessVideo.py "VideoPATH.mp4" WIDTH HEIGHT
```
Replace `YourVideo.mp4` with your video file.
And `WIDTH` and `HEIGHT` with Integers indicating the number of cells.

Then place the generated file in the directory of the .exe
**Note: ** It will load the files sorted by name.

Example of the included file:
```bash
py ProcessVideo.py "badapple.mp4" 50 38
```

Made completely with python's pygame
