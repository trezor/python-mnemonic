from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QPushButton, QComboBox,
                             QSpinBox, QLineEdit, QTextEdit, QVBoxLayout, QGridLayout, QCheckBox)
from PyQt5.QtGui import QFont, QKeyEvent, QFocusEvent
from PyQt5.QtCore import Qt
import mnemonic
from pathlib import Path
import random
import sys

# This prevents IDE from creating a cache file
sys.dont_write_bytecode = True


class BaseTab(QWidget):
    def __init__(self, parent: 'QtFormosa'):
        super().__init__(parent)
        self.parent = parent

        # General tab variables
        self.set_config = True
        self.base_theme = self.parent.base_theme
        self.main_layout = QVBoxLayout()
        self.tab_layout = QGridLayout()

        # Widgets instantiation
        self.select_base_theme = QComboBox(self)
        self.select_base_theme.addItems(self.parent.themes)
        self.select_base_theme.setCurrentText(self.base_theme)
        self.select_base_theme.currentTextChanged.connect(self.set_base_theme)
        self.quit_button = QPushButton(self)
        self.quit_button.setText("Exit")
        self.quit_button.clicked.connect(self.close_application)

        self.set_layout()

    @property
    def is_bip39_theme(self) -> bool:
        """ Evaluates whether the theme chosen is from BIP39 or not"""
        is_bip39 = self.base_theme.startswith(self.parent.DEFAULT_THEME)
        return is_bip39

    def set_layout(self):
        """ Place the tab containers of the widgets"""
        self.main_layout.addWidget(self.select_base_theme)
        self.main_layout.addLayout(self.tab_layout)
        self.main_layout.addWidget(self.quit_button)

        self.setLayout(self.main_layout)

    def init_configuration(self):
        """
            Common base method to initialize the tab configuration of all tabs with config_tab() method
            Do the configuration only once by setting the config variable to False for each of the tabs instances
        """
        if not self.set_config:
            # Do it only once
            return
        self.config_tab()
        self.set_config = False

    def config_tab(self):
        """ Overloaded in each tab, set up the widgets"""
        pass

    def set_tab_layout(self):
        """ Overloaded in each tab, place the widgets"""
        pass

    def set_base_theme(self, theme_chosen: str):
        """
            Set the current base theme

        Parameters
        ----------
        theme_chosen : str
            The theme to be set, must be one of found themes in .json files
        """
        self.parent.set_base_theme(theme_chosen)
        self.base_theme = theme_chosen
        self.select_base_theme.setCurrentText(theme_chosen)

    def close_application(self):
        """ Close the parent which exit the application. Bye, come again!"""
        self.parent.close()


