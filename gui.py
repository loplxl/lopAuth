import customtkinter
from PIL import Image, ImageEnhance
from json import dump
from CTkMessagebox import CTkMessagebox
from PIL import Image
from utils import scanClipboard,entry2fa,dataWrite,hashedPasswordGen,resource_path
def darken(img):
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    return ImageEnhance.Brightness(img).enhance(0.5)
def saveConfig(data,filename: str,master=None): #serves to save data and reload icons
    with open("lopAuth Data/" + filename,'w') as f:
        dump(data,f,indent=4)
    if filename == "config.json":
        master.reload_icons()

#inefficient - could migrate each to their own class
class ToplevelGUI(customtkinter.CTkToplevel):
    #callbacks for settings menu
    def highTransparencyToggle(self):
        self.app.config["highTransparency"] = self.highTransparency.get()
        saveConfig(master=self.master, data=self.app.config, filename="config.json")

    def optionmenu_callback(self, choice):
        self.app.config["theme"] = choice.lower()
        saveConfig(master=self.master, data=self.app.config, filename="config.json")

    def passwordMaskEnabledToggle(self):
        self.app.config["passwordMaskEnabled"] = self.passwordMaskEnabled.get()
        saveConfig(master=self.master, data=self.app.config, filename="config.json")

    def passwordMaskCharacterChanged(self, *args):
        maskChar = self.passwordMaskCharacter.get()
        if len(maskChar) > 1:
            self.passwordMaskCharacter.set(maskChar[0]) # <-- override any other user input (cant mask more than 1 char)
        self.app.config["passwordMaskCharacter"] = self.passwordMaskCharacter.get()
        saveConfig(master=self.master, data=self.app.config, filename="config.json")
    

    def on_close(self):
        activewindows = self.master.toplevel_windows
        if (str(self.__dict__['master']) == ".!sidebar") and (self in activewindows.values()):
            # find key that points to this window
            for key,win in list(activewindows.items()):
                if win == self:
                    del self.master.toplevel_windows[key]
                    break
        self.destroy()
    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name")
        self.app = kwargs.pop("app")
        super().__init__(*args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.on_close) # <-- allows removal from list when toplevelgui closed
        

        if name == "Settings":
            self.geometry("450x250")
            self.title(name)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
            self.grid_columnconfigure(2, weight=1)
            row = 0
            # ----- highTransparency -----
            self.highTransparency = customtkinter.BooleanVar(value=self.app.config["highTransparency"])
            highTransparencyCheckbox = customtkinter.CTkCheckBox(self,text="High Transparency Buttons",command=self.highTransparencyToggle,variable=self.highTransparency,onvalue=True,offvalue=False)
            highTransparencyCheckbox.grid(row=row, column=1, columnspan=2,pady=(20, 10), sticky="w")
            # ----------------------------
            row += 1
            # ----- theme -----
            optionmenu_var = customtkinter.StringVar(value="Colour Theme")
            optionmenu = customtkinter.CTkOptionMenu(self,values=["Yellow", "Blue", "Green", "Mauve"],command=self.optionmenu_callback,variable=optionmenu_var)
            optionmenu.grid(row=row, column=1, columnspan=2,pady=(10, 10), sticky="w")
            # -----------------
            row += 1
            # ------ passwordMaskEnabled -----
            self.passwordMaskEnabled = customtkinter.BooleanVar(value=self.app.config["passwordMaskEnabled"])
            passwordMaskEnabledCheckbox = customtkinter.CTkCheckBox(self,text="Password Masking (restart needed)",command=self.passwordMaskEnabledToggle,variable=self.passwordMaskEnabled,onvalue=True,offvalue=False)
            passwordMaskEnabledCheckbox.grid(row=row, column=1, columnspan=2,pady=(10, 10), sticky="w")
            # --------------------------------
            row += 1
            # ------ passwordMaskCharacter -----
            self.passwordMaskCharacter = customtkinter.StringVar(value=self.app.config["passwordMaskCharacter"])
            passwordMaskCharacterLabel = customtkinter.CTkLabel(self,text="Password Mask Character (restart needed):")
            passwordMaskCharacterLabel.grid(row=row, column=1,sticky="e", padx=(0, 10))
            #frame to align label2 and entry next to eachother
            passwordMaskCharacterEntryFrame = customtkinter.CTkFrame(self,fg_color="transparent",border_width=0,corner_radius=0)
            passwordMaskCharacterEntryFrame.grid(row=row, column=2, sticky="w")
            passwordMaskCharacterEntry = customtkinter.CTkEntry(passwordMaskCharacterEntryFrame,width=60,textvariable=self.passwordMaskCharacter,justify="center")
            passwordMaskCharacterEntry.pack(side="left")
            passwordMaskCharacterLabel2 = customtkinter.CTkLabel(passwordMaskCharacterEntryFrame,text="(empty: • )")
            passwordMaskCharacterLabel2.pack(side="left",padx=(8,0))
            # ----------------------------------

            #detection for writing in box - used to limit char + update config dynamically
            self.passwordMaskCharacter.trace_add("write",self.passwordMaskCharacterChanged)
        elif name == "lopAuth Setup":
            # setup needed - hash password
            self.title("lopAuth Setup")
            self.geometry("300x290")

            self.setupFrame = customtkinter.CTkFrame(self,corner_radius=10)
            self.setupFrame.pack(padx=20, pady=20, fill="both", expand=True)

            self.setupLabel = customtkinter.CTkLabel(self.setupFrame,text="It seems like its your first time using my authenticator, you need to setup a memorable password to encrypt/decrypt your 2FA secrets.\n\nWrite it in both boxes",wraplength=250,justify="center")
            self.setupLabel.pack(pady=10)

            self.setupEntry = customtkinter.CTkEntry(self.setupFrame, show="*")
            self.setupEntry.pack(pady=(0, 10))
            self.setupEntry.focus()

            self.setupConfirmEntry = customtkinter.CTkEntry(self.setupFrame, show="*")
            self.setupConfirmEntry.pack(pady=(0, 10))
            
            self.setupConfirmButton = customtkinter.CTkButton(self.setupFrame,text="Submit",command=lambda: self.submitPassword(self.setupEntry.get(),self.setupConfirmEntry.get()))
            self.setupConfirmButton.pack(pady=10)
        elif name == "Add Secret":
            self.title("Add Secret")
            self.geometry("350x420")

            self.addSecretFrame = customtkinter.CTkFrame(self,corner_radius=10)
            self.addSecretFrame.pack(padx=20, pady=20, fill="both", expand=True)

            self.qrCodeButton = customtkinter.CTkButton(self.addSecretFrame,text="QR Code (clipboard)",corner_radius=10,command=self.qrScan)
            self.qrCodeButton.pack(pady=(10,0))
            self.qrCodeLabel = customtkinter.CTkLabel(self.addSecretFrame,text="", fg_color="transparent")
            self.qrCodeLabel.pack(pady=(5,20))
            self.entry = entry2fa()

            self.titleFrame = customtkinter.CTkFrame(self.addSecretFrame,fg_color="transparent",height=20)
            self.titleLabel = customtkinter.CTkLabel(self.titleFrame,fg_color="transparent",text="Title:")
            self.titleLabel.place(y=10,anchor="w")
            self.titleEntry = customtkinter.CTkEntry(self.titleFrame,corner_radius=10,width=120)
            self.titleEntry.place(y=10,x=40,anchor="w")
            self.titleFrame.pack(pady=(10,0))

            self.secretFrame = customtkinter.CTkFrame(self.addSecretFrame,fg_color="transparent",height=20,width=224)
            self.secretLabel = customtkinter.CTkLabel(self.secretFrame,fg_color="transparent",text="Secret:")
            self.secretLabel.place(y=10,anchor="w")
            self.secretEntry = customtkinter.CTkEntry(self.secretFrame,corner_radius=10,width=120)
            self.secretEntry.place(y=10,x=52,anchor="w")
            self.secretFrame.pack(pady=(10,0))

            self.issuerFrame = customtkinter.CTkFrame(self.addSecretFrame,fg_color="transparent",height=20,width=250)
            self.issuerLabel = customtkinter.CTkLabel(self.issuerFrame,fg_color="transparent",text="Issuer:")
            self.issuerLabel.place(y=10,anchor="w")
            self.issuerEntry = customtkinter.CTkEntry(self.issuerFrame,corner_radius=10,width=120)
            self.issuerEntry.place(y=10,x=52,anchor="w")
            self.issuerHint = customtkinter.CTkLabel(self.issuerFrame,fg_color="transparent",text="(optional)")
            self.issuerHint.place(y=10,x=180,anchor="w")
            self.issuerFrame.pack(padx=(26,0),pady=(10,0))

            self.digitsFrame = customtkinter.CTkFrame(self.addSecretFrame,fg_color="transparent",height=20,width=250)
            self.digitsLabel = customtkinter.CTkLabel(self.digitsFrame,fg_color="transparent",text="Digits:")
            self.digitsLabel.place(y=10,anchor="w")
            self.digitsEntry = customtkinter.CTkEntry(self.digitsFrame,corner_radius=10,width=120)
            self.digitsEntry.place(y=10,x=52,anchor="w")
            self.digitsHint = customtkinter.CTkLabel(self.digitsFrame,fg_color="transparent",text="(optional)")
            self.digitsHint.place(y=10,x=180,anchor="w")
            self.digitsFrame.pack(padx=(26,0),pady=(10,0))

            self.intervalFrame = customtkinter.CTkFrame(self.addSecretFrame,fg_color="transparent",height=20,width=250)
            self.intervalLabel = customtkinter.CTkLabel(self.intervalFrame,fg_color="transparent",text="Interval:")
            self.intervalLabel.place(y=10,anchor="w")
            self.intervalEntry = customtkinter.CTkEntry(self.intervalFrame,corner_radius=10,width=120)
            self.intervalEntry.place(y=10,x=52,anchor="w")
            self.iintervalHint = customtkinter.CTkLabel(self.intervalFrame,fg_color="transparent",text="(optional)")
            self.iintervalHint.place(y=10,x=180,anchor="w")
            self.intervalFrame.pack(padx=(26,0),pady=(10,0))

            self.optionmenu_var = customtkinter.StringVar(value="TOTP")
            typeOptionMenu = customtkinter.CTkOptionMenu(self.addSecretFrame,values=["TOTP", "Steam"],command=self.typeOptionMenu_callback,variable=self.optionmenu_var,fg_color="#313244",button_hover_color="#252639",button_color="#1a1a2a")
            typeOptionMenu.pack(pady=(10,0))

            self.confirmButton = customtkinter.CTkButton(self.addSecretFrame,text="Confirm",corner_radius=10,command=self.confirm)
            self.confirmButton.pack(pady=(20,10))
    def typeOptionMenu_callback(self,choice):
        self.entry.type = choice
    def confirm(self):
        qrLabelText = self.qrCodeLabel.cget("text")
        if not qrLabelText.startswith("Success!"):
            inputTitle = self.titleEntry.get()
            self.entry.title = inputTitle if len(inputTitle) > 0 else "Error"


            inputSecret = self.secretEntry.get()
            self.entry.secret = inputSecret if len(inputSecret) > 0 else "Error"


            inputIssuer = self.issuerEntry.get()
            self.entry.issuer = inputIssuer if inputIssuer else "Unset"


            inputDigits = self.digitsEntry.get()
            inputDigitsInt = "Error"
            try:
                inputDigitsInt = int(inputDigits)
            except ValueError:
                if not inputDigits:
                    inputDigitsInt = 6
            self.entry.digits = inputDigitsInt


            inputInterval = self.intervalEntry.get()
            inputIntervalInt = "Error"
            try:
                inputIntervalInt = int(inputInterval)
            except ValueError:
                if not inputInterval:
                    inputIntervalInt = 30
            self.entry.interval = inputIntervalInt


        safe = 0
        for attr,value in vars(self.entry).items():
            if value != "Error":
                safe += 1
            else:
                self.confirmButton.configure(text="Error at " + attr)
                self.after(2000,lambda: self.confirmButton.configure(text="Confirm"))
        if safe == len(vars(self.entry)):
            print("safe inputs")
            self.confirmButton.configure(text="✅")
            self.titleEntry.delete(0,customtkinter.END)
            self.secretEntry.delete(0,customtkinter.END)
            self.issuerEntry.delete(0,customtkinter.END)
            self.digitsEntry.delete(0,customtkinter.END)
            self.intervalEntry.delete(0,customtkinter.END)
            self.optionmenu_var.set("TOTP")
            self.qrCodeLabel.configure(text="")
            noticeLabelText = self.master.master.codesFrame.noticeLabel.cget("text")
            if "top left" in noticeLabelText:
                lines = noticeLabelText.splitlines()
                notice = "\n"
                for line in lines:
                    if "top left" not in line:
                        notice += line
                self.master.master.codesFrame.noticeLabel.configure(text=notice)
            secretKey = self.master.master.codesFrame.passwordEntry.get()
            dataWrite(self.entry,secretKey)
            del secretKey

            self.after(100,lambda: self.master.master.codesFrame.waitOTP())

            self.after(2000,lambda: self.confirmButton.configure(text="Confirm"))
        

    def qrScan(self):
        entry = scanClipboard()
        if entry != None:
            self.entry = entry
            self.qrCodeLabel.configure(text=f"Success! Loaded from: {entry.issuer}\nConfirm below")
            self.confirmButton.configure(text="Confirm Ready")
        else:
            self.qrCodeLabel.configure(text="Error, is the QR code in your clipboard?")

    def submitPassword(self,password: str,confirmInput: str):
        if min([len(password),len(confirmInput)]) >= 8:
            if password == confirmInput:
                self.setupConfirmButton.configure(text="Hashing...")
                hashedPassword = hashedPasswordGen(password)
                del password,confirmInput # probably a good idea
                self.master.master.userdata["password"] = hashedPassword
                saveConfig(data=self.master.master.userdata,filename="data.json")
                self.on_close() # <-- causes a close
            else:
                self.setupConfirmButton.configure(text="Inputs do not match.")
                self.after(2000,lambda: self.setupConfirmButton.configure(text="Submit"))
        else:
            self.setupConfirmButton.configure(text="Too short. (8 min)")
            self.after(2000,lambda: self.setupConfirmButton.configure(text="Submit"))
    


