"""python3 scripts/podcast/check_mark.py <img.jpg> x y w h -> writes <img>.check.jpg with the mark box drawn (measure, don't eyeball)."""
import subprocess, sys
f, *m = sys.argv[1:]; x, y, w, h = map(float, m)
W, H = map(int, subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', f]).decode().split(','))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', f'drawbox=x={W*x/100}:y={H*y/100}:w={W*w/100}:h={H*h/100}:color=red@0.9:t=5,scale=900:-1', f.replace('.jpg', '.check.jpg')], check=True)
