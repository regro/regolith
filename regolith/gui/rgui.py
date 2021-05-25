import os
import PySimpleGUI as sg
from regolith.schemas import SCHEMAS
from regolith.gui.config_ui import UIConfig
from regolith.fsclient import load_yaml, load_json, dump_yaml, dump_json
import yaml

LOADER_TYPE = 'yaml'  # "json"
DESCRIPTION_KEY = '_description'
ID_KEY = '_id'


def load(filepath, _type=LOADER_TYPE):
    """ load catalog """
    if _type == 'yaml':
        return load_yaml(filepath)
    elif _type == 'json':
        return load_json(filepath)
    else:
        return IOError('Invalid loader type. Can be only "yaml" of "json"')


def dump(filepath, docs, _type=LOADER_TYPE):
    """ dump catalog """
    if _type == 'yaml':
        return dump_yaml(filepath, docs)
    elif _type == 'json':
        return dump_json(filepath, docs)
    else:
        return IOError('Invalid loader type. Can be only "yaml" of "json"')


def local_loader(path):
    """ loads yaml config files, such as defaults """
    with open(path, 'r') as fp:
        return yaml.safe_load(fp)


class DataBase:
    ext = '.yml'
    people_db = "people.yml"
    MUST_EXIST = [people_db]

    def __init__(self, path):
        self.path = path

    @staticmethod
    def get_default_path():
        defaults = os.path.join(os.path.dirname(__file__), 'defaults', 'dbs_path.yml')
        return local_loader(defaults)['dbs_path']

    def get_people(self):
        """ get people from people database"""
        return list(load(self.people_db).keys())


class Messaging:
    @staticmethod
    def win_msg(window, msg, key="_OUTPUT_"):
        window[key].update(value=msg)

    @staticmethod
    def r_msg(msg):
        print(f"\033[91m{msg}\033[0m")

    @staticmethod
    def g_msg(msg):
        print(f"\033[92m{msg}\033[0m")

    @staticmethod
    def y_msg(msg):
        print(f"\033[93m{msg}\033[0m")

    @staticmethod
    def b_msg(msg):
        print(f"\033[94m{msg}\033[0m")

    @staticmethod
    def popup_warning(msg="Error - see log"):
        sg.popup_error(msg, non_blocking=True, keep_on_top=True, auto_close=True, auto_close_duration=3)


class EntryElements(Messaging):
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

        self.errors = list()

    def not_found(self, entry: str, _type: str):
        """ activate when _type is not found """
        self.perfect = False
        self.r_msg(f'WARNING: "{entry}" entry has no attribute "{_type}"')
        self.errors.append((entry, _type))

    def _setter(self, entry, elements: dict):
        """
        set entry elements and assert their existence

        Parameters
        ----------
        entry: str
            the name of the entry
        elements: dict
            the schema elements

        Returns
        -------

        """
        self.perfect = True

        self.y_msg('----------------')
        print('--', entry)
        for element, val in elements.items():
            self.__setattr__(element, val)
            print(element, ":", val)

        # description
        try:
            assert self.description is not None
        except AssertionError:
            self.not_found(entry, 'description')

        # type
        try:
            assert self.anyof_type is not None or self.type is not None
        except AssertionError:
            self.not_found(entry, 'type')

        # required
        if self.type != 'dict':
            try:
                assert self.required is not None
            except AssertionError:
                self.not_found(entry, 'required')

        # test if perfect
        if not self.perfect:
            self.popup_warning()


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
        self.gl = GlobalLayouts(self.layout)

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

    def multyline_lo(self, tooltip):
        self.layout[-1].extend([sg.Multiline('', size=self.multyline_size, tooltip=tooltip, key=self.entry)])

    def date_lo(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry)])
        self.layout[-1].extend([self.gl.icon_button(icon=self.DATE_ICON,
                                                    key=f"@get_date_{self.entry}",
                                                    tooltip=tooltip)])

    def nested_schema_lo(self, tooltip):
        self.layout[-1].extend([sg.T('explore', text_color=self.PALE_BLUE_BUTTON_COLOR, key=self.entry)])  # key keeper
        self.layout[-1].extend([self.gl.icon_button(icon=self.ENTER_ICON,
                                                    key=f"@enter_schema_{self.entry}",
                                                    tooltip=tooltip)])


