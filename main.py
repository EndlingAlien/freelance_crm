import tkinter as tk
import re
import tkinter.font as tkfont
from sql_db import TestDB
from tkinter import *
from tkcalendar import Calendar
from datetime import date, datetime
from PIL import Image, ImageTk
from tkinter import messagebox

root = tk.Tk()
# region Fonts
base_fixed = tkfont.nametofont("TkFixedFont")

fixed_font_title = tkfont.Font(root=root, name="FixedTitle", exists=False, **base_fixed.actual())
fixed_font_title.configure(size=40, underline=True)

fixed_font_header = tkfont.Font(root=root, name="FixedHeader", exists=False, **base_fixed.actual())
fixed_font_header.configure(size=20, underline=True)

fixed_font_text = tkfont.Font(root=root, name="FixedText", exists=False, **base_fixed.actual())
fixed_font_text.configure(size=17)

fixed_font_instruct = tkfont.Font(root=root, name="FixedInstruct", exists=False, **base_fixed.actual())
fixed_font_instruct.configure(size=12)

fixed_font_btn = tkfont.Font(root=root, name="FixedBtn", exists=False, **base_fixed.actual())
fixed_font_btn.configure(size=20)


# endregion

# region Button Functions
def back_to_home():
    display_home_page()


def on_close():
    db.conn.commit()
    db.conn.close()
    root.destroy()


def clear_root():
    for widget in root.winfo_children():
        widget.destroy()


def create_calender(btn):
    today = date.today()
    border_frame = tk.Frame(root, bg="black", bd=2, relief="solid")
    border_frame.pack(pady=20)

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
        selected_date = cal.get_date()
        cal.destroy()
        border_frame.destroy()
        confirm_date_btn.destroy()
        date_obj = datetime.strptime(selected_date, "%m/%d/%y")  # Convert to datetime
        formatted_date = date_obj.strftime("%m-%d-%Y")  # Reformat
        btn.config(text=formatted_date)  # Always consistent format

    confirm_date_btn = tk.Button(root, text='Confirm', font="FixedBtn", command=collect_date_and_destroy)
    confirm_date_btn.pack()

#endregion

# region Limit text in dropdown display
def limit_text(text, max_length=18):
    return text if len(text) <= max_length else text[:max_length - 6] + "..."


def on_select(dropdown, value):
    trimmed = limit_text(value)
    dropdown.set(trimmed)


# endregion

#region DB Functions

def get_client_info(client_name, client_email, client_company):
    global db
    name = client_name.get().title().strip()
    company = client_company.get().strip()
    email = client_email.get().strip()
    if check_client_info(client_name, client_email, client_company):
        if db.create_client(name, email, company):
            client_name.delete(0, tk.END)
            client_email.delete(0, tk.END)
            client_company.delete(0, tk.END)

            confirm_label = tk.Label(root, text="Saved Client", font="FixedText", fg='green')
            confirm_label.place(x=315, y=225)
            root.after(1000, confirm_label.destroy)
        else:
            messagebox.showerror("CLIENT ERROR",
                                 "Was not able to upload Client into database. Client either exists or information entered incorrectly.")


def check_client_info(client_name, client_email, client_company):
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

    return messagebox.askyesno("Check Client Info", f"The information you've entered:\n"
                                                    f"Client Name: {client_name}\n"
                                                    f"Client Email: {client_email}\n"
                                                    f"Client Company: {client_company}\n"
                                                    f"Is this correct?")


def get_project_info(client_name, project_title, start_date, due_date, status):
    global db

    if check_project_info(client_name, project_title, start_date, due_date, status):
        client_name_text = client_name.get().title().strip()
        project_title_text = project_title.get().strip()
        start_date_obj = datetime.strptime(start_date.cget("text"), "%m-%d-%Y").date()
        due_date_obj = datetime.strptime(due_date.cget("text"), "%m-%d-%Y").date()
        status_text = status.get()
        if db.create_project(client_name_text, project_title_text, start_date_obj, due_date_obj, status_text):
            client_name.set("Select Client")
            project_title.delete(0, tk.END)
            status.set("Select Status")
            start_date.config(text="Select Date")
            due_date.config(text="Select Date")
            confirm_label = tk.Label(root, text="Saved Project", font="FixedText", fg='green')
            confirm_label.place(x=295, y=225)
            root.after(1000, confirm_label.destroy)
        else:
            messagebox.showerror("PROJECT ERROR",
                                 "Was not able to upload Project into database.")


