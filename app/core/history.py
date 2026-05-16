"""Undo/Redo stack menggunakan salinan snapshot objects."""
import copy


class History:
    def __init__(self, max_steps: int = 50):
        self._undo_stack: list = []
        self._redo_stack: list = []
        self.max_steps = max_steps

    def _snapshot(self, objects: list, image=None):
        snap = {
            "objects": copy.deepcopy(objects),
            "image": image.copy() if image is not None else None,
        }
        return snap

    def save(self, objects: list, image=None):
        """Simpan snapshot state saat ini sebelum perubahan."""
        self._undo_stack.append(self._snapshot(objects, image))
        if len(self._undo_stack) > self.max_steps:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, current_objects: list, current_image=None):
        """Kembalikan state sebelumnya. Return snapshot dict atau None."""
        if not self._undo_stack:
            return None
        self._redo_stack.append(self._snapshot(current_objects, current_image))
        return self._undo_stack.pop()

    def redo(self, current_objects: list, current_image=None):
        """Maju kembali ke state setelah undo. Return snapshot dict atau None."""
        if not self._redo_stack:
            return None
        self._undo_stack.append(self._snapshot(current_objects, current_image))
        return self._redo_stack.pop()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
