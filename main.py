import tkinter as tk
import re
import tkinter.font as tkfont
from sql_db import CRM_db
from tkinter import *
from tkcalendar import Calendar
from datetime import date, datetime
from PIL import Image, ImageTk
from tkinter import messagebox

root = tk.Tk()  # Initialize main Tkinter window

# region global vars
# Variables for project edit/view UI elements
projects_list = None  # Listbox or similar widget for projects
project_scrollbar = None  # Scrollbar widget for projects list
no_project_label = None  # Label shown when no projects exist
edit_project_dynamic_frame = None  # Frame to dynamically load project edit widgets

# Variables for invoice edit/view UI elements
invoices_list = None  # Listbox or widget for invoices
invoice_scrollbar = None  # Scrollbar for invoices list
no_invoice_label = None  # Label when no invoices exist
edit_invoice_dynamic_frame = None  # Frame for invoice editing UI

# Variables for client edit/view UI elements
clients_list = None  # Listbox or widget for clients
clients_scrollbar = None  # Scrollbar for clients list
no_clients_label = None  # Label shown when no clients exist
edit_clients_dynamic_frame = None  # Frame to hold client edit widgets
# endregion

# region Fonts
# Base fixed-width font from Tkinter system fonts
base_fixed = tkfont.nametofont("TkFixedFont")

# Large underlined title font
fixed_font_title = tkfont.Font(root=root, name="FixedTitle", exists=False, **base_fixed.actual())
fixed_font_title.configure(size=40, underline=True)

# Medium header font, underlined
fixed_font_header = tkfont.Font(root=root, name="FixedHeader", exists=False, **base_fixed.actual())
fixed_font_header.configure(size=20, underline=True)

# Regular text font for general use
fixed_font_text = tkfont.Font(root=root, name="FixedText", exists=False, **base_fixed.actual())
fixed_font_text.configure(size=17)

# Smaller font for views and less important info
fixed_font_view = tkfont.Font(root=root, name="FixedView", exists=False, **base_fixed.actual())
fixed_font_view.configure(size=14)

# Instructional text font, smallest size here
fixed_font_instruct = tkfont.Font(root=root, name="FixedInstruct", exists=False, **base_fixed.actual())
fixed_font_instruct.configure(size=12)

# Button font, bigger and bold for emphasis
fixed_font_btn = tkfont.Font(root=root, name="FixedBtn", exists=False, **base_fixed.actual())
fixed_font_btn.configure(size=20)


# endregion

# region Button Functions

def back_to_home():
    """Navigate back to the home page view."""
    display_home_page()


def on_close():
    """
    Handle window close event:
    - Commit any pending DB transactions.
    - Close DB connection.
    - Destroy the main Tkinter window cleanly.
    """
    db.conn.commit()
    db.conn.close()
    root.destroy()


def clear_root():
    """
    Remove all widgets from the root window.
    Useful for clearing the UI before loading a new screen.
    """
    for widget in root.winfo_children():
        widget.destroy()


def create_calender(btn):
    """
    Create and display a calendar widget for date selection.
    When a date is confirmed:
    - The calendar and confirm button are destroyed.
    - The selected date is reformatted and set as button text.

    Args:
        btn (tk.Button): Button widget whose text will be updated with the selected date.
    """
    today = date.today()
    border_frame = tk.Frame(root, bg="black", bd=2, relief="solid")
    border_frame.pack(pady=20)

    # Initialize the Calendar widget with styling and default to today
    cal = Calendar(
        border_frame,
        selectmode='day',
        year=today.year,
        month=today.month,
        day=today.day,
        background='lightblue',
        foreground='red',
        headersforeground='black',
        normalforeground='gray20',
        weekendforeground='black',
        othermonthforeground='gray60',
        selectforeground='red',
    )
    cal.pack(padx=1, pady=1)

    def collect_date_and_destroy():
        """
        Retrieve the selected date from calendar,
        reformat it to MM-DD-YYYY, update button text,
        and destroy calendar widgets.
        """
        selected_date = cal.get_date()  # e.g. "07/15/25"
        cal.destroy()
        border_frame.destroy()
        confirm_date_btn.destroy()
        date_obj = datetime.strptime(selected_date, "%m/%d/%y")  # Parse date string
        formatted_date = date_obj.strftime("%m-%d-%Y")  # Reformat to MM-DD-YYYY
        btn.config(text=formatted_date)  # Update button text to selected date

    confirm_date_btn = tk.Button(root, text='Confirm', font="FixedBtn", command=collect_date_and_destroy)
    confirm_date_btn.pack()


# endregion

# region Limit text in dropdown display

def limit_text(text, max_length=18):
    """
    Shorten the given text to fit within max_length characters.
    If text is longer, truncate and append ellipsis "..." to indicate omission.

    Args:
        text (str): The original text string.
        max_length (int): Maximum allowed length of the output string.

    Returns:
        str: The original text if short enough, otherwise a truncated version ending with "...".
    """
    return text if len(text) <= max_length else text[:max_length - 6] + "..."


def on_select(dropdown, value):
    """
    Handle selection event on dropdown by trimming the selected value
    and updating the dropdown display text.

    Args:
        dropdown (tk.Variable or widget with set method): The dropdown widget/variable to update.
        value (str): The selected full text value.
    """
    trimmed = limit_text(value)
    dropdown.set(trimmed)


# endregion

# region DB Functions

# region Add Client Page

def get_client_info(client_name, client_email, client_company):
    """
    Retrieve input from client entry fields, validate, and attempt to create a new client in the database.
    On success, display confirmation and navigate to Add Invoice page.
    On failure, show error message.

    Args:
        client_name (tk.Entry): Entry widget for client name.
        client_email (tk.Entry): Entry widget for client email.
        client_company (tk.Entry): Entry widget for client company.
    """
    name = client_name.get().title().strip()
    company = client_company.get().strip()
    email = client_email.get().strip()

    if check_client_info(client_name, client_email, client_company):
        if db.create_client(name, email, company):
            confirm_label = tk.Label(root, text="Saved Client", font="FixedText", fg='green')
            confirm_label.place(x=315, y=225)
            root.after(1000, confirm_label.destroy)  # Remove label after 1 second
            root.after(1400, display_add_invoice_page)  # Navigate shortly after
        else:
            messagebox.showerror("CLIENT ERROR",
                                 "Was not able to upload Client into database. Client either exists or information entered incorrectly.")


def check_client_info(client_name, client_email, client_company):
    """
    Validate the client input fields for name and email formats.
    Prompt user to confirm the entered information if valid.

    Args:
        client_name (tk.Entry): Entry widget for client name.
        client_email (tk.Entry): Entry widget for client email.
        client_company (tk.Entry): Entry widget for client company.

    Returns:
        bool: True if validation and confirmation succeed, False otherwise.
    """
    client_name = client_name.get().title().strip()
    client_company = client_company.get().strip()
    client_email = client_email.get().strip()

    valid_email = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', client_email)
    valid_name = re.match(r'^(?:[A-Z][a-z]+[-\s]?)+$', client_name)

    if not valid_name:
        messagebox.showwarning("Invalid Client Name", "The name you entered contains a number or special character.")
        return False

    if not valid_email:
        messagebox.showwarning("Invalid Client Email", "The email you entered is not a valid email.")
        return False

    # Confirmation dialog showing entered info
    return messagebox.askyesno("Check Client Info", f"The information you've entered:\n"
                                                    f"Client Name: {client_name}\n"
                                                    f"Client Email: {client_email}\n"
                                                    f"Client Company: {client_company}\n"
                                                    f"Is this correct?")


# endregion
# region Add Project Page

def get_project_info(client_name, project_title, start_date, due_date, status):
    """
    Retrieve and validate project input, then create a project record.
    Confirm success or show error accordingly.

    Args:
        client_name (tk.Entry or tk.StringVar): Client selection widget.
        project_title (tk.Entry): Project title input widget.
        start_date (tk.Label): Label widget holding start date text.
        due_date (tk.Label): Label widget holding due date text.
        status (tk.StringVar): Status dropdown selection variable.
    """
    global db

    if check_project_info(client_name, project_title, start_date, due_date, status):
        client_name_text = client_name.get().title().strip()
        project_title_text = project_title.get().strip()
        start_date_obj = datetime.strptime(start_date.cget("text"), "%m-%d-%Y").date()
        due_date_obj = datetime.strptime(due_date.cget("text"), "%m-%d-%Y").date()
        status_text = status.get()
        if db.create_project(client_name_text, project_title_text, start_date_obj, due_date_obj, status_text):
            confirm_label = tk.Label(root, text="Saved Project", font="FixedText", fg='green')
            confirm_label.place(x=295, y=225)
            root.after(1000, confirm_label.destroy)  # Remove after 1 sec
            root.after(1400, display_add_project_page())  # Reload page after slight delay
        else:
            messagebox.showerror("PROJECT ERROR",
                                 "Was not able to upload Project into database.")


