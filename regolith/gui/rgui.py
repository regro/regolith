import os
import yaml
import PySimpleGUI as sg
from regolith.schemas import SCHEMAS

window = sg.Window('')
sg.DEFAULT_WINDOW_LOCATION = map(lambda x: x / 3, window.get_screen_size())
window.close()

DEFAULTS_PATH = "/home/yr2369/github/regolith/dev/regolith/regolith/gui/defaults.yml"


def load(path, type='yaml'):
    if type == 'yaml':
        with open(path, 'r') as f:
            return yaml.safe_load(f)


class DataBase:
    ext = '.yml'
    people_db = "people.yml"
    MUST_EXIST = [people_db]

    def __init__(self, path):
        self.path = path

    def load(self):
        """ load database from file """
        with open(self.path, 'r') as f:
            self.db = yaml.safe_load(f)
        return self.db

    def save(self, db):  # TODO - make sure it follows Simon's format PEP-?
        """ save database to file """
        with open(self.path, 'w') as f:
            yaml.safe_dump(db, f)

    @staticmethod
    def get_default_path():
        return load(DEFAULTS_PATH)['default_path']

    def get_people(self):
        """ get people from people database"""
        return list(load(self.people_db).keys())


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

    sg.change_look_and_feel(gui_theme_4)
    sg.set_options(input_elements_background_color='#ffffff')
    sg.set_options(font=font_11)
    sg.set_options(element_padding=(5, 5))
    sg.set_options(border_width=2)

    sg.set_options(use_ttk_buttons=True)
    sg.set_options(ttk_theme="clam")  # 'clam', 'alt', 'default', 'classic'


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
        self.layout[-1].extend([sg.Text(str(types), size=self.types_size, font=self.font_8)])

    def input_lo(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry)])

    def date_lo(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry),
                                sg.Button('+', key=f'@get_date_{self.entry}')])

    def multyline_lo(self, tooltip):
        self.layout[-1].extend([sg.Multiline('', size=self.multyline_size, tooltip=tooltip, key=self.entry)])

    def nested_schema_lo(self, tooltip):
        self.layout[-1].extend([sg.In('expend -> ', key=self.entry, size=(0, 0), disabled=True),
                                # TODO add to ignore list. currently a dummy space holder for entry name
                                sg.Button("+", tooltip=tooltip, key=f"@enter_schema_{self.entry}")])


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

    def title_lo(self, title, tooltip=''):
        self.layout.append([sg.T(title, text_color='blue', font=self.font_11b, tooltip=tooltip)])