class GlobalLayouts(UIConfig):

    def __init__(self, layout: list):
        """
        the auto layout builder - general standards

        Parameters
        ----------
        layout: list
            ui layout
        """
        self.layout = layout

    def title_lo(self, title, tooltip=''):
        self.layout.append([sg.T(title, font=self.font_11b, tooltip=tooltip)])

    def icon_button(self, icon: str, key: str, tooltip: str = ''):
        """  quick create of icon button

        the defaults work with an icon file that is 1*1 cm
        Parameters
        ----------
        icon: str
            path to png icon file.
        key: str
            a prefix to control the key
        tooltip: str
        Returns
        -------
        sg.Button preconfigured object
        """
        return sg.Button("", image_filename=icon,
                         image_subsample=3, button_color=self.PALE_BLUE_BUTTON_COLOR,
                         tooltip=tooltip, key=key)

    def _id_lo(self):
        self.layout.append([sg.T("Select _id:")])
        self.layout.append([sg.DropDown([], key="_id", enable_events=True, readonly=True,
                                        size=self.selector_long_size)])


class BaseLayouts(UIConfig):

    def __init__(self, layout: list):
        """
        layout builder for specific bases

        Parameters
        ----------
        layout: list
            ui layout
        """
        self.layout = layout

    def projecta(self, people: list):
        """
        projecta ui builder

        filters using people

        Parameters
        ----------
        people: list
            list of people frp, people database

        Returns
        -------
        updated layout
        """

        # filter
        self.layout.append([sg.T("Filter by: User")])
        self.layout.append([sg.DropDown([''] + people, key="_user_", enable_events=True, readonly=True,
                                        size=self.selector_short_size)])