def check_project_info(client_name, project_title, start_date, due_date, status):
    """
    Validate project inputs: client selected, title non-empty, valid dates selected, and status chosen.
    Prompt confirmation if all valid.

    Args:
        client_name (tk.Entry or tk.StringVar): Client selection widget.
        project_title (tk.Entry): Project title input.
        start_date (tk.Label): Start date label.
        due_date (tk.Label): Due date label.
        status (tk.StringVar): Status dropdown variable.

    Returns:
        bool: True if inputs are valid and user confirms, False otherwise.
    """
    client_name = client_name.get().title().strip()
    project_title = project_title.get().strip()
    status = status.get()

    valid_info = {
        "client_name": False,
        "project_title": False,
        "start_date": False,
        "due_date": False,
        "status": False
    }

    if client_name in (None, '', 'Select Client'):
        messagebox.showwarning("Invalid Client Option", "User didn't select Client.")
        return False
    elif re.match(r'^(?:[A-Z][a-z]+[-\s]?)+$', client_name):
        valid_info['client_name'] = True
    else:
        messagebox.showwarning("Invalid Client Name", "Client name is malformed.")
        return False

    if not project_title:
        messagebox.showwarning("Invalid Project Title", "Project title is required.")
        return False
    else:
        valid_info['project_title'] = True

    if start_date.cget('text') in ('Select Date', ''):
        messagebox.showwarning("Invalid Start Date", "User didn't select Start Date.")
        return False
    else:
        valid_info['start_date'] = True

    if due_date.cget('text') in ('Select Date', ''):
        messagebox.showwarning("Invalid Due Date", "User didn't select Due Date.")
        return False
    else:
        valid_info['due_date'] = True

    if status in (None, '', 'Select Status'):
        messagebox.showwarning("Invalid Status Option", "User didn't select Project Status.")
        return False
    else:
        valid_info['status'] = True

    if all(valid_info.values()):
        # Show confirmation dialog with entered info
        return messagebox.askyesno("Check Project Info", f"The information you've entered:\n"
                                                         f"Client Name: {client_name}\n"
                                                         f"Project Title: {project_title}\n"
                                                         f"Project Status: {status}\n"
                                                         f"Start Date: {start_date.cget('text')}\n"
                                                         f"Due Date: {due_date.cget('text')}\n"
                                                         f"Is this correct?")

    return False


# endregion
# region Add Invoice Page

def get_invoice_info(project_name, amount, due_date, radio_var):
    """
    Retrieve and validate invoice data, then attempt to add it to database.
    Confirm success or show error as appropriate.

    Args:
        project_name (tk.StringVar): Selected project name variable.
        amount (tk.Entry): Entry widget for invoice amount.
        due_date (tk.Label): Label widget holding due date.
        radio_var (tk.IntVar): Paid status radio button variable (0 = No, 1 = Yes).
    """
    global db
    result, value = check_invoice_info(amount, due_date, project_name, radio_var)
    if result:
        due_date_obj = datetime.strptime(due_date.cget("text"), "%m-%d-%Y").date()
        if db.create_invoice(project_name.get(), value, due_date_obj, radio_var.get()):
            confirm_label = tk.Label(root, text="Saved Invoice", font="FixedText", fg='green')
            confirm_label.place(x=285, y=225)
            root.after(1000, confirm_label.destroy)
            root.after(1400, display_add_invoice_page)
        else:
            messagebox.showerror("INVOICE ERROR",
                                 "Was not able to upload Invoice into database. Have you already added one for this project?")


def check_invoice_info(amount, due_date, project_name, radio_var):
    """
    Validate invoice form fields: amount numeric, due date selected, project chosen.
    Ask user for confirmation if valid.

    Args:
        amount (tk.Entry): Entry widget for amount.
        due_date (tk.Label): Label widget for due date.
        project_name (tk.StringVar): Selected project name.
        radio_var (tk.IntVar): Paid status radio button variable.

    Returns:
        tuple: (bool confirmation result, float amount value) or False if validation fails.
    """
    project_name = project_name.get().title().strip()
    valid_info = {
        "amount": False,
        "project_name": False,
        "due_date": False
    }
    value, result = check_amount_value(amount)

    if result:
        valid_info['amount'] = True
    else:
        messagebox.showwarning("Invalid Amount", "User didn't enter/entered not a number.")
        return False

    if due_date.cget('text') in ('Select Date', ''):
        messagebox.showwarning("Invalid Due Date", "User didn't select Due Date.")
        return False
    else:
        valid_info['due_date'] = True

    if project_name in (None, '', 'Select Project'):
        messagebox.showwarning("Invalid Project Option", "User didn't select Project.")
        return False
    else:
        valid_info['project_name'] = True

    if radio_var.get() == 0:
        radio = 'No'
    else:
        radio = 'Yes'

    if valid_info:
        # Show confirmation dialog with entered invoice info
        return messagebox.askyesno("Check Client Info", f"The information you've entered:\n"
                                                        f"Project Name: {project_name}\n"
                                                        f"Invoice Amount: {amount.get()}\n"
                                                        f"Due Date: {due_date.cget('text')}\n"
                                                        f"Paid: {radio}\n"
                                                        f"Is this correct?"), value


def check_amount_value(entry):
    """
    Attempt to parse the amount entry to a float rounded to two decimals.

    Args:
        entry (tk.Entry): Entry widget containing amount string.

    Returns:
        tuple: (float amount value or original string, bool success flag)
    """
    value = entry.get().strip("$")
    try:
        value = float(value)
        value = round(value, 2)
        return value, True
    except ValueError:
        return value, False


# endregion

# region Client Filter Page

# region Filter Clients

def get_client_list(filter_params=None):
    """
    Fetch and display a list of clients in the GUI, optionally filtered by parameters.
    Creates or updates the listbox and scrollbar widgets as needed.
    Shows a 'No Invoices' label if no clients found.

    Args:
        filter_params (dict, optional): Filtering options to pass to the database query.
    """
    global clients_list, clients_scrollbar, no_clients_label
    clients = None
    if filter_params:
        clients = db.get_filtered_clients(filter_params)  # Get filtered clients from DB
    else:
        clients = db.get_clients()  # Get all clients from DB

    # If the clients_list widget doesn't exist or was destroyed, create it along with scrollbar
    if clients_list is None or not clients_list.winfo_exists():
        clients_scrollbar = tk.Scrollbar(root, orient='horizontal')  # Horizontal scrollbar
        clients_list = Listbox(root, font="FixedView", width=100, height=12, xscrollcommand=clients_scrollbar.set)
        clients_list.place(x=240, y=85)  # Place listbox on the root window
        clients_scrollbar.config(command=clients_list.xview)  # Link scrollbar to listbox scrolling
        clients_scrollbar.pack(side='bottom', fill='x')  # Pack scrollbar at bottom horizontally

        # Reassign globals to avoid scoping issues elsewhere
        globals()['clients_list'] = clients_list
        globals()['clients_scrollbar'] = clients_scrollbar

    # Clear all current entries before inserting new ones
    clients_list.delete(0, tk.END)

    if clients:
        # Make sure listbox and scrollbar are visible (in case previously hidden)
        if clients_list and not clients_list.winfo_ismapped():
            clients_list.place(x=240, y=85)
        if clients_scrollbar and not clients_scrollbar.winfo_ismapped():
            clients_scrollbar.pack(side='bottom', fill='x')
        # Hide the "No Invoices" label if it exists and is visible
        if no_clients_label and no_clients_label.winfo_exists():
            no_clients_label.place_forget()

        # Insert formatted client info into the listbox
        for index, client in enumerate(clients):
            formatted_invoice = f"{index + 1}) Name: {client[0]} | Company: {client[1]} | Email: {client[2]} | Projects: {client[3]}"
            clients_list.insert(index, formatted_invoice)
    else:
        # No clients found: hide listbox and scrollbar
        clients_list.place_forget()
        clients_scrollbar.pack_forget()

        # Show "No Invoices" label or create it if needed
        if no_clients_label is None or not no_clients_label.winfo_exists():
            no_clients_label = tk.Label(root,
                                        text="No Invoices",
                                        font="FixedText",
                                        fg='green')
            globals()['no_clients_label'] = no_clients_label
        no_clients_label.place(x=240, y=85)


def client_filter(client_radio, client_entry, project_radio):
    """
    Process the filter inputs from UI widgets, build a filter dictionary,
    and fetch filtered client list for display.
    Adds or removes the reset filter button based on whether filters are active.

    Args:
        client_radio (tk.IntVar): Radio button value for client name filtering mode.
        client_entry (tk.Entry): Entry widget for client name input.
        project_radio (tk.IntVar): Radio button value for project count filtering.
    """
    filter_dict = {
        "client_radio": None,
        "client_string": None,
        "project_radio": None
    }

    # Set client_string if entry has a value
    if client_entry.get() not in (None, ''):
        filter_dict["client_string"] = client_entry.get()

    # Set client_radio if valid (0 or 1)
    if client_radio.get() in (0, 1):
        filter_dict["client_radio"] = client_radio.get()

    # Set project_radio if valid (0, 1, or 2)
    if project_radio.get() in (0, 1, 2):
        filter_dict["project_radio"] = project_radio.get()

    # Remove keys with None values to send as actual filters
    filter_params = {k: v for k, v in filter_dict.items() if v is not None}

    # If any filters were provided, update the client list accordingly
    if any(v is not None for v in filter_dict.values()):
        reset = True
        get_client_list(filter_params)  # Show filtered clients
    else:
        reset = False  # No filters applied

    add_reset_client_filter_btn(reset, client_radio, client_entry, project_radio)


