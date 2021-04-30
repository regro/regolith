import os
import yaml
import PySimpleGUI as sg
from regolith.schemas import SCHEMAS

window = sg.Window('')
sg.DEFAULT_WINDOW_LOCATION = map(lambda x: x / 3, window.get_screen_size())
window.close()


class DataBase:
    ext = '.yml'
    def __init__(self, path):
        self.db = yaml.safe_load(path)


class EntryElements(object):
    """
    an entry object components - used to define what layout to use and its content

    comments: I use __init__ and do not set a class-object since I want
              to setup a clean item every iteration
    """

    def __init__(self):
        self.description = None  # str
        self.required = None  # bool
        self.type = None  # str
        self.anyof_type = None  # list
        self.schema = None  # dict


class UIConfig:
    # ui config
    required_entry_size = (13, 1)
    entry_size = (15, 1)
    types_size = (10, 1)
    input_size = (30, 1)
    multyline_size = (30, 3)


class EntryLayouts(UIConfig):
    """
    The entry ui layout
    """

    def __init__(self, layout, entry):
        self.layout = layout
        self.entry = entry

    def required_entry(self):
        layout.append([sg.Text('*', text_color='red')])
        layout[-1].extend([sg.Text(self.entry, size=self.required_entry_size)])

    def entry(self):
        layout.append([sg.Text(self.entry, size=self.entry_size)])

    def types(self, types: [list, str]):
        if isinstance(types, str):
            types = [types]
        self.layout[-1].extend([sg.Text(str(types), size=(10, 1))])

    def input(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry)])

    def date(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry),
                                sg.Button('date', key=f'@get_date_{self.entry}')])

    def multyline(self, tooltip):
        self.layout[-1].extend([sg.Multiline('', size=self.multyline_size, tooltip=tooltip, key=self.entry)])

    def nested_schema(self, tooltip):
        self.layout[-1].extend([sg.Button("+", tooltip=tooltip, key=f"@enter_schema_{self.entry}")])


targets = ["projecta"]  # list of target schemas

schema_structure = {'key', 'type'}

layout = list()  # initiate ui layout


def _setter(entry_elements: EntryElements, elements: dict):
    """
    set entry elements and assert their existence

    Parameters
    ----------
    entry_elements: EntryElements
        initiated EntryElements class object
    elements: dict
        the schema elements

    Returns
    -------

    """
    for element, val in elements:
        entry_elements.__setattr__(element, val)
    assert entry_elements.anyof_type or entry_elements.type
    assert entry_elements.required
    assert entry_elements.description

    return entry_elements


class GUI:
    ### sg config
    # look and feel
    gui_theme_1 = 'LightBrown3'
    gui_theme_2 = 'LightBrown1'
    gui_theme_3 = 'DarkBlue13'
    gui_theme_4 = 'LightBlue'
    sg.change_look_and_feel(gui_theme_3)

    # fonts
    font_style = 'courier 10 pitch'
    font_9 = (font_style, 9)
    font_9b = (font_style, 11, 'bold')
    font_11 = (font_style, 11)
    font_11b = (font_style, 11, 'bold')

    # other
    sg.set_options(font=font_11)
    sg.set_options(element_padding=(5, 5))
    sg.set_options(border_width=2)

    def db_ui(self):
        layout = list()
        layout.append([sg.T("Where the Databases are located?")])
        layout.append([sg.T("Path", tooltip="path to "),
                       sg.Input(size=(30, 1), key="db_path", font=self.font_9, enable_events=True),
                       sg.FolderBrowse()])
        layout.append([sg.Button("explore for databases", key="_explore_")])

        layout.append([sg.T("What Database you would like to explore?")])
        layout.append([sg.DropDown([], key="_existing_dbs_", enable_events=True)])

        layout.append([sg.T("", key="_OUTPUT_", text_color="red")])
        layout.append([sg.Button("submit")])

        window = sg.Window("choose a db", layout,
                           resizable=False)

        while True:
            event, values = window.read()
            if event == "_explore_":
                db_files = list()
                self.db_path = values['db_path']
                if self.db_path:
                    if os.path.isdir(self.db_path):
                        os.chdir(self.db_path)
                        files = os.listdir(self.db_path)
                        for f in files:
                            ext = DataBase.ext
                            if not f.endswith(ext):
                                db_files.append(f)
                        if db_files:
                            window['_existing_dbs_'].update(values=db_files, size=(max(map(len, db_files)),1))
                        else:
                            ext = DataBase.ext
                            window['_existing_dbs_'].update(values=[], size=(1, 1))
                            window['_OUTPUT_'](value=f"Warning: chosen path has no *{ext} files")
                    else:
                        window['_OUTPUT_'](value="Not existing dir")
                else:
                    window['_OUTPUT_'](value="Path is not specified")


            if event == "submit":
                if values["_existing_dbs_"]:
                    selected_db = values["_existing_dbs_"]
                    path = os.path(self.db_path, selected_db)
                    try:
                        self.db = DataBase(path)
                    except:
                        window['_OUTPUT_'](value="Warning: Corrupted file")

                if values['db']:
                    window.hide()
                    self.selected_datum = DataBase()
                    self.edit_ui(values['db'])
                    window.un_hide()

                else:
                    window['_OUTPUT_'](value="choose a {last}")

            if event is None:
                window.close()
                break

    def edit_ui(self, schema):
        for entry, elements in schema:
            tooltip = str()
            ee = EntryElements()
            ee = _setter(ee, elements)
            el = EntryLayouts(layout, entry)

            # add red * if required=True and entry title
            if ee.required is True:
                el.required_entry()
            else:
                el.entry()

            # set tooltip as description
            if ee.description:
                tooltip = f'description: {ee.description}'

            if ee.type:
                el.types(ee.type)
                tooltip += f'\ntype: {ee.type}'
                if ee.schema:
                    el.nested_schema(tooltip=tooltip)
                elif ee.type == 'string':
                    el.input(tooltip=tooltip)
                elif ee.type == 'date':
                    el.date(tooltip=tooltip)
                elif ee.type == 'list':
                    el.multyline(tooltip=tooltip)

            elif ee.anyof_type:
                el.types(ee.anyof_type)
                tooltip += f'\ntypes: {ee.anyof_type}'
                if 'list' in ee.anyof_type:
                    el.input(tooltip=tooltip)
                elif 'date' in ee.anyof_type:
                    el.date(tooltip=tooltip)

        window = sg.Window('', layout,
                           resizable=True)

        while True:
            event, values = window.read(timeout=20)
            if event is None:
                window.close()
                break

            if event.startswith("@enter_schema_"):
                nested_entry = event.replace("@enter_schema_")
                nested_schema = schema[nested_entry]["schema"]
                self.edit_ui(nested_schema)