class MnemonicGeneratorTab(BaseTab):
    def __init__(self, parent: 'QtFormosa'):
        super().__init__(parent)
        self.parent = parent

        # General tab variables
        self.last_text = ""
        self.password_lines = []
        self.last_n_phrases = 0

        # Widgets instantiation
        self.text_box = QTextEdit(self)
        self.run_button = QPushButton(self)
        self.clip_button = QPushButton(self)
        self.redo_button = QPushButton(self)
        self.clear_button = QPushButton(self)
        self.select_phrases = QSpinBox(self)
        self.check_number = QCheckBox(self)
        self.check_char = QCheckBox(self)
        self.check_case = QCheckBox(self)
        self.save_button = QPushButton(self)
        self.save_msg = QLabel(self)
        self.copy_msg = QLabel(self)
        self.enable_checkboxes()

    def config_tab(self):
        """ Set up widgets, config texts, commands and variables """
        self.run_button.setText("Run!")
        self.run_button.clicked.connect(self.generate_text)
        self.clip_button.setText("Copy")
        self.clip_button.clicked.connect(self.copy_to_clipboard)
        self.redo_button.setText("Redo")
        self.redo_button.clicked.connect(self.recover_text)
        self.clear_button.setText("Clear")
        self.clear_button.clicked.connect(self.clear_text)
        self.check_case.setText("Include Uppercase")
        self.check_case.clicked.connect(self.insert_swap_case)
        self.check_number.setText("Include Number")
        self.check_number.clicked.connect(self.insert_number)
        self.check_char.setText("Include Special Character")
        self.check_char.clicked.connect(self.insert_spc_char)
        self.save_button.setText("Save")
        self.save_button.clicked.connect(self.save_file)
        self.copy_msg.setText("Copied to clipboard")
        self.copy_msg.hide()
        self.save_msg.setText("Saved to \'output.txt\'")
        self.save_msg.hide()

        self.config_phrases_selector()
        self.set_tab_layout()

    def set_tab_layout(self):
        """ Place the widgets in the window tab"""
        self.text_box.setGeometry(0, 0, 20, 75)
        self.tab_layout.addWidget(self.run_button, 0, 0)
        self.tab_layout.addWidget(self.clip_button, 1, 0)
        self.tab_layout.addWidget(self.text_box, 0, 4, 10, 5)
        self.tab_layout.addWidget(self.select_phrases, 2, 0)
        self.tab_layout.addWidget(self.check_case, 3, 0)
        self.tab_layout.addWidget(self.check_char, 4, 0)
        self.tab_layout.addWidget(self.check_number, 5, 0)
        self.tab_layout.addWidget(self.redo_button, 6, 0)
        self.tab_layout.addWidget(self.clear_button, 7, 0)
        self.tab_layout.addWidget(self.save_button, 8, 0)
        self.tab_layout.addWidget(QLabel(), 0, 1)
        self.tab_layout.addWidget(self.copy_msg, 1, 1)
        self.tab_layout.addWidget(self.save_msg, 8, 1)

    def set_base_theme(self, theme_chosen: str):
        """
            Set the current base theme

        Parameters
        ----------
        theme_chosen : str
            The theme to be set, must e one of found themes in .json files
        """
        super().set_base_theme(theme_chosen)
        self.config_phrases_selector()
        self.enable_checkboxes()

    def config_phrases_selector(self):
        """ Set the correct values to be selected while generating random phrases"""
        min_phrases = step_phrases = default_value = 3 if self.is_bip39_theme else 1
        max_phrases = 24 if self.is_bip39_theme else 8
        self.select_phrases.setRange(min_phrases, max_phrases)
        self.select_phrases.setSingleStep(step_phrases)
        self.select_phrases.setValue(default_value)
        self.select_phrases.setWrapping(True)

    def enable_checkboxes(self, enable: bool = True):
        """
            Enable or disable the password checkboxes all together

        Parameters
        ----------
        enable : bool
            Enable or disable the checkboxes
        """
        self.check_case.setEnabled(enable)
        self.check_char.setEnabled(enable)
        self.check_number.setEnabled(enable)

    def generate_text(self):
        """ Call generate_format which build a mnemonic phrase in Formosa standard then updates displayed text"""
        self.save_msg.hide()
        phrase_size = self.select_phrases.value()
        strength = 32*phrase_size//3 if self.is_bip39_theme else 32 * phrase_size
        words = self.parent.base_mnemonic.generate(strength)
        text = self.parent.base_mnemonic.format_mnemonic(words)+"\n"
        self.last_text = self.last_text + text
        # Keep the password lines
        password_position = self.password_lines[-1] + self.last_n_phrases + 1 if self.password_lines else 0
        self.password_lines.append(password_position)
        self.last_n_phrases = phrase_size

        self.update_text()
        self.change_password()

    def change_password(self):
        """ Change characters in passwords all together"""
        if self.check_number.isChecked():
            self.insert_number()
        if self.check_char.isChecked():
            self.insert_spc_char()
        if self.check_case.isChecked():
            self.insert_swap_case()

    def update_text(self):
        """ Insert text in the box of Mnemonic Generator tab"""
        self.text_box.setText(self.last_text)
        self.copy_to_clipboard()
        self.copy_msg.show()

    def copy_to_clipboard(self):
        """ Copy the generated phrases to clipboard"""
        app.clipboard = self.last_text

    def recover_text(self):
        """ Recover an edited text in the text box to its former self in the Mnemonic Generator tab"""
        self.text_box.clear()
        self.text_box.setText(self.last_text)

    def clear_text(self):
        """ Clear out the text box, copy label and save label in the Mnemonic Generator tab"""
        self.enable_checkboxes()
        self.save_msg.hide()
        self.copy_msg.hide()
        self.text_box.clear()
        self.last_text = ""
        self.password_lines = []

    def save_file(self):
        """ Save the generated phrases to output.txt file"""
        with open("output.txt", "w", encoding="utf-8") as output_file:
            output_file.write(self.last_text)
        self.save_msg.show()

    def insert_number(self):
        """ Change an ordinary character to a number"""
        to_replace = ["a", "b", "e", "g", "i", "o", "q", "s", "t"]
        replace_by = ["4", "8", "3", "6", "1", "0", "9", "5", "7"]
        self.insert_character(to_replace, replace_by, self.check_number.isChecked())

    def insert_spc_char(self):
        """ Change an ordinary character to a special character"""
        to_replace = ["a", "c", "e", "h", "j", "l", "s", "t", "z"]
        replace_by = ["@", "¢", "&", "#", "!", "£", "$", "+", "%"]
        self.insert_character(to_replace, replace_by, self.check_char.isChecked())

    def insert_swap_case(self):
        """ Swap the case of a character"""
        to_replace = list(map(chr, range(97, 123)))
        replace_by = [each_char.swapcase() for each_char in to_replace]
        self.insert_character(to_replace, replace_by, self.check_case.isChecked())

    def insert_character(self, to_replace: list, replace_by: list, check_box_var: bool):
        """
            Find out if the text in the texbox is written as natural or edited
            and calls method replace_characters() with correct order of lists

        Parameters
        ----------
        to_replace : list
            The list of characters to be removed
        replace_by : list
            The list of characters to be inserted
        check_box_var : bool
            This variable tells if the word is written as natural, or it is already edited
        """
        array_criteria = any([each_char in self.last_text for each_char in to_replace])
        if array_criteria:
            replacement_order = (replace_by, to_replace) if check_box_var else (to_replace, replace_by)
            self.replace_characters(replacement_order[0], replacement_order[1], not check_box_var)
        self.update_text()

    def replace_characters(self, insert: list[str], remove: list[str], checkbox_selected: bool = False):
        """
            Replace in the password a character by another character

        Parameters
        ----------
        insert : list[str]
            The list of characters to be inserted
        remove : list[str]
            The list of characters to be removed
        checkbox_selected : bool
            Indicate the respective checkbox selection, it prevents a changed character to be stuck
        """
        lines = self.last_text.splitlines(False)
        for line_index in self.password_lines:
            password_line = lines[line_index]
            character_index = [remove.index(each_char) for each_char in list(password_line) if each_char in remove]
            changed_character = [each_char for each_char in list(password_line) if each_char in insert]

            if not character_index:
                continue

            remove_char = remove[character_index[0]]
            insert_char = insert[character_index[0]]

            # If there is a changed character then skip it, preventing it to get stuck
            if changed_character and not checkbox_selected:
                if password_line.index(changed_character[0]) < password_line.index(remove_char):
                    continue
            new_line = password_line.replace(remove_char, insert_char, 1)
            self.last_text = self.last_text.replace(password_line, new_line)