def check_project_info(client_name, project_title, start_date, due_date, status):
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
        return messagebox.askyesno("Check Project Info", f"The information you've entered:\n"
                                                         f"Client Name: {client_name}\n"
                                                         f"Project Title: {project_title}\n"
                                                         f"Project Status: {status}\n"
                                                         f"Start Date: {start_date.cget('text')}\n"
                                                         f"Due Date: {due_date.cget('text')}\n"
                                                         f"Is this correct?")

    return False


def get_invoice_info(project_name, amount, due_date, radio_var):
    global db
    due_date_obj = datetime.strptime(due_date.cget("text"), "%m-%d-%Y").date()
    result, value = check_invoice_info(amount, due_date, project_name, radio_var)
    if result:
        if db.create_invoice(project_name.get(), value, due_date_obj, radio_var.get()):
            project_name.set("Select Project")
            amount.delete(1, tk.END)
            due_date.config(text="Select Date")
            radio_var.set(0)
            confirm_label = tk.Label(root, text="Saved Invoice", font="FixedText", fg='green')
            confirm_label.place(x=285, y=225)
            root.after(1000, confirm_label.destroy)
        else:
            messagebox.showerror("INVOICE ERROR",
                                 "Was not able to upload Invoice into database. Have you already added one for this project?")


def check_invoice_info(amount, due_date, project_name, radio_var):
    valid_info = {
        "amount": False,
        "project_name": False,
        "due_date": False
    }
    value, result = check_amount_value(amount)

    if result:
        valid_info['amount'] = True

    if due_date.cget('text') in ('Select Date', ''):
        messagebox.showwarning("Invalid Due Date", "User didn't select Due Date.")
        return False
    else:
        valid_info['due_date'] = True

    if project_name in (None, '', 'Select Project'):
        messagebox.showwarning("Invalid project Option", "User didn't select a Project.")
        return False
    else:
        valid_info['project_name'] = True

    if radio_var.get() == 0:
        radio = 'No'
    else:
        radio = 'Yes'

    if valid_info:
        return messagebox.askyesno("Check Client Info", f"The information you've entered:\n"
                                                        f"Project Name: {project_name.get()}\n"
                                                        f"Invoice Amount: {amount.get()}\n"
                                                        f"Due Date: {due_date.cget('text')}\n"
                                                        f"Paid: {radio}\n"
                                                        f"Is this correct?"), value


def check_amount_value(entry):
    value = entry.get().strip("$")
    try:
        value = float(value)
        value = round(value, 2)
        print("Valid float:", value)
        print("Type:", type(value))
        return value, True
    except ValueError:
        print("Invalid input — not a float.")
        return None
# endregion


# region GUI
def display_home_page():
    clear_root()
    root.geometry("723x300")  # For if user goes to Outstanding

    title_label = tk.Label(root, text="EndlingCRM", font="FixedTitle")
    title_label.place(x=185, y=10)

    # region Logo
    image_path = "ufo_logo.png"
    original_image = Image.open(image_path)
    big_image = original_image.resize((280, 220))
    logo_image = ImageTk.PhotoImage(big_image)
    logo_label = tk.Label(root, image=logo_image)
    logo_label.image = logo_image
    logo_label.place(x=170, y=65)
    # endregion

    add_client_btn = tk.Button(root, text='Add Client', width=9, height=1, font="FixedBtn", command=display_add_client_page)
    add_client_btn.place(x=40, y=90)

    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn", command=display_add_project_page)
    add_project_btn.place(x=40, y=150)

    add_invoice_btn = tk.Button(root, text='Add Invoice', width=9, height=1, font="FixedBtn", command=display_add_invoice_page)
    add_invoice_btn.place(x=40, y=210)

    view_projects_btn = tk.Button(root, text='View/Edit Projects', width=15, height=1, font="FixedBtn", command=view_projects)
    view_projects_btn.place(x=433, y=90)

    view_invoices_btn = tk.Button(root, text='View/Edit Invoices', width=15, height=1, font="FixedBtn", command=view_invoices)
    view_invoices_btn.place(x=433, y=150)

    view_outstanding_btn = tk.Button(root, text='View Outstanding', width=14, height=1, font="FixedBtn", command=view_outstanding)
    view_outstanding_btn.place(x=439, y=210)


