"""Base tool interface."""


class BaseTool:
    def on_mouse_down(self, event, state):
        pass

    def on_mouse_move(self, event, state):
        pass

    def on_mouse_up(self, event, state):
        pass
