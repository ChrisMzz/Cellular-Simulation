from PIL import Image
import numpy as np
from processing import *
from presets import Process
import json

ref_im = Image.open("NMuMG.png")
sample = ref_im.resize((690,515), Image.Resampling.NEAREST)
blurred = ref_im.resize((138,103), Image.Resampling.NEAREST)
blurred.save("blurred.png")

s = open("settings.json")
settings = json.load(s)["settings"]

steps = settings["steps"]
zeros = int(np.log10(steps))+1
process = Process(settings["preset"], steps)
print(process)
    


states = [[] for _ in range(len(list(sample.getdata())))]
gif = []
for step in range(steps):
    print(step)
    image = Image.new('RGB', (690, 515))
    data = []
    blur_pixels = np.array(blurred.getdata()).reshape(103,138,3)
    p = 0
    pixels = list(sample.getdata())
    new_states = [[] for _ in range(len(pixels))]
    for pixel in pixels:
        #print(p)
        current_bp = blur_pixels[(p//25)//138][(p//5)%138]
        adjacents = [pixels[pos] for pos in get_current_adjacents(p)]
        pixel, new_states[p] = process(p, pixel, current_bp, step, adjacents, states)
        p += 1
        data.append(pixel)
    states = new_states
    sample.putdata(data)
    filename = "0"*zeros + str(step)
    sample.save(f"dump/saved_{filename[-zeros:]}.png")
    blurred = sample.resize((138,103), Image.Resampling.NEAREST)
    blurred.save(f"dump/blurred/blurred_{filename[-zeros:]}.png")

# image.putdata(data)
# image.save("saved.png")