def add_reset_client_filter_btn(reset, client_radio, client_entry, project_radio):
    """
    Add a 'Reset Filters' button to the UI if filters are active,
    otherwise destroy the button.

    Args:
        reset (bool): Whether filters are currently active.
        client_radio (tk.IntVar): Client radio button variable.
        client_entry (tk.Entry): Client name entry.
        project_radio (tk.IntVar): Project radio button variable.
    """
    reset_btn = tk.Button(root,
                          text="Reset Filters",
                          font="FixedInstruct",
                          fg='darkred',
                          command=lambda: reset_client_filter(reset_btn, client_radio, client_entry, project_radio))
    if reset:
        reset_btn.place(x=45, y=234)
    else:
        reset_btn.destroy()


def reset_client_filter(reset_btn, client_radio, client_entry, project_radio):
    """
    Clear all filter inputs and reset the client list display to show all clients.
    Destroys the reset button after resetting.

    Args:
        reset_btn (tk.Button): The reset filters button to destroy.
        client_radio (tk.IntVar): Client filter radio button.
        client_entry (tk.Entry): Client name entry widget.
        project_radio (tk.IntVar): Project filter radio button.
    """
    client_entry.delete(0, tk.END)  # Clear client entry field
    client_radio.set(-1)  # Reset client radio buttons to default
    project_radio.set(-1)  # Reset project radio buttons to default
    get_client_list()  # Reload full client list without filters
    reset_btn.destroy()  # Remove reset button from UI


# endregion


# region Edit Clients

def edit_client_select(client_id, project_count, value):
    """
    Show an editable input field inside a frame based on selected client field to edit.
    Handles creation or clearing of the edit frame.

    Args:
        client_id (int): The ID of the client to edit.
        project_count (int): Number of projects associated with the client.
        value (str): Which client field to edit ("Name", "Company name", or "Email").
    """
    global edit_clients_dynamic_frame

    # Create the dynamic edit frame if it doesn't exist or is hidden
    if (edit_clients_dynamic_frame is None
            or not edit_clients_dynamic_frame.winfo_exists()
            or not edit_clients_dynamic_frame.winfo_ismapped()):
        edit_clients_dynamic_frame = tk.Frame(root, bg='gray60', width=300, height=100)
        edit_clients_dynamic_frame.place(x=670, y=160)
    else:
        # Clear existing widgets in the frame
        for widget in edit_clients_dynamic_frame.winfo_children():
            widget.destroy()

    # Initialize entry variables
    name_entry = company_entry = email_entry = None

    tk.Label(edit_clients_dynamic_frame, text="What would you like to change it to?:", font="FixedInstruct").pack(anchor='w')

    # Depending on field selected, create appropriate entry widget
    match value:
        case "Name":
            name_entry = tk.Entry(edit_clients_dynamic_frame, bd=0)
            name_entry.pack(pady=5)
        case "Company name":
            company_entry = tk.Entry(edit_clients_dynamic_frame, bd=0)
            company_entry.pack(pady=5)
        case "Email":
            email_entry = tk.Entry(edit_clients_dynamic_frame, bd=0)
            email_entry.pack(pady=5)

    # Button to submit changes, calls submit_client_edit with entry widgets passed
    submit_btn = tk.Button(edit_clients_dynamic_frame,
                           text="Submit",
                           font="FixedBtn",
                           command=lambda: submit_client_edit(client_id, project_count, name_entry, company_entry, email_entry))
    submit_btn.pack(side="bottom")


def submit_client_edit(client_id, project_count, name_entry, company_entry, email_entry):
    """
    Validate and update client information based on input entries.
    Validates name and email formats, updates DB, reloads client view,
    and shows error message on invalid inputs.

    Args:
        client_id (int): The ID of the client to update.
        project_count (int): Number of projects associated with client (used elsewhere).
        name_entry (tk.Entry or None): Entry widget for client name if editing.
        company_entry (tk.Entry or None): Entry widget for company name if editing.
        email_entry (tk.Entry or None): Entry widget for email if editing.
    """
    if name_entry:
        valid_name = re.match(r'^(?:[A-Z][a-z]+[-\s]?)+$', name_entry.get())
        if valid_name:
            db.update_client_name(client_id, name_entry.get())
            view_clients()  # Refresh client list view
        else:
            messagebox.showerror("Name ERROR",
                                 "User has not entered a valid name.")
            return False
    if company_entry:
        db.update_company_name(client_id, company_entry.get())
        view_clients()
    if email_entry:
        valid_email = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_entry.get())
        if valid_email:
            db.update_client_email(client_id, email_entry.get())
            view_clients()
        else:
            messagebox.showerror("Email ERROR",
                                 "User has not entered a valid email.")
            return False


def remove_client(client_id, project_count):
    """
    Attempt to delete a client if they have no associated projects.
    Shows error if deletion is blocked due to linked projects.

    Args:
        client_id (int): The ID of the client to delete.
        project_count (int): Number of projects linked to the client.
    """
    if project_count == 0:
        db.delete_client(client_id)
        view_clients()  # Refresh client list after deletion
    else:
        messagebox.showerror("Client ERROR",
                             "Client has a Project associated with their account.\nDelete it before deleting Client.")
        return False


# endregion


# region Edit/Delete Clients

def try_edit_client():
    """
    Attempt to get the selected client from the list and open the edit client UI.
    Shows warning if no client is selected.
    """
    selected = get_selected_client()
    if selected:
        client_name = selected.split("Name: ")[1].split(" |")[0]  # Extract client name from listbox entry
        edit_client(client_name)


def get_selected_client():
    """
    Retrieve the currently selected client entry from the clients_list listbox.
    Shows warning if nothing is selected.

    Returns:
        str or None: The selected client string or None if nothing selected.
    """
    global clients_list
    selection = clients_list.curselection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a Client to edit.")
        return None

    index = selection[0]
    selected_text = clients_list.get(index)
    return selected_text


def edit_client(client_name):
    """
    Prepare the UI for editing a client's details by hiding the client list and showing edit options.
    Fetches client details and populates labels and dropdowns for editing.

    Args:
        client_name (str): Name of the client to edit.
    """
    global clients_list, clients_scrollbar, no_clients_label

    # Button to go back to client list view
    back_btn = tk.Button(root, text='Back to List', width=10, height=1, font="FixedInstruct", command=view_clients)
    back_btn.place(x=0, y=0)

    # Get client ID for DB operations
    client_id = db.get_client_id(client_name)

    # Hide listbox and scrollbar to focus on editing UI
    if clients_list and clients_list.winfo_exists():
        clients_list.place_forget()

    if clients_scrollbar and clients_scrollbar.winfo_exists():
        clients_scrollbar.pack_forget()

    if no_clients_label and no_clients_label.winfo_exists():
        no_clients_label.place_forget()

    # Reset global listbox variables to None to prevent bugs on reload
    clients_list = None
    clients_scrollbar = None

    # Fetch detailed client data for editing display
    result = db.get_client_to_edit(client_id)[0]
    project_count = int(result[3])
    formatted_result = f"Client Name: {result[0]}\n\nCompany Name: {result[1]}\n\nEmail: {result[2]}\n\nProject count: {project_count}"

    # Layout frame and labels/buttons for delete and edit options
    filter_frame = tk.Frame(root, width=240, height=240, bg='gray60').place(x=0, y=70)
    delete_instruct = tk.Label(root, text="Are you sure?\nThis cannot be undone.", bg="gray60", fg="darkred", font="FixedInstruct").place(x=50, y=100)
    delete_btn = tk.Button(root, text="Delete Client", fg='darkred', font="FixedBtn", command=lambda: remove_client(client_id, project_count))
    delete_btn.place(x=25, y=140)
    delete_client_instruct = tk.Label(root,
                                      text="Notice:\nWill only delete Client\nif no projects associated.",
                                      bg="gray60",
                                      fg="darkred",
                                      font="FixedInstruct").place(x=25, y=180)
    project_label = tk.Label(root, text=formatted_result, font="FixedText").place(x=240, y=80)
    edit_instruct = tk.Label(root, text="What would you like to edit?:", font="FixedInstruct").place(x=700, y=80)

    # Dropdown menu for choosing which field to edit, triggers edit_client_select on choice
    edit_list = ["Name", "Company name", "Email"]
    edit_menu = StringVar()
    edit_menu.set("Select Field")
    edit_drop = OptionMenu(root, edit_menu, *edit_list, command=lambda val: edit_client_select(client_id, project_count, val))
    edit_drop.config(font="FixedText")
    edit_drop["menu"].config(font="FixedText")
    edit_drop.place(x=720, y=100)


# endregion

# endregion
# region Project Filter Page

# region Filter Projects

