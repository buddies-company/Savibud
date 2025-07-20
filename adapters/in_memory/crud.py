from adapters.ports.crud import CRUD as CRUDBase


class CRUD(CRUDBase):
    """CRUD Repository using in memory data"""

    data: list

    def read(self, **filters):
        filtered = self.data
        for key, value in filters.items():
            filtered = list(filter(lambda d: getattr(d, key, None) == value, filtered))
        return filtered

    def create(self, element):
        self.data.append(element)
        return element

    def update(self, item_id, **modifications):
        item = self.read(id=item_id)
        for key, value in modifications.items():
            setattr(item, key, value)

    def delete(self, item_id):
        item = self.read(id=item_id)
        self.data.remove(item)
