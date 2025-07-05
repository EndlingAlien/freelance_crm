import tkinter as tk
from tkinter import *
import pyglet
import tkinter.font as tkfont
from tkcalendar import Calendar
from datetime import date
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Freelancer_CRM")
root.geometry("723x300")
root.resizable(False, False)

# region TODO: TEMPORARY - TESTING TO SEE IF FONT WORKS ON DIFFERENT DEVICES
preferred_font = "PT Mono"
fallback_font = "TkFixedFont"

pyglet.font.add_file("Alien.ttf")

def get_available_font(preferred, fallback):
    try:
        # Attempt to create a font using the preferred family
        test_font = tkfont.Font(family=preferred, size=12)
        return (preferred, 12)
    except tk.TclError:
        # If it fails, use fallback
        return (fallback, 12)


font_choice = get_available_font(preferred_font, fallback_font)
print(f'font in use: {font_choice[0]}')
# endregion TODO: ABOVE IS TEMPORARY ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#region Fonts
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
#endregion

# region Button Functions
def back_to_home():
    display_home_page()

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
        btn.config(text=selected_date)

    confirm_date_btn = tk.Button(root, text='Confirm', font="FixedBtn", command=collect_date_and_destroy)
    confirm_date_btn.pack()

#region Limit text in dropdown display
def limit_text(text, max_length=18):
    return text if len(text) <= max_length else text[:max_length - 6] + "..."

def on_select(dropdown, value):
    trimmed = limit_text(value)
    dropdown.set(trimmed)
    #TODO: May use this for future db value or put - full_selection = {"value": None} - inside funcs that need it
    print("Full selected value:", value)
#endregion

def check_amount_value(entry):
    value = entry.get().strip("$")
    try:
        value = float(value)
        value = round(value, 2)
        print("Valid float:", value)
        print("Type:", type(value))
        return value
    except ValueError:
        print("Invalid input — not a float.")
        return None


#endregion


#region GUI
def display_home_page():
    clear_root()
    root.geometry("723x300")  # For if user goes to Outstanding

    title_label = tk.Label(root, text="EndlingCRM", font="FixedTitle")
    title_label.place(x=185, y=10)

    #region Logo
    image_path = "ufo_logo.png"
    original_image = Image.open(image_path)
    big_image = original_image.resize((280, 220))
    logo_image = ImageTk.PhotoImage(big_image)
    logo_label = tk.Label(root, image=logo_image)
    logo_label.image = logo_image
    logo_label.place(x=170, y=65)
    #endregion

    add_client_btn = tk.Button(root, text='Add Client', width=9, height=1, font="FixedBtn", command=display_add_client_page)
    add_client_btn.place(x=40, y=90)

    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn", command=display_add_project_page)
    add_project_btn.place(x=40, y=150)

    add_invoice_btn = tk.Button(root, text='Add invoice', width=9, height=1, font="FixedBtn",command=display_add_invoice_page)
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

    # TODO: Add VALID client to db, check all fields first, use ACID Transaction
    add_client_btn = tk.Button(root, text='Add Client', width=9, height=1, font="FixedBtn")
    add_client_btn.place(x=300, y=250)

def display_add_project_page():
    clear_root()
    title_label = tk.Label(root, text="Project Menu", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # TODO: Get clients from db
    client_list = ["test", "testing", "Its the longest name ive ever seen"]
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

    # TODO: Add VALID project to db, check all fields first, use ACID Transaction
    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn")
    add_project_btn.place(x=285, y=250)

def display_add_invoice_page():
    clear_root()
    title_label = tk.Label(root, text="Invoice Menu", font="FixedTitle")
    title_label.pack()

    home_btn = tk.Button(root, text='Back to Home', width=10, height=1, font="FixedInstruct", command=back_to_home)
    home_btn.place(x=0, y=0)

    # TODO: Get projects from db
    project_list = ["What, could it be, another long name", "testing", "tested"]
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
    var = tk.IntVar()
    yes_r1 = Radiobutton(root, text="Yes", variable=var, value=1)
    yes_r1.place(x=344, y=189)
    no_r2 = Radiobutton(root, text="No", variable=var, value=2)
    no_r2.place(x=400, y=189)

    # TODO: Add VALID invoice to db, check all fields first, use ACID Transaction - command currently checks validity of entry amount
    add_invoice_btn = tk.Button(root, text='Add Invoice', width=9, height=1, font="FixedBtn", command=lambda: check_amount_value(amount_entry))
    add_invoice_btn.place(x=280, y=250)

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

    # TODO: Get clients from db
    client_list = ["test", "A Really Long Name that might Exist", "tested"]
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

    # TODO: Get clients from db
    client_list = ["test", "Another super long name oh my", "tested"]
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
    #TODO: In this function, use views for tables below, will go where placeholder frames are
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
    #endregion

    frame_line = tk.Frame(bg="gray60", width=800, height=2)
    frame_line.place(x=0, y=300)

    #region Upcoming Section
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
    #endregion

    #region Placeholder frames for future views
    #TODO: Example lines is info we will pull/create view table with
    overdue_project_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    overdue_project_frame.place(x=40, y=50)
    example_line_overdue_project = tk.Label(overdue_project_frame, text="1) Month/Day/Year - Project_Status - Project_Name - Client_Name", bg='gray40', font="FixedText")
    example_line_overdue_project.place(x=0, y=0)

    overdue_invoice_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    overdue_invoice_frame.place(x=40, y=190)
    example_line_overdue_invoice = tk.Label(overdue_invoice_frame, text="1) Month/Day/Year - Client_Name - Project_Name - Amount_Due", bg='gray40', font="FixedText")
    example_line_overdue_invoice.place(x=0, y=0)

    upcoming_project_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    upcoming_project_frame.place(x=40, y=355)
    example_line_upcoming_project = tk.Label(upcoming_project_frame, text="1) Month/Day/Year - Project_Status - Project_Name - Client_Name", bg='gray40', font="FixedText")
    example_line_upcoming_project.place(x=0, y=0)

    upcoming_invoice_frame = tk.Frame(root, width=650, height=100, bg='gray40')
    upcoming_invoice_frame.place(x=40, y=495)
    example_line_upcoming_invoice = tk.Label(upcoming_invoice_frame, text="1) Month/Day/Year - Client_Name - Project_Name - Amount_Due", bg='gray40', font="FixedText")
    example_line_upcoming_invoice.place(x=0, y=0)
    #endregion

#endregion


display_add_invoice_page()

root.mainloop()
