import unittest
from src.menu_interface import MenuInterface


class TestMenuInterface(unittest.TestCase):
    def test_action_blocking(self):
        """Тест блокировки интерфейса во время выполнения"""
        interface = MenuInterface()

        self.assertTrue(interface.is_available())
        interface.start_processing()

        self.assertFalse(interface.is_available())
        self.assertTrue(interface.is_busy())

        interface.finish_processing()
        self.assertTrue(interface.is_available())