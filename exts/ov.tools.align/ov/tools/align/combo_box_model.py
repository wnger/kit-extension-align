__all__ = ["ComboBoxModel"]

import omni.ui as ui

class ListItem(ui.AbstractItem):
    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        
    def __repr__(self):
        return f'"{self.name_model.as_string}"'

    @property
    def as_string(self):
        """Return the string of the name model"""
        return self.name_model.as_string

class ComboBoxModel(ui.AbstractItemModel):
    def __init__(self):
        super().__init__()
        self._values = ["Center", "Top", "Bottom", "Left", "Right", "Front", "Back"]
        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(
            lambda a: self._item_changed(None))

        self._items = [
            ListItem(text)
            for text in self._values
        ]

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.name_model