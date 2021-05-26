import PySimpleGUI as sg
import os

class UIConfig:
    # fonts
    font_style = 'courier 10 pitch'
    font_8 = (font_style, 8)
    font_8b = (font_style, 8, 'bold')
    font_9 = (font_style, 9)
    font_9b = (font_style, 9, 'bold')
    font_11 = (font_style, 11)
    font_11b = (font_style, 11, 'bold')

    # standard_sizes
    selector_short_size = (20, 8)
    selector_long_size = (40, 8)
    required_entry_size = (17, 1)
    entry_size = (20, 1)
    types_size = (20, 1)
    input_size = (60, 1)
    multyline_size = (60, 3)

    ### globals
    # look and feel
    gui_theme_1 = 'LightBrown3'
    gui_theme_2 = 'LightBrown1'
    gui_theme_3 = 'DarkBlue13'
    gui_theme_4 = 'LightBlue'

    # selected colors
    PALE_BLUE_BUTTON_COLOR = '#A5CADD'
    YELLOW_BUTTON_COLOR = '#d8d584'
    WHITE_COLOR = '#ffffff'
    BLACK_COLOR = '#000000'

    # icons
    LOGO_ICON = os.path.join(os.path.dirname(__file__), 'icons', 'regolith-logo.png')
    ENTER_ICON = os.path.join(os.path.dirname(__file__), 'icons', 'enter.png')
    DATE_ICON = os.path.join(os.path.dirname(__file__), 'icons', 'date.png')
    FILTER_ICON = os.path.join(os.path.dirname(__file__), 'icons', 'filter.png')

    # global setup
    sg.change_look_and_feel(gui_theme_4)
    sg.set_options(icon=LOGO_ICON)
    sg.set_options(input_elements_background_color=WHITE_COLOR)
    sg.set_options(button_color=(BLACK_COLOR, YELLOW_BUTTON_COLOR))
    sg.set_options(text_color=BLACK_COLOR)
    sg.set_options(font=font_11)
    sg.set_options(element_padding=(5, 5))
    sg.set_options(border_width=2)
    sg.set_options(use_ttk_buttons=True)
    sg.set_options(ttk_theme="clam")  # 'clam', 'alt', 'default', 'classic'

    # set window position
    window = sg.Window('')
    sg.DEFAULT_WINDOW_LOCATION = map(lambda x: x / 3, window.get_screen_size())
    window.close()