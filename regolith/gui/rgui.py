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
    # fonts
    font_style = 'courier 10 pitch'
    font_9 = (font_style, 9)
    font_9b = (font_style, 11, 'bold')
    font_11 = (font_style, 11)
    font_11b = (font_style, 11, 'bold')

    # standard_sizes
    required_entry_size = (13, 1)
    entry_size = (15, 1)
    types_size = (10, 1)
    input_size = (30, 1)
    multyline_size = (30, 3)

    ### globals
    # look and feel
    gui_theme_1 = 'LightBrown3'
    gui_theme_2 = 'LightBrown1'
    gui_theme_3 = 'DarkBlue13'
    gui_theme_4 = 'LightBlue'
    sg.change_look_and_feel(gui_theme_3)

    sg.set_options(font=font_11)
    sg.set_options(element_padding=(5, 5))
    sg.set_options(border_width=2)


class EntryLayouts(UIConfig):

    def __init__(self, layout: list, entry: str):
        """
        the auto layout builder for entries in a schema

        Parameters
        ----------
        layout: list
            that lyaout list
        entry: str
            the entry name
        """
        self.layout = layout
        self.entry = entry

    def required_entry_lo(self):
        self.layout.append([sg.Text('*', text_color='red')])
        self.layout[-1].extend([sg.Text(self.entry, size=self.required_entry_size)])

    def entry_lo(self):
        self.layout.append([sg.Text(self.entry, size=self.entry_size)])

    def types_lo(self, types: [list, str]):
        if isinstance(types, str):
            types = [types]
        self.layout[-1].extend([sg.Text(str(types), size=(10, 1))])

    def input_lo(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry)])

    def date_lo(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry),
                                sg.Button('date_lo', key=f'@get_date_{self.entry}')])

    def multyline_lo(self, tooltip):
        self.layout[-1].extend([sg.Multiline('', size=self.multyline_size, tooltip=tooltip, key=self.entry)])

    def nested_schema_lo(self, tooltip):
        self.layout[-1].extend([sg.Button("+", tooltip=tooltip, key=f"@enter_schema_{self.entry}")])


class Layouts(UIConfig):

    def __init__(self, layout: list):
        """
        the auto layout builder - general standards

        Parameters
        ----------
        layout: list
            that layout list
        """
        self.layout = layout

    def title_lo(self):
        self.layout.append([sg.T(self.entry, text_color='blue', font=self.font_11b)])
        self.layout.append([sg.T("")])


class GUI(UIConfig):

    def __init__(self):
        self.dbs_path = str()
        self.db_fpath = str()
        self.db = dict()
        self.ext = DataBase.ext
        self.select_db_ui()

    def select_db_ui(self):
        layout = list()

        title = "Select a Database"
        Layouts(layout).title_lo(title)

        layout.append([sg.T("Where the Databases are located?")])
        layout.append([sg.T("Path", tooltip="path to "),
                       sg.Input(size=(30, 1), key="db_path", font=self.font_9, enable_events=True),
                       sg.FolderBrowse()])
        layout.append([sg.Button("explore for databases", key="_explore_")])

        layout.append([sg.T("What Database you would like to explore?")])
        layout.append([sg.DropDown([], key="_existing_dbs_", enable_events=True)])

        layout.append([sg.T("", key="_OUTPUT_", text_color="red")])
        layout.append([sg.Button("submit")])

        window = sg.Window("select a database", layout,
                           resizable=False)

        while True:
            event, values = window.read()
            if event == "_explore_":
                db_files = list()
                self.dbs_path = values['db_path']
                if self.dbs_path:
                    if os.path.isdir(self.dbs_path):
                        os.chdir(self.dbs_path)
                        files = os.listdir(self.dbs_path)
                        for f in files:
                            if not f.endswith(self.ext):
                                db_files.append(f)
                        if db_files:
                            window['_existing_dbs_'].update(values=db_files, size=(max(map(len, db_files)), 1))
                        else:
                            window['_existing_dbs_'].update(values=[], size=(1, 1))
                            window['_OUTPUT_'](value=f"Warning: chosen path has no *{self.ext} files")
                    else:
                        window['_OUTPUT_'](value="Not existing dir")
                else:
                    window['_OUTPUT_'](value="Path is not specified")

            if event == "submit":
                if values["_existing_dbs_"]:
                    selected_db = values["_existing_dbs_"]
                    selected_db_name = selected_db.replace(self.ext, '')
                    self.db_fpath = os.path.join(self.dbs_path, selected_db)
                    try:
                        self.db = DataBase(self.db_fpath).db
                    except:
                        window['_OUTPUT_'](value="Warning: Corrupted file")

                    window.hide()
                    self.edit_ui(selected_db_name)
                    window.un_hide()

                else:
                    window['_OUTPUT_'](value="Please select a database")

            if event is None:
                window.close()
                break

    def edit_ui(self, selected_db_name):
        layout = list()

        title = f"Edit Datbase {selected_db_name}"
        Layouts(layout).title_lo()

        schema = SCHEMAS[selected_db_name]
        for entry, elements in schema:
            tooltip = str()
            ee = EntryElements()
            ee = _setter(ee, elements)
            el = EntryLayouts(layout, entry)

            # add red * if required=True and entry title
            if ee.required is True:
                el.required_entry_lo()
            else:
                el.entry_lo()

            # set tooltip as description
            if ee.description:
                tooltip = f'description: {ee.description}'

            if ee.type:
                el.types_lo(ee.type)
                tooltip += f'\ntype: {ee.type}'
                if ee.schema:
                    el.nested_schema_lo(tooltip=tooltip)
                elif ee.type == 'string':
                    el.input_lo(tooltip=tooltip)
                elif ee.type == 'date_lo':
                    el.date_lo(tooltip=tooltip)
                elif ee.type == 'list':
                    el.multyline_lo(tooltip=tooltip)

            elif ee.anyof_type:
                el.types_lo(ee.anyof_type)
                tooltip += f'\ntypes: {ee.anyof_type}'
                if 'list' in ee.anyof_type:
                    el.input_lo(tooltip=tooltip)
                elif 'date_lo' in ee.anyof_type:
                    el.date_lo(tooltip=tooltip)

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


if __name__ == '__main__':
    GUI()