def display_add_client_page():
    clear_root()
    title_label = tk.Label(root, text="Client Menu", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    name_label = tk.Label(root, font="FixedText", text='Client Name:')
    name_label.place(x=185, y=93)
    name_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    name_frame.place(x=320, y=92)
    name_entry = tk.Entry(root, bd=0)
    name_entry.place(x=323, y=95)

    email_label = tk.Label(root, font="FixedText", text='Client Email:')
    email_label.place(x=178, y=126)
    email_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    email_frame.place(x=320, y=125)
    email_entry = tk.Entry(root, bd=0)
    email_entry.place(x=323, y=128)

    company_label = tk.Label(root, font="FixedText", text='Client Company:')
    company_label.place(x=155, y=157)
    company_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    company_frame.place(x=320, y=158)
    company_entry = tk.Entry(root, bd=0)
    company_entry.place(x=323, y=161)

    add_client_btn = tk.Button(root,
                               text='Add Client',
                               width=9,
                               height=1,
                               font="FixedBtn",
                               command=lambda: get_client_info(name_entry, email_entry, company_entry))
    add_client_btn.place(x=300, y=250)


def display_add_project_page():
    global db
    clear_root()
    title_label = tk.Label(root, text="Project Menu", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    client_list = db.get_list_of_clients()
    client_drop_label = tk.Label(root, font="FixedText", text='Client Name:')
    client_drop_label.place(x=185, y=60)
    client_menu = StringVar()
    client_menu.set("Select Client")
    client_drop = OptionMenu(root, client_menu, *client_list, command=lambda val: on_select(client_menu, val))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=320, y=60)

    project_title_label = tk.Label(root, font="FixedText", text='Project Title:')
    project_title_label.place(x=185, y=96)
    project_title_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    project_title_frame.place(x=340, y=95)
    project_title_entry = tk.Entry(root, bd=0)
    project_title_entry.place(x=343, y=98)

    start_label = tk.Label(root, font="FixedText", text='Start Date:')
    start_label.place(x=220, y=130)
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(start_btn))
    start_btn.place(x=345, y=129)

    due_label = tk.Label(root, font="FixedText", text='Due Date:')
    due_label.place(x=240, y=165)
    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(due_btn))
    due_btn.place(x=345, y=164)

    status_list = ["Not Started", "Started", "In Progress", "Testing", "Finished"]
    status_drop_label = tk.Label(root, font="FixedText", text='Status:')
    status_drop_label.place(x=240, y=200)
    status_menu = StringVar()
    status_menu.set("Select Status")
    status_drop = OptionMenu(root, status_menu, *(status_list))
    status_drop.config(font="FixedText")
    status_drop["menu"].config(font="FixedText")
    status_drop.place(x=325, y=200)

    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn",
                                command=lambda: get_project_info(client_menu, project_title_entry, start_btn, due_btn, status_menu))
    add_project_btn.place(x=285, y=250)