class GUI(UIConfig, Messaging):

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
        GlobalLayouts(layout).title_lo(title)

        layout.append([sg.T("Where the Databases are located?")])
        layout.append([sg.T("Path", tooltip="path to "),
                       sg.Input(DataBase.get_default_path(),
                                size=(50, 1), key="db_path", font=self.font_9, enable_events=True),
                       sg.FolderBrowse()])
        layout.append([sg.Button("explore databases", key="_explore_")])
        layout.append([sg.T("")])
        layout.append([sg.T("What Database you would like to explore?")])
        layout.append([sg.DropDown([], key="_existing_dbs_", enable_events=True, readonly=True)])

        layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(50, 1))])
        layout.append([sg.Button("submit")])

        # build window
        window = sg.Window("select a database", layout, resizable=False, element_justification='center', finalize=True)

        # run
        first = True
        while True:
            event, values = window.read(timeout=50)

            if event == "_explore_" or first:
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
                                self.win_msg(window, f"Warning: chosen path has no *{self.ext} files")
                            if count_must_exist > 0:
                                self.win_msg(window, f"Warning: not all 'must exist' files are present\n"
                                                     f"must exist files: {self.must_exist}")

                    else:
                        self.win_msg(window, "Not existing dir")

                else:
                    self.win_msg(window, "Path is not specified")

            if event == "submit":
                if values["_existing_dbs_"]:
                    self.selected_db = values["_existing_dbs_"]
                    self.db_fpath = os.path.join(self.dbs_path, self.selected_db)
                    try:
                        self.db = load(self.db_fpath)
                    except:
                        self.win_msg(window, "Warning: Corrupted file")

                    self.master_data_title = self.selected_db.replace(self.ext, '')
                    try:
                        schema = SCHEMAS[self.master_data_title]
                    except KeyError:
                        self.win_msg(window, f"SORRY! '{self.master_data_title}' schema does not exist.")
                        continue

                    window.hide()
                    self.edit_ui(self.master_data_title, schema)
                    window.un_hide()

                else:
                    self.win_msg(window, "Please select a database")

            if event is None:
                window.close()
                break

            # terminate first
            first = False

    def _show_data(self, window, values, data):
        perfect = True

        # clean
        for entry, val in values.items():
            if entry in data:
                window[entry].update(value='')  # FIXME

        # fill
        for entry, val in data.items():
            self.y_msg('------------------')
            print(entry, ":", val)

            if entry == ID_KEY:
                continue

            else:
                if isinstance(val, dict) or (isinstance(val, list) and val and isinstance(val[0], dict)):
                    continue
                elif entry in values:
                    window[entry].update(value=val)
                else:
                    perfect = False
                    self.r_msg(f'WARNING: "{entry}" is not part of the schema')

        if not perfect:
            self.popup_warning()

    def _update_selected_ids(self, window, selectec_ids):
        window['_id'].update(value='', values=[''] + list(selectec_ids))

    def edit_ui(self, data_title: str, schema, nested: bool = False, nested_data: dict = None):

        layout = list()

        gl = GlobalLayouts(layout)
        bl = BaseLayouts(layout)

        DB = DataBase(self.db_fpath)

        if nested:
            self.dynamic_db_name += "." + data_title
            GlobalLayouts(layout).title_lo(f"nested data: {self.dynamic_db_name}")

        elif not nested:

            self.dynamic_db_name = data_title
            _description = schema.pop(DESCRIPTION_KEY)
            _id = schema.pop(ID_KEY)
            GlobalLayouts(layout).title_lo(f"Database: {data_title}", tooltip=_description)

            # build unique base-related filter layouts
            if data_title == "projecta":
                # load filtration databases
                people = DB.get_people()
                bl.projecta(people)

                layout[-1].extend([gl.icon_button(icon=self.FILTER_ICON, key='_filter_', tooltip='filter')])

        # build _id layout
        gl._id_lo()

        layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(50, 1))])

        for entry, elements in schema.items():
            tooltip = str()

            # set entry elements from schema
            ee = EntryElements()
            ee._setter(entry, elements)

            # set standard layout builder for entry from schema
            el = EntryLayouts(layout, entry)

            # set tooltip as description
            if ee.description:
                tooltip = f'description: {ee.description}'

            # build layout based on type
            if ee.type or ee.anyof_type:
                if ee.required is True:
                    el.required_entry_lo()
                else:
                    el.entry_lo()

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

        layout.append([sg.Button('save', key="_save_")])

        # build window
        window = sg.Window('', layout, resizable=True, finalize=True)

        # run
        _first = True
        while True:
            event, values = window.read(timeout=20)
            if event is None:
                window.close()
                break

            # choose _id
            if _first:
                all_ids = list(self.db)
                selectec_ids = all_ids
                self._update_selected_ids(window, selectec_ids)

            if event == '_filter_':
                # specific filters
                if self.master_data_title == "projecta":
                    # filter _id's by user
                    if values['_user_']:
                        initials = values['_user_'][:2]
                        filtered_ids = list()
                        for _id in self.db:
                            if _id[2:4] == initials:
                                filtered_ids.append(_id)
                        selectec_ids = filtered_ids
                    else:
                        selectec_ids = all_ids

                # set selected _id's
                self._update_selected_ids(window, selectec_ids)

            if not nested:
                if event == "_id":
                    self._id = values['_id']
                    if not self._id:
                        self.win_msg(window, f'choose a non-empty "{ID_KEY}"')
                        continue
                    else:
                        self._data = self.db[self._id]
                        self._show_data(window, values, self._data)

            if nested:
                self._data = nested_data
                self._show_data(window, values, self._data)

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

            if event == "_save_":  # TODO
                print("==> SAVING ")
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
                dump(self.db_fpath, self.db)
                sg.popup_quick(f"Saved!")

            _first = False


if __name__ == '__main__':
    GUI()()
