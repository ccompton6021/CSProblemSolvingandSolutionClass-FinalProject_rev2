import tkinter as tk
from project_model import Model
from project_view import View
from project_controller import Controller

if __name__ == "__main__":
    model = Model()
    root = tk.Tk()
    view = View(root)
    controller = Controller(model, view)
    controller.run()