import gui

def main():
    gui.ChatBotUI()

    # Run app in a window instead of browser
    gui.ui.run(native=True, window_size=(400, 600), reload=False, title="AI Chat")

if __name__ == "__main__":
    main()