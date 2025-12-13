import customtkinter
from utils import correctPassword,entry2fa,decrypt,getOTP
from json import load,dump
from tkinter import font as tkFont
from time import time
from os import replace

class codeFrame(customtkinter.CTkScrollableFrame):
    def flash_red(self,frame:customtkinter.CTkFrame,steps:int=20,time:float=0.5):
        originalCol = "#181825"
        flashCol = "#2C1825"
        #flashCol has 20 more red hex values than original, so, step down by 1 hex value every step
        def stepDown(hexCode):
            redValue = hexCode[1:3]
            denaryRedValue = int(redValue,16)
            newHex = hex(denaryRedValue - 1)
            return newHex[2:] #slice off the 0x
        stepsPerSec = steps / time
        delayBetweenSteps = time*1000 / stepsPerSec
        currentCol = flashCol
        def fadeOut(step=1):
            nonlocal currentCol #make python realise currentCol is in scope
            if step <= steps: #fade more
                newRedVal = stepDown(currentCol)
                currentCol = "#" + newRedVal + currentCol[3:7]
                frame.configure(fg_color=currentCol)
                frame.after(round(delayBetweenSteps),fadeOut,step+1)
            else:
                frame.configure(fg_color=originalCol)
        fadeOut()
    def flash_green(self,frame:customtkinter.CTkFrame,steps:int=20,time:float=0.5):
        originalCol = "#181825"
        flashCol = "#182C25"
        #flashCol has 20 more green hex values than original, so, step down by 1 hex value every step
        def stepDown(hexCode):
            greenValue = hexCode[3:5]
            denaryGreenValue = int(greenValue,16)
            newHex = hex(denaryGreenValue - 1)
            return newHex[2:] #slice off the 0x
        stepsPerSec = steps / time
        delayBetweenSteps = time*1000 / stepsPerSec
        currentCol = flashCol
        def fadeOut(step=1):
            nonlocal currentCol #make python realise currentCol is in scope
            if step <= steps: #fade more
                newGreenVal = stepDown(currentCol)
                currentCol = currentCol[0:3] + newGreenVal + currentCol[5:]
                frame.configure(fg_color=currentCol)
                frame.after(round(delayBetweenSteps),fadeOut,step+1)
            else:
                frame.configure(fg_color=originalCol)
        fadeOut()

    def deleteFrame(self,frame:customtkinter.CTkFrame):
        print("delete called " + str(self.deleteWarnings))
        self.flash_red(frame)
        
        index = self.otpFrames.index(frame)
        if not index in self.deleteWarnings:
            self.deleteWarnings.append(index) #requires 2 clicks
            self.after(2000, lambda: self.deleteWarnings.remove(index))
        else:
            frame.destroy()
            del self.otpFrames[index]
            del self.loadedData["data"][index]
            with open("lopAuth Data/deletejson.json",'w') as f:
                dump(self.loadedData,f,indent=4)
            replace("lopAuth Data/deletejson.json","lopAuth Data/data.json")

    def clickFrame(self,frame:customtkinter.CTkFrame):
        code = frame.codeLabel.cget("text")
        self.clipboard_clear()
        self.clipboard_append(code.strip())
        self.update()
        self.flash_green(frame)
        

    def waitOTP(self):
        with open("lopAuth Data/data.json",'r') as f:
            tdata = load(f)
            if len(tdata["data"]) == 0:
                self.after(200, self.waitOTP)
            else:
                self.loadedData = tdata
                self.OTPProcess()
    
    def refreshCode(self,frame:customtkinter.CTkFrame):
        entry = frame.entry
        code = getOTP(entry)
        frame.codeLabel.configure(text=code)
        #refresh
        time_remaining = entry.interval - (int(time() % entry.interval))
        self.after(time_remaining*1000,lambda: self.refreshCode(frame))


    def newOTPFrame(self, entry):
        otpFrame = customtkinter.CTkFrame(self, fg_color="#181825", width=86, height=45, corner_radius=10)
        code = getOTP(entry)
        otpFrame.entry = entry

        otpFrame.titleLabel = customtkinter.CTkLabel(otpFrame, text=entry.title)
        otpFrame.codeLabel = customtkinter.CTkLabel(otpFrame, text=code)
        otpFrame.codeLabel.place(relx=0.5, rely=0.8, anchor="center")
        otpFrame.titleLabel.place(relx=0.5, rely=0.35, anchor="center")
        size = 12
        while True:
            test_font = customtkinter.CTkFont(family="Roboto", size=size)
            text_width = test_font.measure(entry.title)
            if text_width > 86:
                size -= 1
            else:
                otpFrame.titleLabel.configure(font=test_font)
                break

        otpFrame.grid(row=self.row, column=self.column, padx=2, pady=4)
        otpFrame.bind("<Button-1>", lambda e, f=otpFrame: self.clickFrame(f))
        otpFrame.bind("<Button-2>", lambda e, f=otpFrame: self.deleteFrame(f))
        for child in otpFrame.winfo_children():
            child.bind("<Button-1>", lambda e, f=otpFrame: self.clickFrame(f))
            child.bind("<Button-2>", lambda e, f=otpFrame: self.deleteFrame(f))
        self.otpFrames.append(otpFrame)

        #refresh
        time_remaining = entry.interval - (int(time() % entry.interval))
        self.after(time_remaining*1000,lambda: self.refreshCode(otpFrame))

    def OTPProcess(self):
            try:
                for frame in self.otpFrames:
                    frame.destroy()
            except AttributeError:
                pass
            self.otpFrames = []
            encryptedEntries = self.loadedData["data"]
            entries = [decrypt(otp, self.pwString) for otp in encryptedEntries]
            # start grid position
            self.row = 1
            self.column = 0
            max_cols = 3
            for entry in entries:
                self.column += 1
                if self.column > max_cols:
                    self.column = 1
                    self.row += 1
                self.newOTPFrame(entry)
                


    def verifyPassword(self, *args):
        self.pwString = self.pw.get()

        if self.pwString != "N/A" and correctPassword(self.pwString):
            self.validityBox.configure(text="✅")
            noticeLabelText = self.noticeLabel.cget("text")
            if "top)" in noticeLabelText: #filters for password notice
                lines = noticeLabelText.splitlines()
                notice = "\n"
                for line in lines:
                    if "top)" not in line:
                        notice += line
                self.noticeLabel.configure(text=notice)
            self.passwordEntry.configure(state="disabled")

            #wait until an OTP exists
            self.deleteWarnings = []
            self.waitOTP()
        else:
            self.validityBox.configure(text="❌")

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.passwordBar = customtkinter.CTkFrame(self, height=20, fg_color="#313244", corner_radius=0)
        self.passwordBar.grid(row=0, column=0, columnspan=6, sticky="ew")
        self.columnconfigure(tuple(range(6)), weight=1)

        self.pw = customtkinter.StringVar(value="")
        self.pw.trace_add("write", self.verifyPassword)

        self.passwordLabel = customtkinter.CTkLabel(self.passwordBar, text="Secret key:")
        self.passwordLabel.grid(row=0, column=0, padx=(5, 2))

        self.passwordEntry = customtkinter.CTkEntry(self.passwordBar,fg_color="transparent",corner_radius=0,textvariable=self.pw)
        self.passwordEntry.grid(row=0, column=1, sticky="ew", padx=2)

        self.passwordBar.columnconfigure(1, weight=1)

        if master.config["passwordMaskEnabled"]:
            character = master.config["passwordMaskCharacter"] or "•"
            self.passwordEntry.configure(show=character)

        self.validityBox = customtkinter.CTkLabel(self.passwordBar, text="❌", width=50)
        self.validityBox.grid(row=0, column=2, padx=5)

        with open("lopAuth Data/data.json",'r') as f:
            length = len(load(f)["data"])
        notice = ""
        if self.validityBox.cget("text") == "❌":
            notice += ("\n    Input your password key to continue. (top)")
        if length == 0:
            notice += ("\n   Add an OTP to continue. (top left)")
        self.noticeLabel = customtkinter.CTkLabel(self,text=notice,justify="left")
        self.noticeLabel.grid(row=1,column=0)

        self.after(50, self.passwordEntry.focus_set)