def display_add_invoice_page():
    global db
    clear_root()
    title_label = tk.Label(root, text="Invoice Menu", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    project_list = db.get_list_of_projects()
    project_drop_label = tk.Label(root, font="FixedText", text='Project Name:')
    project_drop_label.place(x=185, y=80)
    project_menu = StringVar()
    project_menu.set("Select Project")
    project_drop = OptionMenu(root, project_menu, *project_list, command=lambda val: on_select(project_menu, val))
    project_drop.config(font="FixedText")
    project_drop["menu"].config(font="FixedText")
    project_drop.place(x=320, y=80)

    amount_label = tk.Label(root, font="FixedText", text='Invoice Amount:')
    amount_label.place(x=183, y=121)
    amount_frame = tk.Frame(root, bg='gray60', width=194, height=30)
    amount_frame.place(x=340, y=120)
    amount_entry = tk.Entry(root, bd=0)
    amount_entry.place(x=343, y=123)
    amount_entry.insert(0, "$")

    due_label = tk.Label(root, font="FixedText", text='Due Date:')
    due_label.place(x=248, y=155)
    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(due_btn))
    due_btn.place(x=340, y=155)

    paid_label = tk.Label(root, text="Paid:", font="FixedText")
    paid_label.place(x=280, y=187)
    radio_var = tk.IntVar()
    yes_r1 = Radiobutton(root, text="Yes", variable=radio_var, value=1)
    yes_r1.place(x=344, y=189)
    no_r2 = Radiobutton(root, text="No", variable=radio_var, value=0)
    no_r2.place(x=400, y=189)

    add_invoice_btn = tk.Button(root, text='Add Invoice', width=9, height=1, font="FixedBtn",
                                command=lambda: get_invoice_info(project_menu, amount_entry, due_btn, radio_var))
    add_invoice_btn.place(x=280, y=250)


#TODO: Finish DB logic starting here
def view_projects():
    clear_root()
    title_label = tk.Label(root, text="Projects", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # region Aesthetic
    instruct_label = tk.Label(root,
                              text="Fill in the fields you'd like to filter by, otherwise press filter to display all projects.",
                              font="FixedInstruct")
    instruct_label.place(x=40, y=50)
    filter_line_side = tk.Frame(bg="gray60", width=2, height=240)
    filter_line_side.place(x=223, y=70)
    filter_line_top = tk.Frame(bg="gray60", width=800, height=2)
    filter_line_top.place(x=0, y=70)
    # endregion

    client_list = db.get_list_of_clients()
    client_menu = StringVar()
    client_menu.set("Select Client")
    client_drop = OptionMenu(root, client_menu, *client_list, command=lambda val: on_select(client_menu, val))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=25, y=80)

    status_list = ["Not Started", "Started", "In Progress", "Testing", "Finished"]
    status_menu = StringVar()
    status_menu.set("Select Status")
    status_drop = OptionMenu(root, status_menu, *(status_list))
    status_drop.config(font="FixedText")
    status_drop["menu"].config(font="FixedText")
    status_drop.place(x=25, y=110)

    start_label = tk.Label(root, text="Start Date:", font="FixedInstruct")
    start_label.place(x=75, y=140)
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(start_btn))
    start_btn.place(x=45, y=155)

    due_label = tk.Label(root, text="Due Date:", font="FixedInstruct")
    due_label.place(x=80, y=190)
    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(due_btn))
    due_btn.place(x=45, y=205)

    # TODO: When user selects btn, will check above filters to see if None, filter based off above
    filter_btn = tk.Button(root, text='Filter', width=4, height=1, font="FixedText")
    filter_btn.place(x=70, y=260)


