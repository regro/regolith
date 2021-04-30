import os
import yaml
import PySimpleGUI as sg
from regolith.schemas import SCHEMAS

window = sg.Window('')
sg.DEFAULT_WINDOW_LOCATION = map(lambda x: x / 3, window.get_screen_size())
window.close()


class DataBase:
    ext = '.yml'
    people_db = "people.yml"
    MUST_EXIST = [people_db]

    def __init__(self, path):
        self.path = path

    def load(self):
        """ load database from file """
        self.db = yaml.safe_load(self.path)
        return self.db

    def save(self):  # TODO - make sure it follows Simon's format PEP-?
        """ save database to file """
        yaml.safe_dump(self.db, self.path)

    def get_people(self):
        """ get people from people database"""
        return yaml.safe_load(self.people_db)


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
    # sg.change_look_and_feel(gui_theme_4)

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

    def title_lo(self, title):
        self.layout.append([sg.T(title, text_color='blue', font=self.font_11b)])
        self.layout.append([sg.T("")])


class GUI(UIConfig):

    def __init__(self):
        self.dbs_path = str()
        self.db_fpath = str()
        self.db = dict()
        self.ext = DataBase.ext
        self.must_exist = DataBase.MUST_EXIST
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

        layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(30, 1))])
        layout.append([sg.Button("submit")])

        # build window
        window = sg.Window("select a database", layout, resizable=False)

        # run
        while True:
            event, values = window.read()

            if event == "_explore_":
                db_files = list()
                self.dbs_path = values['db_path']

                if self.dbs_path:

                    if os.path.isdir(self.dbs_path):
                        os.chdir(self.dbs_path)
                        files = os.listdir(self.dbs_path)
                        count_must_exist = len(self.must_exist)
                        for f in files:
                            if f in self.must_exist:
                                count_must_exist -= 1
                            if f.endswith(self.ext):
                                db_files.append(f)
                            if count_must_exist == 0:
                                window['_existing_dbs_'].update(values=db_files, size=(max(map(len, db_files)), 10))

                        # bad path
                        if not db_files or count_must_exist > 0:
                            window['_existing_dbs_'].update(values=[], size=(1, 1))
                            if not db_files:
                                window['_OUTPUT_'](value=f"Warning: chosen path has no *{self.ext} files")
                            if count_must_exist > 0:
                                window['_OUTPUT_'](value=f"Warning: not all 'must exist' files are present\n"
                                                         f"must exist files: {self.must_exist}")

                    else:
                        window['_OUTPUT_'](value="Not existing dir")

                else:
                    window['_OUTPUT_'](value="Path is not specified")

            if event == "submit":
                if values["_existing_dbs_"]:
                    self.selected_db = values["_existing_dbs_"]
                    self.db_fpath = os.path.join(self.dbs_path, self.selected_db)
                    try:
                        self.db = DataBase(self.db_fpath).load()
                    except:
                        window['_OUTPUT_'](value="Warning: Corrupted file")

                    window.hide()

                    self.master_data_title = self.selected_db.replace(self.ext, '')
                    schema = SCHEMAS[self.master_data_title]
                    self.edit_ui(self.master_data_title, schema)

                    window.un_hide()

                else:
                    window['_OUTPUT_'](value="Please select a database")

            if event is None:
                window.close()
                break

    def edit_ui(self, data_title: str, schema, nested: bool = False):

        DB = DataBase(self.db_fpath)

        layout = list()

        if nested:
            self.dynamic_db_name += "." + data_title
            Layouts(layout).title_lo(f"nested data: {self.dynamic_db_name}")

        elif not nested:

            self.dynamic_db_name = data_title

            Layouts(layout).title_lo(f"Database: {data_title}")

            # build uneque layout
            if data_title == "projecta":
                # load filtration databases
                people = DB.get_people()

                # build
                layout.append([sg.T("Select User")])
                layout.append([sg.DropDown(people, key="_user_", enable_events=True)])

                layout.append([sg.T("Select Prum")])
                layout.append([sg.DropDown([], key="_prum_", enable_events=True)])

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

        layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(30, 1))])
        layout.append([sg.Button("Save")])

        # build window
        window = sg.Window('', layout,
                           resizable=True)

        # run
        while True:
            event, values = window.read(timeout=20)
            if event is None:
                window.close()
                break

            if self.master_data_title == "projecta":
                sub_db = dict()
                if values['_user_']:
                    if event == '_user_':
                        sub_db = self.db[values['_user_']]
                        window['_prum_'].update(values=sub_db)
                else:
                    window['_prum_'].update(values=[])

                if values['_prum_']:
                    if event == '_prum_':
                        for entry, val in sub_db.items():
                            if isinstance(val, str):
                                window[entry].update(value=val)
                            if isinstance(val, list):
                                if isinstance(val[0], str):
                                    window[entry].update(value=str(val))

                    window['save'].update(disabled=False)
                else:
                    window['save'].update(disabled=True)

            if event.startswith("@enter_schema_"):
                nested_entry = self.selected_db.replace(self.ext, '')
                nested_schema = schema[nested_entry]["schema"]
                self.edit_ui(nested_entry, nested_schema, nested=True)

            if event == "save":
                # for entry, val in values.items():
                #     if isinstance(val, str):
                #         window[entry].update(value=val)
                #     if isinstance(val, list):
                #         if isinstance(val[0], str):
                #             window[entry].update(value=str(val))

                DB.save()
                sg.popup_quick(f"Saved!")


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
