from tkinter import ttk, Toplevel, Tk, Frame
from tkinter.constants import *
from tkinter import messagebox
from tkinter.font import Font
from tkinter import StringVar, BooleanVar
from tkinter import Label, Text, Entry, Listbox, Scrollbar
from generator import Generator
from mn_address import MnAddress
from themes.theme_verify import Verifier, ThemeDict
import mnemonic
from pathlib import Path
import random
import swapper
import json
import gc
import traceback
import copy
import datetime


def handle_exception(exception, value, trace_object):
    print("Caught exception:", value)
    path = Path(__file__).parent.absolute()
    path = Path(path).parent.absolute()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not Path.exists(path / "LogErrors"):
        Path.mkdir(path / "LogErrors")
    log = str("Time: " + str(time) + "\n" + "Error: " + str(exception) + "\n" + traceback.format_exc() + "\n")

    with open((path / "LogErrors" / "LogErrors.txt"), "a") as file:
        file.write(log)


class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        self.style = ttk.Style()
        # Change the layout themes here, use print(self.style.theme_names()) to see available themes
        self.style.theme_use("clam")

        self.tab_control = ttk.Notebook(root)
        self.pass_gen = Frame(self.tab_control)
        self.address_converter = Frame(self.tab_control)
        self.table_selector = Frame(self.tab_control)
        self.table_selector.grid(column=0, row=0, rowspan=5)
        self.grid_frame_selector = Frame(self.table_selector)
        self.grid_frame_selector.grid(column=2, row=0, rowspan=64)
        self.swapper = Frame(self.tab_control)

        tab00 = "Password Generator"
        tab01 = "Address Converter"
        self.tab02 = "Table Selector"
        self.tab03 = "Word Swapper"

        self.tab_control.add(self.pass_gen, text=tab00)
        self.tab_control.add(self.address_converter, text=tab01)
        self.tab_control.add(self.table_selector, text=self.tab02)
        self.tab_control.add(self.swapper, text=self.tab03)
        self.tab_control.pack(expand=1, fill="both")

        # General variables
        self.selected_theme = "finances"
        self.theme_option_var = StringVar(self)
        directory_path = (self._get_directory() / "themes")
        files_path = Path(directory_path)
        # Finding paths and filtering .json files
        self.themes = tuple([each_directory.stem for each_directory in files_path.glob(r"*.json")])
        self.base_dict = mnemonic.Mnemonic(self.selected_theme).words_dictionary
        self.edited_dict = copy.deepcopy(self.base_dict)
        self.natural_word = self.edited_dict["NATURAL_ORDER"][0]
        self.all_words = []
        for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]:
            self.all_words += self.edited_dict[each_syntactic_word]["TOTAL_LIST"]

        # Variables of generator
        self.last_text = ""
        self.password_lines = []
        self.last_n_phrases = 0
        self.var_check_number = BooleanVar()
        self.var_check_char = BooleanVar()
        self.var_check_case = BooleanVar()

        # Variables of converter
        self.M = MnAddress()
        self.addresses_types = self.M.accepted_addresses()

        # Variables of table selector
        self.Spreadsheet_Dimension_Size = 8
        # Setting a green color to represent an adequate frase
        self.check_color = "#3AC73A"
        self.defaultbg = self.cget("bg")
        self.valid_phrase = True
        self.words_dictionary = {}
        self.highlight_checkbox_var = BooleanVar()
        self.use_custom_checkbox_var = BooleanVar()
        self.object_dict = {}
        self.column_objects = []
        self.row_objects = []
        self.paragraph_objects = []
        self.input_set_caseless = []
        self.input_set_column = []
        self.input_set_row = []
        self.input_set_paragraph = []
        self.picked_passphrase = []
        self.custom_characters_var = StringVar(self)
        self.trace_custom_characters = self.custom_characters_var.trace_add("write", self.define_key_list)
        # The states represent what was the last defined dimension
        self.states = ("initial", "column_done", "row_done", "paragraph_done")
        self.current_state = self.states[0]
        self.selected_indexes = {key: self.Spreadsheet_Dimension_Size for key in self.states}
        self.permutation_map = {
            "initial": self.input_set_column,
            "column_done": self.input_set_row,
            "row_done": self.input_set_paragraph,
            "paragraph_done": self.input_set_caseless
        }

        # Variables of Word Swapper
        self.swap_file_name_var = StringVar(self)
        self.trace_file_name = self.swap_file_name_var.trace_add("write", self.evaluate_state)
        self.swap_syntactic_word_replace_by_var = StringVar(self)
        self.trace_syntactic_replace_by = \
            self.swap_syntactic_word_replace_by_var.trace_add("write", self.change_syntactic_replace_by)
        self.swap_replace_by_var = StringVar(self)
        self.trace_replace_by = \
            self.swap_replace_by_var.trace_add("write", self.changed_replace_by)
        self.swap_syntactic_replace_by_list = [each_syntactic_word
                                               for each_syntactic_word in self.base_dict["NATURAL_ORDER"]
                                               ]
        self.swap_syntactic_replace_in_list = [each_syntactic_word
                                               for each_syntactic_word in self.base_dict["NATURAL_ORDER"]
                                               if self.base_dict[each_syntactic_word]["RESTRICTS"] != []
                                               ]
        self.swap_syntactic_word_replace_in_var = StringVar(self)
        self.trace_syntactic_replace_in = self.swap_syntactic_word_replace_in_var.trace_add(
            "write", self.change_syntactic_replace_in
        )
        self.wrong_typo_var = StringVar(self)
        self.trace_wrong_typo = self.wrong_typo_var.trace_add("write", self.enable_replace_button)
        # States are replace_by filled, replace_in filled, to_replace filled respectively
        self.swap_fill_state_list = [False, False, False]
        self.use_copy_list = True
        self.can_save = False

        # Creation of buttons and labels widget of generator tab
        self.gen_theme_button = None
        self.text_box = Text(self.pass_gen)
        self.run_button = ttk.Button(self.pass_gen)
        self.clip_button = ttk.Button(self.pass_gen)
        self.redo_button = ttk.Button(self.pass_gen)
        self.clear_button = ttk.Button(self.pass_gen)
        self.select_phrases = ttk.Spinbox(self.pass_gen)
        self.check_number = ttk.Checkbutton(self.pass_gen)
        self.check_char = ttk.Checkbutton(self.pass_gen)
        self.check_case = ttk.Checkbutton(self.pass_gen)
        self.save_button = ttk.Button(self.pass_gen)
        self.save_msg = Label(self.pass_gen)
        self.copy_msg = Label(self.pass_gen)
        self.gen_quit_button = ttk.Button(self.pass_gen)

        # Creation of buttons and labels widget of converter tab
        warning_text = "Warning! DO NOT use this tool to change the type of address to another type," \
                       " the network will see this as a valid transaction but funds will be PERMANENTLY LOST"
        self.warning_msg = Label(self.address_converter, text=warning_text, fg="red")
        self.conv_theme_button = None
        self.address_box = Text(self.address_converter)
        self.phrases_box = Text(self.address_converter)
        self.address_button = ttk.Button(self.address_converter)
        self.phrases_button = ttk.Button(self.address_converter)
        self.conv_quit_button = ttk.Button(self.address_converter)

        # Creation of buttons and labels widget of table selector tab
        self.sel_theme_button = None
        self.reset_button = ttk.Button(self.table_selector)
        self.sel_valid_phrase_label = Label(self.table_selector)
        self.highlight_checkbox = ttk.Checkbutton(self.table_selector)
        self.warning_label = Label(self.table_selector)
        self.use_custom_set = ttk.Checkbutton(self.table_selector)
        self.custom_character_entry = Entry(self.table_selector, textvariable=self.custom_characters_var)
        self.output_button = ttk.Button(self.table_selector)

        # Creation of buttons and labels widget of word swapper tab
        self.swap_theme_button = None
        self.swap_file_name_label = Label(self.swapper)
        self.swap_file_name_entry = Entry(self.swapper, textvariable=self.swap_file_name_var)
        self.swap_replace_by_label = Label(self.swapper)
        self.swap_replace_by_entry = Entry(self.swapper, textvariable=self.swap_replace_by_var)
        self.swap_syntactic_replace_by = None
        self.swap_replace_in_label = Label(self.swapper)
        self.swap_replace_in_listbox = Listbox(self.swapper, exportselection=False)
        self.swap_replace_in_scrollbar = Scrollbar(self.swapper, orient=VERTICAL)
        self.swap_syntactic_replace_in = None
        self.swap_to_replace_label = Label(self.swapper)
        self.swap_to_replace_listbox = Listbox(self.swapper, exportselection=False)
        self.swap_to_replace_scrollbar = Scrollbar(self.swapper, orient=VERTICAL)
        self.swap_copy_from_label = Label(self.swapper)
        self.swap_copy_from_listbox = Listbox(self.swapper, exportselection=False)
        self.swap_copy_from_scrollbar = Scrollbar(self.swapper, orient=VERTICAL)
        self.swap_words_button = ttk.Button(self.swapper)
        self.swap_reset_button = ttk.Button(self.swapper)
        self.swap_save_button = ttk.Button(self.swapper)
        self.swap_collision_warning_label = Label(self.swapper)
        self.swap_history_label = Label(self.swapper)
        self.swap_history_textbox = Text(self.swapper)
        self.swap_correct_typo_label = Label(self.swapper)
        self.swap_correct_typo_button = ttk.Button(self.swapper)
        self.swap_correct_typo_entry = Entry(self.swapper)
        self.swap_wrong_typo_entry = Entry(self.swapper, textvariable=self.wrong_typo_var)

        self.init_generator_window()
        self.init_converter_window()
        self.init_table_window()
        self.init_swapper_window()

    class ToolTip(object):

        def __init__(self, widget):
            self.widget = widget
            self.tip_window = None
            self.id = None
            self.x = self.y = 0
            self.text = ""

        def showtip(self, text: str):
            """This method display a text in tooltip window

            Parameters
            ----------
            text : str
                This is the text to show in the tip
            """
            self.text = text
            if self.tip_window or not self.text:
                return
            x, y, cx, cy = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 57
            y = y + cy + self.widget.winfo_rooty() + 27
            self.tip_window = tw = Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(tw, text=self.text, justify=LEFT,
                          background="#ffffe0", relief=SOLID, borderwidth=1,
                          font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)

        def hidetip(self):
            """
                This method hides the tooltip window
            """
            tw = self.tip_window
            self.tip_window = None
            if tw:
                tw.destroy()

    def create_tooltip(self, widget: Label, text: str):
        """
            This method creates the tooltip windows and show or hide them when the cursor enters or leaves the widget
        Parameters
        ----------
        widget : Label
            This is the widget where the tip will pop up
        text : str
            This is the text to show in the tip
        """
        tooltip = self.ToolTip(widget)

        def enter(event):
            """
                This function is called when the cursor enters the widget area
                It shows the tooltip close to the widget

            Parameters
            ----------
            event :
                The event is the event calling the method, it is not used by the method
            """
            if self.highlight_checkbox_var.get():
                tooltip.showtip(text)

        def leave(event):
            tooltip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    @staticmethod
    def _get_directory() -> Path:
        """
            This method finds out in which directory the code is running

        Returns
        -------
        path
            Returns the absolute path found of the file
        """
        return Path(__file__).parent.absolute()

    @staticmethod
    def client_exit():
        """
            This method closes the application
        """
        exit()

    def init_generator_window(self):
        """
            This method sets up of widgets texts, labels, buttons and menus
            It then positions those widgets in the Password Generator tab
        """
        # Set texts and positions of generator tab
        self.run_button.config(text="Run!", command=self.generate_text)
        self.clip_button.config(text="Copy", command=self.copy_to_clipboard)
        self.redo_button.config(text="Redo", command=self.recover_text)
        self.clear_button.config(text="Clear", command=self.clear_text)
        self.gen_quit_button.config(text="Exit", command=self.client_exit)
        self.select_phrases.config(width=2, to=8, from_=1, wrap=True)
        self.select_phrases.set(1)
        self.theme_option_var.set(self.selected_theme)
        self.gen_theme_button = ttk.OptionMenu(self.pass_gen,
                                               self.theme_option_var,
                                               self.selected_theme,
                                               *self.themes,
                                               command=self.theme_changed
                                               )
        self.check_case.config(text="Include Uppercase", variable=self.var_check_case,
                               onvalue=True, offvalue=False, command=self.insert_swap_case
                               )
        self.check_number.config(text="Include Number", variable=self.var_check_number,
                                 onvalue=True, offvalue=False, command=self.insert_number
                                 )
        self.check_char.config(text="Include Special Character", variable=self.var_check_char,
                               onvalue=True, offvalue=False, command=self.insert_spc_char
                               )
        self.save_button.config(text="Save", command=self.gen_save_file)
        self.text_box.config(height=25, width=75)

        self.run_button.grid(column=0, row=0, padx=5, pady=5)
        self.clip_button.grid(column=2, row=0, padx=5, pady=5)
        self.redo_button.grid(column=0, row=3, padx=5, pady=5)
        self.clear_button.grid(column=1, row=3, padx=5, pady=5)
        self.gen_quit_button.grid(column=0, row=4, padx=5, pady=5)
        self.select_phrases.grid(column=0, row=1, padx=5, pady=5)
        self.gen_theme_button.grid(column=1, row=0, padx=5, pady=5)
        self.check_case.grid(column=0, row=2, padx=5, pady=5)
        self.check_number.grid(column=1, row=2, padx=5, pady=5)
        self.check_char.grid(column=2, row=2, padx=5, pady=5)
        self.save_button.grid(column=1, row=4, padx=5, pady=5)
        self.text_box.grid(column=4, row=0, padx=5, pady=5, columnspan=5, rowspan=5)

    def init_converter_window(self):
        """
            This method sets up of widgets texts, labels, buttons and menus
            It then positions those widgets in the Converter tab
        """
        # Set texts and positions of converter tab
        self.conv_quit_button.config(text="Exit", command=self.client_exit)
        self.address_button.config(text="Convert to phrases", command=self.address_to_phrase_text)
        self.phrases_button.config(text="Convert to address", command=self.phrase_to_address_text)
        self.conv_theme_button = ttk.OptionMenu(self.address_converter,
                                                self.theme_option_var,
                                                self.selected_theme,
                                                *self.themes,
                                                command=self.theme_changed
                                                )
        self.address_box.config(height=20, width=75)
        self.phrases_box.config(height=20, width=75)

        self.warning_msg.grid(column=0, row=0, padx=5, pady=5, columnspan=6, rowspan=1)
        self.address_box.grid(column=0, row=1, padx=4, pady=4, columnspan=3, rowspan=3)
        self.conv_quit_button.grid(column=0, row=8, padx=4, pady=4)
        self.phrases_box.grid(column=4, row=1, padx=4, pady=4, columnspan=4, rowspan=3)
        self.address_button.grid(column=0, row=7, padx=4, pady=4)
        self.phrases_button.grid(column=4, row=7, padx=4, pady=4)
        self.conv_theme_button.grid(column=1, row=7, padx=4, pady=4)

    def init_table_window(self):
        """
            This method sets up of widgets texts, labels, buttons and menus
            It then positions those widgets in the Table Selector tab
        """
        self.theme_option_var.set(self.selected_theme)
        self.sel_theme_button = ttk.OptionMenu(self.table_selector,
                                               self.theme_option_var,
                                               self.selected_theme,
                                               *self.themes,
                                               command=self.selector_theme_changed
                                               )
        self.highlight_checkbox.config(text="Show\nHighlight",
                                       command=self.changed_show_highlight,
                                       variable=self.highlight_checkbox_var,
                                       onvalue=True,
                                       offvalue=False
                                       )
        self.highlight_checkbox.bind_all("<Alt-h>", self.change_highlight_var)
        self.reset_button.config(text="Reset", command=self.reset_password)
        valid_message = "Selected phrase\nso far is compatible"
        self.sel_valid_phrase_label.config(text=valid_message, bg=self.check_color)
        warning_message = "Very careful\nwith prying eyes"
        self.warning_label.config(text=warning_message, fg="red")
        self.use_custom_set.config(text="Use custom\nset of keys",
                                   command=self.enable_custom_keys_set,
                                   variable=self.use_custom_checkbox_var,
                                   onvalue=True,
                                   offvalue=False
                                   )
        self.custom_character_entry.config(width=10)
        self.output_button.config(text="Generate\nPhrase",
                                  command=self.output_phrases, state=DISABLED
                                  )

        self.sel_theme_button.grid(column=0, row=0, padx=5, pady=5, sticky=W)
        self.sel_valid_phrase_label.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.sel_valid_phrase_label.grid_columnconfigure(2, minsize=100)
        self.highlight_checkbox.grid(row=1, column=0, columnspan=1, padx=5, pady=5, sticky=W)
        self.warning_label.grid(row=1, column=1, columnspan=1, sticky=W)
        self.use_custom_set.grid(row=2, column=0, columnspan=1, padx=5, pady=5, sticky=W)
        self.custom_character_entry.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky=W)
        self.custom_character_entry.config(state=DISABLED)
        self.reset_button.grid(row=7, column=0, padx=5, pady=5, sticky=W)
        self.output_button.grid(row=7, column=1, padx=5, pady=5, sticky=W)

        self.new_grid()
        columns = self.grid_frame_selector.grid_size()[0]
        [self.grid_frame_selector.grid_columnconfigure(each_column, minsize=75) for each_column in range(columns)]
        [self.table_selector.grid_columnconfigure(each_column, minsize=75) for each_column in range(columns)]

    def init_swapper_window(self):
        """
            This method sets up of widgets texts, labels, buttons and menus
            It then positions those widgets in the Word Swapper tab
        """
        self.theme_option_var.set(self.selected_theme)
        self.swap_theme_button = ttk.OptionMenu(self.swapper,
                                                self.theme_option_var,
                                                self.selected_theme,
                                                *self.themes,
                                                command=self.selector_theme_changed
                                                )
        self.swap_file_name_label.config(text="File name to save")
        self.swap_file_name_entry.config(width=20)
        self.swap_replace_by_label.config(text="Word to insert")
        self.swap_replace_by_entry.config(width=20)
        self.swap_replace_in_label.config(text="Word that restricts")
        self.swap_syntactic_replace_by = ttk.OptionMenu(self.swapper,
                                                        self.swap_syntactic_word_replace_by_var,
                                                        None,
                                                        *self.swap_syntactic_replace_by_list
                                                        )
        self.swap_replace_in_listbox.bind("<<ListboxSelect>>", self.changed_replace_in)
        self.swap_replace_in_listbox.config(state=DISABLED,
                                            yscrollcommand=self.swap_replace_in_scrollbar.set,
                                            selectmode=SINGLE
                                            )
        self.swap_replace_in_scrollbar.config(command=self.swap_replace_in_listbox.yview)
        self.swap_syntactic_replace_in = ttk.OptionMenu(self.swapper,
                                                        self.swap_syntactic_word_replace_in_var,
                                                        None,
                                                        *self.swap_syntactic_replace_in_list
                                                        )
        self.swap_to_replace_label.config(text="Word to be removed")
        self.swap_to_replace_listbox.bind("<<ListboxSelect>>", self.changed_to_replace)
        self.swap_to_replace_listbox.config(state=DISABLED, yscrollcommand=self.swap_to_replace_scrollbar.set,
                                            selectmode=SINGLE
                                            )
        self.swap_to_replace_scrollbar.config(command=self.swap_to_replace_listbox.yview)
        self.swap_copy_from_label.config(text="Source of clone list")
        self.swap_copy_from_listbox.bind("<<ListboxSelect>>", self.evaluate_options_chosen)
        self.swap_copy_from_listbox.config(state=DISABLED, yscrollcommand=self.swap_copy_from_scrollbar.set,
                                           selectmode=SINGLE
                                           )
        self.swap_copy_from_scrollbar.config(command=self.swap_copy_from_listbox.yview)
        self.swap_words_button.config(text="Swap Words", command=self.swap_words, state=DISABLED)
        self.swap_reset_button.config(text="Reset", command=self.swap_reset)
        self.swap_save_button.config(text="Save", command=self.swap_save, state=DISABLED)
        self.swap_history_label.config(padx=10, pady=5, text="History")
        self.swap_history_textbox.config(height=10, width=100, state=DISABLED)
        self.swap_correct_typo_label.config(text="Find and replace all")
        self.swap_correct_typo_button.config(text="Replace", command=self.swap_correct_typo, state=DISABLED)
        self.swap_correct_typo_entry.config(width=20)
        self.swap_wrong_typo_entry.config(width=20)

        self.swap_theme_button.grid(column=0, row=0, padx=5, pady=5)
        self.swap_file_name_label.grid(column=0, row=1, padx=5, pady=0, sticky=S)
        self.swap_replace_by_label.grid(column=1, row=1, padx=5, pady=0, sticky=S)
        self.swap_replace_in_label.grid(column=2, row=1, padx=5, pady=0, sticky=S)
        self.swap_file_name_entry.grid(column=0, row=3, padx=5, pady=5, sticky=N)
        self.swap_replace_by_entry.grid(column=1, row=3, padx=5, pady=5, sticky=N)
        self.swap_replace_in_listbox.grid(column=2, row=3, rowspan=3, padx=0, pady=5)
        self.swap_replace_in_scrollbar.grid(column=3, row=3, rowspan=3, padx=0, pady=5, sticky=N + S + W)
        self.swap_syntactic_replace_by.grid(column=1, row=2, padx=5, pady=5)
        self.swap_syntactic_replace_in.grid(column=2, row=2, padx=5, pady=5)
        self.swap_to_replace_listbox.grid(column=4, row=3, rowspan=3, padx=0, pady=5)
        self.swap_to_replace_scrollbar.grid(column=5, row=3, rowspan=3, padx=0, pady=5, sticky=N + S + W)
        self.swap_to_replace_label.grid(column=4, row=1, padx=5, pady=0, sticky=S)
        self.swap_copy_from_listbox.grid(column=6, row=3, rowspan=3, padx=0, pady=5)
        self.swap_copy_from_scrollbar.grid(column=7, row=3, rowspan=3, padx=0, pady=5, sticky=N + S + W)
        self.swap_copy_from_label.grid(column=6, row=1, padx=5, pady=0, sticky=S)
        self.swap_words_button.grid(column=7, row=0, padx=5, pady=5)
        self.swap_reset_button.grid(column=1, row=0, padx=5, pady=5)
        self.swap_save_button.grid(column=7, row=1, padx=5, pady=5)
        self.swap_history_label.grid(column=0, row=6, padx=10, pady=5, sticky=W + S)
        self.swap_history_textbox.grid(column=0, row=7, columnspan=9, rowspan=10, padx=10, pady=5, sticky=W)
        self.swap_correct_typo_label.grid(column=0, row=4, padx=5, pady=5, sticky=S)
        self.swap_correct_typo_button.grid(column=1, row=4, padx=5, pady=5, sticky=S)
        self.swap_correct_typo_entry.grid(column=1, row=5, padx=5, pady=5, sticky=S)
        self.swap_wrong_typo_entry.grid(column=0, row=5, padx=5, pady=5, sticky=S)

    def theme_changed(self, event=None):
        """
            When the theme is changed this method is called to set the variable to the new theme selected

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.selected_theme = self.theme_option_var.get()

    def selector_theme_changed(self, event=None):
        """
            This method changes the base dictionary used with the theme selected
            and ask a new grid in the Table Selector tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.theme_changed()
        self.base_dict = mnemonic.Mnemonic(self.selected_theme).words_dictionary
        self.edited_dict = copy.deepcopy(self.base_dict)
        self.all_words = []
        for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]:
            self.all_words += self.edited_dict[each_syntactic_word]["TOTAL_LIST"]
        self.natural_word = self.edited_dict["NATURAL_ORDER"][0]
        self.swap_syntactic_replace_by_list = self.edited_dict["NATURAL_ORDER"]
        self.swap_syntactic_replace_in_list = self.edited_dict["NATURAL_ORDER"]
        self.swap_syntactic_word_replace_by_var.set(self.natural_word)
        self.swap_syntactic_word_replace_in_var.set(self.natural_word)
        self.change_syntactic_replace_by(None)
        self.change_syntactic_replace_in(None)
        self.new_grid()
        self.grayout_gen_button()

    def generate_text(self):
        """
            This method calls object Generator which build a mnemonic phrase in formosa standard
            then updates displayed text
        """
        self.save_msg.grid_forget()
        number_phrases = int(self.select_phrases.get())
        g = Generator(number_phrases * 32, self.selected_theme, None)
        phrases = g.show_phrases()

        text = ""
        phrase_len = len(self.base_dict["NATURAL_ORDER"])
        for word_index in range(len(phrases)):
            text = text + phrases[word_index][0:2]
        text = text + "\n"
        for phrase_index in range(len(phrases) // phrase_len):
            text = text + " ".join(phrases[phrase_len * phrase_index:phrase_len * (phrase_index + 1)]) + "\n"

        self.last_text = self.last_text + text
        self.password_lines.append(0) if len(self.password_lines) == 0 \
            else self.password_lines.append(self.password_lines[-1] + self.last_n_phrases + 1)
        self.last_n_phrases = number_phrases

        self.update_text(text)
        self.insert_number()
        self.insert_spc_char()
        self.insert_swap_case()

    def update_text(self, text: str):
        """
            This method receives a text and inserts in text box in the tab Password Generator tab

        Parameters
        ----------
        text : str
            Text to be received and displayed in the window
        """
        self.text_box.insert(END, text)
        self.copy_to_clipboard()

        self.copy_msg.config(text="Copied to clipboard")
        self.copy_msg.grid(column=2, row=1, padx=5, pady=5)

    def copy_to_clipboard(self):
        """
            This method copies the text displayed to the clipboard
        """
        text = self.text_box.get("0.0", END)
        root.clipboard_clear()
        root.clipboard_append(text[:-1])
        root.update()

    def insert_number(self):
        """
            This method changes an ordinary character to a number
        """
        to_replace = ["a", "e", "i", "o", "b", "g", "t"]
        replace_by = ["4", "3", "1", "0", "8", "6", "7"]
        self.insert_character(to_replace, replace_by, self.var_check_number.get())

    def insert_spc_char(self):
        """
            This method changes an ordinary character to a special character
        """
        to_replace = ["c", "h", "l", "s", "j"]
        replace_by = ["¢", "#", "£", "$", "!"]
        self.insert_character(to_replace, replace_by, self.var_check_char.get())

    def insert_swap_case(self):
        """
            This method swaps the case of a character
        """
        to_replace = list(map(chr, range(97, 123)))
        replace_by = [each_char.swapcase() for each_char in to_replace]
        self.insert_character(to_replace, replace_by, self.var_check_case.get())

    def insert_character(self, to_replace: list, replace_by: list, check_box_var: bool):
        """
            This method finds out if the text in the texbox is written as natural or edited
            and calls method replace_characters() with correct order of variables

        Parameters
        ----------
        to_replace : list
            The list of characters to be removed
        replace_by : list
            The list of characters to be inserted
        check_box_var : bool
            This variable tells if the word is written as natural, or it is already edited
        """
        array_criteria = [each_char in self.last_text for each_char in to_replace]
        if check_box_var and any(array_criteria):
            self.replace_characters(replace_by, to_replace, False)
        elif not check_box_var:
            self.replace_characters(to_replace, replace_by, True)
        self.text_box.delete(index1="0.0", index2=END)
        self.update_text(self.last_text)

    def replace_characters(self, insert: list, remove: list, check_var: bool = False):
        """
            This method replaces a character given by another character given

        Parameters
        ----------
        insert : list
            The list of characters to be removed
        remove : list
            The list of characters to be inserted
        check_var : bool
            Controls which criteria are used, if it is any or none element in the list
        """
        lines = self.last_text.splitlines(False)
        for line_index in self.password_lines:
            # If there is any character to be removed in the line and
            # There is any or none character inserted in the line depending on the control variable "check_var"
            if any([each_char in lines[line_index] for each_char in remove]) and \
                    check_var == any([each_char in lines[line_index] for each_char in insert]):
                index_list = []
                [index_list.append(lines[line_index].find(each_char)) for each_char in remove]
                lesser_char = min([each_index for each_index in index_list if each_index >= 0])
                lesser_char_index = remove.index(lines[line_index][lesser_char])
                new_line = lines[line_index].replace(remove[lesser_char_index], insert[lesser_char_index], 1)
                self.last_text = self.last_text.replace(lines[line_index], new_line)

    def clear_text(self):
        """
            This method clears out the text of text box and copy and save labels in the Password Generator tab
        """
        self.save_msg.grid_forget()
        self.copy_msg.grid_forget()
        self.text_box.delete(index1="0.0", index2=END)
        self.last_text = ""
        self.password_lines = []

    def recover_text(self):
        """
            This method returns an edited text in the text box to its former self in the Password Generator tab
        """
        self.text_box.delete(index1="0.0", index2=END)
        self.text_box.insert(END, self.last_text)

    def gen_save_file(self):
        """
            This method saves the generated phrases to a txt file
        """
        with open("output.txt", "w", encoding="utf-8") as output_file:
            output_file.write(self.last_text)
        self.save_msg.config(text="Saved to \'output.txt\'")
        self.save_msg.grid(column=1, row=6, padx=5, pady=5)

    def address_to_phrase_text(self):
        """
            This method converts a bitcoin address to mnemonic phrases in Formosa standard
        """
        self.phrases_box.delete("0.0", END)
        if self.address_box.get("0.0", END).replace(" ", "").replace("\n", "") != "":
            phrases = list(self.M.decode_address(self.address_box.get("0.0", END), self.selected_theme))
            if phrases is not None:
                phrase_len = len(self.base_dict["NATURAL_ORDER"])
                text = " ".join(phrases[:3]) + "\n"
                for word_index in range(3, len(phrases[3:])):
                    text += phrases[word_index][0:2]
                text += "\n"
                for phrase_index in range((len(phrases) - 3) // phrase_len):
                    text += " ".join(phrases[
                                     phrase_len * phrase_index + 3:phrase_len * (phrase_index + 1) + 3]) + "\n"
                self.phrases_box.insert(END, text)
                root.clipboard_clear()
                root.clipboard_append(text[:-1])
                root.update()
            else:
                self.phrases_box.insert("0.0", "Not a compatible address format")
        else:
            self.phrases_box.insert("0.0", "Empty Input")

    def phrase_to_address_text(self):
        """
            This method converts a mnemonic phrases in formosa standard to a bitcoin address
        """
        self.address_box.delete("0.0", END)
        print(self.phrases_box.get("0.0", END))
        if (self.phrases_box.get("0.0", END) is not None) and \
                (self.phrases_box.get("0.0", END).replace(" ", "").replace("\n", "") != ""):
            address = self.M.encode_address(self.phrases_box.get("0.0", END))
            if address is not None:
                self.address_box.insert("0.0", address)
                root.clipboard_clear()
                root.clipboard_append(address)
                root.update()
            else:
                self.address_box.insert("0.0", "Not a compatible mnemonic format")
        else:
            self.address_box.insert("0.0", "Empty Input")

    def init_label_objects(self):
        """
            This method configures the objects in the grid of the Table Selector tab
        """
        a = self.Spreadsheet_Dimension_Size
        words_dictionary = self.base_dict
        syntactic_word_list = words_dictionary["NATURAL_ORDER"]

        # Clear all objects of the grid
        [[each_object.grid_forget()
          for each_object in self.object_dict[each_syntactic_word]]
         for each_syntactic_word in self.object_dict.keys()
         ]
        self.object_dict = {}
        [self.object_dict.update({each_word: []}) for each_word in syntactic_word_list]
        gc.collect()

        limited_list = {}
        row_len_limited = {}
        for each_syntactic_word in syntactic_word_list:
            limited_list.update({each_syntactic_word: []})
            row_len_limited.update({each_syntactic_word: []})
            returned_list, returned_bools = \
                self.limit_word_length(words_dictionary[each_syntactic_word]["TOTAL_LIST"])
            limited_list.update({each_syntactic_word: returned_list})
            row_len_limited.update({each_syntactic_word: returned_bools})

        font_sizes = {}
        for each_syntactic_word in syntactic_word_list:
            if row_len_limited[each_syntactic_word]:
                font_sizes.update({each_syntactic_word: 8})
            else:
                font_sizes.update({each_syntactic_word: 9})

        [[[[self.object_dict[each_syntactic_word].append(
            Label(self.grid_frame_selector,
                  text=str(self.input_set_column[each_column]) +
                  str(self.input_set_paragraph[each_paragraph]) +
                  str(self.input_set_row[each_row]) +
                  "-" +
                  limited_list[each_syntactic_word][each_column + a * a * each_paragraph + a * each_row],
                  font=Font(size=font_sizes[each_syntactic_word])
                  )
            )
            for each_column in range(a)
            if
            each_column + a * a * each_paragraph + a * each_row < len(
                words_dictionary[each_syntactic_word]["TOTAL_LIST"])]
            for each_row in range(a)]
            for each_paragraph in range(a)]
            for each_syntactic_word in syntactic_word_list
         ]

        [self.create_tooltip(self.object_dict[each_syntactic_word][each_label_index],
                             words_dictionary[each_syntactic_word]["TOTAL_LIST"][each_label_index])
         for each_syntactic_word in syntactic_word_list
         for each_label_index in range(len(self.object_dict[each_syntactic_word]))
         ]

    def limit_word_length(self, wordlist: list) -> (list, bool):
        """
            This method limits the characters in words of the grid

        Parameters
        ----------
        wordlist : list
            This is the list containing the words used in the grid
        Returns
        -------
        list, bool
            Returns the list with the words used in the grid updated with limited length
            Returns if the row is long and a smaller font should be used
        """
        a = self.Spreadsheet_Dimension_Size
        char_len_limit = 12
        limited_list = []
        row_len_limited = False
        row_chars = ""

        for each_word in wordlist:
            if len(each_word) > char_len_limit:
                limited_list.append(each_word[0:char_len_limit-3]+"...")
            else:
                limited_list.append(each_word)

        row_len_limited = True if any([
            len("".join(wordlist[a*each_row_index:(a+1)*each_row_index])) > a*char_len_limit
            for each_row_index in range(len(wordlist)//a)]) else row_len_limited

        for each_row_index in range(len(wordlist)//a):
            row_chars += "".join(wordlist[a*each_row_index:(a+1)*each_row_index])
            row_len_limited = True if len(row_chars) > a*char_len_limit else row_len_limited

        return limited_list, row_len_limited

    def define_columns_width(self):
        pass

    def new_grid(self):
        """
            This method calls the sequence to create and show a new words grid in the Table Selector tab
        """
        self.randomize_character_set()
        self.init_label_objects()
        self.allocate_grid()

    def enable_custom_keys_set(self):
        """
            This method enables the use of custom keys in the Table Selector tab
        """
        if self.use_custom_checkbox_var.get():
            self.custom_character_entry.config(state=NORMAL)
            self.define_key_list(None)
        else:
            self.custom_character_entry.config(state=DISABLED)
            self.custom_characters_var.set("")
            self.new_grid()

    def define_key_list(self, *event) -> list[str]:
        """
            This method set the keys used as index of the grid in the Table Selector tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method

        Returns
        -------
        list
            Returns the character list to be used as grid indexes
        """
        return_list = ["A", "S", "D", "F", "J", "K", "L", "Ç"]
        characters_list = list(self.custom_characters_var.get().upper())
        if len(characters_list) == self.Spreadsheet_Dimension_Size and \
                len(set(characters_list)) == len(characters_list):
            return_list = characters_list
        elif len(characters_list) > self.Spreadsheet_Dimension_Size:
            # Trim the Entry widget to have at max the constant maximum
            self.custom_characters_var.set(self.custom_characters_var.get()[0:self.Spreadsheet_Dimension_Size])
        return return_list

    def randomize_character_set(self):
        """
            This method randomizes the indexes of the grid independently of each other in the Table Selector tab
        """
        a = self.Spreadsheet_Dimension_Size
        input_character_set = list(self.define_key_list())
        random.shuffle(input_character_set)
        self.input_set_caseless = input_character_set + list([each_char.swapcase()
                                                              for each_char in input_character_set]
                                                             )
        column_char_set = input_character_set.copy()
        random.shuffle(column_char_set)
        self.input_set_column = column_char_set + list([each_char.swapcase() for each_char in column_char_set])
        row_char_set = input_character_set.copy()
        random.shuffle(row_char_set)
        self.input_set_row = row_char_set + list([each_char.swapcase() for each_char in row_char_set])
        paragraph_char_set = input_character_set.copy()
        random.shuffle(paragraph_char_set)
        self.input_set_paragraph = paragraph_char_set + list([each_char.swapcase() for each_char in paragraph_char_set])
        self.permutation_map.update({self.states[0]: self.input_set_caseless})
        self.permutation_map.update({self.states[1]: self.input_set_column})
        self.permutation_map.update({self.states[2]: self.input_set_paragraph})
        self.permutation_map.update({self.states[3]: self.input_set_row})

        # Clear column, row and paragraph index objects
        [each_object.grid_forget() for each_object in self.column_objects]
        self.column_objects = []
        [each_object.grid_forget() for each_object in self.row_objects]
        self.row_objects = []
        [each_object.grid_forget() for each_object in self.paragraph_objects]
        self.paragraph_objects = []

        # Write the characters in indexes
        self.column_objects = [Label(self.grid_frame_selector, text=self.input_set_column[column]) for column in
                               range(a)
                               ]
        self.row_objects = [Label(self.grid_frame_selector, text=self.input_set_row[row // a])
                            for row in range(a * a)
                            ]
        self.paragraph_objects = [Label(self.grid_frame_selector,
                                        text=self.input_set_paragraph[paragraph % a]
                                        )
                                  for paragraph in range(a * a)
                                  ]

    def allocate_grid(self, row_initial_position: int = 1, column_initial_position: int = 0):
        """
            This method allocates the grid objects in the grid accordingly to each index in the Table Selector tab

        Parameters
        ----------
        row_initial_position : int
            Initial position of objects in the row
        column_initial_position : int
            Initial position of objects in the column
        """
        current_objects = self.object_dict[self.natural_word]
        a = self.Spreadsheet_Dimension_Size
        # The ceil division to determine rows and paragraphs limits
        b = int(len(current_objects)/a) + (len(current_objects) % a > 0)
        c = int(b/a) + (b % a > 0)

        # Allocate the objects of the column, row and paragraph
        [self.column_objects[each_column].grid(
            row=row_initial_position,
            column=column_initial_position + 1 + each_column
        )
            for each_column in range(a)
        ]
        [[self.row_objects[each_row + a * each_paragraph].grid(
            row=row_initial_position + 1 + each_paragraph + a * each_row,
            column=a + 1
        )
            for each_row in range(c)
        ]
            for each_paragraph in range(a)]
        [[self.paragraph_objects[each_row + a * each_paragraph].grid(
            row=row_initial_position + 1 + each_paragraph + a * each_row,
            column=column_initial_position
        )
            for each_row in range(c)]
            for each_paragraph in range(a)
        ]

        [[[current_objects[each_column + a * each_paragraph + a * each_row].grid(
            row=row_initial_position + 1 + a * each_paragraph + each_row,
            column=column_initial_position + 1 + each_column,
            sticky=W)
            for each_column in range(a)
            if each_column + a * each_paragraph + a * each_row < len(current_objects)]
            for each_paragraph in range(a * a)]
            for each_row in range(a * a)
         ]

    def key_pressed(self, event):
        """
            This method is called when a key is pressed, it does the selection in the Table Selector tab

        Parameters
        ----------
        event : tkinter.event
            The event is the event calling the method, it is the key pressed and selects
        """

        # # Prints which key is pressed, used as test
        # print("key pressed: " + event.char + "; keysymbol: " + str(event.keysym_num) + "; state: " + str(
        #     self.current_state) + "; tab " + str(self.tab_control.tab(self.tab_control.select(), "text"))
        #       )

        if self.tab_control.tab(self.tab_control.select(), "text") == self.tab02 and \
                not self.table_selector.focus_get() == self.custom_character_entry:

            redo_set_keys = [65307, 32, 65288, 65535]  # esc, space, backspace, delete, respectively
            # key 65293 is the Enter key
            if event.char in self.input_set_caseless and self.current_state != self.states[-1]:

                self.current_state = self.states[self.states.index(self.current_state) + 1]
                self.selected_indexes[self.current_state] = \
                    self.permutation_map[self.current_state].index(event.char) \
                    % self.Spreadsheet_Dimension_Size

                char_index = self.permutation_map[self.current_state].index(event.char)
                self.delineate_cells(char_index)

            elif (event.keysym_num in redo_set_keys) and self.current_state != self.states[0]:
                self.current_state = self.states[0]
                char_index = 0
                self.set_validation_colored_msg()
                self.delineate_cells(char_index)

            elif event.keysym_num == 65293 and self.current_state == self.states[-1]:
                if self.check_color == "yellow":
                    self.valid_phrase = False
                self.pick_word()

        elif self.tab_control.tab(self.tab_control.select(), "text") == self.tab02 and \
                self.table_selector.focus_get() == self.custom_character_entry and event.keysym_num == 65293:
            self.tab_control.focus()
            self.new_grid()

    def delineate_cells(self, index: int):
        """
            This method specifies which words should be highlighted
            accordingly with words selected in the Table Selector tab

        Parameters
        ----------
        index : int
            This is the index of column, or paragraph or row selected which will highlighted
        """
        current_objects = self.object_dict[self.natural_word]
        a = self.Spreadsheet_Dimension_Size
        index = index % a
        begin = index
        end = len(current_objects)
        step = a

        if self.current_state == self.states[0]:
            step = 1
            begin = index
            end = len(current_objects)

        elif self.current_state == self.states[1]:
            begin = index
            end = len(current_objects)

        elif self.current_state == self.states[2]:
            column = self.selected_indexes[self.states[1]]
            begin = (a * a) * index + column
            end = (a * a) * index + column + a * (a - 1)

        elif self.current_state == self.states[3]:
            column = self.selected_indexes[self.states[1]]
            row = self.selected_indexes[self.states[2]]
            begin = column + a * index + (a * a) * row
            end = begin
            if end + 1 < len(self.object_dict[self.natural_word]):
                self.check_word_list(self.object_dict[self.natural_word][begin:end + 1][0].cget("text"))
        color = self.defaultbg if self.current_state == self.states[0] else self.check_color
        self.fill_bg_color(color, begin, end, step)

    def fill_bg_color(self, color: str, begin: int, end: int, step: int):
        """
            This method highlights the background of the selected set of words in the Table Selector tab

        Parameters
        ----------
        color : str
            This is the color which the background is highlighted
        begin : int
            This is the initial index to highlight words
        end : int
            This is the end to highlight the words
        step : int
            This is the step which maps the selected serialized objects to a grid layout
        """
        current_objects = self.object_dict[self.natural_word]
        if self.highlight_checkbox_var.get():
            current_objects = self.object_dict[self.natural_word]
            [each_label.config(bg=color) for each_label in current_objects[begin:end + 1:step]]
            [each_label.config(bg=self.defaultbg) for each_label in current_objects
             if (each_label not in current_objects[begin:end + 1:step])
             ]
        else:
            begin = 0
            [each_label.config(bg=self.defaultbg) for each_label in current_objects
             if (each_label not in current_objects[begin:end + 1:step])
             ]

    def pick_word(self):
        """
            This method stores the selection when a word is selected in the Table Selector tab
        """
        a = self.Spreadsheet_Dimension_Size
        column = self.selected_indexes[self.states[1]]
        row = self.selected_indexes[self.states[2]]
        paragraph = self.selected_indexes[self.states[3]]
        words_list = self.base_dict[self.natural_word]["TOTAL_LIST"]
        self.current_state = self.states[0]
        char_index = 0
        if column + (a * a) * row + a * paragraph < len(words_list):
            natural_order_list = self.base_dict["NATURAL_ORDER"]

            # print("word selected: " + str(words_list[column + (a * a) * row + a * paragraph]))
            self.sel_theme_button.configure(state=DISABLED)
            self.picked_passphrase.append(words_list[column + (a * a) * row + a * paragraph])
            self.delineate_cells(char_index)
            [self.selected_indexes.update({each_key: a}) for each_key in self.selected_indexes.keys()]

            self.natural_word = natural_order_list[natural_order_list.index(self.natural_word) + 1] if \
                self.natural_word != natural_order_list[-1] else natural_order_list[0]

            self.new_grid()
            self.set_validation_colored_msg()
        else:
            self.delineate_cells(char_index)
            [self.selected_indexes.update({each_key: a}) for each_key in self.selected_indexes.keys()]

        self.grayout_gen_button()

    def change_highlight_var(self, event=None):
        """
            This method switches the variable of the highlight checkbox

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.highlight_checkbox_var.set(not self.highlight_checkbox_var.get())
        self.changed_show_highlight()

    def changed_show_highlight(self, event=None):
        """
            This method is called by the interaction with highlight_checkbox,
            it shows or hides the background of the selected words in the Table Selector tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        if self.highlight_checkbox_var.get():
            char_index = self.selected_indexes[self.current_state]
            self.delineate_cells(char_index)
        else:
            [[each_label.config(bg=self.defaultbg) for each_label in self.object_dict[each_syntactic_word]]
             for each_syntactic_word in self.object_dict.keys()
             ]

    def reset_password(self):
        """
            This method resets the variables and words which were selected so far in the Table Selector tab
        """
        self.picked_passphrase = []
        natural_order_list = self.base_dict["NATURAL_ORDER"]
        self.natural_word = natural_order_list[0]
        self.current_state = self.states[0]
        self.valid_phrase = True
        self.set_validation_colored_msg()

        [self.selected_indexes.update({each_key: self.Spreadsheet_Dimension_Size})
         for each_key in self.selected_indexes.keys()
         ]
        self.sel_theme_button.configure(state=NORMAL)

        [[each_label.config(bg=self.defaultbg) for each_label in self.object_dict[each_syntactic_word]]
         for each_syntactic_word in self.object_dict.keys()
         ]
        self.new_grid()
        self.grayout_gen_button()

    def grayout_gen_button(self):
        """
            This method enables the Generate Phrase button when a whole phrase is picked
            and disables the Generate Phrase button
            when the words picked does not form whole phrase in the Table Selector tab
        """
        phrase_len = len(self.base_dict["NATURAL_ORDER"])
        if (len(self.picked_passphrase) % phrase_len == 0) and len(self.picked_passphrase) > 0:
            self.output_button.configure(state=NORMAL)
        else:
            self.output_button.configure(state=DISABLED)

    def output_phrases(self):
        """
            This method prints the phrases with the selected words in the Table Selector tab
        """
        phrase_len = len(self.base_dict["NATURAL_ORDER"])
        if (len(self.picked_passphrase) % phrase_len == 0) and len(self.picked_passphrase) > 0:
            for i in range(len(self.picked_passphrase)):
                print(self.picked_passphrase[i][0:2], end="")
            print("")
            for i in range(len(self.picked_passphrase) // phrase_len):
                print(" ".join(self.picked_passphrase[phrase_len * i:phrase_len * (i + 1)]))

    def check_word_list(self, word=None):
        """
            This method checks if the phrase so far follows the words list
            according to theme dictionary in the Table Selector tab

        Parameters
        ----------
        word :
            This is the word selected that is get from the grid, it can None as not the whole grid is filled with words
            also not all steps are evaluated because the filling order is not the same
            as natural order of the language
        """
        checklist = self.picked_passphrase.copy()
        if word is not None:
            checklist.append(word[word.find("-") + 1:])
        state = True
        natural_order = self.edited_dict["NATURAL_ORDER"]
        filling_order = self.edited_dict["FILLING_ORDER"]
        phrases_shift = (len(checklist) // len(natural_order)) * len(natural_order)
        check_size = len(checklist) % len(natural_order)

        if (word is None and check_size != 0) or \
                (word is not None and check_size != 1):
            for filling_order_word in filling_order[1:check_size]:
                if all(value in natural_order[:check_size] for value in filling_order[:check_size]):
                    restricted_by = self.edited_dict[filling_order_word]["RESTRICTED_BY"]
                    restricted_by_word = checklist[natural_order.index(restricted_by) + phrases_shift]
                    state = False if checklist[natural_order.index(filling_order_word) + phrases_shift] not in \
                                     self.edited_dict[restricted_by][filling_order_word]["MAPPING"][restricted_by_word] \
                        else state

        self.set_validation_colored_msg(state)

    def set_validation_colored_msg(self, state=True):
        """
            This method warns with a yellow background when the
            word selected doesn't follow the list in the theme dictionary and if it is not yet confirmed as selected
            but keep the background red if it was selected outside the rules before in the Table Selector tab

        Parameters
        ----------
        state : bool
            This is the state of the selected word, if it follows or not the list in the theme dictionary
        """
        valid_message = "Incompatible\nPhrase"
        if not self.valid_phrase:
            # Setting a red color to represent an inadequate frase
            self.check_color = "#FF4040"
        elif not state:
            self.check_color = "yellow"
        else:
            valid_message = "Selected phrase\nso far is compatible"
            self.check_color = "#3AC73A"
        self.sel_valid_phrase_label.config(text=valid_message, bg=self.check_color)

    def changed_replace_by(self, *event):
        """
            This method is called when typing in the word to insert entry
            It enables or disables the copy from listbox depending on the word inserted

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        if self.swap_syntactic_word_replace_by_var.get() in self.edited_dict["NATURAL_ORDER"]:
            if self.swap_replace_by_var.get() in \
                    self.edited_dict[self.swap_syntactic_word_replace_by_var.get()]["TOTAL_LIST"]:
                self.swap_copy_from_listbox.config(state=NORMAL)
                self.swap_copy_from_listbox.delete(0, END)
                self.swap_copy_from_listbox.config(state=DISABLED)
                self.use_copy_list = False
            elif self.swap_to_replace_listbox.get(0, END) is not None and self.swap_replace_by_var.get() is not None:
                current_dict = self.edited_dict
                syntactic_replace_by = self.swap_syntactic_word_replace_by_var.get()
                syntactic_replace_in = self.swap_syntactic_word_replace_in_var.get()
                replace_in = self.swap_replace_in_listbox.get(ANCHOR)
                restricted_words_list = current_dict[syntactic_replace_in][syntactic_replace_by]["MAPPING"][replace_in]
                self.swap_copy_from_listbox.config(state=NORMAL)
                [self.swap_copy_from_listbox.insert(each_index, restricted_words_list[each_index])
                 for each_index in range(len(restricted_words_list))
                 ]
                self.swap_words_button.config(state=DISABLED)
                self.swap_copy_from_listbox.selection_clear(0, END)
                self.use_copy_list = True

        self.evaluate_state()

    def change_syntactic_replace_by(self, *event):
        """
            This method is called when the OptionMenu of the word to be inserted is interacted
            It selects the words that restrict the selected type of word to be inserted in the Word Swapper tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.swap_syntactic_word_replace_in_var.trace_remove("write", self.trace_syntactic_replace_in)
        restricted_by = self.edited_dict[self.swap_syntactic_word_replace_by_var.get()]["RESTRICTED_BY"]
        self.swap_syntactic_word_replace_in_var.set(restricted_by)
        self.swap_syntactic_replace_in_list = [each_syntactic_word
                                               for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]
                                               if self.edited_dict[each_syntactic_word]["RESTRICTS"] != []
                                               ]
        self.swap_replace_in_listbox.delete(0, END)
        self.swap_replace_in_listbox.config(state=NORMAL)
        if restricted_by != "NONE":
            total_list = self.edited_dict[restricted_by]["TOTAL_LIST"]
            self.swap_replace_in_listbox.config(state=NORMAL)
            self.swap_to_replace_listbox.delete(0, END)
            self.swap_to_replace_listbox.config(state=DISABLED)
        else:
            total_list = []
            self.swap_replace_in_listbox.config(state=DISABLED)
            self.changed_replace_in()

        self.swap_syntactic_replace_in["menu"].delete(0, "end")
        [self.swap_syntactic_replace_in["menu"].add_command(
            label=each_option, command=lambda option=each_option: self.swap_syntactic_word_replace_in_var.set(option)
        )
            for each_option in self.swap_syntactic_replace_in_list
        ]

        self.swap_copy_from_listbox.config(state=NORMAL)
        self.swap_copy_from_listbox.delete(0, END)
        self.swap_copy_from_listbox.config(state=DISABLED)
        self.swap_fill_state_list[0] = True
        self.swap_fill_state_list[2] = False

        [self.swap_replace_in_listbox.insert(each_index, total_list[each_index])
         for each_index in range(len(total_list))
         ]

        self.trace_syntactic_replace_in = \
            self.swap_syntactic_word_replace_in_var.trace_add("write", self.change_syntactic_replace_in)
        self.evaluate_state()

    def change_syntactic_replace_in(self, *event):
        """
            This method is called when the OptionMenu of the word that restricts the inserted word is interacted
            It selects words of the OptionMenu of the words restricted in the Word Swapper tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.swap_syntactic_word_replace_by_var.trace_remove("write", self.trace_syntactic_replace_by)
        restricts = self.edited_dict[self.swap_syntactic_word_replace_in_var.get()]["RESTRICTS"]
        self.swap_syntactic_replace_by_list = self.edited_dict["NATURAL_ORDER"]
        set_var = restricts[0] if isinstance(restricts, list) and len(restricts) > 0 else restricts
        self.swap_syntactic_word_replace_by_var.set(set_var)

        self.swap_syntactic_replace_by["menu"].delete(0, "end")
        [self.swap_syntactic_replace_by["menu"].add_command(
            label=each_option, command=lambda option=each_option: self.swap_syntactic_word_replace_by_var.set(option)
        )
            for each_option in self.swap_syntactic_replace_by_list
        ]

        self.swap_replace_in_listbox.delete(0, END)
        self.swap_replace_in_listbox.config(state=NORMAL)
        self.swap_fill_state_list[1] = False
        total_list = self.edited_dict[self.swap_syntactic_word_replace_in_var.get()]["TOTAL_LIST"]
        [self.swap_replace_in_listbox.insert(each_index, total_list[each_index])
         for each_index in range(len(total_list))
         ]

        self.swap_copy_from_listbox.delete(0, END)
        self.swap_copy_from_listbox.config(state=DISABLED)

        self.swap_to_replace_listbox.delete(0, END)
        self.swap_to_replace_listbox.config(state=DISABLED)
        self.swap_fill_state_list[0] = True
        self.swap_fill_state_list[2] = False

        self.trace_syntactic_replace_by = \
            self.swap_syntactic_word_replace_by_var.trace_add("write", self.change_syntactic_replace_by)
        self.evaluate_state()

    def changed_replace_in(self, event=None):
        """
            This method is called when the word to be inserted is selected
            It selects the words restricted by the selected word that restricts in the Word Swapper tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.swap_to_replace_listbox.selection_clear(0, END)
        self.swap_words_button.config(state=DISABLED)

        current_dict = self.edited_dict
        syntactic_replace_by = self.swap_syntactic_word_replace_by_var.get()
        self.swap_to_replace_listbox.delete(0, len(self.swap_to_replace_listbox.get(0, END)))
        self.swap_to_replace_listbox.config(state=NORMAL)
        words_list = current_dict[self.swap_syntactic_word_replace_in_var.get()][
            self.swap_syntactic_word_replace_by_var.get()]["MAPPING"][self.swap_replace_in_listbox.get(ANCHOR)] \
            if self.swap_syntactic_word_replace_in_var.get() != "NONE" \
            else current_dict[syntactic_replace_by]["TOTAL_LIST"]
        [self.swap_to_replace_listbox.insert(each_index, words_list[each_index])
         for each_index in range(len(words_list))
         ]
        [self.swap_to_replace_listbox.insert(each_index, words_list[each_index])
         for each_index in range(len(words_list))
         ]
        self.swap_fill_state_list[1] = True

        self.evaluate_state()

    def changed_to_replace(self, event=None):
        """
            This method is called when the word where the change will happen is selected
            It selects the words that can be removed in the Word Swapper tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.swap_fill_state_list[2] = True
        self.swap_copy_from_listbox.selection_clear(0, END)
        self.swap_words_button.config(state=DISABLED)

        replace_by = self.swap_replace_by_entry.get()
        syntactic_replace_by = self.swap_syntactic_word_replace_by_var.get()
        current_dict = self.edited_dict
        if replace_by not in current_dict[syntactic_replace_by]["TOTAL_LIST"]:
            self.use_copy_list = True
            replace_in = self.swap_syntactic_word_replace_in_var.get()
            self.swap_copy_from_listbox.config(state=NORMAL)
            if replace_in != "NONE":
                mapped_words = current_dict[replace_in][syntactic_replace_by][
                    "MAPPING"
                ]
                restricted_words_list = mapped_words[self.swap_replace_in_listbox.get(ANCHOR)]
            else:
                restricted_words_list = current_dict[syntactic_replace_by]["TOTAL_LIST"]
            [self.swap_copy_from_listbox.insert(each_index, restricted_words_list[each_index])
             for each_index in range(len(restricted_words_list))
             ]
        else:
            self.use_copy_list = False
            self.evaluate_options_chosen()

        self.evaluate_state()

    def evaluate_state(self, *event):
        """
            This method evaluates the state of Word Swapper tab and enables buttons to be pressed
            Evaluates if all options were chosen
            Evaluates if the file name is correctly written

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        self.swap_theme_button.config(state=DISABLED)
        if all(self.swap_fill_state_list):
            self.evaluate_options_chosen()
        file_name = self.swap_file_name_entry.get()
        dot_index = file_name.find(".")
        if len(file_name) == 0 or dot_index == 0:
            self.swap_save_button.config(state=DISABLED)
        elif self.can_save:
            self.swap_save_button.config(state=NORMAL)

    def evaluate_options_chosen(self, event=None):
        """
            This method evaluates the words chosen in the Word Swapper tab
            It applies the collision criteria which rejects words with same first two letters in the same list
            It rejects a repeated word to be inserted
            It rejects empty strings to be inserted

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        replace_by = self.swap_replace_by_entry.get()
        if len(replace_by) > 1:
            current_dict = self.edited_dict
            syntactic_replace_by = self.swap_syntactic_word_replace_by_var.get()
            syntactic_restricted_by = current_dict[syntactic_replace_by]["RESTRICTED_BY"]
            replace_in_selected_index = self.swap_replace_in_listbox.curselection()
            replace_in = self.swap_replace_in_listbox.get(replace_in_selected_index[0]) \
                if len(replace_in_selected_index) > 0 else ""
            to_replace_selected_index = self.swap_to_replace_listbox.curselection()
            to_replace = self.swap_to_replace_listbox.get(to_replace_selected_index[0]) \
                if len(to_replace_selected_index) > 0 else ""
            syntactic_replace_in = self.swap_syntactic_word_replace_in_var.get()
            syntactic_replace_by = self.swap_syntactic_word_replace_by_var.get()

            words_list = current_dict[syntactic_replace_in][syntactic_replace_by]["MAPPING"][replace_in] \
                if syntactic_replace_in != "NONE" else current_dict[syntactic_replace_by]["TOTAL_LIST"]
            first_letters_list = [each_word[:2]
                                  for each_word in words_list
                                  ]
            first_letters_string = " ".join(first_letters_list)
            first_letters_word = replace_by[:2]
            first_letters_to_replace = to_replace[:2]
            # Set collision_criteria to be always False to remove the check of the unicity of first two letters
            collision_criteria = (first_letters_word in first_letters_string) and\
                                 (first_letters_word != first_letters_to_replace)

            listbox_tuple = self.swap_copy_from_listbox.curselection()
            copy_from = self.swap_copy_from_listbox.get(listbox_tuple[0]) if len(listbox_tuple) > 0 else ""

            if collision_criteria or replace_by in words_list:
                warning_message = "Collision\nDetected"
                self.swap_collision_warning_label.config(text=warning_message, fg="red")
                self.swap_collision_warning_label.grid(column=7, row=2, padx=5, pady=5)
                self.swap_words_button.config(state=DISABLED)

            elif not (collision_criteria or replace_by in words_list):
                self.swap_collision_warning_label.grid_forget()

            if not (collision_criteria or replace_by in words_list) and \
                    (syntactic_restricted_by == "NONE" or replace_in != "") and to_replace != "" and \
                    (not self.use_copy_list or copy_from != ""):
                self.swap_collision_warning_label.grid_forget()
                self.swap_words_button.config(state=NORMAL)

    def swap_words(self):
        """
            This method calls the swapper function to swap one word for another in the Word Swapper tab
        """
        file_load = self.edited_dict
        replace_by = self.swap_replace_by_entry.get()
        syntactic_replace_by = self.swap_syntactic_word_replace_by_var.get()
        replace_in = self.swap_replace_in_listbox.get(ANCHOR)
        syntactic_replace_in = self.swap_syntactic_word_replace_in_var.get()
        to_replace = self.swap_to_replace_listbox.get(ANCHOR)
        copy_from = self.swap_copy_from_listbox.get(ANCHOR) if self.use_copy_list else None
        self.edited_dict, success_phrase = swapper.word_swap(file_load, replace_by, syntactic_replace_by, replace_in,
                                                             syntactic_replace_in, to_replace, copy_from
                                                             )
        self.all_words = []
        for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]:
            self.all_words += self.edited_dict[each_syntactic_word]["TOTAL_LIST"]
        self.write_texbox(self.swap_history_textbox, success_phrase)
        self.can_save = True
        self.reset_variables()
        self.evaluate_state()

    def swap_reset(self):
        """
            This method resets all widgets in the Word Swapper tab
        """
        self.can_save = False
        self.swap_file_name_entry.delete(0, END)
        self.swap_history_textbox.config(state=NORMAL)
        self.swap_history_textbox.delete(index1="0.0", index2=END)
        self.swap_history_textbox.config(state=DISABLED)
        self.edited_dict = copy.deepcopy(self.base_dict)
        self.swap_save_button.config(state=DISABLED)
        self.swap_collision_warning_label.grid_forget()
        self.swap_theme_button.config(state=NORMAL)
        self.reset_variables()

    def reset_variables(self):
        """
            This method resets all variables in the Word Swapper tab
        """
        # Trace must be removed in order to update the traced variable
        self.swap_syntactic_word_replace_by_var.trace_remove("write", self.trace_syntactic_replace_by)
        self.swap_syntactic_word_replace_by_var.set("")
        self.swap_syntactic_replace_by_list = self.edited_dict["NATURAL_ORDER"]
        self.swap_syntactic_replace_by["menu"].delete(0, "end")
        [self.swap_syntactic_replace_by["menu"].add_command(
            label=each_option, command=lambda option=each_option: self.swap_syntactic_word_replace_by_var.set(option)
        )
            for each_option in self.swap_syntactic_replace_by_list
        ]
        self.trace_syntactic_replace_by = \
            self.swap_syntactic_word_replace_by_var.trace_add("write",
                                                              self.change_syntactic_replace_by
                                                              )

        self.swap_syntactic_word_replace_in_var.trace_remove("write", self.trace_syntactic_replace_in)
        self.swap_syntactic_word_replace_in_var.set("")
        self.swap_syntactic_replace_in_list = [each_syntactic_word
                                               for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]
                                               if self.edited_dict[each_syntactic_word]["RESTRICTS"] != []
                                               ]
        self.swap_syntactic_replace_in["menu"].delete(0, "end")
        [self.swap_syntactic_replace_in["menu"].add_command(
            label=each_option, command=lambda option=each_option: self.swap_syntactic_word_replace_in_var.set(option))
            for each_option in self.swap_syntactic_replace_in_list
         ]
        self.trace_syntactic_replace_in = \
            self.swap_syntactic_word_replace_in_var.trace_add("write", self.change_syntactic_replace_in)

        self.all_words = []
        for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]:
            self.all_words += self.edited_dict[each_syntactic_word]["TOTAL_LIST"]
        self.swap_fill_state_list = [False] * len(self.swap_fill_state_list)
        self.use_copy_list = True

        self.swap_replace_by_entry.delete(0, END)
        self.swap_syntactic_replace_by.config(state=NORMAL)
        self.swap_replace_in_listbox.delete(0, len(self.swap_replace_in_listbox.get(0, END)))
        self.swap_replace_in_listbox.config(state=DISABLED)
        self.swap_syntactic_replace_in.config(state=NORMAL)
        self.swap_to_replace_listbox.delete(0, len(self.swap_to_replace_listbox.get(0, END)))
        self.swap_to_replace_listbox.config(state=DISABLED)
        self.swap_copy_from_listbox.delete(0, len(self.swap_copy_from_listbox.get(0, END)))
        self.swap_copy_from_listbox.config(state=DISABLED)
        self.swap_words_button.config(state=DISABLED)
        self.swap_correct_typo_entry.delete(0, END)
        self.swap_wrong_typo_entry.delete(0, END)

    def swap_save(self):
        """
            This method saves in a json file the changes done in the Word Swapper tab
            It only saves if the given file name is valid
        """
        file_name = self.swap_file_name_entry.get()
        dot_index = file_name.find(".")
        if len(file_name) > 0:
            if dot_index == -1:
                file_name += ".json"
            elif dot_index > 0:
                file_name = file_name[:dot_index] + ".json"

            words_dictionary = ThemeDict(self.edited_dict)
            verifier = Verifier()
            verifier.start_verification(words_dictionary)

            path = self._get_directory() / "themes" / file_name

            if path.is_file():
                answer = messagebox.askquestion("Overwrite File?",
                                                "File %s already exist.\nDo you want to overwrite it?" % file_name
                                                )
                if answer == "yes":
                    pass
                elif answer == "no":
                    return
                else:
                    warning_message = "something went wrong"
                    self.write_texbox(self.swap_history_textbox, warning_message, "warning", "orange")
                    return
            with open(path, "w+") as file:
                json.dump(self.edited_dict, file, indent=4, sort_keys=True)
            saved_phrase = "Saved file %s successfully" % file_name
            self.write_texbox(self.swap_history_textbox, saved_phrase)

    def swap_correct_typo(self):
        """
            This method replaces all occurrences of a word in the dictionary.

        Returns
        -------
            Nothing is returned. Just swap the words when they aren't the same and not empty.
        """
        insert_word = self.swap_correct_typo_entry.get()
        remove_word = self.swap_wrong_typo_entry.get()
        if insert_word == remove_word or insert_word == "" or remove_word == "":
            self.check_same_words(remove_word, insert_word)
            return
        has_changed = False
        has_collision = False
        has_found = False

        syntactic_words_list = self.edited_dict["NATURAL_ORDER"]
        for each_syntactic_word in syntactic_words_list:
            current_dict = copy.deepcopy(self.edited_dict[each_syntactic_word])
            restrictions = current_dict["RESTRICTS"]
            current_dict, has_changed, collided, found = self.check_find_word(
                remove_word, insert_word, current_dict, "TOTAL_LIST", has_changed, restrictions
            )
            if collided:
                has_collision = True
            if found:
                has_found = True

            for each_restriction in restrictions:
                restrict_dict = current_dict[each_restriction]
                restrict_dict, has_changed, collided, found = self.check_find_word(
                    remove_word, insert_word, restrict_dict, "IMAGE", has_changed
                )
                if collided:
                    has_collision = True
                if found:
                    has_found = True
                current_dict.update({each_restriction: restrict_dict})
            self.edited_dict.update({each_syntactic_word: current_dict})

        if has_collision:
            warning_message = "Error: Typo correction introduced a collision in some of the lists"
            self.write_texbox(self.swap_history_textbox, warning_message, "error", "red")

        if has_changed:
            self.reset_variables()
            replaced_phrase = "Typo error %s corrected by %s" % (remove_word, insert_word)
            self.write_texbox(self.swap_history_textbox, replaced_phrase)
            self.all_words = []
            for each_syntactic_word in self.edited_dict["NATURAL_ORDER"]:
                self.all_words += self.edited_dict[each_syntactic_word]["TOTAL_LIST"]
            self.can_save = True
            self.evaluate_state()
        elif not has_found:
            warning_message = "Warning: word %s was not found" % remove_word
            self.write_texbox(self.swap_history_textbox, warning_message, "warning", "orange")

    def enable_replace_button(self, *event):
        """
            This method enables or disables the Replace button in Word Swapper tab

        Parameters
        ----------
        event :
            The event is the event calling the method, it is not used by the method
        """
        remove_word = self.swap_wrong_typo_entry.get()
        button_state = DISABLED if remove_word not in self.all_words else NORMAL
        self.swap_correct_typo_button.config(state=button_state)

    def check_same_words(self, remove: str, insert: str):
        """
            This method checks the words given to insert and remove in the Replace All functionality

        Parameters
        ----------
        remove : str
            This is the word to be removed from the items of the dictionary
        insert : str
            This is the word to be inserted into the items of the dictionary
        """
        if remove == insert and (not insert == "" or not remove == ""):
            warning_message = "Warning: word wanted to remove and insert are the same"
            self.write_texbox(self.swap_history_textbox, warning_message, "warning", "orange")
        if remove == "":
            warning_message = "Warning: word wanted to remove was not filled"
            self.write_texbox(self.swap_history_textbox, warning_message, "warning", "orange")
        if insert == "":
            warning_message = "Warning: word wanted to insert was not filled"
            self.write_texbox(self.swap_history_textbox, warning_message, "warning", "orange")

    def check_find_word(self, remove: str, insert: str,
                        current_dict: dict, complete_list: str,
                        has_changed: bool, restrictions: list = None) -> (dict, bool, bool, bool):
        """
            This method search a word in total lists, image lists and in the items of the dictionary
            Then swaps all occurrences of this word by another

        Parameters
        ----------
        remove : str
            This is the word to be removed from all the keys and lists
        insert : str
            This is the word to be inserted into all the keys and lists
        current_dict : dict
            This is the dictionary to be edited
        complete_list : str
            This is which list will be searched, a TOTAL_LIST or IMAGE list
        has_changed : bool
            This is a state that tells if the word was found and exchanged
        restrictions : list
            This is the restrictions of each syntactic word of the dictionary

        Returns
        -------
        dict, bool, bool, bool
            Returns the original dictionary with the new word inserted
            Returns the state if a word was swapped
            Returns the state if there was any collision
            Returns the state if the word to be removed was found in any list
        """
        has_collision = False
        if remove in current_dict[complete_list] and restrictions is not None:
            for each_restriction in restrictions:
                current_dict[each_restriction]["MAPPING"][insert] = \
                    current_dict[each_restriction]["MAPPING"].pop(remove)
                current_dict[each_restriction]["MAPPING"][insert].sort()
            current_dict[complete_list] = self.replace_in_list(current_dict[complete_list], insert, remove)
            return current_dict, True, has_collision, True

        elif remove in current_dict[complete_list] and restrictions is None:
            for each_key in current_dict["MAPPING"]:
                if remove in current_dict["MAPPING"][each_key]:

                    words_list = current_dict["MAPPING"][each_key]

                    first_letters_list = [each_word[:2] for each_word in words_list]
                    first_letters_string = " ".join(first_letters_list)
                    first_letters_word = insert[:2]
                    first_letters_to_replace = remove[:2]
                    collision_criteria = (first_letters_word in first_letters_string) and \
                                         (first_letters_word != first_letters_to_replace)
                    if collision_criteria:
                        has_collision = True

                    words_list = self.replace_in_list(words_list, insert, remove)

                    current_dict["MAPPING"].update({each_key: words_list})

            current_dict.update({complete_list: self.replace_in_list(current_dict[complete_list], insert, remove)})
            return current_dict, True, has_collision, True
        return current_dict, has_changed, has_collision, False

    def replace_in_list(self, base_list: list, insert: str, remove: str) -> list:
        """
            This method inserts a given word in exchange for another given word in a given list

        Parameters
        ----------
        base_list : list
            This is the list where to swap words
        insert : str
            This is the word to be inserted in the list
        remove : str
            This is the word to be removed in the list

        Returns
        -------
        list
            Returns the list sorted with the new word inserted
        """
        duplicates = [duplicated_word for duplicated_word in base_list if base_list.count(duplicated_word) > 1]
        if duplicates:
            base_list = list(set(base_list))
            warning_message = "Duplicates %s found and removed" % ", ".join(list(set(duplicates)))
            self.write_texbox(self.swap_history_textbox, warning_message, "warning", "orange")
        word_index = base_list.index(remove)
        base_list[word_index] = insert
        base_list.sort()
        return base_list

    def write_texbox(self, textbox, text: str, type_msg: str = None, color: str = None):
        """
            This method writes a text into the given textbox

        Parameters
        ----------
        textbox :
            This is the object textbox in the window which will be written
        text : str
            This is the text that will be written
        type_msg : str
            This is the type of given message, a simple warning or an error
        color : str
            This is the optional color of the text
        """
        textbox.config(state=NORMAL)
        if color is not None:
            textbox.tag_configure(type_msg, foreground=color)
            textbox.insert(0.0, text + "\n", type_msg)
        else:
            textbox.insert(0.0, text + "\n")
        textbox.config(state=DISABLED)


root = Tk()
root.geometry("1280x600")
app = Window(root)
root.bind("<Key>", app.key_pressed)
root.report_callback_exception = handle_exception
root.mainloop()
