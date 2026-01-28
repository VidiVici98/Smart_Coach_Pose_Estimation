"""
Unit tests for Mask R-CNN caching functionality.

Tests the cache logic, performance tracking, and robustness.
"""
import unittest
import numpy as np
import time
from smart_coach.utils.maskrcnn_cache import MaskRCNNCache


class TestMaskRCNNCache(unittest.TestCase):
    """Test cases for MaskRCNNCache class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = MaskRCNNCache(cache_frames=5)
    
    def test_initialization(self):
        """Test cache initialization."""
        self.assertEqual(self.cache.cache_frames, 5)
        self.assertIsNone(self.cache._cached_mask)
        self.assertEqual(self.cache._cache_counter, 0)
        self.assertEqual(self.cache._total_computations, 0)
        self.assertEqual(self.cache._total_cache_hits, 0)
    
    def test_invalid_cache_frames(self):
        """Test that invalid cache_frames raises ValueError."""
        with self.assertRaises(ValueError):
            MaskRCNNCache(cache_frames=0)
        
        with self.assertRaises(ValueError):
            MaskRCNNCache(cache_frames=-1)
    
    def test_first_computation(self):
        """Test that first call computes the mask."""
        def compute_func():
            return np.ones((480, 640), dtype=bool)
        
        mask = self.cache.get_or_compute(0, compute_func)
        
        self.assertIsNotNone(mask)
        self.assertEqual(self.cache._total_computations, 1)
        self.assertEqual(self.cache._total_cache_hits, 0)
    
    def test_cache_reuse(self):
        """Test that mask is reused for N frames."""
        def compute_func():
            return np.ones((480, 640), dtype=bool)
        
        # First computation
        mask1 = self.cache.get_or_compute(0, compute_func)
        
        # Should use cache for next 4 frames
        for i in range(1, 5):
            mask = self.cache.get_or_compute(i, compute_func)
            self.assertIs(mask, mask1)  # Same object (cached)
        
        # Stats check
        self.assertEqual(self.cache._total_computations, 1)
        self.assertEqual(self.cache._total_cache_hits, 4)
    
    def test_cache_expiration(self):
        """Test that cache expires after N frames."""
        computation_count = [0]
        
        def compute_func():
            computation_count[0] += 1
            return np.ones((480, 640), dtype=bool) * computation_count[0]
        
        # Process 11 frames (cache_frames = 5)
        for i in range(11):
            mask = self.cache.get_or_compute(i, compute_func)
        
        # Should compute 3 times: frames 0, 5, 10
        self.assertEqual(computation_count[0], 3)
        self.assertEqual(self.cache._total_computations, 3)
        self.assertEqual(self.cache._total_cache_hits, 8)
    
    def test_handle_none_computation(self):
        """Test graceful handling when computation returns None."""
        def compute_none():
            return None
        
        # First call returns None, cache should handle it
        mask = self.cache.get_or_compute(0, compute_none)
        self.assertIsNone(mask)
        
        # Provide a valid mask
        def compute_valid():
            return np.ones((480, 640), dtype=bool)
        
        mask = self.cache.get_or_compute(5, compute_valid)
        self.assertIsNotNone(mask)
        
        # None computation after valid should keep old cache
        mask_after = self.cache.get_or_compute(10, compute_none)
        self.assertIs(mask_after, mask)  # Still using cached mask
    
    def test_handle_exception(self):
        """Test graceful handling of computation exceptions."""
        call_count = [0]
        
        def compute_with_error():
            call_count[0] += 1
            if call_count[0] == 1:
                return np.ones((480, 640), dtype=bool)
            raise RuntimeError("Test error")
        
        # First computation succeeds
        mask1 = self.cache.get_or_compute(0, compute_with_error)
        self.assertIsNotNone(mask1)
        
        # Later computation fails but cache is reused
        mask2 = self.cache.get_or_compute(5, compute_with_error)
        self.assertIs(mask2, mask1)  # Falls back to cached mask
    
    def test_cache_invalidation(self):
        """Test cache can be manually invalidated."""
        def compute_func():
            return np.ones((480, 640), dtype=bool)
        
        mask1 = self.cache.get_or_compute(0, compute_func)
        
        # Invalidate cache
        self.cache.invalidate()
        
        # Next call should recompute
        mask2 = self.cache.get_or_compute(1, compute_func)
        self.assertIsNot(mask2, mask1)  # New computation
    
    def test_statistics(self):
        """Test cache statistics calculation."""
        def compute_func():
            time.sleep(0.001)  # Small delay to simulate work
            return np.ones((480, 640), dtype=bool)
        
        # Process 10 frames
        for i in range(10):
            self.cache.get_or_compute(i, compute_func)
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['total_requests'], 10)
        self.assertEqual(stats['computations'], 2)  # Frames 0 and 5
        self.assertEqual(stats['cache_hits'], 8)
        self.assertAlmostEqual(stats['hit_rate'], 0.8, places=2)
        self.assertGreater(stats['theoretical_speedup'], 1.0)
        self.assertGreater(stats['time_saved_seconds'], 0.0)
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation for different scenarios."""
        def compute_func():
            return np.ones((480, 640), dtype=bool)
        
        # Test with exactly cache_frames calls
        for i in range(5):
            self.cache.get_or_compute(i, compute_func)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['hit_rate'], 0.8)  # 4 hits out of 5
    
    def test_backward_frame_index(self):
        """Test that cache recomputes when frame index goes backward."""
        def compute_func():
            return np.ones((480, 640), dtype=bool)
        
        # Normal forward progression
        mask1 = self.cache.get_or_compute(5, compute_func)
        mask2 = self.cache.get_or_compute(6, compute_func)
        self.assertIs(mask2, mask1)  # Cache hit
        
        # Frame index goes backward (video restarted/seeked)
        mask3 = self.cache.get_or_compute(0, compute_func)
        self.assertEqual(self.cache._total_computations, 2)  # Should recompute
    
    def test_string_representation(self):
        """Test string representation of cache stats."""
        def compute_func():
            return np.ones((480, 640), dtype=bool)
        
        for i in range(10):
            self.cache.get_or_compute(i, compute_func)
        
        stats_str = str(self.cache)
        self.assertIn("MaskRCNN Cache Stats", stats_str)
        self.assertIn("Cache frames: 5", stats_str)
        self.assertIn("Hit rate:", stats_str)
        self.assertIn("Theoretical speedup:", stats_str)


class TestComputeBodyMask(unittest.TestCase):
    """Test compute_body_mask function (without actual model)."""
    
    def test_function_signature(self):
        """Test that compute_body_mask has correct signature."""
        from smart_coach.utils.maskrcnn_cache import compute_body_mask
        import inspect
        
        sig = inspect.signature(compute_body_mask)
        params = list(sig.parameters.keys())
        
        self.assertIn('maskrcnn', params)
        self.assertIn('frame', params)
        self.assertIn('confidence_threshold', params)


if __name__ == '__main__':
    unittest.main()
