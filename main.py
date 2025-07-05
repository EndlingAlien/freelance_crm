import tkinter as tk
from tkinter import *
import pyglet
import tkinter.font as tkfont
from tkcalendar import Calendar
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Freelancer_CRM")

# root.maxsize(824, 480)
# root.minsize(723, 300)

root.geometry("723x300")
root.resizable(False, False)

# Load ufo image
image_path = "ufo_logo.png"
original_image = Image.open(image_path)
big_image = original_image.resize((280, 220))
logo_image = ImageTk.PhotoImage(big_image)

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

base_fixed = tkfont.nametofont("TkFixedFont")

fixed_font_title = tkfont.Font(root=root, name="FixedTitle", exists=False, **base_fixed.actual())
fixed_font_title.configure(size=40, underline=True)

fixed_font_text = tkfont.Font(root=root, name="FixedText", exists=False, **base_fixed.actual())
fixed_font_text.configure(size=17)

fixed_font_btn = tkfont.Font(root=root, name="FixedBtn", exists=False, **base_fixed.actual())
fixed_font_btn.configure(size=20)


# endregion TODO: ABOVE IS TEMPORARY ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Left old rel x/y in case still want a min and max window
def display_home_page():
    global logo_image

    welcome_label = tk.Label(root, text="EndlingCRM", font="FixedTitle")
    welcome_label.place(x=185, y=10)

    logo_label = tk.Label(root, image=logo_image)
    logo_label.image = logo_image
    logo_label.place(x=170, y=65)

    add_client_btn = tk.Button(root, text='Add Client', width=9, height=1, font="FixedBtn")
    add_client_btn.place(x=40, y=90)  # relx=.1, rely=.3

    add_project_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn")
    add_project_btn.place(x=40, y=150)  # relx=.1, rely=.5

    add_invoice_btn = tk.Button(root, text='Add invoice', width=9, height=1, font="FixedBtn")
    add_invoice_btn.place(x=40, y=210)  # relx=.1, rely=.7

    view_projects_btn = tk.Button(root, text='View/Edit Projects', width=15, height=1, font="FixedBtn")
    view_projects_btn.place(x=433, y=90)  # relx=.6, rely=.5

    view_invoices_btn = tk.Button(root, text='View/Edit Invoices', width=15, height=1, font="FixedBtn")
    view_invoices_btn.place(x=433, y=150)  # relx=.6, rely=.7

    view_outstanding_btn = tk.Button(root, text='View Outstanding', width=14, height=1, font="FixedBtn")
    view_outstanding_btn.place(x=439, y=210)  # relx=.6, rely=.3
def display_add_client_page():
    client_label = tk.Label(root, text="Client Menu", font="FixedTitle")
    client_label.pack(pady=10)

    # TODO: Dont let them click if any fields are empty
    add_client_btn = tk.Button(root, text='Add Client', width=9, height=1, font="FixedBtn")
    add_client_btn.place(x=433, y=147)  # relx=.6, rely=.49

    name_label = tk.Label(root, font="FixedText", text='Client Name:')
    name_label.place(x=72, y=120)  # relx=.1, rely=.4

    email_label = tk.Label(root, font="FixedText", text='Client Email:')
    email_label.place(x=72, y=150)  # relx=.1, rely=.5

    company_label = tk.Label(root, font="FixedText", text='Client Company:')
    company_label.place(x=36, y=180)  # relx=.05, rely=.6

    name_entry = tk.Entry(root, relief='groove')
    name_entry.place(x=195, y=117)  # relx=.27, rely=.39

    email_entry = tk.Entry(root, relief='groove')
    email_entry.place(x=195, y=147)  # relx=.27, rely=.49

    company_entry = tk.Entry(root, relief='groove')
    company_entry.place(x=195, y=177)  # relx=.27, rely=.59


