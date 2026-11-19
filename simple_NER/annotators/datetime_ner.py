"""Backward compatibility module for datetime NER.

This module is deprecated. Use TemporalNER from temporal_ner.py instead.
"""
from simple_NER.annotators.temporal_ner import DateTimeNER, TemporalNER, TimedeltaNER

__all__ = ["DateTimeNER", "TemporalNER", "TimedeltaNER"]
