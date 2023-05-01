from PIL import Image
import os, os.path

files = [name for name in os.listdir('dump') if os.path.isfile(f"dump/{name}")]
gif = []
print(files)
for f in files:
    gif.append(Image.open(f"dump/{f}"))
with open("name.txt") as name:
    gif[0].save(f'{name.readlines()[0][:-1]}.gif', save_all=True, optimize=False, append_images=gif[1:], loop=0)