def display_add_project_page():
    project_label = tk.Label(root, text="Project Menu", font="FixedTitle")
    project_label.pack(pady=10)

    # TODO: Replace client_list with clients in db, current list for testing
    client_list = ["test", "testing", "tested"]

    client_drop_label = tk.Label(root, font="FixedText", text='Client Name:')
    client_drop_label.place(x=50, y=80)

    client_menu = StringVar()
    client_menu.set("Select Client")
    client_drop = OptionMenu(root, client_menu, *(client_list))
    client_drop.config(font="FixedText")
    client_drop["menu"].config(font="FixedText")
    client_drop.place(x=185, y=80)

    project_title_label = tk.Label(root, font="FixedText", text='Project Title:')
    project_title_label.place(x=30, y=120)

    title_entry = tk.Entry(root, relief='groove')
    title_entry.place(x=185, y=120)

    project_start_label = tk.Label(root, font="FixedText", text='Start Date:')
    project_start_label.place(x=60, y=155)

    project_due_label = tk.Label(root, font="FixedText", text='Due Date:')
    project_due_label.place(x=80, y=190)

    # TODO: When user selects date on popup calender (create_calneder), change text to match date selected
    start_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText")
    start_btn.place(x=185, y=154)

    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText")
    due_btn.place(x=185, y=189)

    status_list = ["Started", "In Progress", "Finished"]

    status_drop_label = tk.Label(root, font="FixedText", text='Status:')
    status_drop_label.place(x=100, y=230)

    status_menu = StringVar()
    status_menu.set("Select Status")
    status_drop = OptionMenu(root, status_menu, *(status_list))
    status_drop.config(font="FixedText")
    status_drop["menu"].config(font="FixedText")
    status_drop.place(x=185, y=230)

    # TODO: Dont let them click if any fields are empty
    add_client_btn = tk.Button(root, text='Add Project', width=9, height=1, font="FixedBtn")
    add_client_btn.place(x=500, y=150)


# TODO: Create Calender for Start/Due date entry for Project Menu
def create_calender():
    # Outer frame acts as your visual border
    border_frame = tk.Frame(root, bg="black", bd=2, relief="solid")  # <- control border here
    border_frame.pack(pady=20)

    # Calendar inside the border frame
    cal = Calendar(
        border_frame,
        selectmode='day',
        year=2025,
        month=5,
        day=22,
        background='lightblue',
        foreground='red',
        headersforeground='black',
        normalforeground='gray20',
        weekendforeground='black',
        othermonthforeground='gray60',
        selectforeground='red',
    )
    cal.pack(padx=1, pady=1)  # pad to keep it inside the border

def display_add_invoice_page():

    invoice_label = tk.Label(root, text="Invoice Menu", font="FixedTitle")
    invoice_label.pack(pady=10)

    add_invoice_btn = tk.Button(root, text='Add Invoice', width=9, height=1, font="FixedBtn")
    add_invoice_btn.place(x=450, y=147)

    # TODO: Replace project_list with projects in db, current list for testing
    project_list = ["test", "testing", "tested"]

    project_drop_label = tk.Label(root, font="FixedText", text='Project Name:')
    project_drop_label.place(x=50, y=80)

    project_menu = StringVar()
    project_menu.set("Select Project")
    project_drop = OptionMenu(root, project_menu, *(project_list))
    project_drop.config(font="FixedText")
    project_drop["menu"].config(font="FixedText")
    project_drop.place(x=185, y=80)

    amount_label = tk.Label(root, font="FixedText", text='Invoice Amount:')
    amount_label.place(x=30, y=120)

    amount_entry = tk.Entry(root, relief='groove')
    amount_entry.place(x=185, y=120)
    amount_entry.insert(0, "$")

    project_due_label = tk.Label(root, font="FixedText", text='Due Date:')
    project_due_label.place(x=90, y=155)

    due_btn = tk.Button(root, text='Select Date', width=9, height=1, font="FixedText")
    due_btn.place(x=185, y=155)

    paid_label = tk.Label(root, text="Paid:", font="FixedText")
    paid_label.place(x=130, y=187)

    var = tk.IntVar()
    yes_r1 = Radiobutton(root, text="Yes", variable=var, value=1)
    yes_r1.place(x=194, y=188)
    no_r2 = Radiobutton(root, text="No", variable=var, value=2)
    no_r2.place(x=250, y=188)


#TODO:
# make a back to home page button in left corner
# Create pages for:
# View Outstanding = fixed filtering/view table for only the stuff that needs immediate action, pulled from both invoices and projects
# View/edit Projects = Display all projects [by filtering for: status, due date, start date, client] user-driven
# View/edit Invoices = Display all invoices [by filter for: due this month/week, unpaid vs paid] user-driven


display_home_page()

root.mainloop()