def get_project_list(filter_params=None):
    """
    Fetch and display a list of projects in the GUI, optionally filtered by parameters.
    Creates or updates the listbox and scrollbar widgets as needed.
    Shows a 'No Projects' label if no projects found.

    Args:
        filter_params (dict, optional): Filtering options to pass to the database query.
    """
    global projects_list, project_scrollbar, no_project_label

    projects = None
    if filter_params:
        projects = db.get_filtered_projects(filter_params)  # Get filtered projects from DB
    else:
        projects = db.get_projects()  # Get all projects from DB

    # If the projects_list widget doesn't exist or was destroyed, create it along with scrollbar
    if projects_list is None or not projects_list.winfo_exists():
        project_scrollbar = tk.Scrollbar(root, orient='horizontal')  # Horizontal scrollbar
        projects_list = Listbox(root, font="FixedView", width=100, height=12, xscrollcommand=project_scrollbar.set)
        projects_list.place(x=240, y=85)  # Place listbox on the root window
        project_scrollbar.config(command=projects_list.xview)  # Link scrollbar to listbox scrolling
        project_scrollbar.pack(side='bottom', fill='x')  # Pack scrollbar at bottom horizontally

        # Reassign globals to avoid scoping issues elsewhere
        globals()['projects_list'] = projects_list
        globals()['project_scrollbar'] = project_scrollbar

    # Clear all current entries before inserting new ones
    projects_list.delete(0, tk.END)

    if projects:
        # Make sure listbox and scrollbar are visible (in case previously hidden)
        if projects_list and not projects_list.winfo_ismapped():
            projects_list.place(x=240, y=85)
        if project_scrollbar and not project_scrollbar.winfo_ismapped():
            project_scrollbar.pack(side='bottom', fill='x')
        # Hide the "No Projects" label if it exists and is visible
        if no_project_label and no_project_label.winfo_exists():
            no_project_label.place_forget()

        # Insert formatted project info into the listbox
        for index, project in enumerate(projects):
            # Format dates from YYYY-MM-DD to MM/DD/YYYY for display
            formatted_start = datetime.strptime(project[2], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_due = datetime.strptime(project[3], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_project = f"{index + 1}) Project: {project[0]} | Client: {project[1]} | Start: {formatted_start} | Due: {formatted_due} | Status: {project[4]}"
            projects_list.insert(index, formatted_project)
    else:
        # No projects found: hide listbox and scrollbar
        projects_list.place_forget()
        project_scrollbar.pack_forget()

        # Show "No Projects" label or create it if needed
        if no_project_label is None or not no_project_label.winfo_exists():
            no_project_label = tk.Label(root,
                                        text="No Projects",
                                        font="FixedText",
                                        fg='green')
            globals()['no_project_label'] = no_project_label
        no_project_label.place(x=240, y=85)


def project_filter(client_menu, status_menu, month_menu, start_btn):
    """
    Collect filter selections from UI widgets, build filter dict, and refresh project list accordingly.
    Adds or removes the reset filter button based on whether filters are active.

    Args:
        client_menu (tk.StringVar): Dropdown for client filtering.
        status_menu (tk.StringVar): Dropdown for status filtering.
        month_menu (tk.StringVar): Dropdown for month filtering.
        start_btn (tk.Button): Button displaying selected start date for filtering.
    """
    filter_dict = {
        "client": None,
        "status": None,
        "month": None,
        "week_date": None
    }

    # Set filter values if valid selections
    if client_menu.get() not in (None, '', 'Select Client'):
        filter_dict["client"] = client_menu.get()

    if status_menu.get() not in (None, '', 'Select Status'):
        filter_dict["status"] = status_menu.get()

    if month_menu.get() not in (None, '', 'Select Month'):
        filter_dict["month"] = month_menu.get()

    # Convert button text date to proper format if date selected
    if start_btn.cget('text') != "Select Date":
        date_obj = datetime.strptime(start_btn.cget('text'), "%m-%d-%Y")
        filter_dict["week_date"] = date_obj.strftime("%Y-%m-%d")

    # Remove keys with None values to send as actual filters
    filter_params = {k: v for k, v in filter_dict.items() if v is not None}

    # If any filters were provided, update the project list accordingly
    if any(v is not None for v in filter_dict.values()):
        reset = True
        get_project_list(filter_params)  # Show filtered projects
    else:
        reset = False  # No filters applied

    add_reset_project_filter_btn(reset, client_menu, status_menu, month_menu, start_btn)


def add_reset_project_filter_btn(reset, client_menu, status_menu, month_menu, start_btn):
    """
    Add a 'Reset Filters' button to the UI if filters are active,
    otherwise destroy the button.

    Args:
        reset (bool): Whether filters are currently active.
        client_menu (tk.StringVar): Client dropdown variable.
        status_menu (tk.StringVar): Status dropdown variable.
        month_menu (tk.StringVar): Month dropdown variable.
        start_btn (tk.Button): Start date button.
    """
    reset_btn = tk.Button(root,
                          text="Reset Filters",
                          font="FixedInstruct",
                          fg='darkred',
                          command=lambda: reset_project_filter(reset_btn, client_menu, status_menu, month_menu, start_btn))
    if reset:
        reset_btn.place(x=45, y=234)
    else:
        reset_btn.destroy()


def reset_project_filter(reset_btn, client_menu, status_menu, month_menu, start_btn):
    """
    Clear all filter inputs and reset the project list display to show all projects.
    Destroys the reset button after resetting.

    Args:
        reset_btn (tk.Button): The reset filters button to destroy.
        client_menu (tk.StringVar): Client dropdown variable.
        status_menu (tk.StringVar): Status dropdown variable.
        month_menu (tk.StringVar): Month dropdown variable.
        start_btn (tk.Button): Start date button.
    """
    client_menu.set('Select Client')  # Reset client dropdown
    status_menu.set('Select Status')  # Reset status dropdown
    month_menu.set('Select Month')  # Reset month dropdown
    start_btn.config(text='Select Date')  # Reset date button text
    get_project_list()  # Reload full project list without filters
    reset_btn.destroy()  # Remove reset button from UI


# endregion


# region Edit Project

def edit_project_select(project_id, value):
    """
    Display appropriate input widget for editing the selected project field.
    Creates or clears a dynamic frame to hold the input widgets.

    Args:
        project_id (int): The ID of the project being edited.
        value (str): The field selected for editing (e.g., "Project Name", "Client Name", "Status", "Start Date", "Due Date").
    """
    global edit_project_dynamic_frame

    # Create the dynamic edit frame if it doesn't exist or is hidden
    if (edit_project_dynamic_frame is None
            or not edit_project_dynamic_frame.winfo_exists()
            or not edit_project_dynamic_frame.winfo_ismapped()):
        edit_project_dynamic_frame = tk.Frame(root, bg='gray60', width=300, height=100)
        edit_project_dynamic_frame.place(x=670, y=160)
    else:
        # Clear existing widgets in the frame
        for widget in edit_project_dynamic_frame.winfo_children():
            widget.destroy()

    # Initialize entry variables
    project_name_entry = client_menu = status_menu = date_btn = None

    tk.Label(edit_project_dynamic_frame, text="What would you like to change it to?:", font="FixedInstruct").pack(anchor='w')

    # Depending on field selected, create appropriate input widget
    match value:
        case "Project Name":
            project_name_entry = tk.Entry(edit_project_dynamic_frame, bd=0)
            project_name_entry.pack(pady=5)
        case "Client Name":
            client_list = db.get_list_of_clients()
            client_menu = StringVar()
            client_menu.set("Select Client")
            client_drop = OptionMenu(edit_project_dynamic_frame, client_menu, *client_list)
            client_drop.config(font="FixedText")
            client_drop["menu"].config(font="FixedText")
            client_drop.pack(pady=5)
        case "Status":
            status_list = ["Not Started", "Started", "In Progress", "Testing", "Finished"]
            status_menu = StringVar()
            status_menu.set("Select Status")
            status_drop = OptionMenu(edit_project_dynamic_frame, status_menu, *status_list)
            status_drop.config(font="FixedText")
            status_drop["menu"].config(font="FixedText")
            status_drop.pack(pady=5)
        case "Start Date" | "Due Date":
            date_btn = tk.Button(edit_project_dynamic_frame, text='Select Date', width=9, font="FixedText", command=lambda: create_calender(date_btn))
            date_btn.pack(pady=5)

    # Submit button to apply changes, calls submit_project_edit with relevant widgets passed
    submit_btn = tk.Button(edit_project_dynamic_frame,
                           text="Submit",
                           font="FixedBtn",
                           command=lambda: submit_project_edit(project_id, value, project_name_entry, client_menu, status_menu, date_btn))
    submit_btn.pack(side="bottom")


def submit_project_edit(project_id, value, project_name_entry, client_menu, status_menu, date_btn):
    """
    Update project details based on user input from the editing widgets.
    Calls relevant database update functions and refreshes the project list view.

    Args:
        project_id (int): The ID of the project to update.
        value (str): The field being edited.
        project_name_entry (tk.Entry or None): Entry widget for project name.
        client_menu (tk.StringVar or None): Dropdown variable for client.
        status_menu (tk.StringVar or None): Dropdown variable for status.
        date_btn (tk.Button or None): Button widget containing the selected date text.
    """
    if project_name_entry:
        db.update_project_name(project_id, project_name_entry.get())
        view_projects()
    if client_menu:
        db.update_project_client(project_id, client_menu.get())
        view_projects()
    if status_menu:
        db.update_project_status(project_id, status_menu.get())
        view_projects()
    if date_btn:
        # Convert button text date to date object for DB update
        formatted_date = datetime.strptime(date_btn.cget("text"), "%m-%d-%Y").date()
        db.update_project_date(project_id, value, formatted_date)
        view_projects()


def remove_project(project_id):
    """
    Delete a project from the database and refresh the project list.

    Args:
        project_id (int): The ID of the project to delete.
    """
    db.delete_project(project_id)
    view_projects()


# endregion


# region Edit/Delete Project

def try_edit_project():
    """
    Attempt to get the selected project from the list and open the edit project UI.
    Shows warning if no project is selected.
    """
    selected = get_selected_project()
    if selected:
        project_name = selected.split("Project: ")[1].split(" |")[0]  # Extract project name from listbox entry
        edit_project(project_name)


def get_selected_project():
    """
    Retrieve the currently selected project entry from the projects_list listbox.
    Shows warning if nothing is selected.

    Returns:
        str or None: The selected project string or None if nothing selected.
    """
    global projects_list
    selection = projects_list.curselection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a project to edit.")
        return None

    index = selection[0]
    selected_text = projects_list.get(index)
    return selected_text


def edit_project(project_name):
    """
    Prepare the UI for editing a project's details by hiding the project list and showing edit options.
    Fetches project details and populates labels and dropdowns for editing.

    Args:
        project_name (str): Name of the project to edit.
    """
    global projects_list, project_scrollbar, no_project_label

    # Button to go back to project list view
    back_btn = tk.Button(root, text='Back to List', width=10, height=1, font="FixedInstruct", command=view_projects)
    back_btn.place(x=0, y=0)

    # Get project ID for DB operations
    project_id = db.get_project_id(project_name)

    # Hide listbox and scrollbar to focus on editing UI
    if projects_list and projects_list.winfo_exists():
        projects_list.place_forget()

    if project_scrollbar and project_scrollbar.winfo_exists():
        project_scrollbar.pack_forget()

    if no_project_label and no_project_label.winfo_exists():
        no_project_label.place_forget()

    # Reset global listbox variables to None to prevent bugs on reload
    projects_list = None
    project_scrollbar = None

    # Fetch detailed project data for editing display
    result = db.get_project_to_edit(project_id)[0]
    formatted_start = datetime.strptime(result[2], "%Y-%m-%d").strftime("%m/%d/%Y")
    formatted_due = datetime.strptime(result[3], "%Y-%m-%d").strftime("%m/%d/%Y")
    formatted_result = f"Project Name: {result[0]}\n\nClient Name: {result[1]}\n\nStart Date: {formatted_start}\n\nDue Date: {formatted_due}\n\nStatus: {result[4]}"

    # Layout frame and labels/buttons for delete and edit options
    filter_frame = tk.Frame(root, width=240, height=240, bg='gray60').place(x=0, y=70)
    delete_instruct = tk.Label(root, text="Are you sure?\nThis cannot be undone.", bg="gray60", fg="darkred", font="FixedInstruct").place(x=50, y=100)
    delete_btn = tk.Button(root, text="Delete project", fg='darkred', font="FixedBtn", command=lambda: remove_project(project_id))
    delete_btn.place(x=25, y=140)
    project_label = tk.Label(root, text=formatted_result, font="FixedText").place(x=240, y=80)
    edit_instruct = tk.Label(root, text="What would you like to edit?:", font="FixedInstruct").place(x=700, y=80)

    # Dropdown menu for choosing which field to edit, triggers edit_project_select on choice
    edit_list = ["Project Name", "Client Name", "Start Date", "Due Date", "Status"]
    edit_menu = StringVar()
    edit_menu.set("Select Field")
    edit_drop = OptionMenu(root, edit_menu, *edit_list, command=lambda val: edit_project_select(project_id, val))
    edit_drop.config(font="FixedText")
    edit_drop["menu"].config(font="FixedText")
    edit_drop.place(x=720, y=100)


# endregion


# endregion
# region Invoice Filter Page

# region Filter Invoices

def get_invoice_list(filter_params=None):
    """
    Fetch and display invoices in a listbox, optionally filtered by parameters.
    Recreates listbox and scrollbar if needed. Shows 'No Invoices' if none found.
    """
    global invoices_list, invoice_scrollbar, no_invoice_label

    invoices = db.get_filtered_invoices(filter_params) if filter_params else db.get_invoices()

    # Create listbox and scrollbar if missing or destroyed
    if invoices_list is None or not invoices_list.winfo_exists():
        invoice_scrollbar = tk.Scrollbar(root, orient='horizontal')
        invoices_list = Listbox(root, font="FixedView", width=100, height=12, xscrollcommand=invoice_scrollbar.set)
        invoices_list.place(x=240, y=85)
        invoice_scrollbar.config(command=invoices_list.xview)
        invoice_scrollbar.pack(side='bottom', fill='x')

        globals()['invoices_list'] = invoices_list
        globals()['invoice_scrollbar'] = invoice_scrollbar

    invoices_list.delete(0, tk.END)

    if invoices:
        # Show widgets if hidden
        if not invoices_list.winfo_ismapped():
            invoices_list.place(x=240, y=85)
        if not invoice_scrollbar.winfo_ismapped():
            invoice_scrollbar.pack(side='bottom', fill='x')
        if no_invoice_label and no_invoice_label.winfo_exists():
            no_invoice_label.place_forget()

        # Insert formatted invoices into listbox
        for index, invoice in enumerate(invoices):
            formatted_date = datetime.strptime(invoice[3], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_paid = "Yes" if invoice[4] else "No"
            formatted_invoice = f"{index + 1}) Project: {invoice[0]} | Client: {invoice[1]} | Amount: ${invoice[2]} | Due: {formatted_date} | Paid: {formatted_paid}"
            invoices_list.insert(index, formatted_invoice)
    else:
        # Hide widgets and show 'No Invoices'
        invoices_list.place_forget()
        invoice_scrollbar.pack_forget()

        if no_invoice_label is None or not no_invoice_label.winfo_exists():
            no_invoice_label = tk.Label(root, text="No Invoices", font="FixedText", fg='green')
            globals()['no_invoice_label'] = no_invoice_label
        no_invoice_label.place(x=240, y=85)


def invoice_filter(client_menu, paid_var, month_menu, start_btn):
    """
    Gather filter selections and apply them to the invoice list.
    Also manage the reset filter button visibility.
    """
    filter_dict = {
        "client": client_menu.get() if client_menu.get() not in (None, '', 'Select Client') else None,
        "paid": paid_var.get() if paid_var.get() in (0, 1) else None,
        "month": month_menu.get() if month_menu.get() not in (None, '', 'Select Month') else None,
        "week_date": None
    }

    if start_btn.cget('text') != "Select Date":
        date_obj = datetime.strptime(start_btn.cget('text'), "%m-%d-%Y")
        filter_dict["week_date"] = date_obj.strftime("%Y-%m-%d")

    filter_params = {k: v for k, v in filter_dict.items() if v is not None}

    reset = any(v is not None for v in filter_dict.values())
    get_invoice_list(filter_params if reset else None)

    add_reset_invoice_filter_btn(reset, client_menu, paid_var, month_menu, start_btn)


def add_reset_invoice_filter_btn(reset, client_menu, paid_var, month_menu, start_btn):
    """
    Display or remove the 'Reset Filters' button depending on whether filters are active.
    """
    reset_btn = tk.Button(root,
                          text="Reset Filters",
                          font="FixedInstruct",
                          fg='darkred',
                          command=lambda: reset_invoice_filter(reset_btn, client_menu, paid_var, month_menu, start_btn))
    if reset:
        reset_btn.place(x=45, y=234)
    else:
        reset_btn.destroy()


def reset_invoice_filter(reset_btn, client_menu, paid_var, month_menu, start_btn):
    """
    Clear all filter inputs and refresh invoice list with no filters.
    Destroy the reset button after resetting.
    """
    client_menu.set('Select Client')
    paid_var.set(0)  # Assuming 0 means 'No' or unselected
    month_menu.set('Select Month')
    start_btn.config(text='Select Date')
    get_invoice_list()
    reset_btn.destroy()


# endregion


# region Edit Invoices

def edit_invoice_select(invoice_id, value):
    """
    Show appropriate editing widget in a dynamic frame based on field chosen.
    """
    global edit_invoice_dynamic_frame

    if edit_invoice_dynamic_frame is None or not edit_invoice_dynamic_frame.winfo_exists() or not edit_invoice_dynamic_frame.winfo_ismapped():
        edit_invoice_dynamic_frame = tk.Frame(root, bg='gray60', width=300, height=100)
        edit_invoice_dynamic_frame.place(x=670, y=160)
    else:
        for widget in edit_invoice_dynamic_frame.winfo_children():
            widget.destroy()

    invoice_amount_entry = None
    paid_var = None
    date_btn = None

    tk.Label(edit_invoice_dynamic_frame, text="What would you like to change it to?:", font="FixedInstruct").pack(anchor='w')

    match value:
        case "Amount":
            invoice_amount_entry = tk.Entry(edit_invoice_dynamic_frame, bd=0)
            invoice_amount_entry.pack(pady=5)
            invoice_amount_entry.insert(0, "$")  # Prompt user to enter amount with dollar sign
        case "Due Date":
            date_btn = tk.Button(edit_invoice_dynamic_frame, text='Select Date', width=9, font="FixedText", command=lambda: create_calender(date_btn))
            date_btn.pack(pady=5)
        case "Paid":
            tk.Label(edit_invoice_dynamic_frame, text="Paid:", font="FixedText", bg='gray60').pack(side=TOP, anchor=W)
            paid_var = tk.IntVar()
            Radiobutton(edit_invoice_dynamic_frame, bg='gray60', text="Yes", variable=paid_var, value=1).pack(side=TOP, anchor=E, pady=5)
            Radiobutton(edit_invoice_dynamic_frame, bg='gray60', text="No", variable=paid_var, value=2).pack(side=TOP, anchor=E, pady=5)

    submit_btn = tk.Button(edit_invoice_dynamic_frame,
                           text="Submit",
                           font="FixedBtn",
                           command=lambda: submit_invoice_edit(invoice_id, invoice_amount_entry, paid_var, date_btn))
    submit_btn.pack(side="bottom")


def submit_invoice_edit(invoice_id, invoice_amount_entry, paid_var, date_btn):
    """
    Validate and update invoice fields based on user input.
    """
    if invoice_amount_entry:
        if check_amount_value(invoice_amount_entry):
            amount_val = invoice_amount_entry.get().strip("$")
            db.update_invoice_amount(invoice_id, amount_val)
            view_invoices()
        else:
            messagebox.showerror("Invoice ERROR", "User entered invalid number amount.")
            return False
    if paid_var:
        # Convert radiobutton value 2 ("No") to 0 to match DB schema (assuming 0 = No, 1 = Yes)
        paid_value = 0 if paid_var.get() == 2 else paid_var.get()
        db.update_invoice_paid(invoice_id, paid_value)
        view_invoices()
    if date_btn:
        formatted_date = datetime.strptime(date_btn.cget("text"), "%m-%d-%Y").date()
        db.update_invoice_date(invoice_id, formatted_date)
        view_invoices()


def remove_invoice(invoice_id):
    """
    Remove invoice from database and refresh the invoice list.
    """
    db.delete_invoice(invoice_id)
    view_invoices()


# endregion


# region Edit/Delete Invoices

def try_edit_invoice():
    """
    Attempt to retrieve the selected invoice and open it for editing.
    """
    selected = get_selected_invoice()
    if selected:
        project_name = selected.split("Project: ")[1].split(" |")[0]
        edit_invoice(project_name)


def get_selected_invoice():
    """
    Retrieve currently selected invoice from the listbox. Show warning if none selected.
    Returns:
        str or None: Selected invoice string or None if nothing selected.
    """
    global invoices_list
    selection = invoices_list.curselection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select an invoice to edit.")
        return None

    index = selection[0]
    selected_text = invoices_list.get(index)
    return selected_text


def edit_invoice(project_name):
    """
    Set up the UI to edit a specific invoice, hiding invoice list and showing details.
    """
    global invoices_list, invoice_scrollbar, no_invoice_label

    back_btn = tk.Button(root, text='Back to List', width=10, height=1, font="FixedInstruct", command=view_invoices)
    back_btn.place(x=0, y=0)

    invoice_id = db.get_invoice_id(project_name)

    # Hide invoice listbox and scrollbar to focus on editing UI
    if invoices_list and invoices_list.winfo_exists():
        invoices_list.place_forget()

    if invoice_scrollbar and invoice_scrollbar.winfo_exists():
        invoice_scrollbar.pack_forget()

    if no_invoice_label and no_invoice_label.winfo_exists():
        no_invoice_label.place_forget()

    invoices_list = None
    invoice_scrollbar = None

    result = db.get_invoice_to_edit(invoice_id)[0]
    formatted_paid = "Yes" if result[4] else "No"
    formatted_date = datetime.strptime(result[3], "%Y-%m-%d").strftime("%m/%d/%Y")
    formatted_result = (f"Project Name: {result[0]}\n\nClient Name: {result[1]}\n\n"
                        f"Payment Amount: ${result[2]}\n\nDue Date: {formatted_date}\n\n"
                        f"Paid Status: {formatted_paid}")

    tk.Frame(root, width=240, height=240, bg='gray60').place(x=0, y=70)
    tk.Label(root, text="Are you sure?\nThis cannot be undone.", bg="gray60", fg="darkred", font="FixedInstruct").place(x=50, y=100)
    tk.Button(root, text="Delete invoice", fg='darkred', font="FixedBtn", command=lambda: remove_invoice(invoice_id)).place(x=25, y=140)
    tk.Label(root, text=formatted_result, font="FixedText").place(x=240, y=80)
    tk.Label(root, text="What would you like to edit?:", font="FixedInstruct").place(x=700, y=80)

    edit_list = ["Amount", "Due Date", "Paid"]
    edit_menu = StringVar()
    edit_menu.set("Select Field")
    edit_drop = OptionMenu(root, edit_menu, *edit_list, command=lambda val: edit_invoice_select(invoice_id, val))
    edit_drop.config(font="FixedText")
    edit_drop["menu"].config(font="FixedText")
    edit_drop.place(x=720, y=100)


# endregion

# endregion

# endregion

# region GUI

def display_home_page():
    """
    Clears the root window and sets up the home page layout.
    Displays the logo, title, and buttons for navigation to add/view clients, projects, invoices, and outstanding items.
    """
    clear_root()
    root.geometry("710x315")

    # region Logo
    image_path = "ufo_logo.png"
    original_image = Image.open(image_path)  # Load the original logo image
    big_image = original_image.resize((280, 220))  # Resize the logo to fit the home page
    logo_image = ImageTk.PhotoImage(big_image)  # Convert image for Tkinter display
    logo_label = tk.Label(root, image=logo_image)  # Create a label widget to hold the logo image
    logo_label.image = logo_image  # Keep a reference to avoid garbage collection
    logo_label.place(x=175, y=50)  # Position the logo on the window
    # endregion

    # Display the title label
    title_label = tk.Label(root, text="EndlingCRM", font="FixedTitle")
    title_label.place(x=185, y=10)

    # Buttons to add clients, projects, and invoices
    add_client_btn = tk.Button(root, text='Add Client', width=9, height=1, font="FixedBtn", command=display_add_client_page)
    add_client_btn.place(x=40, y=90)

    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn", command=display_add_project_page)
    add_project_btn.place(x=40, y=150)

    add_invoice_btn = tk.Button(root, text='Add Invoice', width=9, height=1, font="FixedBtn", command=display_add_invoice_page)
    add_invoice_btn.place(x=40, y=210)

    # Buttons to view/edit clients, projects, invoices
    view_clients_btn = tk.Button(root, text='View/Edit Clients', width=15, height=1, font="FixedBtn", command=view_clients)
    view_clients_btn.place(x=433, y=90)

    view_projects_btn = tk.Button(root, text='View/Edit Projects', width=15, height=1, font="FixedBtn", command=view_projects)
    view_projects_btn.place(x=433, y=150)

    # Check if there are any projects needing invoicing, display label if yes
    project_list = db.get_list_of_projects()
    if project_list[0] != '':
        invoice_label = tk.Label(root, text="Projects need to be Invoiced", font="FixedInstruct", fg='darkred')
        invoice_label.place(x=10, y=190)

    view_invoices_btn = tk.Button(root, text='View/Edit Invoices', width=15, height=1, font="FixedBtn", command=view_invoices)
    view_invoices_btn.place(x=433, y=210)

    # Button to view outstanding invoices/projects
    view_outstanding_btn = tk.Button(root, text='View Outstanding', width=14, height=1, font="FixedBtn", command=view_outstanding)
    view_outstanding_btn.place(x=210, y=260)


def display_add_client_page():
    """
    Clears the root and sets up the add client page with entry fields for client name, email, and company.
    Also adds navigation back to the home page.
    """
    clear_root()
    title_label = tk.Label(root, text="Client Menu", font="FixedTitle")
    title_label.pack()

    # Back to home button
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # Client name label and entry field inside a gray frame
    name_label = tk.Label(root, font="FixedText", text='Client Name:')
    name_label.place(x=185, y=93)
    name_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    name_frame.place(x=320, y=92)
    name_entry = tk.Entry(root, bd=0)
    name_entry.place(x=323, y=95)

    # Client email label and entry field inside a gray frame
    email_label = tk.Label(root, font="FixedText", text='Client Email:')
    email_label.place(x=178, y=126)
    email_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    email_frame.place(x=320, y=125)
    email_entry = tk.Entry(root, bd=0)
    email_entry.place(x=323, y=128)

    # Client company label and entry field inside a gray frame
    company_label = tk.Label(root, font="FixedText", text='Client Company:')
    company_label.place(x=155, y=157)
    company_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    company_frame.place(x=320, y=158)
    company_entry = tk.Entry(root, bd=0)
    company_entry.place(x=323, y=161)

    # Button to add client, calls function to gather entry info
    add_client_btn = tk.Button(root,
                               text='Add Client',
                               width=9,
                               height=1,
                               font="FixedBtn",
                               command=lambda: get_client_info(name_entry, email_entry, company_entry))
    add_client_btn.place(x=300, y=250)


def display_add_project_page():
    """
    Clears the root and sets up the add project page with dropdown for clients,
    entries for project title, start/due dates, and status selection.
    Includes a back to home button.
    """
    clear_root()
    title_label = tk.Label(root, text="Project Menu", font="FixedTitle")
    title_label.pack()

    # Back to home button
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # Get client list for dropdown; show message if empty
    client_list = db.get_list_of_clients()
    if client_list[0] == '':
        no_project_label = tk.Label(root, text="No Clients in database", font="FixedInstruct", fg='darkred')
        no_project_label.place(x=500, y=62)

    # Client dropdown menu setup
    client_drop_label = tk.Label(root, font="FixedText", text='Client Name:')
    client_drop_label.place(x=185, y=60)
    client_menu = StringVar()
    client_menu.set("Select Client")
    client_drop = OptionMenu(root, client_menu, *client_list, command=lambda val: on_select(client_menu, val))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=320, y=60)

    # Project title entry with label and gray frame
    project_title_label = tk.Label(root, font="FixedText", text='Project Title:')
    project_title_label.place(x=185, y=96)
    project_title_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    project_title_frame.place(x=340, y=95)
    project_title_entry = tk.Entry(root, bd=0)
    project_title_entry.place(x=343, y=98)

    # Start date button for calendar picker
    start_label = tk.Label(root, font="FixedText", text='Start Date:')
    start_label.place(x=220, y=130)
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(start_btn))
    start_btn.place(x=345, y=129)

    # Due date button for calendar picker
    due_label = tk.Label(root, font="FixedText", text='Due Date:')
    due_label.place(x=240, y=165)
    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(due_btn))
    due_btn.place(x=345, y=164)

    # Status dropdown menu setup with preset status options
    status_list = ["Not Started", "Started", "In Progress", "Testing", "Finished"]
    status_drop_label = tk.Label(root, font="FixedText", text='Status:')
    status_drop_label.place(x=240, y=200)
    status_menu = StringVar()
    status_menu.set("Select Status")
    status_drop = OptionMenu(root, status_menu, *(status_list))
    status_drop.config(font="FixedText")
    status_drop["menu"].config(font="FixedText")
    status_drop.place(x=325, y=200)

    # Button to add project, calls function to gather info
    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn",
                                command=lambda: get_project_info(client_menu, project_title_entry, start_btn, due_btn, status_menu))
    add_project_btn.place(x=285, y=250)


