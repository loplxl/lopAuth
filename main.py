import customtkinter
from json import load,dump
from os.path import exists # <-- only for config file ofc
from time import time
from os import mkdir
if not exists("lopAuth Data/"):
    mkdir("lopAuth Data")
createData = { 
    "config.json": {
        "highTransparency": True,
        "theme": "mauve",
        "passwordMaskCharacter": "•",
        "passwordMaskEnabled": True
    },
    "data.json": {
        "data": []
    },
    "theme.json": {
        "CTk": {
            "fg_color": ["gray92", "#181825"]
        },
        "CTkToplevel": {
            "fg_color": ["gray92", "#181825"]
        },
        "CTkFrame": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": ["#ffffff", "#1e1e2e"],
            "top_fg_color": ["gray81", "gray20"],
            "border_color": ["gray65", "gray28"]
        },
        "CTkButton": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": ["#2CC985", "#313244"],
            "hover_color": ["#0C955A", "#262739"],
            "border_color": ["#3E454A", "#313244"],
            "text_color": ["gray98", "#DCE4EE"],
            "text_color_disabled": ["gray78", "gray68"]
        },
        "CTkLabel": {
            "corner_radius": 0,
            "fg_color": "transparent",
            "text_color": ["gray10", "#DCE4EE"]
        },
        "CTkEntry": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": ["#343638", "#343638"],
            "border_color": ["#343638", "#343638"],
            "text_color":["gray10", "#DCE4EE"],
            "placeholder_text_color": ["gray52", "gray62"]
        },
        "CTkCheckBox": {
            "corner_radius": 6,
            "border_width": 3,
            "fg_color": ["#2CC985", "#313244"],
            "border_color": ["#3E454A", "#949A9F"],
            "hover_color": ["#0C955A", "#313244"],
            "checkmark_color": ["#DCE4EE", "gray90"],
            "text_color": ["gray10", "#DCE4EE"],
            "text_color_disabled": ["gray60", "gray45"]
        },
        "CTkOptionMenu": {
            "corner_radius": 6,
            "fg_color": ["#2cbe79", "#202133"],
            "button_color": ["#0C955A", "#1e1e2e"],
            "button_hover_color": ["#0b6e3d", "#313244"],
            "text_color": ["gray98", "#DCE4EE"],
            "text_color_disabled": ["gray78", "gray68"]
        },
        "CTkScrollbar": {
            "corner_radius": 1000,
            "border_spacing": 4,
            "fg_color": "transparent",
            "button_color": ["gray55", "gray41"],
            "button_hover_color": ["gray40", "gray53"]
        },
        "CTkScrollableFrame": {
            "label_fg_color": ["gray78", "gray23"]
        },
        "DropdownMenu": {
            "fg_color": ["gray90", "gray20"],
            "hover_color": ["gray75", "gray28"],
            "text_color": ["gray10", "gray90"]
        },
        "CTkFont": {
            "macOS": {
            "family": "SF Display",
            "size": 13,
            "weight": "normal"
            },
            "Windows": {
            "family": "Roboto",
            "size": 13,
            "weight": "normal"
            },
            "Linux": {
            "family": "Roboto",
            "size": 13,
            "weight": "normal"
            }
        }
    }
}

def fileCreate(name: str):
    name = "lopAuth Data/" + name
    if not exists(name):
        data = createData[name[13:]]
        open(name,'x').close()
        with open(name,'w') as f:
            dump(data,f,indent=4)
    else:
        with open(name,'r') as f:
            data = load(f)
    return data
fileCreate("theme.json")
customtkinter.set_default_color_theme("lopAuth Data/theme.json")


#if not exists("assets/"):






from codeframe import codeFrame
from gui import sidebar

class App(customtkinter.CTk):
    def titleUpdater(self,mainTitle:str):
        time_remaining = 30 - (int(time() % 30))
        self.title(f"{mainTitle} ({time_remaining}s)")
        self.after(1000, lambda: self.titleUpdater(mainTitle))
    def __init__(self):
        self.config = fileCreate("config.json")
        self.userdata = fileCreate("data.json")
        super().__init__()
        
        self.geometry("400x200")
        mainTitle = "lopAuth"
        self.title(mainTitle)

        self.wm_attributes("-topmost", True)
        self.sidebarFrame = sidebar(master=self,width=100)
        self.sidebarFrame.pack(side="left",padx=(10,0),pady=10)
        self.codesFrame = codeFrame(master=self)
        self.codesFrame.pack(fill="both",expand=True,padx=(5,10),pady=10)

        self.after(16,lambda: self.attributes("-topmost", False))
        self.titleUpdater(mainTitle)
        

app = App()
app.mainloop()