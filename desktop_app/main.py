import customtkinter as ctk


class SentinelViewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SentinelView CustomTkinter App")
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="Hello, SentinelView!", font=("Arial", 20))
        self.label.pack(pady=20)

        self.button = ctk.CTkButton(self, text="Click Me", command=self.on_button_click)
        self.button.pack(pady=20)

    def on_button_click(self):
        self.label.configure(text="Button Clicked!")


def main():
    app = SentinelViewApp()
    app.mainloop()


if __name__ == "__main__":
    main()
