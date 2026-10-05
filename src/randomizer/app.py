import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

class Randomizer(toga.App):
    def startup(self):
        main_box = toga.Style(direction=COLUMN, alignment=CENTER)
        
        self.label = toga.Label(
            "Interface OK - Test réussi !",
            style=Pack(padding=20)
        )
        
        box = toga.Box(style=main_box)
        box.add(self.label)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

def main():
    return Randomizer()
