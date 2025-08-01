# Tests package for Poker System MVP
"""
Test suite for Poker System MVP

This package contains tests for all layers:
- test_l1_rules.py: Pure domain logic tests (no external dependencies)
- test_l2_translator.py: Translation layer integration tests  
- test_integration.py: End-to-end integration tests

Design philosophy:
- L1 tests are completely independent
- L2 tests verify translator behavior
- Integration tests verify full system behavior
"""