def display_add_invoice_page():
    """
    Clears the root and sets up the add invoice page with dropdown for projects,
    entry for invoice amount, due date picker, and paid status radio buttons.
    Includes a back to home button.
    """
    clear_root()
    title_label = tk.Label(root, text="Invoice Menu", font="FixedTitle")
    title_label.pack()

    # Back to home button
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # Get project list for dropdown; show message if all invoiced
    project_list = db.get_list_of_projects()
    if project_list[0] == '':
        no_project_label = tk.Label(root, text="All projects invoiced", font="FixedInstruct", fg='darkred')
        no_project_label.place(x=320, y=62)

    # Project dropdown menu setup
    project_drop_label = tk.Label(root, font="FixedText", text='Project Name:')
    project_drop_label.place(x=185, y=80)
    project_menu = StringVar()
    project_menu.set("Select Project")
    project_drop = OptionMenu(root, project_menu, *project_list, command=lambda val: on_select(project_menu, val))
    project_drop.config(font="FixedText")
    project_drop["menu"].config(font="FixedText")
    project_drop.place(x=320, y=80)

    # Invoice amount entry with label and gray frame
    amount_label = tk.Label(root, font="FixedText", text='Invoice Amount:')
    amount_label.place(x=183, y=121)
    amount_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    amount_frame.place(x=340, y=120)
    amount_entry = tk.Entry(root, bd=0)
    amount_entry.place(x=343, y=123)
    amount_entry.insert(0, "$")  # Default dollar sign

    # Due date button for calendar picker
    due_label = tk.Label(root, font="FixedText", text='Due Date:')
    due_label.place(x=248, y=155)
    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(due_btn))
    due_btn.place(x=340, y=155)

    # Paid status radio buttons (Yes/No)
    paid_label = tk.Label(root, text="Paid:", font="FixedText")
    paid_label.place(x=280, y=187)
    radio_var = tk.IntVar()
    yes_r1 = Radiobutton(root, text="Yes", variable=radio_var, value=1)
    yes_r1.place(x=344, y=189)
    no_r2 = Radiobutton(root, text="No", variable=radio_var, value=0)
    no_r2.place(x=400, y=189)

    # Button to add invoice, calls function to gather info
    add_invoice_btn = tk.Button(root, text='Add Invoice', width=9, height=1, font="FixedBtn",
                                command=lambda: get_invoice_info(project_menu, amount_entry, due_btn, radio_var))
    add_invoice_btn.place(x=280, y=250)


