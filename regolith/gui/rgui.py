# todo - open the ability to run helpers and present the results (dropdowns with updating lists)
# todo - include Zacks suggestion  --> ask the user to set a root and use the rc.json file as a path memory. remember defaults
# todo - test when nesting level > 1


import os
import PySimpleGUI as sg
from regolith.schemas import SCHEMAS, EXEMPLARS
from regolith.gui.config_ui import UIConfig
from regolith.fsclient import load_yaml, load_json, dump_yaml, dump_json
import yaml

# _static globals
LOADER_TYPE = 'yaml'  # "json"
DESCRIPTION_KEY = '_description'
ID_KEY = '_id'
IGNORE_KEYS = [DESCRIPTION_KEY, ID_KEY]

# dynamic globals
POPOUT_ERROR = False
VERBOSE = 0

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

    def popup_warning(self, msg="Warnings - see log"):
        if POPOUT_ERROR:
            sg.popup_error(msg, non_blocking=True, keep_on_top=True, auto_close=True, auto_close_duration=3)
        else:
            self.r_msg('')
            self.r_msg('-----------------')
            self.r_msg(msg)
            self.r_msg('-----------------')


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

        if VERBOSE == 1:
            self.y_msg('----------------')
            self.b_msg('-- ' + entry)
        for element, val in elements.items():
            self.__setattr__(element, val)
            if VERBOSE == 1:
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

    def checkbox_lo(self, tooltip):
        self.layout[-1].extend([sg.Checkbox('', tooltip=tooltip, key=self.entry)])

    def multyline_lo(self, tooltip):
        self.layout[-1].extend([sg.Multiline('', size=self.multyline_size, tooltip=tooltip, key=self.entry)])
        self.layout[-1].extend([self.gl.icon_button(icon=self.EDIT_ICON,
                                                    key=f"@edit_list_{self.entry}")])

    def date_lo(self, tooltip):
        self.layout[-1].extend([sg.Input('', size=self.input_size, tooltip=tooltip, key=self.entry)])
        self.layout[-1].extend([self.gl.icon_button(icon=self.DATE_ICON,
                                                    key=f"@get_date_{self.entry}")])

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

    def padx(self):
        self.layout[-1].extend([sg.T('')])

    def pady(self):
        self.layout.append([sg.T('')])

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

    def update_button(self, extend=False):
        if extend:
            self.layout[-1].extend([sg.Button('Update', key="_update_",
                                              disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])
        else:
            self.layout.append([sg.Button('Update', key="_update_",
                                          disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])

    def finish_button(self, extend=False):
        if extend:
            self.layout[-1].extend([sg.Button('Finish', key="_finish_", button_color=self.PALE_BLUE_BUTTON_COLOR,
                                              disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])
        else:
            self.layout.append([sg.Button('Finish', key="_finish_", button_color=self.PALE_BLUE_BUTTON_COLOR,
                                          disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])

    def save_button(self, extend=False):
        if extend:
            self.layout[-1].extend([sg.Button('Save', key="_save_", button_color=self.PALE_BLUE_BUTTON_COLOR,
                                              disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])
        else:
            self.layout.append([sg.Button('Save', key="_save_", button_color=self.PALE_BLUE_BUTTON_COLOR,
                                          disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])

    def add_button(self, extend=False):
        if extend:
            self.layout[-1].extend([sg.Button('Add', key="_add_", button_color=self.GREEN_COLOR,
                                              disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])
        else:
            self.layout.append([sg.Button('Add', key="_add_", button_color=self.GREEN_COLOR,
                                          disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])

    def delete_button(self, extend=False):
        if extend:
            self.layout[-1].extend([sg.Button('Delete', key="_delete_", button_color=self.RED_COLOR,
                                              disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])
        else:
            self.layout.append([sg.Button('Delete', key="_delete_", button_color=self.RED_COLOR,
                                          disabled_button_color=(self.GREY_COLOR, self.WHITE_COLOR))])

    def title_lo(self, title, tooltip='', extend=False):
        if extend:
            self.layout[-1].extend([sg.T(";")])
            self.layout[-1].extend([sg.T(title, font=self.font_11b, tooltip=tooltip)])
        else:
            self.layout.append([sg.T(title, font=self.font_11b, tooltip=tooltip)])

    def output_msg_lo(self):
        self.layout.append([sg.T("", key="_OUTPUT_", text_color="red", size=(50, 1))])

    def _id_lo(self):
        self.layout.append([sg.T("Select _id:", text_color=self.RED_COLOR)])
        self.layout[-1].extend([sg.DropDown([], key="_id", enable_events=True, readonly=True,
                                            size=self.selector_long_size)])

    def nested_id_lo(self, nested_entries):
        self.layout.append([sg.T("Select nested entry:", text_color=self.RED_COLOR)])
        self.layout[-1].extend([sg.DropDown(nested_entries, key="_nested_index_", enable_events=True, readonly=True,
                                            size=self.selector_index_size)])

    def menu_lo(self):
        menu = [
            [' - File - ', [":Save", "---", ":Exit"]],
            # [' - Info - ', [":About", ":Docs"]],  # TODO - functionalize
        ]
        self.layout.append([sg.Menu(menu)])

    def schema_lo(self, schema):
        """ auto builder of layout from schemas.SCHEMA item"""
        box = list()
        for entry, elements in schema.items():
            if entry not in IGNORE_KEYS:
                tooltip = str()

                # set entry elements from schema
                ee = EntryElements()
                ee._setter(entry, elements)

                # set standard layout builder for entry from schema
                el = EntryLayouts(box, entry)

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
                        elif ee.type == 'date':
                            el.date_lo(tooltip=tooltip)
                        elif ee.type == 'list':
                            el.multyline_lo(tooltip=tooltip)
                        elif ee.type == 'boolean':
                            el.checkbox_lo(tooltip=tooltip)


                    elif ee.anyof_type:
                        el.types_lo(ee.anyof_type)
                        tooltip += f'\ntypes: {ee.anyof_type}'
                        if 'list' in ee.anyof_type:
                            el.multyline_lo(tooltip=tooltip)
                        elif 'date' in ee.anyof_type:
                            el.date_lo(tooltip=tooltip)
                        else:
                            el.input_lo(tooltip=tooltip)

        self.layout.append([sg.Column(box, size=self.schema_box_size, scrollable=True, vertical_scroll_only=True)])


class FilterLayouts(UIConfig):

    def __init__(self, layout: list):
        """
        layout builder for specific bases

        Parameters
        ----------
        layout: list
            ui layout
        """
        self.layout = layout

    def title_lo(self):
        self.layout.append([sg.T("Filter by:")])

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
        self.layout.append([sg.T("User:")])
        self.layout[-1].extend([sg.DropDown([''] + people, key="_user_",
                                            enable_events=True, readonly=True, size=self.selector_short_size)])


class GUI(UIConfig, Messaging):

    def __init__(self):
        self.dbs_path = str()
        self.db_fpath = str()
        self.ext = DataBase.ext
        self.must_exist = DataBase.MUST_EXIST
        self.db = dict()
        self.entry_keys = list()

    def __call__(self):
        self.select_db_ui()

    def select_db_ui(self):
        # sg.show_debugger_window()
        layout = list()
        gl = GlobalLayouts(layout)
        title = "Select a Database"
        gl.title_lo(title)

        layout.append([sg.T("Where the Databases are located?")])
        layout.append([sg.T("Path", tooltip="path to "),
                       sg.Input(DataBase.get_default_path(),
                                size=(50, 1), key="db_path", font=self.font_9, enable_events=True),
                       sg.FolderBrowse()])
        layout.append([sg.Button("explore databases", key="_explore_")])
        layout.append([sg.T("")])
        layout.append([sg.T("What Database you would like to explore?")])
        layout.append([sg.DropDown([], key="_existing_dbs_", enable_events=True, readonly=True)])
        gl.output_msg_lo()
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
                                window['_existing_dbs_'].update(values=sorted(db_files),
                                                                size=(max(map(len, db_files)), 10))

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

                    self.head_data_title = self.selected_db.replace(self.ext, '')
                    try:
                        schema = SCHEMAS[self.head_data_title]
                    except KeyError:
                        self.win_msg(window, f"SORRY! '{self.head_data_title}' schema does not exist.")
                        continue

                    window.hide()
                    self.edit_head_ui(self.head_data_title, schema)
                    window.un_hide()

                else:
                    self.win_msg(window, "Please select a database")

            if event is None:
                window.close()
                break

            # terminate first
            first = False

    def edit_head_ui(self, data_title: str, schema: dict):
        """
        main auto-built ui for presenting and updating entries in a selected catalog

        Parameters
        ----------
        data_title: str
            the title of the catalog
        schema: dict
            the schema for building the ui. Follows schemas.SCHEMA.

        Returns
        -------

        """
        # sg.show_debugger_window()
        # init
        layout = list()
        gl = GlobalLayouts(layout)
        fl = FilterLayouts(layout)
        self.dynamic_nested_entry = ''
        self.db_name = data_title

        # build layout
        gl.menu_lo()
        gl.title_lo(f"Database: {data_title}", tooltip=schema[DESCRIPTION_KEY])
        # -- filters (base-specific)
        if data_title == "projecta":
            # -- load filtration databases
            people = DataBase(self.db_fpath).get_people()
            fl.title_lo()
            fl.projecta(people)
            layout[-1].extend([gl.icon_button(icon=self.FILTER_ICON, key='_filter_', tooltip='filter')])
        gl.pady()
        gl._id_lo()
        gl.output_msg_lo()
        gl.schema_lo(schema)
        gl.pady()
        gl.update_button()
        gl.padx()
        gl.save_button(extend=True)

        # build window
        window = sg.Window('', layout, resizable=True, finalize=True)

        # run
        _first = True
        while True:
            event, values = window.read(timeout=20)
            if event is None or event == ":Exit":
                window.close()
                break

            # control
            if values['_id']:
                window["_update_"].update(disabled=False)
                window["_save_"].update(disabled=False)
            else:
                window["_update_"].update(disabled=True)
                window["_save_"].update(disabled=True)

            # choose _id
            if _first:
                all_ids = list(self.db)
                selectec_ids = all_ids
                self._update_selected_ids(window, selectec_ids)

            # specific filters
            if event == '_filter_':
                if self.head_data_title == "projecta":
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

            # set _id and show data
            if event == "_id":
                self._id = values['_id']
                if not self._id:
                    continue
                self.entry_keys = [self._id]
                _data = self._get_nested_data()
                self._show_data(window, values, schema, _data)

            # explore nested:
            if event.startswith("@enter_schema_"):
                if values["_id"]:
                    nested_entry = event.replace("@enter_schema_", '')
                    nested_type = schema[nested_entry]["type"]
                    nested_schema = schema[nested_entry]["schema"]

                    #  TODO - fix in SCHEMA so after list of dict it is be clear that there is a need to dig deeper
                    if 'schema' in nested_schema and 'type' in nested_schema:
                        nested_schema = nested_schema['schema']

                    # extract relevant data
                    self.entry_keys.append(nested_entry)
                    _data = self._get_nested_data()

                    # window.hide()
                    window.alpha_channel = 0.7
                    self.edit_nested_ui(nested_entry, nested_schema, nested_type)
                    window.alpha_channel = 1.0
                    # window.un_hide()

                    # exit nest
                    self.entry_keys.remove(nested_entry)
                    self.dynamic_nested_entry = ''

                else:
                    self.win_msg(window, f'"{ID_KEY}" is not selected')

            # edit list
            if event.startswith("@edit_list_"):
                self._edit_list(window, values, event)

            # select date
            if event.startswith('@get_date_'):
                self._select_date(window, event)

            # update , save
            if event in ["_update_", "_finish_", "_save_", ":Save"]:
                _data = self._get_nested_data()
                self._update_data(values, schema, _data)

                if event == "_finish_":
                    window.Close()
                    break

                if event in ["_save_", ":Save"]:
                    self._dump_to_local()

            _first = False

    def edit_nested_ui(self, nested_entry: str, nested_schema: dict, nested_type: str = 'dict'):
        """
        main auto-built ui for presenting and updating entries in a selected catalog

        Parameters
        ----------
        nested_entry: str
            the title of the nested_entry
        nested_schema: dict
            the schema for building the ui. uses the nested dictionary of the head schema.SCHEMA
        nested_type: str
            can get 'list' or 'dict'. By selection, builds accordingly

        Returns
        -------

        """
        # sg.show_debugger_window()
        assert nested_type in ['list', 'dict']

        # init
        layout = list()
        gl = GlobalLayouts(layout)

        # build layout
        gl.title_lo(f"Database: {self.db_name}")
        gl.title_lo(f"{self._id}", extend=True)
        self.dynamic_nested_entry += ">>" + nested_entry
        gl.title_lo(f"{self.dynamic_nested_entry}")
        if nested_type == 'list':
            _data = self._get_nested_data()
            nested_entries = self._get_nested_list_entries(_data)
            gl.nested_id_lo(nested_entries)
        gl.output_msg_lo()
        gl.schema_lo(nested_schema)
        gl.pady()
        gl.update_button()
        gl.finish_button(extend=True)
        if nested_type == 'list':
            gl.padx()
            gl.add_button(extend=True)
            gl.delete_button(extend=True)

        # build window
        window = sg.Window('', layout, resizable=True, finalize=True)

        # run
        _first = True
        while True:
            event, values = window.read(timeout=20)
            if event is None or event == ":Exit":
                window.close()
                break

            # control
            if nested_type == 'list':
                if values['_nested_index_']:
                    window["_update_"].update(disabled=False)
                    window["_finish_"].update(disabled=False)
                    # window["_add_"].update(disabled=False)
                    window["_delete_"].update(disabled=False)
                else:
                    window["_update_"].update(disabled=True)
                    window["_finish_"].update(disabled=True)
                    # window["_add_"].update(disabled=True)
                    window["_delete_"].update(disabled=True)

            # --list
            if nested_type == 'list':
                if event == '_nested_index_' and values['_nested_index_']:
                    selected_index = self._get_selected_index(values)
                    _data = self._get_nested_data()[selected_index]
                    self._show_data(window, values, nested_schema, _data)
                if event == '_add_':
                    _data = self._get_nested_data()
                    _data.append(self.build_skel_dict())
                    last_index = len(_data) - 1
                    self._show_data(window, values, nested_schema, _data[last_index])
                    new_index_list = self._get_nested_list_entries(_data)
                    window['_nested_index_'].update(values=new_index_list, value=last_index)
                if event == '_delete_':
                    answer = sg.popup_yes_no(f"Are you sure you want to delete entry # {values['_nested_index_']} ?")
                    if answer == 'Yes':
                        _data = self._get_nested_data()
                        if len(_data) > 1:
                            selected_index = self._get_selected_index(values)
                            _data.pop(selected_index)
                            last_index = len(_data) - 1
                            self._show_data(window, values, nested_schema, _data[last_index])
                            new_index_list = self._get_nested_list_entries(_data)
                            window['_nested_index_'].update(values=new_index_list, value=last_index)
                        elif len(_data) == 1:
                            self._quick_error('will not delete last item in list')
                            continue


            # --dict
            elif nested_type == 'dict' and _first:
                _data = self._get_nested_data()
                self._show_data(window, values, nested_schema, _data)

            # if not nested:
            if event.startswith("@enter_schema_"):
                if values["_nested_index_"]:
                    _nested_entry = event.replace("@enter_schema_", '')
                    _nested_type = nested_schema[_nested_entry]["type"]
                    _nested_schema = nested_schema[_nested_entry]["schema"]
                    #  TODO - fix in SCHEMA so after list of dict it is be clear that there is a need to dig deeper
                    if 'schema' in _nested_schema and 'type' in _nested_schema:
                        _nested_schema = _nested_schema['schema']

                    # --extract relevant data
                    self.entry_keys.append(_nested_entry)
                    _data = self._get_nested_data()

                    # --enter nesting
                    # window.hide()
                    window.alpha_channel = 0.7
                    self.edit_nested_ui(_nested_entry, _nested_schema, _nested_type)
                    window.alpha_channel = 1.0
                    # window.un_hide()

                    # --exit nesting
                    self.entry_keys.remove(_nested_entry)
                    self.dynamic_nested_entry = self.dynamic_nested_entry.rsplit('.', 1)[0]

                else:
                    self.win_msg(window, f'"{ID_KEY}" is not selected')

            # edit list
            if event.startswith("@edit_list_"):
                self._edit_list(window, values, event)

            # select date
            if event.startswith('@get_date_'):
                self._select_date(window, event)

            # update , save
            if event in ["_update_", "_finish_", "_save_", ":Save"]:
                # -- always update first
                _data = self._get_nested_data()
                self._update_data(values, nested_schema, _data)
                if event == "_finish_":
                    window.Close()
                    break
                if event in ["_save_", ":Save"]:
                    self._dump_to_local()

            _first = False

    def edit_list_ui(self, entry: str, data: list):
        data_string = yaml.safe_dump(data, indent=2, sort_keys=False)
        rows = len(data) + 3
        layout = list()

        # build layout
        _gl = GlobalLayouts(layout)
        _gl.title_lo(entry)
        layout.append([sg.Multiline(data_string, size=(self.edit_list_len, rows), key='_data_')])
        _gl.update_button()
        # build window
        window = sg.Window('', layout, resizable=True, finalize=True)

        # run
        while True:
            event, values = window.read(timeout=20)
            if event is None:
                window.close()
                return data

            if event == "_update_":
                striped_data = values["_data_"]
                try:  # to update data
                    data = yaml.safe_load(striped_data)
                    assert isinstance(data, list)
                    window.close()
                    return data

                except:
                    self._quick_error("must represent a valid yaml list format")

    def _quick_error(self, msg):
        sg.popup_error(msg,
                       non_blocking=True, auto_close=True, auto_close_duration=3)

    def _get_selected_index(self, values):
        return int(values['_nested_index_'].strip())

    def _get_nested_data(self) -> dict or list:
        _data = self.db
        for ek in self.entry_keys:
            _data = _data[ek]
        return _data

    def _get_nested_list_entries(self, _data):
        nested_entries = list(str(i) for i in range(len(_data)))
        return nested_entries

    def _dump_to_local(self):
        dump(self.db_fpath, self.db)
        # TODO - the next line is required because of the fsclient.dump function pops-out the _id key
        self.db = load(self.db_fpath)
        sg.popup_quick(f"Saved!")

    def _update_data(self, values, schema, _data):
        for key, val in values.items():
            if val:
                if val.strip() and key in schema:
                    _pass = True
                    try:
                        try:
                            _val = eval(val)
                            if isinstance(_val, list):
                                val = _val
                            else:
                                val = str(val)
                        except:
                            val = str(val)
                    except:
                        self.r_msg(f"ErrorEvalList:  {key}")
                        self._quick_error(f"Error saving - see ")
                        _pass = False
                    if _pass:
                        if isinstance(_data, list):
                            index = self._get_selected_index(values)
                            _data[index].update({key: val})
                        else:
                            _data.update({key: val})

    def _select_date(self, window, event):
        date = sg.popup_get_date()
        if date:
            date = f'{date[2]}-{date[0]}-{date[1]}'
        else:
            return
        entry = event.replace('@get_date_', '')
        window[entry].update(value=date)

    def _edit_list(self, window, values, event):
        entry = event.replace('@edit_list_', '')
        try:
            data = eval(values[entry])
            assert isinstance(data, list)
        except:
            self._quick_error("must represent a valid list-like string format")
            return
        data = self.edit_list_ui(entry, data)
        window[entry].update(value=data)

    def _show_data(self, window, values, schema, data):
        """
        fill data of _id entry

        Parameters
        ----------
        window: sg.window
        values: dict
            values of window.read()
        schema: dict
            the layout dict
        data: dict
            data from _id entry
        Returns
        -------

        """
        perfect = True

        # clean
        for entry, val in values.items():
            if entry not in IGNORE_KEYS:
                if entry in schema:
                    window[entry].update(value='')

        # fill
        for entry, val in data.items():
            if VERBOSE == 1:
                self.y_msg('------------------')
                print(entry, ":", val)

            if entry not in IGNORE_KEYS:
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

    def build_skel_dict(self):
        exemplar = EXEMPLARS[self.head_data_title]
        for ek in self.entry_keys[1:]:
            exemplar = exemplar[ek]
        if isinstance(exemplar, list):
            exemplar = exemplar[0]
        skel_dict = dict()
        for k, v in exemplar.items():
            if isinstance(v, list):
                skel_dict.update({k: list()})
                # if isinstance(v[0], dict):
                #     skel_dict[k].append(self.build_skel_dict(v[0]))
            # elif isinstance(v, dict):
            #     skel_dict.update({k: self.build_skel_dict(v)})
            else:
                skel_dict.update({k: str()})
        return skel_dict

if __name__ == '__main__':
    GUI()()
