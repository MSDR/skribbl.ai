import pygame

class ChatBox:
    def __init__(self, chat_font):
        self.chat_history = []
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
        for i, msg in enumerate(self.chat_history):
            msg_surface = self.chat_font.render(msg, True, [0,0,0])
            self.surface.blit(msg_surface, (4, 400-i*40))