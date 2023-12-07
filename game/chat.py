import pygame

class ChatBox:
    def __init__(self, chat_font):
        self.chat_history = []
        self.old_chat_history = []
        self.surface = pygame.Surface([350, 440])
        self.surface.fill((255, 255, 255))

        self.chat_font = chat_font

    # append "[agent]: [message]" to chat history and redraw
    # chat history is limited to 11 items 
    def chat(self, agent, message):
        self.chat_history.insert(0, agent+": "+message)
        self.chat_history = self.chat_history[:11]
        self.draw_messages()

    # draw messages. only called when a new message is added to chat history
    def draw_messages(self):
        self.surface.fill((255, 255, 255))
        full_chat = self.chat_history + self.old_chat_history
        for i, msg in enumerate(full_chat[:11]):
            msg_surface = self.chat_font.render(msg, True, [0,0,0])
            self.surface.blit(msg_surface, (3, 400-i*40))

    def correct_guess(self, prompt):
        for msg in self.chat_history:
            if prompt.lower() in msg.lower():
                return True
            if "nsfw" in msg:
                return None
        return False
    
    def new_round(self):
        self.old_chat_history = self.chat_history
        self.chat_history = []

    def get_last_ai_guess(self):
        for msg in self.chat_history:
            if "ai" not in msg:
                continue
            return msg[5:]
        return ""