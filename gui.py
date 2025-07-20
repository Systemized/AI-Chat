from nicegui import app, ui

# Dark mode enabled & window resizing disabled
app.native.window_args['resizable'] = False
ui.dark_mode().enable()

ui.add_css('''
    .message-bubble {
        padding: 0 10px;
        max-width: 75%;
        word-wrap: break-word;
    }
    
    .user-bubble {
        background-color: #007AFF;
        margin-left: auto;
        border-radius: 12px 12px 0 12px;
    }
    
    .bot-bubble {
        background-color: #3C3C3E;
        margin-right: auto;
        border-radius: 12px 12px 12px 0;
    }
    

''')



class ChatBotUI:
    def __init__(self):
        self.messages = []

        with ui.column().style('width: 368px; height: 540px;'):
            ui.label('AI Chat!').style('margin: 0 auto;')
            self.chat_container = ui.column().style('width: 100%; flex: 1; overflow-y: auto; justify-content: flex-end;')
            with ui.row().style('width: 100%; align-items: center; justify-content: space-between; background-color: gray; padding: 5px; border-radius: 10px;'):
                self.user_prompt = ui.textarea().props('clearable rows=3').style('flex: 1;').classes('text-area')
                ui.button('Send', on_click=self.send_message)

    def send_message(self):
        user_text = self.user_prompt.value.strip()
        if not user_text:
            return
        
        self.add_message('User', user_text)
        self.user_prompt.value = ''

        # Placeholder for now
        self.add_message('Bot', f'user said {user_text}')

    
    # # May add recieve_message() later, to recieve messages from bot.
    # # if not, then maybe bot messages will be sent with the user's on the send_message function

    # def recieve_message(self):
    #     self.add_message('Bot')
    
    def add_message(self, sender, message):
        self.messages.append([sender, message])
        with self.chat_container:
            if sender == 'User':
                ui.markdown(message).classes('message-bubble user-bubble')
            else:
                ui.markdown(message).classes('message-bubble bot-bubble')

