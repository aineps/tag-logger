from email import message
from email.policy import default
import sys
import os.path
from tkinter import dialog
from click import style
from numpy import size
import wx
import wx.stc as stc
from datetime import date

# class MyFrame
# class MyApp

allowed_filetypes = "Text (*.txt)|*.txt|"        \
                    "Config (*.cfg)|*.cfg|"      \
                    "Python (*.py)|*.py|"        \
                    "Python (*.pyw)|*.pyw|"      \
                    "All (*.*)|*.*"

class MyFrame(wx.Frame):
    # init function
    def __init__(self, filename="Untitled.txt"):
        super(MyFrame, self).__init__(None, size=(800, 600))

        # icon folder goes here
        self.filename = filename
        self.dirname = "."
        self.flagDirty = False
        self.isNew = True
        
        self.SetProperties()
        self.CreateMenuBar()
        self.CreateStyledTextControl()
        self.CreateStatusBar()
        self.BindEvents()

    def SetProperties(self):
        self.SetTitle()
        # set icon
        self.SetBackgroundColour('BLACK')
    
    def SetTitle(self):
        super(MyFrame, self).SetTitle("%s - TagLogger" % self.filename)

    def CreateMenuBar(self):
        menubar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_edit = wx.Menu()
        menu_tags = wx.Menu()
    
        self.menu_File_Open = menu_file.Append(wx.ID_OPEN,"&Open"+"\t"+"Ctrl+O","Open a new file.")

        menu_file.AppendSeparator()

        self.menu_File_Save = menu_file.Append(wx.ID_SAVE,"&Save"+"\t"+"Ctrl+S","Save current file.")
        self.menu_File_SaveAs = menu_file.Append(wx.ID_SAVEAS,"&Save as"+"\t"+"Ctrl+Shift+S","Save under a different name.")

        menu_file.AppendSeparator()

        self.menu_File_Close = menu_file.Append(wx.ID_EXIT,"&Exit" + "\t" + "Ctrl+X", "Exit the program.")
        
        #------------

        self.menu_Edit_Cut = menu_edit.Append(wx.ID_CUT, "&Cut" + "\t" + "Ctrl+X", "Cut")
        self.menu_Edit_Copy = menu_edit.Append(wx.ID_COPY, "&Copy" + "\t" + "Ctrl+C", "Copy")
        self.menu_Edit_Paste = menu_edit.Append(wx.ID_PASTE, "&Paste" + "\t" + "Ctrl+V", "Paste")
        #------------

        menu_edit.AppendSeparator()

        #------------

        self.menu_Edit_Undo = menu_edit.Append(wx.ID_UNDO,"&Undo" + "\t" + "Ctrl+Z", "Undo")
        self.menu_Edit_Redo = menu_edit.Append(wx.ID_REDO, "&Redo" + "\t" + "Ctrl+Shift+Z", "Redo")
        
        #------------
        self.menu_Tag_Open = menu_tags.Append(-1, "&Open tag")
        self.menu_Tag_Write = menu_tags.Append(-1, "&Write to tag")

        menubar.Append(menu_file, "File")
        menubar.Append(menu_edit, "Edit")
        menubar.Append(menu_tags, "Tags")

        self.SetMenuBar(menubar)

    def CreateStyledTextControl(self):
        self.St_TextCtrl = stc.StyledTextCtrl(self)
        self.St_TextCtrl.SetWindowStyle(self.St_TextCtrl.GetWindowStyle() | wx.BORDER_SUNKEN)
        self.St_TextCtrl.StyleSetSpec(stc.STC_STYLE_DEFAULT, "size:11, face:Century Gothic")
        self.St_TextCtrl.SetWrapMode(stc.STC_WRAP_WORD)

        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(self.St_TextCtrl, proportion=1, border=0, flag=wx.ALL|wx.EXPAND)
        self.SetSizer(layout)

    def BindEvents(self):
        self.Bind(wx.EVT_MENU, self.OnOpen, self.menu_File_Open)
        self.Bind(wx.EVT_MENU, self.OnSave, self.menu_File_Save)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, self.menu_File_SaveAs)
        self.Bind(wx.EVT_MENU, self.OnCloseMe, self.menu_File_Close)
        self.Bind(wx.EVT_MENU, self.OnCut, self.menu_Edit_Cut)
        self.Bind(wx.EVT_MENU, self.OnCopy, self.menu_Edit_Copy)
        self.Bind(wx.EVT_MENU, self.OnPaste, self.menu_Edit_Paste)
        self.Bind(wx.EVT_MENU, self.OnUndo, self.menu_Edit_Undo)
        self.Bind(wx.EVT_MENU, self.OnRedo, self.menu_Edit_Redo)
        self.Bind(wx.EVT_MENU, self.OnOpenTag, self.menu_Tag_Open)
        self.Bind(wx.EVT_MENU, self.OnWriteTag, self.menu_Tag_Write)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    
    def DefaultFileDialogOptions(self):
        return dict(message="Choose a file:", defaultDir=self.dirname, wildcard=allowed_filetypes)

    def AskUserForFileName(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        if dialog.ShowModal() == wx.ID_OK:
            userProvidedFilename = True
            self.filename = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()
            self.SetTitle()
        else:
            userProvidedFilename = False
        return userProvidedFilename

    def OnWriteTag(self, event):
        # if it's the proper notation create a file named that
        # write the text until the end or until the next tag marker
        isTagged = False
        tags = []
        for line in range(self.St_TextCtrl.GetLineCount()):
            if isTagged:
                # open file
                # write content
                if self.St_TextCtrl.GetLine(line)[0:2] != "++":
                    tagged_line = self.St_TextCtrl.GetLine(line).strip("\n")
                    # print(tagged_line)
                    for tag in range(len(tags)):
                        tag_filename = tags[tag] + "_tag.txt"
                        with open(os.path.join(self.dirname, tag_filename), 'a', encoding='utf-8') as tag_file: 
                            tag_file.write(tagged_line + "\n")
                else:
                    isTagged = False

            if self.St_TextCtrl.GetLine(line)[0:2] == "++":
                isTagged = True
                tags = self.St_TextCtrl.GetLine(line)[3:].split(",")
                for tag in range(len(tags)):
                    tags[tag] = tags[tag].strip(" ").strip("#").strip("\n").strip("\r")
                    with open(os.path.join(self.dirname, tags[tag] + "_tag.txt"), 'a', encoding='utf-8') as tag_file: 
                        tag_file.write(str(date.today())) 

    def OnOpenTag(self, event):
        # find correct file and open it
        dialog = wx.TextEntryDialog(self, "Enter a tag to open", "Find Tag")
        dialog.ShowModal()
        if dialog.ShowModal() == wx.ID_OK:
            tag_file = open(os.path.join(dialog.GetValue() + "_tag.txt"), 'r', encoding='utf-8')
            tag_dialog = wx.MessageDialog(self, tag_file.read(), "tag:" + dialog.GetValue(), wx.OK)
            tag_file.close()
            tag_dialog.ShowModal()
            tag_dialog.Destroy()
        dialog.Destroy()
        pass

    def OnOpen(self, event):
        if self.AskUserForFileName(style=wx.FD_OPEN, **self.DefaultFileDialogOptions()):
            file = open(os.path.join(self.dirname, self.filename), 'r', encoding='utf-8')
            self.St_TextCtrl.SetValue(file.read())
            file.close()
            self.isNew = False

    def OnSave(self, event):
        if self.isNew:
            self.AskUserForFileName(defaultFile=self.dirname, style=wx.FD_SAVE, **self.DefaultFileDialogOptions()) 
            self.isNew = False   
        with open(os.path.join(self.dirname, self.filename), 'w', encoding='utf-8') as file:
            file.write(self.St_TextCtrl.GetValue())

    def OnSaveAs(self, event):
        if self.AskUserForFileName(defaultFile=self.dirname, style=wx.FD_SAVE, **self.DefaultFileDialogOptions()):
            self.OnSave(event)

    def OnCut(self, event):
        self.St_TextCtrl.Cut()

    def OnCopy(self, event):
        self.St_TextCtrl.Copy()

    def OnPaste(self, event):
        self.St_TextCtrl.Paste()

    def OnUndo(self, event):
        self.St_TextCtrl.Undo()

    def OnRedo(self, event):
        self.St_TextCtrl.Redo()

    def OnCloseMe(self, event):
        self.St_TextCtrl.Close()

    def OnCloseWindow(self, event):
        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        self.installDir = os.path.split(os.path.abspath(sys.argv[0]))[0]

        frame = MyFrame()
        self.SetTopWindow(frame)
        frame.Show(True)

        return True

    def GetInstallDir(self):
        return self.installDir

def main():
    app = MyApp(False)
    app.MainLoop()

if __name__ == "__main__":
    main()