class ThemeConverterTab(BaseTab):
    def __init__(self, parent: 'QtFormosa'):
        super().__init__(parent)
        self.parent = parent

        # General tab variables
        self.new_theme = self.parent.base_theme
        self.new_mnemonic = self.parent.base_mnemonic

        # Widgets instantiation
        self.select_new_theme = QComboBox(self)
        self.base_mnemonic_box = QTextEdit(self)
        self.new_mnemonic_box = QTextEdit(self)
        self.convert_button = QPushButton(self)

    def config_tab(self):
        """ Set up widgets, config texts, commands and variables"""
        self.set_new_theme(self.parent.base_theme)

        self.convert_button.setText("Convert to theme")
        self.convert_button.clicked.connect(self.convert_theme)
        self.select_new_theme.addItems(self.parent.themes)
        self.select_new_theme.setCurrentText(self.new_theme)
        self.select_new_theme.currentTextChanged.connect(self.set_new_theme)

        self.set_tab_layout()

    def set_tab_layout(self):
        """ Place the widgets in the window tab"""
        self.base_mnemonic_box.setGeometry(0, 0, 20, 75)
        self.new_mnemonic_box.setGeometry(0, 0, 20, 75)
        self.tab_layout.addWidget(self.base_mnemonic_box, 1, 0)
        self.tab_layout.addWidget(self.new_mnemonic_box, 1, 4)
        self.tab_layout.addWidget(self.convert_button, 4, 0)
        self.tab_layout.addWidget(self.select_new_theme, 4, 4)

    def set_new_theme(self, theme_chosen):
        """ Config the new theme to the phrases be converted to"""
        self.new_theme = theme_chosen
        self.new_mnemonic = mnemonic.Mnemonic(theme_chosen)

    def convert_theme(self):
        """ Converts a seed phrase in Formosa standard from a theme to another also in Formosa standard"""
        mnemonic_words = self.base_mnemonic_box.toPlainText().replace("\n", " ").split(" ")
        mnemonic_words = [each_word for each_word in mnemonic_words if each_word]
        if not len(mnemonic_words):
            self.new_mnemonic_box.clear()
            self.new_mnemonic_box.setText("Empty Input")
            return
        self.new_mnemonic_box.clear()
        phrase_size = self.parent.base_mnemonic.words_dictionary.words_per_phrase
        display_text = ""
        n = 4 if self.is_bip39_theme else 2
        try:
            new_mnemonic_words = self.new_mnemonic.convert_theme(mnemonic_words, self.new_theme, self.base_theme)
            new_mnemonic_words = self.new_mnemonic.format_mnemonic(new_mnemonic_words)
            display_text = new_mnemonic_words
        except (ValueError, KeyError) as first_error:
            try:
                try_words = mnemonic_words[1:]
                new_mnemonic_words = self.new_mnemonic.convert_theme(try_words, self.new_theme, self.base_theme)
                new_mnemonic_words = self.new_mnemonic.format_mnemonic(new_mnemonic_words)
                display_text = new_mnemonic_words
            except Exception as error:
                if len(mnemonic_words) % phrase_size == 1 and len(mnemonic_words[0]) == n * len(mnemonic_words[1:]):
                    display_text = "{}".format(error)
                else:
                    display_text = "{}".format(first_error)
        except Exception as unexpected_error:
            display_text = "Something unexpected went wrong\n{}".format(unexpected_error)
        finally:
            self.new_mnemonic_box.setText(display_text)


