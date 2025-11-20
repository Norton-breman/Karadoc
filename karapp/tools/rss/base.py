from abc import ABC, abstractmethod

class RssSearchTool(ABC):

    def __init__(self):
        self.name = ''

    @classmethod
    @abstractmethod
    def search(self, keyword):
        pass