class GUI(UIConfig):

    def __init__(self):
        self.dbs_path = str()
        self.db_fpath = str()
        self.ext = DataBase.ext
        self.must_exist = DataBase.MUST_EXIST
        self.db = dict()

    def __call__(self):
        self.select_db_ui()

    def select_db_ui(self):
        layout = list()

        title = "Select a Database"
        Layouts(layout).title_lo(title)

        layout.append([sg.T("Where the Databases are located?")])
        layout.append([sg.T("Path", tooltip="path to "),
                       sg.Input(DataBase.get_default_path(),
                                size=(50, 1), key="db_path", font=self.font_9, enable_events=True),
                       sg.FolderBrowse()])
        layout.append([sg.Button("explore databases", key="_explore_")])
        layout.append([sg.T("")])
        layout.append([sg.T("What Database you would like to explore?")])
        layout.append([sg.DropDown([], key="_existing_dbs_", enable_events=True)])

        layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(50, 1))])
        layout.append([sg.Button("submit")])

        # build window
        window = sg.Window("select a database", layout, resizable=False, element_justification='center', finalize=True)

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

    def edit_ui(self, data_title: str, schema, nested: bool = False, nested_data: dict = None):
        DESCRIPTION_KEY = '_description'
        ID_KEY = '_id'

        DB = DataBase(self.db_fpath)

        layout = list()

        if nested:
            self.dynamic_db_name += "." + data_title
            Layouts(layout).title_lo(f"nested data: {self.dynamic_db_name}")

        elif not nested:

            self.dynamic_db_name = data_title
            _description = schema.pop(DESCRIPTION_KEY)
            _id = schema.pop(ID_KEY)
            Layouts(layout).title_lo(f"Database: {data_title}", tooltip=_description)

            # build uneque layout
            if data_title == "projecta":
                # load filtration databases
                people = DB.get_people()

                # build
                layout.append([sg.T("Select User")])
                layout.append([sg.DropDown(people, key="_user_", enable_events=True, size=self.selector_short_size)])

                layout.append([sg.T("Select target prum")])
                layout.append([sg.DropDown([], key="_prum_", enable_events=True, size=self.selector_long_size)])

        layout.append([sg.Button('load', key='_load_', font=self.font_9b)])
        for entry, elements in schema.items():
            tooltip = str()
            ee = EntryElements()

            ee = _setter(entry, ee, elements)
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
                    el.multyline_lo(tooltip=tooltip)
                elif 'date' in ee.anyof_type:
                    el.date_lo(tooltip=tooltip)
                else:
                    el.input_lo(tooltip=tooltip)

        layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(30, 1))])
        # layout.append([sg.Button('save', key="_save_")])

        # build window
        window = sg.Window('', layout, resizable=True, finalize=True)

        # run
        while True:
            event, values = window.read(timeout=20)
            if event is None:
                window.close()
                break

            ###  specific targeting for a database
            if not nested:
                if self.master_data_title == "projecta":
                    sub_db = dict()
                    if values['_user_']:
                        initials = values['_user_'][:2]
                        if event == '_user_':
                            user_prums = list()
                            for _id in self.db:
                                if _id[2:4] == initials:
                                    user_prums.append(_id)
                            window['_prum_'].update(values=user_prums)
                    else:
                        window['_prum_'].update(values=[])

            if event == '_load_':
                if nested:
                    self._data = nested_data
                else:
                    self._id = values['_prum_']
                    self._data = self.db[self._id]
                perfect = True
                for entry, val in self._data.items():
                    print(f'\033[93m------------------ \033[0m')
                    print(entry, ":", val)

                    if entry in values:
                        window[entry].update(value='')
                        if isinstance(val, list):
                            if val:
                                if isinstance(val[0], str):
                                    window[entry].update(value=str(val))

                        elif isinstance(val, dict):
                            pass

                        else:
                            window[entry].update(value=val)

                    else:
                        perfect = False
                        print(f'\033[91m WARNING: "{entry}" is not part of the schema \033[0m')
                if not perfect:
                    sg.popup_error('Error - see log', non_blocking=True)


            if event.startswith("@enter_schema_"):
                nested_entry = event.replace("@enter_schema_", '')
                nested_schema = schema[nested_entry]["schema"]
                window.hide()
                self.edit_ui(nested_entry, nested_schema, nested=True, nested_data=self._data[nested_entry])
                window.un_hide()

            if event.startswith('@get_date_'):
                date = sg.popup_get_date()
                date = f'{date[2]}-{date[0]}-{date[1]}'
                entry = event.replace('@get_date_', '')
                window[entry].update(value=date)

            if event == "_save_":
                # for entry, val in values.items():
                #     if isinstance(val, str):
                #         window[entry].update(value=val)
                #     if isinstance(val, list):
                #         if isinstance(val[0], str):
                #             window[entry].update(value=str(val))
                print ("==> SAVE ")
                for key, val in values.items():
                    if key in self._data:
                        try:
                            val = eval(val)
                            if isinstance(val, list):
                                pass
                            else:
                                val = str(val)
                        except:
                            val = str(val)
                            print(f"ERROR:  {key}")

                        self._data[key] = val
                self.db.update({self._id: self._data})
                DB.save(self.db)
                sg.popup_quick(f"Saved!")


def _setter(entry, entry_elements: EntryElements, elements: dict):
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
    print("\033[93m ---------------- \033[0m")
    print('--', entry)
    for element, val in elements.items():
        entry_elements.__setattr__(element, val)
        print(element, ":", val)

    perfect = True

    # description
    try:
        assert entry_elements.description is not None
    except:
        perfect = False
        print(f'\033[91m WARNING: "{entry}" entry has no "description"\033[0m')

    # type
    try:
        assert entry_elements.anyof_type is not None or entry_elements.type is not None
    except:
        perfect = False

        print(f'\033[91m WARNING: "{entry}" entry has no "type"\033[0m')

    # required
    if entry_elements.type != 'dict':
        try:
            assert entry_elements.required is not None
        except:
            print(f'\033[91m WARNING: "{entry}" entry has no "required"\033[0m')

    # not perfect
    if not perfect:
        sg.popup_error("Error - see log", non_blocking=True, auto_close_duration=8)

    return entry_elements


if __name__ == '__main__':
    GUI()()
