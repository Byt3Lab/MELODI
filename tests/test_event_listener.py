import unittest
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils.event_listener import EventListener

class TestEventListener(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.listener = EventListener()
        self.callback_called = False
        self.callback_data = None

    async def callback(self, data):
        self.callback_called = True
        self.callback_data = data

    async def test_add_and_notify_event(self):
        """Test adding a listener and notifying an event."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        await self.listener.notify_event("module1", "test_event", "data1")
        
        await asyncio.sleep(0.01)
        
        self.assertTrue(self.callback_called)
        self.assertEqual(self.callback_data, "data1")

    async def test_multiple_modules_same_event(self):
        """Test that multiple modules can listen to the same event."""
        callback2_called = False
        
        async def callback2(data):
            nonlocal callback2_called
            callback2_called = True

        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.add_event_listener("module2", "test_event", callback2)
        
        await self.listener.notify_event("module1", "test_event", "data_multi")
        await self.listener.notify_event("module2", "test_event", "data_multi")
        
        await asyncio.sleep(0.01)
        
        self.assertTrue(self.callback_called)
        self.assertTrue(callback2_called)

    async def test_remove_event_listener_specific_module(self):
        """Test removing a listener from a specific module."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.remove_event_listener("module1", "test_event", self.callback)
        
        await self.listener.notify_event("module1", "test_event", "data")
        await asyncio.sleep(0.01)
        self.assertFalse(self.callback_called)

    async def test_clear_event_listeners_specific_module(self):
        """Test clearing events for a specific module."""
        self.listener.add_event_listener("module1", "test_event", self.callback)
        self.listener.clear_event_listeners("module1", "test_event")
        
        await self.listener.notify_event("module1", "test_event", "data")
        await asyncio.sleep(0.01)
        self.assertFalse(self.callback_called)

    async def test_remove_all_listeners(self):
        """Test removing all listeners globally."""
        self.listener.add_event_listener("module1", "event1", self.callback)
        self.listener.add_event_listener("module1", "event2", self.callback)
        
        self.listener.remove_all_listeners()
        
        await self.listener.notify_event("module1", "event1", "data")
        await asyncio.sleep(0.01)
        self.assertFalse(self.callback_called)
        
        await self.listener.notify_event("module1", "event2", "data")
        await asyncio.sleep(0.01)
        self.assertFalse(self.callback_called)

if __name__ == '__main__':
    unittest.main()
