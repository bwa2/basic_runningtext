# preprocess
def inews (width, height) :
    height_process_top = round((24.5 / 27) * height)
    height_process_bottom = round((26 / 27) * height)
    width_process_left = round((1.25999/7.6) * width)
    width_process_right = round((7.6/7.6) * width)

    return height_process_top, height_process_bottom,  width_process_left, width_process_right

def mnc (width, height) :
    height_process_top = round((24.5 / 27) * height)
    height_process_bottom = round((26 / 27) * height)
    width_process_left = round((1.25999/7.6) * width)
    width_process_right = round((7.6/7.6) * width)
    
    return height_process_top, height_process_bottom,  width_process_left, width_process_right