def view_clients():
    """
    Clears the root and sets up the clients view page with a listbox of clients,
    filtering options, and edit/delete project button.
    """
    root.geometry("1050x305")
    clear_root()
    title_label = tk.Label(root, text="Clients", font="FixedTitle")
    title_label.pack()

    # Back to home button
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    get_client_list()  # Populate the listbox with clients

    # Edit/delete button triggers client edit function
    edit_btn = tk.Button(root, text="Edit/Delete Project", font="FixedInstruct", command=lambda: try_edit_client())
    edit_btn.place(x=875, y=30)

    # region Aesthetic - instructions and visual separators
    instruct_label = tk.Label(root,
                              text="Fill in the fields you'd like to filter by.",
                              font="FixedInstruct")
    instruct_label.place(x=25, y=50)
    filter_line_side = tk.Frame(root, bg="gray60", width=2, height=240)
    filter_line_side.place(x=223, y=70)
    filter_line_top = tk.Frame(root, bg="gray60", width=1050, height=2)
    filter_line_top.place(x=0, y=70)
    # endregion

    # Client search by name radio buttons and entry
    client_label = tk.Label(root, font="FixedInstruct", text='Search by Client name:')
    client_label.place(x=25, y=85)
    client_radio = tk.IntVar()
    client_r1 = Radiobutton(root, text="Starts with", variable=client_radio, value=0)
    client_r1.place(x=25, y=105)
    client_r2 = Radiobutton(root, text="Contains", variable=client_radio, value=1)
    client_r2.place(x=125, y=105)
    client_radio.set(-1)  # Default no selection

    client_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    client_frame.place(x=22, y=132)
    client_entry = tk.Entry(root, bd=0)
    client_entry.place(x=25, y=135)

    # Filter by project count radio buttons
    project_count_label = tk.Label(root, font="FixedInstruct", text='Filter by project count:')
    project_count_label.place(x=25, y=185)
    project_radio = tk.IntVar()
    project_r1 = Radiobutton(root, text="None", variable=project_radio, value=0)
    project_r1.place(x=25, y=205)
    project_r2 = Radiobutton(root, text="1+", variable=project_radio, value=1)
    project_r2.place(x=90, y=205)
    project_r3 = Radiobutton(root, text="3+", variable=project_radio, value=2)
    project_r3.place(x=135, y=205)
    project_radio.set(-1)  # Default no selection

    # Filter button to apply filters
    filter_btn = tk.Button(root, text='Filter', width=4, height=1, font="FixedText",
                           command=lambda: client_filter(client_radio, client_entry, project_radio))
    filter_btn.place(x=70, y=260)