class TableSelectorTab(BaseTab):
    COLUMN_LINE_PARAGRAPH_SIZE = 8

    class QHighlightCheckBox(QCheckBox):
        def __init__(self, parent: 'TableSelectorTab'):
            super().__init__(parent)
            self.parent = parent

        def focusInEvent(self, e: QFocusEvent) -> None:
            """ Change focus to parent"""
            super().focusInEvent(e)
            self.parent.setFocus()

    class QKeysCheckBox(QCheckBox):
        def __init__(self, parent: 'TableSelectorTab'):
            super().__init__(parent)
            self.parent = parent

        def focusInEvent(self, e: QFocusEvent) -> None:
            """ Change focus to custom characters input"""
            super().focusInEvent(e)
            self.parent.custom_character_entry.setFocus()

    class QKeysLineEdit(QLineEdit):
        def __init__(self, parent: 'TableSelectorTab'):
            super().__init__(parent)
            self.parent = parent

        def keyPressEvent(self, a0: QKeyEvent) -> None:
            """ Set grid indexes when key is pressed"""
            super().keyPressEvent(a0)
            self.parent.define_key_list()

        def change_focus(self):
            """ Change focus to parent"""
            self.parent.setFocus()

    class QResetPushButton(QPushButton):
        def __init__(self, parent: 'TableSelectorTab'):
            super().__init__(parent)
            self.parent = parent

        def focusInEvent(self, e: QFocusEvent) -> None:
            """ Change focus to parent"""
            super().focusInEvent(e)
            self.parent.setFocus()

    def __init__(self, parent: 'QtFormosa'):
        super().__init__(parent)

        # General tab variables
        self.font = QFont('Times', 7)
        self.check_color = "#3AC73A"
        self.defaultbg = ""
        self.valid_phrase = True
        self.words_dictionary = {}
        self.natural_word = self.parent.base_dict.natural_order[0]
        self.object_dict = {}
        self.column_objects = []
        self.line_objects = []
        self.paragraph_objects = []
        self.input_character_set = []
        self.input_set_caseless = []
        self.input_set_column = []
        self.input_set_line = []
        self.input_set_paragraph = []
        self.picked_passphrase = []
        self.panel_widgets = []
        # The states represent what was the last defined dimension
        self.states = ("initial", "column_done", "line_done", "paragraph_done")
        self.current_state = self.states[0]
        self.selected_indexes = {key: self.COLUMN_LINE_PARAGRAPH_SIZE for key in self.states}
        self.permutation_map = {"initial": self.input_set_column,
                                "column_done": self.input_set_line,
                                "line_done": self.input_set_paragraph,
                                "paragraph_done": self.input_set_caseless}

        # Widgets instantiation
        self.reset_button = self.QResetPushButton(self)
        self.sel_valid_phrase_label = QLabel(self)
        self.highlight_checkbox = self.QHighlightCheckBox(self)
        self.warning_label = QLabel(self)
        self.use_custom_set = self.QKeysCheckBox(self)
        self.custom_character_entry = self.QKeysLineEdit(self)
        self.output_button = QPushButton(self)
        self.grid_frame_selector = QGridLayout()
        self.panel_widgets = [self.reset_button, self.sel_valid_phrase_label,
                              self.highlight_checkbox, self.warning_label,
                              self.use_custom_set, self.custom_character_entry, self.output_button]
        [each_widget.setEnabled(False) for each_widget in self.panel_widgets]

        self.define_key_list()

    def clear_grid(self):
        """ Clear grid variables and widgets"""
        self.column_objects = []
        self.line_objects = []
        self.paragraph_objects = []

        self.object_dict = {}
        [self.object_dict.update({each_word: []})
         for each_word in self.parent.base_dict.natural_order]

        for i in reversed(range(self.grid_frame_selector.count())):
            self.grid_frame_selector.itemAt(i).widget().deleteLater()
            self.grid_frame_selector.itemAt(i).widget().setParent(None)

    def config_tab(self):
        """ Set up widgets, config texts, commands and variables"""
        self.highlight_checkbox.setText("Show\nHighlight")
        self.highlight_checkbox.clicked.connect(self.changed_show_highlight)
        self.reset_button.setText("Reset")
        self.reset_button.clicked.connect(self.reset_selection)
        valid_message = "Selected phrase\nso far is compatible"
        self.sel_valid_phrase_label.setText(valid_message)
        self.sel_valid_phrase_label.setStyleSheet("background-color: " + self.check_color)
        warning_message = "Very careful\nwith prying eyes"
        self.warning_label.setText('<font color="red"> ' + warning_message + '</font>')
        self.use_custom_set.setText("Use custom\nset of keys")
        self.use_custom_set.clicked.connect(self.enable_custom_keys_set)
        self.output_button.setText("Generate\nPhrase")
        self.output_button.clicked.connect(self.output_phrases)
        self.output_button.setEnabled(False)

        self.new_grid()
        self.set_tab_layout()

    def set_tab_layout(self):
        """ Place the widgets in the window tab"""
        max_width = max(self.parent.width()//3, 1)
        # Set max width to each widget
        [each_widget.setMaximumWidth(max_width) for each_widget in self.panel_widgets]
        # Position each widget to next row
        [self.tab_layout.addWidget(each_widget, self.panel_widgets.index(each_widget), 0)
         for each_widget in self.panel_widgets]

        self.grid_frame_selector.setAlignment(Qt.AlignTop)
        self.tab_layout.addLayout(self.grid_frame_selector, 0, 2,
                                  self.COLUMN_LINE_PARAGRAPH_SIZE * self.COLUMN_LINE_PARAGRAPH_SIZE,
                                  self.COLUMN_LINE_PARAGRAPH_SIZE + 2)

    def set_base_theme(self, theme_chosen):
        """
            Set the current base theme, enabling or not each widget on the panel according to theme chosen

        Parameters
        ----------
        theme_chosen : str
            The theme to be set, must e one of found themes in .json files
        """
        super().set_base_theme(theme_chosen)
        state = self.is_bip39_theme
        [each_widget.setEnabled(not state) for each_widget in self.panel_widgets]
        self.natural_word = self.parent.base_dict.natural_order[0]
        self.new_grid()
        self.setFocus()

    def init_label_objects(self):
        """ Configure the objects in the grid of the Table Selector tab, all labels must initialize hidden"""
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
        words_dictionary = self.parent.base_dict
        syntactic_word_list = words_dictionary.natural_order

        # Clear grid widgets
        self.clear_grid()

        # Trim long words to limit the grid occupied space
        limited_list = {}
        row_len_limited = {}
        for each_syntactic_word in syntactic_word_list:
            limited_list.update({each_syntactic_word: []})
            row_len_limited.update({each_syntactic_word: []})
            returned_list, returned_bools = \
                self.limit_word_length(words_dictionary[each_syntactic_word].total_words)
            limited_list.update({each_syntactic_word: returned_list})
            row_len_limited.update({each_syntactic_word: returned_bools})

        font_sizes = {}
        [font_sizes.update({each_syntactic_word: 7 if row_len_limited[each_syntactic_word] else 8})
         for each_syntactic_word in syntactic_word_list]

        # Write the characters in column, line and paragraph indexes
        self.column_objects = [QLabel(parent=self, text=self.input_set_column[column])
                               for column in range(a)]
        # Index line is get by repeating 0 to 'a' for 'a' times, e.g. [0, ...7, 0, ...7, 0, ...7]
        self.line_objects = [QLabel(parent=self, text=self.input_set_line[line])
                             for paragraph in range(a) for line in range(a)]
        # Index line is get by repeating 0 'a' times to 'a', e.g. [0, 0, ..., 1, 1, ..., 7, 7]
        self.paragraph_objects = [QLabel(parent=self, text=self.input_set_paragraph[paragraph])
                                  for paragraph in range(a) for line in range(a)]
        [(each_object.setFont(self.font), each_object.hide())
         for each_object in self.column_objects + self.line_objects + self.paragraph_objects]

        [[[[self.object_dict[each_syntactic_word].append(
            QLabel(parent=self,
                   text=self._get_text(limited_list[each_syntactic_word], column, line, paragraph)))
            for column in range(a) if self._cell_idx(column, line, paragraph) < len(
                words_dictionary[each_syntactic_word].total_words)]
            for line in range(a)]
            for paragraph in range(a)]
            for each_syntactic_word in syntactic_word_list]

        [(each_object.setFont(QFont('Times', font_sizes[each_syntactic_word])), each_object.hide())
         for each_syntactic_word in syntactic_word_list
         for each_object in self.object_dict[each_syntactic_word]]

    def limit_word_length(self, wordlist: list) -> (list, bool):
        """
            Limit the characters in words of the grid

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
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
        char_len_limit = 12
        row_len_limited = False
        row_chars = ""

        limited_list = [each_word[0:char_len_limit-3]+"..."
                        if len(each_word) > char_len_limit else each_word
                        for each_word in wordlist]

        row_len_limited = True if any([
            len("".join(wordlist[a*each_row_index:(a+1)*each_row_index])) > a*char_len_limit
            for each_row_index in range(len(wordlist)//a)]
        ) else row_len_limited

        for each_row_index in range(len(wordlist)//a):
            row_chars += "".join(wordlist[a*each_row_index:(a+1)*each_row_index])
            row_len_limited = True if len(row_chars) > a*char_len_limit else row_len_limited

        return limited_list, row_len_limited

    def new_grid(self):
        """ Call the sequence to create and show a new words grid in the Table Selector tab"""
        self.randomize_character_set()
        self.init_label_objects()
        self.allocate_grid()

    def enable_custom_keys_set(self):
        """ Enable the use of custom keys in the Table Selector tab"""
        if self.use_custom_set.isChecked():
            self.custom_character_entry.setEnabled(True)
        else:
            self.custom_character_entry.setEnabled(False)
            self.custom_character_entry.setText("")
            self.new_grid()

    def define_key_list(self):
        """ Set the keys used as index of the grid in the Table Selector tab"""
        input_character_set = ["A", "S", "D", "F", "J", "K", "L", ";"]
        characters_list = list(self.custom_character_entry.text().upper())
        self.input_character_set = input_character_set

        # Check whether the characters are all given and unique
        if len(set(characters_list)) == self.COLUMN_LINE_PARAGRAPH_SIZE:
            input_character_set = characters_list
            self.input_character_set = input_character_set
            self.new_grid()
            self.custom_character_entry.change_focus()
        elif len(characters_list) > self.COLUMN_LINE_PARAGRAPH_SIZE:
            # Trim the Entry widget at maximum the size constant
            self.custom_character_entry.setText(self.custom_character_entry.text()[0:self.COLUMN_LINE_PARAGRAPH_SIZE])
        elif len(set(characters_list)) != len(characters_list):
            # Trim the Entry widget to unique characters
            self.custom_character_entry.setText(self.custom_character_entry.text()[0:-1])

    def randomize_character_set(self):
        """ Randomize the indexes of the grid independently of each other in the Table Selector tab"""
        input_chars = self.input_character_set
        random.shuffle(input_chars)
        self.input_set_caseless = input_chars + list([each_char.swapcase() for each_char in input_chars])
        column_char_set = input_chars.copy()
        random.shuffle(column_char_set)
        self.input_set_column = column_char_set + list([each_char.swapcase() for each_char in column_char_set])
        line_char_set = input_chars.copy()
        random.shuffle(line_char_set)
        self.input_set_line = line_char_set + list([each_char.swapcase() for each_char in line_char_set])
        paragraph_char_set = input_chars.copy()
        random.shuffle(paragraph_char_set)
        self.input_set_paragraph = paragraph_char_set + list([each_char.swapcase() for each_char in paragraph_char_set])
        self.permutation_map.update({self.states[0]: self.input_set_caseless})
        self.permutation_map.update({self.states[1]: self.input_set_column})
        self.permutation_map.update({self.states[2]: self.input_set_paragraph})
        self.permutation_map.update({self.states[3]: self.input_set_line})

    def _get_text(self, word_list: list[str], column: int, line: int, paragraph: int):
        """
            Build up the string to be displayed in the word Label

        Parameters
        ----------
        word_list : list[str]
            The total words of the current displayed grid
        column : int
            Index of column
        line : int
            Index of line
        paragraph : int
            Index of paragraph

        Returns
        -------
            The string ready to be displayed
        """
        column_index = str(self.input_set_column[column])
        line_index = str(self.input_set_line[line])
        paragraph_index = str(self.input_set_paragraph[paragraph])
        word = str(word_list[self._cell_idx(column, line, paragraph)])
        label_text = column_index + paragraph_index + line_index + "-" + word
        return label_text

    def _cell_idx(self, column: int, line: int, paragraph: int):
        """
            Convert the index of a position in the grid to the index of position in the total words

        Parameters
        ----------
        column : int
            Index of column
        line : int
            Index of line
        paragraph : int
            Index of paragraph

        Returns
        -------
            The index of a list of total words of the given grid position
        """
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
        return column + a*a*paragraph + a*line

    def _line_idx(self, line: int, paragraph: int):
        """
            Convert a given line and paragraph position in the grid to its row

        Parameters
        ----------
        line : int
        paragraph : int

        Returns
        -------
            The index of the row corresponding to its line and paragraph
        """
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
        return line + a*paragraph

    def allocate_grid(self, row_init: int = 1, col_init: int = 1):
        """
            Allocate the grid objects in the grid accordingly to each index in the Table Selector tab

        Parameters
        ----------
        row_init : int
            Initial position of objects in the row
        col_init : int
            Initial position of objects in the column
        """
        if self.is_bip39_theme:
            # The grid does not support BIP39 theme, as the "phrase" is one word long and the total words doesn't fit
            return

        current_objects = self.object_dict[self.natural_word]
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
        # The floor division to determine paragraph limit
        b = max([1, len(current_objects)//(a*a)])

        # Add aligned widgets to the grid and reveal them
        for paragraph in range(a):
            if paragraph > b:
                break
            for line in range(a):
                line_widget = self.line_objects[self._line_idx(line, paragraph)]
                paragraph_widget = self.paragraph_objects[self._line_idx(line, paragraph)]
                self.grid_frame_selector.addWidget(line_widget,
                                                   self._line_idx(line, paragraph) + row_init, a + 2*col_init)
                self.grid_frame_selector.addWidget(paragraph_widget, self._line_idx(line, paragraph) + row_init, 0)

                line_widget.setAlignment(Qt.AlignTop)
                line_widget.show()
                paragraph_widget.setAlignment(Qt.AlignTop)
                paragraph_widget.show()

                for column in range(a):
                    self.grid_frame_selector.addWidget(self.column_objects[column],
                                                       0, col_init + 1 + column)
                    self.column_objects[column].setAlignment(Qt.AlignTop)
                    self.column_objects[column].show()

                    if len(current_objects) > self._cell_idx(column, line, paragraph):
                        word_widget = current_objects[self._cell_idx(column, line, paragraph)]
                        self.grid_frame_selector.addWidget(word_widget,
                                                           self._line_idx(line, paragraph) + 1, col_init + 1 + column)
                        word_widget.setAlignment(Qt.AlignLeft)
                        word_widget.show()

    def keyReleaseEvent(self, event: 'QKeyEvent'):
        """
            Select words and commands in the Table Selector tab

        Parameters
        ----------
        event : 'QKeyEvent'
            It is the key pressed
        """
        redo_set_keys = [Qt.Key_Escape, Qt.Key_Backspace, Qt.Key_Delete]
        if event.text() in self.input_set_caseless and self.current_state != self.states[-1]:

            self.current_state = self.states[self.states.index(self.current_state) + 1]
            self.selected_indexes[self.current_state] = \
                self.permutation_map[self.current_state].index(event.text()) \
                % self.COLUMN_LINE_PARAGRAPH_SIZE

            char_index = self.permutation_map[self.current_state].index(event.text())
            self.delineate_cells(char_index)

        elif (event.key() in redo_set_keys) and self.current_state != self.states[0]:
            self.current_state = self.states[0]
            char_index = 0
            self.set_validation_colored_msg()
            self.delineate_cells(char_index)

        elif (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return or event.key() == Qt.Key_Space) and \
                self.current_state == self.states[-1]:
            if self.check_color == "#FFFF99":
                self.valid_phrase = False
            self.pick_word()

    def changed_show_highlight(self):
        """ Show or hide the background of the selected words in the Table Selector tab"""
        if self.highlight_checkbox.isChecked():
            char_index = self.selected_indexes[self.current_state]
            self.delineate_cells(char_index)
        else:
            [[each_label.setStyleSheet(self.defaultbg) for each_label in self.object_dict[each_syntactic_word]]
             for each_syntactic_word in self.object_dict.keys()]

    def reset_selection(self):
        """ Reset the variables and words which were selected so far in the Table Selector tab"""
        self.picked_passphrase = []
        self.natural_word = self.parent.base_dict.natural_order[0]
        self.current_state = self.states[0]
        self.valid_phrase = True
        self.set_validation_colored_msg()

        [self.selected_indexes.update({each_key: self.COLUMN_LINE_PARAGRAPH_SIZE})
         for each_key in self.selected_indexes.keys()]
        self.select_base_theme.setEnabled(True)

        [[each_label.setStyleSheet(self.defaultbg) for each_label in self.object_dict[each_syntactic_word]]
         for each_syntactic_word in self.object_dict.keys()]
        self.new_grid()
        self.grayout_gen_button()

    def grayout_gen_button(self):
        """
            Enable the Generate Phrase button when a whole phrase is picked
            and disables the Generate Phrase button when the words picked does not form
            the whole phrase in the Table Selector tab
        """
        phrase_len = len(self.parent.base_dict.natural_order)
        state = (len(self.picked_passphrase) % phrase_len == 0) and len(self.picked_passphrase) > 0
        self.output_button.setEnabled(state)

    def output_phrases(self):
        """ Print the phrases with the selected words in the Table Selector tab"""
        phrase_len = len(self.parent.base_dict.natural_order)
        if (len(self.picked_passphrase) % phrase_len == 0) and len(self.picked_passphrase) > 0:
            output_phrases = ""
            for i in range(len(self.picked_passphrase)):
                print(self.picked_passphrase[i][0:2], end="")
            print("")
            for i in range(len(self.picked_passphrase) // phrase_len):
                phrase = " ".join(self.picked_passphrase[phrase_len * i:phrase_len * (i + 1)])
                output_phrases += phrase + " "
                print(phrase)
            app.clipboard().setText(output_phrases)

    def check_word_list(self, word=None):
        """
            Check if the phrase so far follows the words list
            according to theme dictionary in the Table Selector tab

        Parameters
        ----------
        word :
            This is the word selected that is get from the grid,
            it can None as not the whole grid is filled with words
            also not all steps are evaluated
            because the filling order is not the same as natural order
        """
        checklist = self.picked_passphrase.copy()
        if word is not None:
            # Slice the string to get the word after the hyphen
            checklist.append(word[word.find("-") + 1:])
        state = True
        themed_dict = self.parent.base_dict
        natural_order = themed_dict.natural_order
        filling_order = themed_dict.filling_order
        # The number of complete phrases
        phrases_shift = (len(checklist) // len(natural_order)) * len(natural_order)
        check_size = len(checklist) % len(natural_order)

        # If no word is selected and the size isn't zero
        #  or a word is selected and the size isn't one
        #  then it keep going, else it returns
        if not ((not word and check_size != 0) or (word and check_size != 1)):
            self.set_validation_colored_msg(state)
            return
        for filling_order_word in filling_order[1:check_size]:
            if not all(value in natural_order[:check_size] for value in filling_order[:check_size]):
                continue
            led_by = themed_dict[filling_order_word].led_by
            led_by_word = checklist[natural_order.index(led_by) + phrases_shift]
            natural_index = themed_dict.natural_index(filling_order_word)
            word_mapping = themed_dict[led_by][filling_order_word].mapping[led_by_word]
            state = False if checklist[natural_index + phrases_shift] not in word_mapping else state

        self.set_validation_colored_msg(state)

    def set_validation_colored_msg(self, state=True):
        """
            Warn with a yellow background when the
            word selected doesn't follow the list in the theme dictionary and if it is not yet confirmed as selected
            but keep the background red if it was selected outside the rules before in the Table Selector tab

        Parameters
        ----------
        state : bool
            This is the state of the selected word, if it follows or not the list in the theme dictionary
        """
        valid_message = "Incompatible phrase"
        if not self.valid_phrase:
            # Inadequate phrase
            # #FF4040 is Red
            self.check_color = "#FF4040"
            self.sel_valid_phrase_label.setText(valid_message)
            self.sel_valid_phrase_label.setStyleSheet("background-color: " + self.check_color)
        elif not state:
            # Adequate phrase about to become inadequate
            # #FFFF99 is Yellow
            self.check_color = "#FFFF99"
        else:
            # Adequate phrase
            # #3AC73A is Green
            valid_message = "Selected phrase\nso far is compatible"
            self.check_color = "#3AC73A"
            self.sel_valid_phrase_label.setText(valid_message)
            self.sel_valid_phrase_label.setStyleSheet("background-color: " + self.check_color)

    def delineate_cells(self, index: int):
        """
            Specify which words should be highlighted accordingly with words selected in the Table Selector tab

        Parameters
        ----------
        index : int
            This is the index of column, or paragraph or line selected which will highlighted
        """
        current_objects = self.object_dict[self.natural_word]
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
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
            line = self.selected_indexes[self.states[2]]
            begin = column + a * index + (a * a) * line
            end = begin
            if end + 1 < len(self.object_dict[self.natural_word]):
                self.check_word_list(self.object_dict[self.natural_word][begin:end + 1][0].text())
        color = self.defaultbg if self.current_state == self.states[0] else self.check_color
        self.fill_bg_color(color, begin, end, step)

    def fill_bg_color(self, color: str, begin: int, end: int, step: int):
        """
            Highlight the background of the selected set of words in the Table Selector tab

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
        if self.highlight_checkbox.isChecked():
            current_objects = self.object_dict[self.natural_word]
            [each_label.setStyleSheet("background-color: " + color)
             for each_label in current_objects[begin:end + 1:step]]
            [each_label.setStyleSheet(self.defaultbg) for each_label in current_objects
             if (each_label not in current_objects[begin:end + 1:step])]
        else:
            begin = 0
            [each_label.setStyleSheet(self.defaultbg) for each_label in current_objects
             if (each_label not in current_objects[begin:end + 1:step])]

    def pick_word(self):
        """ Store the selection when a word is selected in the Table Selector tab"""
        a = self.COLUMN_LINE_PARAGRAPH_SIZE
        column = self.selected_indexes[self.states[1]]
        line = self.selected_indexes[self.states[2]]
        paragraph = self.selected_indexes[self.states[3]]
        word_index = self._cell_idx(column, paragraph, line)
        words_list = self.parent.base_dict[self.natural_word]["TOTAL_LIST"]
        self.current_state = self.states[0]
        char_index = 0
        if word_index < len(words_list):
            natural_order_list = self.parent.base_dict.natural_order

            self.select_base_theme.setEnabled(False)
            self.picked_passphrase.append(words_list[word_index])
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

    def change_highlight_var(self):
        """ Switch the variable of the highlight checkbox """
        self.highlight_checkbox.setEnabled(not self.highlight_checkbox.isChecked())
        self.changed_show_highlight()


class QtFormosa(QMainWindow):
    DEFAULT_THEME = "BIP39"

    def __init__(self, parent=None):
        super(QtFormosa, self).__init__(parent)
        self.setWindowTitle("Formosa Application")
        self.setGeometry(0, 0, 1024, 600)

        self.themes = self.sorted_themes()
        self.base_theme = self.DEFAULT_THEME

        self.table_widget = FeaturesTabs(self)
        self.setCentralWidget(self.table_widget)

        self.show()

    def sorted_themes(self) -> tuple[str]:
        """
            Find all themes in json files
            All .json files in the themes directory are considered themes,
            force the default theme as the first element

        Returns
        -------
        tuple[str]
            Return a tuple of themes, the first element is the default theme and rest is sorted
        """
        directory_path = (Path(__file__).parent.absolute() / "themes")
        files_path = Path(directory_path)
        themes = sorted([each_directory.stem for each_directory in files_path.glob(r"*.json")])
        default_index = themes.index(self.DEFAULT_THEME)
        default_theme = themes.pop(default_index)
        sorted_themes = tuple([default_theme]) + tuple(themes[:default_index] + themes[default_index:])
        return sorted_themes

    def set_base_theme(self, theme_chosen: str):
        """
            Set the current base theme

        Parameters
        ----------
        theme_chosen : str
            The theme to be set, must e one of found themes in .json files
        """
        self.base_theme = theme_chosen

    @property
    def base_mnemonic(self) -> mnemonic.Mnemonic:
        """ Return the base Mnemonic object"""
        base_mnemonic = mnemonic.Mnemonic(self.base_theme)
        return base_mnemonic

    @property
    def base_dict(self) -> mnemonic.ThemeDict:
        """ Return the base theme dictionary"""
        return self.base_mnemonic.words_dictionary


class FeaturesTabs(QWidget):
    def __init__(self, parent: QtFormosa):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)

        self.tab_control = QTabWidget()
        self.mnemonic_generator = MnemonicGeneratorTab(parent)
        self.address_converter = QWidget(self)
        self.theme_converter = ThemeConverterTab(parent)
        self.table_selector = TableSelectorTab(parent)
        self.swapper = QWidget(self)

        self.tab00 = "Password Generator"
        self.tab01 = "Theme Converter"
        self.tab02 = "Table Selector"
        self.tab03 = "Word Swapper"

        self.tab_control.addTab(self.mnemonic_generator, self.tab00)
        self.tab_control.addTab(self.theme_converter, self.tab01)
        self.tab_control.addTab(self.table_selector, self.tab02)

        # Config the first tab due to be opening without being clicked
        self.mnemonic_generator.init_configuration()
        self.tab_control.tabBarClicked.connect(self.tab_clicked)

        layout.addWidget(self.tab_control)
        self.setLayout(layout)

    def tab_clicked(self, tab_index):
        base_theme = self.tab_control.currentWidget().base_theme
        self.tab_control.setCurrentIndex(tab_index)
        self.tab_control.currentWidget().init_configuration()
        self.tab_control.currentWidget().set_base_theme(base_theme)


app = QApplication(sys.argv)
ex = QtFormosa()
sys.exit(app.exec_())
