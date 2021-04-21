from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def imageGrid(buildsinfo):
    icon_w = 100 # img width in pixels
    icon_h = 100 # img height in pixels
    padding = 14 # padding around each image in pixels
    canvas_x = 7 # number of images horizontally
    canvas_y = 1 # number of images vertically
    width = int((icon_w + padding*2) * canvas_x + padding*2) # canvas width
    height = int((icon_h + padding*2) * canvas_y + padding*2 + 30) # canvas height
    arial = ImageFont.truetype('assets/arial.ttf', size=24)
    arialbd = ImageFont.truetype('assets/arialbd.ttf', size=18)
    recommendFont = ImageFont.truetype('assets/arialbd.ttf', size=20)
    section_w = int(icon_w + padding*2)
    builds = [] # list to store the compiled build images
    vis_icon_no = Image.open('assets/heroes_build_talent_tier_no.png')
    vis_icon_yes = Image.open('assets/heroes_build_talent_tier_yes.png')
    vis_icon_sit = Image.open('assets/heroes_build_talent_tier_situational.png')
    vis_icons = {'heroes_build_talent_tier_no': vis_icon_no,
                 'heroes_build_talent_tier_yes': vis_icon_yes,
                 'heroes_build_talent_tier_situational': vis_icon_sit}

    for name, build in buildsinfo.items():
        base = Image.new("RGBA", (width, height), color=(19, 46, 73, 255))  # Canvas for this build
        section_x = padding
        for lv_name, lv_info in build.get('levels').items():
            icon_bg = Image.open('assets/icon-bg.png')
            with Image.open(BytesIO(lv_info.get('image_data'))).convert('RGBA') as icon:
                if icon.width != 128:
                    icon = icon.resize((128, 128), resample=Image.LANCZOS)
                icon = add_corners(icon, 9)  # round the corners of the image
                icon_bg.paste(icon, (2, 2), mask=icon)
            icon = icon_bg.resize((icon_w, icon_h), resample=Image.LANCZOS)

            # Create a separate "section" image for each level, and paste it onto the base canvas when we're done.
            section = Image.new('RGBA', (section_w, height), color=(0, 0, 0, 0))
            section_draw = ImageDraw.Draw(section)
            section.paste(icon, (padding, 68), mask=icon)
            text_width = section_draw.textsize(lv_name, font=arialbd)[0]
            section_draw.text(((section_w/2 - text_width/2), 10), text=lv_name, fill=(255, 177, 0), font=arialbd) # Draw the level text

            # Create a separate image to lay out the mini solid-color icons, and paste it onto the section canvas when we're done.
            visuals_icon_width = 18
            visuals_icon_height = 18
            visuals_icon_padding = 4
            visuals = lv_info['visuals']
            visuals_canvas_w = (visuals_icon_width + visuals_icon_padding) * len(visuals) - visuals_icon_padding
            visuals_w = visuals_icon_width + visuals_icon_padding
            visuals_canvas = Image.new('RGBA', (visuals_canvas_w, visuals_icon_height), color=(0, 0, 0, 0))
            visuals_x = 0
            for v in visuals:
                vis_icon = vis_icons[v]
                visuals_canvas.paste(vis_icon, (visuals_x, 0), mask=vis_icon)
                visuals_x += visuals_w
            section.paste(visuals_canvas, (int((section_w/2 - visuals_canvas_w/2)), 38), mask=visuals_canvas)

            base.paste(section, (section_x, 0), mask=section) # paste the level section onto the build canvas
            section_x += section_w # Increase the x-coordinate for the next time through the loop.
        with Image.open('assets/toc-texture-light.jpg').convert('RGBA') as bg:
            bg.paste(base, (0, bg.height - base.height))
            bg_draw = ImageDraw.Draw(bg)
            bg_draw.text((34, 12), text=name, fill=(255, 255, 255), font=arial)
            with Image.open(f"assets/{build['recommend']}.png") as recommend:
                bg.paste(recommend, (874, 15), mask=recommend)
            recommend_text_w = bg_draw.textsize(build['recommend'], font=recommendFont)[0]
            bg_draw.text((860 - recommend_text_w, 15), text=build['recommend'], fill=build['recommend_color'], font=recommendFont)
            builds.append([build['code'], bg])
    return builds


def add_corners (im, rad):
    """
    :param im: PIL Image object.
    :param rad: Corner radius to apply to the image.
    :return: PIL Image object.
    """
    circle = Image.new ('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw (circle)
    draw.ellipse ((0, 0, rad * 2, rad * 2), fill = 255)
    alpha = Image.new ('L', im.size, 255)
    w, h = im.size
    alpha.paste (circle.crop ((0, 0, rad, rad)), (0, 0))
    alpha.paste (circle.crop ((0, rad, rad, rad * 2)), (0, h-rad))
    alpha.paste (circle.crop ((rad, 0, rad * 2, rad)), (w-rad, 0))
    alpha.paste (circle.crop ((rad, rad, rad * 2, rad * 2)), (w-rad, h-rad))
    im.putalpha (alpha)
    return im