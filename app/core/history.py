"""Undo/Redo stack menggunakan salinan snapshot objects."""
import copy


class History:
    def __init__(self, max_steps: int = 50):
        self._undo_stack: list = []
        self._redo_stack: list = []
        self.max_steps = max_steps

    def save(self, objects: list):
        """Simpan snapshot state saat ini sebelum perubahan."""
        self._undo_stack.append(copy.deepcopy(objects))
        if len(self._undo_stack) > self.max_steps:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, current_objects: list):
        """Kembalikan state sebelumnya. Return list objects atau None."""
        if not self._undo_stack:
            return None
        self._redo_stack.append(copy.deepcopy(current_objects))
        return copy.deepcopy(self._undo_stack.pop())

    def redo(self, current_objects: list):
        """Maju kembali ke state setelah undo. Return list objects atau None."""
        if not self._redo_stack:
            return None
        self._undo_stack.append(copy.deepcopy(current_objects))
        return copy.deepcopy(self._redo_stack.pop())

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
