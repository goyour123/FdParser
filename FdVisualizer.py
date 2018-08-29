import re, os, sys, json
import tkinter, tkinter.filedialog
from FdfParser import parse, get_value

MAX_FD_NUM = 3

def cnvRgnName(RgnDef):
    return re.search(r'FLASH_REGION_(.+)_[A-Z]+', RgnDef).group(1)

def getJsnKey(jsnPath, key):
    try:
        with open(cfgPath, 'r') as f:
            cfgDict = json.load(f)
            return cfgDict[key]
    except:
        return None

class MainGui:
    def __init__(self, rt, cfgDict):
        self.fdDict, self.macroDict, self.cfgDict = parse(cfgDict)
        self.rt = rt
        self.gui_interface_init()

        # Menubar
        menubar = tkinter.Menu(self.rt)
        fileMenu = tkinter.Menu(menubar, tearoff=0)
        fileMenu.add_command(label=" Load file... ", command=self.browser)
        menubar.add_cascade(label=" File ", menu=fileMenu)
        self.rt.config(menu=menubar)

        self.flashFrame = tkinter.Frame(self.rt, relief='groove', bd=2)
        self.flashFrame.grid(row=1, padx=15)

        # Listbox for each FD
        self.fdListbox = tkinter.Listbox(self.rt, height=MAX_FD_NUM, selectmode=tkinter.SINGLE)
        self.curFd = None
        self.cr8FdListbox()

        self.buildFlashMap()

    def gui_interface_init(self):
        self.rt.title('FdVisualizer')
        self.rt.geometry("600x600+300+50")

    def browser(self):
        initDir = os.getcwd()
        filePath = tkinter.filedialog.askopenfile(title='Browse source path', initialdir=initDir)
        if filePath:
            self.fdfPath = filePath

    def onSelect(self, evt):
        selFd = self.fdListbox.get(self.fdListbox.curselection()[0])
        if self.curFd != selFd:
            self.curFd = selFd
            self.buildFlashMap()

    def cr8FdListbox(self):
        self.fdListbox.delete(0, 'end')
        for fd in self.fdDict:
            self.fdListbox.insert('end', fd)
        self.fdListbox.grid(row=0, column=0, rowspan=1, columnspan=1, sticky='w', padx=15, pady=5)
        self.fdListbox.bind('<<ListboxSelect>>', self.onSelect)
        self.fdListbox.selection_set(0, None)
        self.fdListbox.event_generate('<<ListboxSelect>>')

    def buildFlashMap(self):
        fdOffset, nulBlk= 0, 0
        
        for w in self.flashFrame.winfo_children():
            w.destroy()

        for idx, rgn in enumerate(self.fdDict[self.curFd]):
            rgnOffset, rgnSize = get_value(rgn[0], self.macroDict), get_value(rgn[1], self.macroDict)
            if fdOffset < rgnOffset:
                tkinter.Label(self.flashFrame, text="", relief='ridge', bg='gray'+ str(6 + ((idx + nulBlk) % 2) * 2) +'1', bd=2, width=50).grid(row=idx + nulBlk + 2, column=0, rowspan=2, columnspan=1, padx=15)
                tkinter.Label(self.flashFrame, text=hex(fdOffset)).grid(row=idx + nulBlk + 2, column=2, rowspan=1, columnspan=1, sticky='w')
                nulBlk += 1
            tkinter.Label(self.flashFrame, text=cnvRgnName(rgn[0]), relief='ridge', bg='gray'+ str(6 + ((idx + nulBlk) % 2) * 2) +'1', bd=2, width=50).grid(row=idx + nulBlk + 2, column=0, rowspan=2, columnspan=1, padx=15)
            tkinter.Label(self.flashFrame, text=hex(rgnOffset)).grid(row=idx + nulBlk + 2, column=2, rowspan=1, columnspan=1, sticky='w')
            fdOffset = rgnOffset + rgnSize
        tkinter.Label(self.flashFrame, text=hex(fdOffset)).grid(row=idx + nulBlk + 2 + 1, column=2, rowspan=1, columnspan=1, sticky='w')

def main():

    with open('config.json', 'r') as f:
        cfgDict = json.load(f)

    root = tkinter.Tk()
    app = MainGui(root, cfgDict)
    root.mainloop()

if __name__ == '__main__':
    main()