#start
class sidebar(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        self.toplevel_windows = {} # <-- safe to assume no toplevel windows are open (for obvious reasons)
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        config = master.config
        print(f"Config: {config}")
        icons = [
            resource_path(f"assets/{config['theme']}_{config['highTransparency']}_Add Secret.png"),
            resource_path(f"assets/{config['theme']}_{config['highTransparency']}_Settings.png")
        ]

        self.buttons = []
        for i, icon_path in enumerate(icons):
            self.grid_rowconfigure(i, weight=1)
            icon = Image.open(icon_path)
            icon_dark = darken(icon)
            ctk_img = customtkinter.CTkImage(
                light_image=icon,
                dark_image=icon,
                size=(45, 45)
            )
            ctk_img_dark = customtkinter.CTkImage(
                light_image=icon_dark,
                dark_image=icon_dark,
                size=(45, 45)
            )
            btn = customtkinter.CTkButton(
                self,
                image=ctk_img,
                text="",
                command=lambda p=icon_path: self.button_callbck(p.removesuffix(".png").rsplit("_",1)[1]),
                fg_color=self.cget("fg_color"),
                hover=False,
                width=45
            )
            btn.img_normal = ctk_img
            btn.img_dark = ctk_img_dark
            btn.grid(row=i, column=0, padx=3, pady=20,sticky="ns")
            self.buttons.append(btn)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(image=b.img_dark))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(image=b.img_normal))
    def reload_icons(self):
        config = self.master.config
        icons = [
            resource_path(f"assets/{config['theme']}_{config['highTransparency']}_Add Secret.png"),
            resource_path(f"assets/{config['theme']}_{config['highTransparency']}_Settings.png")
        ]

        for btn, icon_path in zip(self.buttons, icons):
            icon = Image.open(icon_path)
            icon_dark = darken(icon)
            ctk_img = customtkinter.CTkImage(
                light_image=icon,
                dark_image=icon,
                size=(45, 45)
            )
            ctk_img_dark = customtkinter.CTkImage(
                light_image=icon_dark,
                dark_image=icon_dark,
                size=(45, 45)
            )
            btn.img_normal = ctk_img
            btn.img_dark = ctk_img_dark
            btn.configure(image=ctk_img)
    def button_callbck(self, name): # <-- create a top level
        if name == "Add Secret":
            secretKeyState = self.master.codesFrame.validityBox.cget("text") #gets the x or tick from validity box
            secretKey = self.master.codesFrame.passwordEntry.get() #gets the value from pass box
            passwordSet = "password" in self.master.userdata
            if secretKeyState == "❌":
                if passwordSet:
                    CTkMessagebox(title="Missing Secret Key", message=("Input your secret key before proceeding. This is needed to encrypt/decrypt 2FA secrets." if secretKey == "" else "Secret key is incorrect, please re-enter it."),icon=("warning" if secretKey == "" else "cancel"), option_1="Close",button_color="#313244",button_hover_color="#262739",fg_color="#1a1a2a")
                    return
                else:
                    name = "lopAuth Setup"
            del secretKey #probably a good idea? again
        if not name in self.toplevel_windows:
            win = self.toplevel_windows[name] = ToplevelGUI(self,app=self.master,name=name)
        else:
            win = self.toplevel_windows[name]
        win.attributes("-topmost", True)
        win.after(10,lambda: win.attributes("-topmost", False))
    