def view_projects():
    """
    Display the Projects page in the GUI.

    This function configures the main window size and clears previous widgets.
    It shows a title, a back-to-home button, a list of projects, and an edit/delete button.
    Additionally, it provides filters for projects by client, status, month, and start date,
    including UI elements like dropdown menus and buttons.
    """
    root.geometry("1050x305")  # Set window size for project view
    clear_root()  # Remove existing widgets to start fresh

    title_label = tk.Label(root, text="Projects", font="FixedTitle")  # Title label for the page
    title_label.pack()

    # Button to return to the home page
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    get_project_list()  # Populate and display the project listbox

    # Button to edit or delete selected project
    edit_btn = tk.Button(root, text="Edit/Delete Project", font="FixedInstruct", command=lambda: try_edit_project())
    edit_btn.place(x=875, y=30)

    # region Aesthetic UI elements for filtering section
    instruct_label = tk.Label(root,
                              text="Fill in the fields you'd like to filter by.",
                              font="FixedInstruct")
    instruct_label.place(x=25, y=50)
    filter_line_side = tk.Frame(root, bg="gray60", width=2, height=240)  # Vertical separator line
    filter_line_side.place(x=223, y=70)
    filter_line_top = tk.Frame(root, bg="gray60", width=1050, height=2)  # Horizontal separator line
    filter_line_top.place(x=0, y=70)
    # endregion

    client_list = db.get_list_of_clients()  # Fetch client list for filter dropdown
    client_menu = StringVar()
    client_menu.set("Select Client")  # Default dropdown text
    client_drop = OptionMenu(root, client_menu, *client_list, command=lambda val: on_select(client_menu, val))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=25, y=80)  # Place client filter dropdown

    status_list = ["Not Started", "Started", "In Progress", "Testing", "Finished"]  # Status filter options
    status_menu = StringVar()
    status_menu.set("Select Status")
    status_drop = OptionMenu(root, status_menu, *(status_list))
    status_drop.config(font="FixedText")
    status_drop["menu"].config(font="FixedText")
    status_drop.place(x=25, y=110)  # Place status filter dropdown

    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]  # Month filter options
    month_menu = StringVar()
    month_menu.set("Select Month")
    month_drop = OptionMenu(root, month_menu, *(month_list))
    month_drop.config(font="FixedText")
    month_drop["menu"].config(font="FixedText")
    month_drop.place(x=25, y=140)  # Place month filter dropdown

    # Label and button to select the starting weekday for filtering
    start_label = tk.Label(root, text="Select starting week day:", font="FixedInstruct")
    start_label.place(x=25, y=175)
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText",
                          command=lambda: create_calender(start_btn))  # Opens a calendar popup
    start_btn.place(x=45, y=195)

    # Filter button to apply selected filters on the projects list
    filter_btn = tk.Button(root, text='Filter', width=4, height=1, font="FixedText",
                           command=lambda: project_filter(client_menu, status_menu, month_menu, start_btn))
    filter_btn.place(x=70, y=260)


