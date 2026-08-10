"""
DeepStream 7.x & Triton Integration Module for Edge ANPR & Vehicle Analytics
"""

from app.deepstream.stream_manager import StreamManager, get_stream_manager
from app.deepstream.nvds_event_bridge import NVDSEventBridge, get_event_bridge

__all__ = ["StreamManager", "get_stream_manager", "NVDSEventBridge", "get_event_bridge"]
