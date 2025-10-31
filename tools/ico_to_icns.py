import sys, os, subprocess
from PIL import Image

def main(src_ico, dst_icns):
    # Make a temp .iconset dir
    iconset = dst_icns.replace('.icns', '.iconset')
    if os.path.exists(iconset):
        subprocess.run(['rm', '-rf', iconset])
    os.makedirs(iconset, exist_ok=True)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    im = Image.open(src_ico)
    for s in sizes:
        im_resized = im.resize((s, s), Image.LANCZOS)
        im_resized.save(os.path.join(iconset, f"icon_{s}x{s}.png"))

    # Use iconutil to create .icns (macOS tool)
    subprocess.check_call(['iconutil', '-c', 'icns', iconset, '-o', dst_icns])
    # Cleanup
    subprocess.run(['rm', '-rf', iconset])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tools/ico_to_icns.py <src.ico> <dst.icns>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
