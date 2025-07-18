from nicegui import ui

dark = ui.dark_mode().enable()
ui.label('Hello World!')

ui.run(native=True, reload=False)
