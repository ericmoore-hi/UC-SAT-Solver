# This code is licensed under the Affero General Public License v1.0 only.
# You are free to use, modify, and distribute the code under the following terms:
# 1. Attribution: You must provide proper credit, including a link to the license, and indicate if any changes were made.
# 2. Non-Commercial: Commercial use of this code is prohibited without explicit permission from the author.
# For permissions beyond this license, contact: ericmoore@financier.com

import wx
import wx.grid as gridlib
import random

# Open and read CNF file
def open_cnf_file():
    with wx.FileDialog(None, "Select CNF File", wildcard="CNF Files (*.cnf)|*.cnf|All Files (*)|*",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return None  # Canceled
        path = fileDialog.GetPath()
        try:
            with open(path, "r") as file:
                content = file.readlines()
                return content  # Return file content
        except IOError:
            wx.LogError("CNF file could not be opened.")
            return None

# Parse CNF content and extract literals
def parse_cnf_content(cnf_content):
    literals = set()
    clauses = []

    for line in cnf_content:
        line = line.strip()  # Remove whitespace
        if not line or line.startswith('p') or line.startswith('c'):
            continue  # Skip comments and empty lines
        clause = line.split()[:-1]  # Remove '0' character
        if len(clause) == 0:
            continue  # Skip empty clauses
        clauses.append(clause)
        for lit in clause:
            literals.add(lit.lstrip('-'))  # Distinguish positive and negative literals

    return sorted(list(literals), key=lambda x: int(x)), clauses  # Sort and return literals

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title="UC-SAT Solver", size=(1200, 600))  # Title changed to UC-SAT Solver

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Select CNF file button
        self.open_button = wx.Button(self.panel, label="Select CNF File")
        self.vbox.Add(self.open_button, 0, wx.ALL | wx.CENTER, 10)
        self.open_button.Bind(wx.EVT_BUTTON, self.on_open_file)

        # Create grid
        self.grid = gridlib.Grid(self.panel)
        self.grid.CreateGrid(0, 0)  # Rows/columns will be created after CNF is loaded
        self.vbox.Add(self.grid, 1, wx.EXPAND)

        # Disable editing
        self.grid.EnableEditing(False)  # Disable cell editing
        self.grid.DisableDragRowSize()  # Disable manual row resizing
        self.grid.DisableDragColSize()  # Disable manual column resizing

        # Random assignment button
        self.random_button = wx.Button(self.panel, label="Monte Carlo Assignment")
        self.vbox.Add(self.random_button, 0, wx.ALL | wx.CENTER, 10)
        self.random_button.Bind(wx.EVT_BUTTON, self.on_random_assign)
        self.random_button.Disable()  # Initially disabled

        self.panel.SetSizer(self.vbox)

        self.true_color = '#85c1e9'  # Blue color
        self.false_color = '#FF0000'  # Red color
        self.clauses = []
        self.literals = []


    def on_open_file(self, event):
        cnf_content = open_cnf_file()
        if cnf_content:
            self.literals, self.clauses = parse_cnf_content(cnf_content)
            self.display_grid()
            self.random_button.Enable()  # Enable button after file is loaded

    def display_grid(self):
        num_literals = len(self.literals)
        num_clauses = len(self.clauses)

        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        if self.grid.GetNumberCols() > 0:
            self.grid.DeleteCols(0, self.grid.GetNumberCols())

        self.grid.AppendRows(num_clauses)
        self.grid.AppendCols(num_literals)

        for col, literal in enumerate(self.literals):
            self.grid.SetColLabelValue(col, literal)

        for row, clause in enumerate(self.clauses):
            for literal in clause:
                literal_index = self.literals.index(literal.lstrip('-'))
                self.grid.SetCellValue(row, literal_index, literal)

        self.grid.AutoSizeColumns()  # Automatically resize columns to fit contents
        self.grid.SetScrollRate(20, 20)  # Set scroll rate for smoother scrolling
        self.grid.FitInside()  # Fit the grid inside the frame
        self.grid.Scroll(0, 0)  # Reset scrolling position

    def on_random_assign(self, event):
        if not self.literals or not self.clauses:
            wx.LogError("No CNF file is loaded.")
            return

        # Random True/False assignment for each literal using Monte Carlo method
        true_false_assignments = {literal: random.choice([True, False]) for literal in self.literals}

        # Color cells based on True/False assignments
        for row in range(self.grid.GetNumberRows()):
            for col in range(self.grid.GetNumberCols()):
                literal = self.grid.GetCellValue(row, col)

                if literal:  # If the cell is not empty
                    if literal.startswith('-'):
                        literal_value = not true_false_assignments[literal.lstrip('-')]
                    else:
                        literal_value = true_false_assignments[literal]

                    # Apply color
                    if literal_value:
                        self.grid.SetCellBackgroundColour(row, col, self.true_color)
                    else:
                        self.grid.SetCellBackgroundColour(row, col, self.false_color)

        self.grid.ForceRefresh()  # Force grid to refresh


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, title="Monte Carlo 3-SAT Viewer")
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()