"""
    gui.py
    Control the GUI and processes
    :copyright: (c) 2022-2023 Juan Carcedo, All rights reserved
    :licence: MIT, see LICENSE.txt for further details.
    Updates:
    - V2 used with customtkinter by TomSchimansky [https://github.com/TomSchimansky/CustomTkinter]
"""
# GUI
import tkinter as tk
from tkinter.messagebox import showerror, showinfo, showwarning, askyesno
import customtkinter  # included in V2 - 2023 Better UX

# Other classes
from filemanagement import JsonFileManager
import genpassword as gp

# CONSTANTS ========================
FONT = ('Consolas', 10, 'bold')
FONT_TITLE = ('Consolas', 25, 'bold')
# Config of customtkinter
customtkinter.set_appearance_mode('System')
customtkinter.set_default_color_theme('blue')  # Available: Blue, dark-blue, green


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.file_manager = JsonFileManager()
        self.eval('tk::PlaceWindow . center')  # Set the window to the middle of screen
        self.title('Password Vault')
        self.geometry(f'{400}x{250}')
        # Grid Layout: (number_of_row/column,
        #   weight=[0: As big as it needs, 1: Expand equally to fill the window])
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_columnconfigure((1, 2), weight=1)

        # Widgets
        self.__welcome_widgets()
        self.__entry_frames()
        self.__bottom_buttons()

    def end_screen(self) -> None:
        """
        End program.
        :return: None
        """
        self.mainloop()

    def __welcome_widgets(self) -> None:
        """
        Create a welcome (upper part) widget --> Text.
        :return: None
        """
        # Title
        self.welcome_title = customtkinter.CTkLabel(self, text='Never forget your pass!',
                                                    font=customtkinter.CTkFont(size=20, weight='bold'))
        self.welcome_title.grid(row=0, column=0, columnspan=3, pady=5)

    def __entry_frames(self) -> None:
        """
        Widget for input part: Site, User, Password.
        :return: None
        """
        # Grid of options
        self.central_frame = customtkinter.CTkFrame(self, width=300)
        self.central_frame.grid(row=1, column=0, rowspan=3, columnspan=3, padx=10, pady=10)
        self.site_label = customtkinter.CTkLabel(self.central_frame, text='Site:', anchor='w')
        self.site_label.grid(row=0, column=0, padx=10)
        self.site_entry = customtkinter.CTkEntry(self.central_frame, width=200)
        self.site_entry.grid(row=0, column=1, columnspan=2, pady=5)

        self.user_label = customtkinter.CTkLabel(self.central_frame, text='User:', anchor='w')
        self.user_label.grid(row=1, column=0, padx=10)
        self.user_entry = customtkinter.CTkEntry(self.central_frame, width=200)
        self.user_entry.grid(row=1, column=1, columnspan=2, pady=5)

        self.password_label = customtkinter.CTkLabel(self.central_frame, text='Password:', anchor='w')
        self.password_label.grid(row=2, column=0, padx=10)
        self.password_entry = customtkinter.CTkEntry(self.central_frame, width=200)
        self.password_entry.grid(row=2, column=1, pady=5)
        self.password_button_suggest = customtkinter.CTkButton(master=self.central_frame,
                                                               command=self.suggest_password,
                                                               text='Suggest',
                                                               fg_color='transparent',
                                                               border_width=2,
                                                               width=30)
        self.password_button_suggest.grid(row=2, column=3, pady=5, padx=10)

    def __bottom_buttons(self) -> None:
        """
        Create the last bottom part of the main widget [3]
        :return: None
        """
        # Final buttons
        self.buttons_frame = customtkinter.CTkFrame(self, width=300, fg_color='transparent')
        self.buttons_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        self.search_button = customtkinter.CTkButton(master=self.buttons_frame,
                                                     command=self.search_data,
                                                     text='Search data')
        self.search_button.grid(row=0, column=0, pady=10, padx=10)
        self.add_button = customtkinter.CTkButton(master=self.buttons_frame,
                                                  command=self.update_file,
                                                  text='Add data')
        self.add_button.grid(row=0, column=2, pady=10, padx=10)

    # ---------------- Methods from buttons ------------- #
    def update_file(self):
        """ Refresh the file's data.
            It is called update because if the item exists, it will update it.
            Checks parameters before adding data.
        """
        input_fields = (self.get_site_entry(), self.get_user_entry(), self.get_password_entry())
        if not input_fields[0] or not input_fields[1] or not input_fields[2]:
            App.pop_up(title='Warning', message='Empty fields.', type_mess='warning')

        else:  # All fields filled
            message = f'User: {self.get_user_entry()}\n Password: {self.get_password_entry()}\n for site' \
                      f' {self.get_site_entry()} is this ok?'
            if App.pop_up(title='Review fields', message=message, type_mess='yesno'):
                if self.file_manager.create_file_json(user=input_fields[1],
                                                      password=input_fields[2],
                                                      site=input_fields[0]):
                    self.clear_inputs()

    def search_data(self):
        """Search in the data for the website/place. Retrieve the values in a popup."""
        web_search = self.get_site_entry()
        if web_search:  # not empty
            title, message, message_type, password = self.file_manager.search_data_json(web_search)
            if password:
                # Copy password to clipboard
                self.clipboard_clear()
                self.clipboard_append(password)

        else:
            title, message, message_type = 'Warning', 'Site is empty', 'warning'

        App.pop_up(title=title, message=message, type_mess=message_type)

    def suggest_password(self):
        """
        Generate a new password every time is called
        """
        # Update password field
        self.set_password_entry(1, gp.create_password())
        # Copy to clipboard.
        self.clipboard_clear()
        self.clipboard_append(self.get_password_entry())

    # -- Setters/getters ----
    def set_site_entry(self, method: int = 0, value: str = ''):
        """
        Set the site entry field.
        :param method: 0 to delete the field, 1 to set it to value.
        :param value: string to set.
        :return:
        """
        self.site_entry.insert(0, value) if method == 1 else self.site_entry.delete(0, tk.END)

    def get_site_entry(self):
        return self.site_entry.get()

    def set_password_entry(self, method: int = 0, value: str = ''):
        """
        Set the password entry field.
        :param method: 0 to delete the field, 1 to set it to value.
        :param value: string to set.
        :return:
        """
        self.password_entry.insert(0, value) if method == 1 else self.password_entry.delete(0, tk.END)

    def get_password_entry(self):
        return self.password_entry.get()

    def set_user_entry(self, method: int = 0, value: str = ''):
        """
        Set the user entry field.
        :param method: 0 to delete the field, 1 to set it to value.
        :param value: string to set.
        :return:
        """
        self.user_entry.insert(0, value) if method == 1 else self.user_entry.delete(0, tk.END)

    def get_user_entry(self):
        return self.user_entry.get()

    # -------- Other methods ------ #
    def clear_inputs(self):
        """
        Cleans all parameters from screen (new input)
        """
        self.set_user_entry()
        self.set_password_entry()
        self.set_site_entry()

    # -------- classmethods ------ #
    # 2023-JCA-New classmethod
    @classmethod
    def pop_up(cls, title: str = '', message: str = '', type_mess: str = ''):
        """
        Generate messages when requested.
        :param str title: Title of the message.
        :param str message: Message to display.
        :param str type_mess: Selection of kind of message; warning, error, info or yesno.
        :return: Only with yesno, other -> None
        """
        if type_mess == 'warning':
            showwarning(title=title, message=message)
        elif type_mess == 'error':
            showerror(title=title, message=message)
        elif type_mess == 'info':
            showinfo(title=title, message=message)
        elif type_mess == 'yesno':
            return askyesno(title=title, message=message)
        else:
            pass
        return None


if __name__ == '__main__':
    print('I am not supposed to be the main...')