def view_invoices():
    """
    Display the Invoices page in the GUI.

    This function sets the window size and clears existing widgets.
    It shows a title, a back button, a list of invoices, and an edit/delete invoice button.
    It also includes filters for client, payment status, month, and start date,
    with UI elements like dropdowns, radio buttons, and a filter button.
    """
    root.geometry("1050x305")  # Set window size for invoice view
    clear_root()  # Clear current widgets

    title_label = tk.Label(root, text="Invoices", font="FixedTitle")  # Title label
    title_label.pack()

    # Button to return to the home page
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    get_invoice_list()  # Populate invoice listbox

    # Button for editing or deleting selected invoice
    edit_btn = tk.Button(root, text="Edit/Delete invoice", font="FixedInstruct", command=lambda: try_edit_invoice())
    edit_btn.place(x=875, y=30)

    # region Aesthetic UI elements for filtering section
    instruct_label = tk.Label(root,
                              text="Fill in the fields you'd like to filter by, otherwise press filter to display all Invoices.",
                              font="FixedInstruct")
    instruct_label.place(x=40, y=50)
    filter_line_side = tk.Frame(root, bg="gray60", width=2, height=240)  # Vertical separator line
    filter_line_side.place(x=223, y=70)
    filter_line_top = tk.Frame(root, bg="gray60", width=1050, height=2)  # Horizontal separator line
    filter_line_top.place(x=0, y=70)
    # endregion

    client_list = db.get_list_of_clients()  # Get client list for invoice filtering
    client_menu = StringVar()
    client_menu.set("Select Client")
    client_drop = OptionMenu(root, client_menu, *client_list, command=lambda val: on_select(client_menu, val))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=25, y=80)  # Place client filter dropdown

    # Label and radio buttons for Paid status filter
    paid_label = tk.Label(root, text="Paid:", font="FixedText")
    paid_label.place(x=25, y=110)
    paid_var = tk.IntVar()
    yes_r1 = Radiobutton(root, text="Yes", variable=paid_var, value=1)
    yes_r1.place(x=89, y=111)
    no_r2 = Radiobutton(root, text="No", variable=paid_var, value=2)
    no_r2.place(x=145, y=111)

    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_menu = StringVar()
    month_menu.set("Select Month")
    month_drop = OptionMenu(root, month_menu, *(month_list))
    month_drop.config(font="FixedText")
    month_drop["menu"].config(font="FixedText")
    month_drop.place(x=25, y=140)  # Place month filter dropdown

    # Label and button for selecting start date filter
    start_label = tk.Label(root, text="Select starting week day:", font="FixedInstruct")
    start_label.place(x=25, y=175)
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(start_btn))
    start_btn.place(x=45, y=195)

    # Filter button to apply filters on invoice list
    filter_btn = tk.Button(root,
                           text='Filter',
                           width=4,
                           height=1,
                           font="FixedText",
                           command=lambda: invoice_filter(client_menu, paid_var, month_menu, start_btn))
    filter_btn.place(x=70, y=260)


def view_outstanding():
    """
    Display the Outstanding section of the CRM GUI showing due and upcoming projects and invoices.

    This function clears the current GUI, resizes the window, and lays out widgets to present:
    - Overdue projects and invoices with details formatted for clarity.
    - Upcoming projects and invoices due within the next 3 days.
    - Visual indicators (color changes) on headers based on presence of overdue/upcoming items.

    The data is fetched from the database via helper methods, and dynamically inserted into listboxes.
    If no overdue or upcoming items exist, a green label indicates the absence of such entries.
    """

    clear_root()  # Clear any existing widgets from the root window
    root.geometry("803x610")  # Set window size to fit outstanding items layout

    # Button to navigate back to the home screen
    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # region Due/Overdue Section
    due_header_label = tk.Label(root, text="Due/Past Due", font="FixedHeader")
    due_header_label.pack()  # Pack header at the top

    project_due_label = tk.Label(root,
                                 text="Due/Overdue Projects",
                                 font="FixedInstruct")
    project_due_label.place(x=40, y=30)  # Label above the overdue projects listbox

    overdue_projects_info = db.create_overdue_projects()  # Fetch overdue projects data
    if overdue_projects_info:
        overdue_projects = Listbox(root, font="FixedView", width=90, height=6)
        for index, project in enumerate(overdue_projects_info):
            # Format due date and project details for readability
            formatted_due = datetime.strptime(project[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_project = f"{index + 1}) Due: {formatted_due} | Project: {project[1]} | Client: {project[2]} | Status: {project[3]}"
            overdue_projects.insert(index, formatted_project)
        overdue_projects.place(x=40, y=50)
    else:
        # Inform user there are no overdue projects
        no_project_label = tk.Label(root,
                                    text="No Overdue Projects",
                                    font="FixedText",
                                    fg='green')
        no_project_label.place(x=40, y=50)

    invoice_due_label = tk.Label(root,
                                 text="Due/Overdue Invoices",
                                 font="FixedInstruct")
    invoice_due_label.place(x=40, y=170)  # Label above overdue invoices listbox

    overdue_invoices_info = db.create_overdue_invoices()  # Fetch overdue invoices data
    if overdue_invoices_info:
        overdue_invoices = Listbox(root, font="FixedView", width=90, height=6)
        for index, invoice in enumerate(overdue_invoices_info):
            # Format invoice details with due date and amount
            formatted_due = datetime.strptime(invoice[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_invoice = f"{index + 1}) Due: {formatted_due} | Client: {invoice[1]} | Project: {invoice[2]} | Amount: ${invoice[3]}"
            overdue_invoices.insert(index, formatted_invoice)
        overdue_invoices.place(x=40, y=190)
    else:
        # Inform user there are no overdue invoices
        no_invoice_label = tk.Label(root,
                                    text="No Overdue Invoices",
                                    font="FixedText",
                                    fg='green')
        no_invoice_label.place(x=40, y=190)
    # endregion

    frame_line = tk.Frame(root, bg="gray60", width=800, height=2)
    frame_line.place(x=0, y=300)  # Horizontal separator between overdue and upcoming sections

    # region Upcoming Section
    up_header_label = tk.Label(root, text="Upcoming", font="FixedHeader")
    up_header_label.place(x=330, y=305)  # Upcoming section header

    project_due_label = tk.Label(root,
                                 text="Projects Due within 3 days",
                                 font="FixedInstruct")
    project_due_label.place(x=40, y=335)  # Label above upcoming projects listbox

    upcoming_projects_info = db.create_upcoming_projects()  # Fetch projects due soon
    if upcoming_projects_info:
        upcoming_projects = Listbox(root, font="FixedView", width=90, height=6)
        for index, project in enumerate(upcoming_projects_info):
            # Format each upcoming project similarly to overdue
            formatted_due = datetime.strptime(project[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_project = f"{index + 1}) Due: {formatted_due} | Project: {project[1]} | Client: {project[2]} | Status: {project[3]}"
            upcoming_projects.insert(index, formatted_project)
        upcoming_projects.place(x=40, y=355)
    else:
        # Inform user no upcoming projects soon
        no_up_project_label = tk.Label(root,
                                       text="No Upcoming Projects",
                                       font="FixedText",
                                       fg='green')
        no_up_project_label.place(x=40, y=355)

    invoice_due_label = tk.Label(root,
                                 text="Invoices due within 3 days",
                                 font="FixedInstruct")
    invoice_due_label.place(x=40, y=475)  # Label above upcoming invoices listbox

    upcoming_invoices_info = db.create_upcoming_invoices()  # Fetch invoices due soon
    if upcoming_invoices_info:
        upcoming_invoices = Listbox(root, font="FixedView", width=90, height=6)
        for index, invoice in enumerate(upcoming_invoices_info):
            # Format upcoming invoice details for display
            formatted_due = datetime.strptime(invoice[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            formatted_invoice = f"{index + 1}) Due: {formatted_due} | Client: {invoice[1]} | Project: {invoice[2]} | Amount: ${invoice[3]}"
            upcoming_invoices.insert(index, formatted_invoice)
        upcoming_invoices.place(x=40, y=495)
    else:
        # Inform user no upcoming invoices soon
        no_up_invoice_label = tk.Label(root,
                                       text="No Upcoming Invoices",
                                       font="FixedText",
                                       fg='green')
        no_up_invoice_label.place(x=40, y=495)
    # endregion

    # Change header text color to red if there are overdue projects/invoices, else black
    if overdue_invoices_info or overdue_projects_info:
        due_header_label.config(fg='darkred')
    else:
        due_header_label.config(fg='black')

    # Change header text color to red if there are upcoming projects/invoices, else black
    if upcoming_invoices_info or upcoming_projects_info:
        up_header_label.config(fg='darkred')
    else:
        up_header_label.config(fg='black')


# endregion


# Set the window title for the main application window
root.title("Endling Customer Relations Manager")

# Set the initial window size to 723x300 pixels
root.geometry("723x300")

# Disable window resizing to keep UI layout consistent
root.resizable(False, False)

# Bind the window close event to a custom handler to properly close the database connection
root.protocol("WM_DELETE_WINDOW", on_close)  # ensures DB connection closes cleanly on exit

# Instantiate the CRM database object for data access throughout the app
db = CRM_db()

# Display the initial home page UI when the app launches
display_home_page()

# Start the Tkinter event loop to listen for user interactions
root.mainloop()