def view_invoices():
    clear_root()
    title_label = tk.Label(root, text="Invoices", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # region Aesthetic
    instruct_label = tk.Label(root,
                              text="Fill in the fields you'd like to filter by, otherwise press filter to display all Invoices.",
                              font="FixedInstruct")
    instruct_label.place(x=40, y=50)
    filter_line_side = tk.Frame(bg="gray60", width=2, height=240)
    filter_line_side.place(x=223, y=70)
    filter_line_top = tk.Frame(bg="gray60", width=800, height=2)
    filter_line_top.place(x=0, y=70)
    # endregion

    client_list = db.get_list_of_clients()
    client_menu = StringVar()
    client_menu.set("Select Client")
    client_drop = OptionMenu(root, client_menu, *client_list, command=lambda val: on_select(client_menu, val))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=25, y=80)

    paid_label = tk.Label(root, text="Paid:", font="FixedText")
    paid_label.place(x=25, y=110)
    var = tk.IntVar()
    yes_r1 = Radiobutton(root, text="Yes", variable=var, value=1)
    yes_r1.place(x=89, y=111)
    no_r2 = Radiobutton(root, text="No", variable=var, value=2)
    no_r2.place(x=145, y=111)

    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_menu = StringVar()
    month_menu.set("Select Month")
    month_drop = OptionMenu(root, month_menu, *(month_list))
    month_drop.config(font="FixedText")
    month_drop["menu"].config(font="FixedText")
    month_drop.place(x=25, y=140)

    # TODO: Day user selected + 6 days
    start_label = tk.Label(root, text="Select starting week day:", font="FixedInstruct")
    start_label.place(x=25, y=175)
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText", command=lambda: create_calender(start_btn))
    start_btn.place(x=45, y=195)

    # TODO: When user selects btn, will check above filters to see if None, filter based off above
    filter_btn = tk.Button(root, text='Filter', width=4, height=1, font="FixedText")
    filter_btn.place(x=70, y=260)


def view_outstanding():
    clear_root()
    # TODO: In this function, use views for tables below, will go where placeholder frames are
    root.geometry("723x610")

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # region Due/Overdue Section
    due_header_label = tk.Label(root, text="Due/Past Due", font="FixedHeader")
    due_header_label.pack()
    project_due_label = tk.Label(root,
                                 text="Due/Overdue Projects",
                                 font="FixedInstruct")
    project_due_label.place(x=40, y=30)

    invoice_due_label = tk.Label(root,
                                 text="Due/Overdue Invoices",
                                 font="FixedInstruct")
    invoice_due_label.place(x=40, y=170)
    # endregion

    frame_line = tk.Frame(bg="gray60", width=800, height=2)
    frame_line.place(x=0, y=300)

    # region Upcoming Section
    due_header_label = tk.Label(root, text="Upcoming", font="FixedHeader")
    due_header_label.place(x=300, y=305)
    project_due_label = tk.Label(root,
                                 text="Projects Due within 3 days",
                                 font="FixedInstruct")
    project_due_label.place(x=40, y=335)

    invoice_due_label = tk.Label(root,
                                 text="Invoices due within 3 days",
                                 font="FixedInstruct")
    invoice_due_label.place(x=40, y=475)
    # endregion

    # region Placeholder frames for future views
    # TODO: Example lines is info we will pull/create view table with
    overdue_project_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    overdue_project_frame.place(x=40, y=50)
    example_line_overdue_project = tk.Label(overdue_project_frame,
                                            text="1) Month/Day/Year - Project_Status - Project_Name - Client_Name",
                                            bg='gray40',
                                            font="FixedText")
    example_line_overdue_project.place(x=0, y=0)

    overdue_invoice_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    overdue_invoice_frame.place(x=40, y=190)
    example_line_overdue_invoice = tk.Label(overdue_invoice_frame,
                                            text="1) Month/Day/Year - Client_Name - Project_Name - Amount_Due",
                                            bg='gray40',
                                            font="FixedText")
    example_line_overdue_invoice.place(x=0, y=0)

    upcoming_project_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    upcoming_project_frame.place(x=40, y=355)
    example_line_upcoming_project = tk.Label(upcoming_project_frame,
                                             text="1) Month/Day/Year - Project_Status - Project_Name - Client_Name",
                                             bg='gray40',
                                             font="FixedText")
    example_line_upcoming_project.place(x=0, y=0)

    upcoming_invoice_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    upcoming_invoice_frame.place(x=40, y=495)
    example_line_upcoming_invoice = tk.Label(upcoming_invoice_frame,
                                             text="1) Month/Day/Year - Client_Name - Project_Name - Amount_Due",
                                             bg='gray40',
                                             font="FixedText")
    example_line_upcoming_invoice.place(x=0, y=0)
    # endregion


# endregion


root.title("Freelancer_CRM")
root.geometry("723x300")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_close)  # closes db connection so no need to keep reopening

db = TestDB()
display_home_page()

root.mainloop()
