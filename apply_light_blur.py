import os
from PIL import Image, ImageFilter, ImageDraw

base_dir = r"C:\Users\hansh\Desktop\Rag Multilingual"

def subtle_feathered_blur(rel_in, regions, blur_radius=3.2, feather=10, rel_out=None):
    in_path = os.path.join(base_dir, rel_in)
    out_path = os.path.join(base_dir, rel_out)
    im = Image.open(in_path)
    has_alpha = (im.mode == 'RGBA')
    
    if has_alpha:
        base = im.convert('RGBA')
        r, g, b, a = base.split()
        rgb = Image.merge('RGB', (r, g, b))
        blurred_rgb = rgb.filter(ImageFilter.GaussianBlur(blur_radius))
        blurred = Image.merge('RGBA', (*blurred_rgb.split(), a))
    else:
        base = im.convert('RGB')
        blurred = base.filter(ImageFilter.GaussianBlur(blur_radius))
        
    mask = Image.new('L', base.size, 0)
    draw = ImageDraw.Draw(mask)
    for (x1, y1, x2, y2) in regions:
        draw.rectangle([x1 + feather, y1 + feather, x2 - feather, y2 - feather], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    
    result = Image.composite(blurred, base, mask)
    
    if rel_out:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        result.save(out_path)
        print(f"Successfully saved: {rel_out}")
    return result

if __name__ == "__main__":
    # 1. Turmeric clipping
    subtle_feathered_blur(r"Yt_video\1790084591.png", [(110, 440, 890, 850)], blur_radius=3.2, rel_out=r"Yt_video\1790084591_light_blur.png")
    subtle_feathered_blur(r"Yt_video\iloveimg-background-removed\1790084591.png", [(110, 440, 890, 850)], blur_radius=3.2, rel_out=r"Yt_video\iloveimg-background-removed\1790084591_light_blur.png")

    # 2. Neem clipping
    subtle_feathered_blur(r"Yt_video\1790084597.png", [(90, 340, 450, 870), (1220, 340, 1580, 870)], blur_radius=3.2, rel_out=r"Yt_video\1790084597_light_blur.png")
    subtle_feathered_blur(r"Yt_video\iloveimg-background-removed\1790084597.png", [(90, 340, 450, 870), (1220, 340, 1580, 870)], blur_radius=3.2, rel_out=r"Yt_video\iloveimg-background-removed\1790084597_light_blur.png")

    # 3. 2000 Attempts
    subtle_feathered_blur(r"Yt_video\1790084605.png", [(90, 355, 550, 850), (1110, 355, 1570, 850)], blur_radius=3.2, rel_out=r"Yt_video\1790084605_light_blur.png")
    subtle_feathered_blur(r"Yt_video\iloveimg-background-removed\1790084605-Photoroom.png", [(90, 355, 550, 850), (1110, 355, 1570, 850)], blur_radius=3.2, rel_out=r"Yt_video\iloveimg-background-removed\1790084605_light_blur.png")

    # 4. Heritage Under Siege
    subtle_feathered_blur(r"Yt_video\1790084612.png", [(130, 620, 1100, 870)], blur_radius=3.2, rel_out=r"Yt_video\1790084612_light_blur.png")
    subtle_feathered_blur(r"Yt_video\iloveimg-background-removed\1790084612-Photoroom.png", [(130, 620, 1100, 870)], blur_radius=3.2, rel_out=r"Yt_video\iloveimg-background-removed\1790084612_light_blur.png")
