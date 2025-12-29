import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils.event_listener import EventListener

class TestEventListener(unittest.TestCase):
    def setUp(self):
        self.listener = EventListener()
        self.callback_called = False
        self.callback_data = None

    def callback(self, data):
        self.callback_called = True
        self.callback_data = data

    def test_add_and_notify_event(self):
        """Test adding a listener and notifying an event."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.notify_event("test_event", "data1")
        
        self.assertTrue(self.callback_called)
        self.assertEqual(self.callback_data, "data1")

    def test_multiple_modules_same_event(self):
        """Test that multiple modules can listen to the same event."""
        callback2_called = False
        
        def callback2(data):
            nonlocal callback2_called
            callback2_called = True

        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.add_event_listener("module2", "test_event", callback2)
        
        self.listener.notify_event("test_event", "data_multi")
        
        self.assertTrue(self.callback_called)
        self.assertTrue(callback2_called)

    def test_remove_event_listener_specific_module(self):
        """Test removing a listener from a specific module."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.remove_event_listener("test_event", self.callback, module_name="module1")
        
        self.listener.notify_event("test_event", "data")
        self.assertFalse(self.callback_called)

    def test_remove_event_listener_global(self):
        """Test removing a listener globally (from all modules)."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.remove_event_listener("test_event", self.callback)
        
        self.listener.notify_event("test_event", "data")
        self.assertFalse(self.callback_called)

    def test_clear_event_listeners_specific_module(self):
        """Test clearing events for a specific module."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.clear_event_listeners("test_event", module_name="module1")
        
        self.listener.notify_event("test_event", "data")
        self.assertFalse(self.callback_called)

    def test_remove_module_listeners(self):
        """Test removing all listeners for a module."""
        self.listener.add_event_listener("module1", "event1", self.callback)
        self.listener.add_event_listener("module1", "event2", self.callback)
        
        self.listener.remove_module_listeners("module1")
        
        self.listener.notify_event("event1", "data")
        self.assertFalse(self.callback_called)
        
        self.listener.notify_event("event2", "data")
        self.assertFalse(self.callback_called)

if __name__ == '__main__':
    unittest.main()
