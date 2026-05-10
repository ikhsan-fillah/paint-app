"""Undo/redo history management."""


class History:
    def __init__(self, limit=50):
        self.limit = limit
        self._undo = []
        self._redo = []

    def push(self, state):
        self._undo.append(state)
        self._redo.clear()
        if len(self._undo) > self.limit:
            self._undo.pop(0)

    def can_undo(self):
        return len(self._undo) > 0

    def can_redo(self):
        return len(self._redo) > 0

    def undo(self, current_state):
        if not self.can_undo():
            return current_state
        self._redo.append(current_state)
        return self._undo.pop()

    def redo(self, current_state):
        if not self.can_redo():
            return current_state
        self._undo.append(current_state)
        return self._redo.pop()
