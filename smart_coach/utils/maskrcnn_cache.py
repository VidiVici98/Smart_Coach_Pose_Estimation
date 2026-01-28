"""
Mask R-CNN caching utility for performance optimization.

This module provides frame-based caching for Mask R-CNN body segmentation,
which is the primary bottleneck in the pipeline (250ms vs 45ms for other models).

Usage:
    cache = MaskRCNNCache(cache_frames=5)
    
    # In main loop:
    mask = cache.get_or_compute(frame_idx, compute_func, frame)
"""
import numpy as np
from typing import Optional, Callable, Any
import time


class MaskRCNNCache:
    """Frame-based cache for Mask R-CNN segmentation masks.
    
    Caches the body mask for N frames to avoid expensive re-computation.
    Body position typically changes slowly between frames, making this safe.
    
    Attributes:
        cache_frames: Number of frames to cache before recomputing
        _cached_mask: Currently cached mask
        _cache_frame_idx: Frame index when mask was cached
        _cache_counter: Number of frames since last computation
        _total_computations: Total times mask was computed
        _total_cache_hits: Total times cache was used
    """
    
    def __init__(self, cache_frames: int = 5):
        """Initialize the cache.
        
        Args:
            cache_frames: Number of frames to reuse cached mask (>= 1)
        """
        if cache_frames < 1:
            raise ValueError(f"cache_frames must be >= 1, got {cache_frames}")
        
        self.cache_frames = cache_frames
        self._cached_mask: Optional[np.ndarray] = None
        self._cache_frame_idx: int = -1
        self._cache_counter: int = 0
        self._total_computations: int = 0
        self._total_cache_hits: int = 0
        self._computation_times: list = []
    
    def get_or_compute(
        self,
        frame_idx: int,
        compute_func: Callable[[Any], Optional[np.ndarray]],
        *args,
        **kwargs
    ) -> Optional[np.ndarray]:
        """Get cached mask or compute new one if cache expired.
        
        Args:
            frame_idx: Current frame index
            compute_func: Function to call to compute mask (if needed)
            *args: Arguments to pass to compute_func
            **kwargs: Keyword arguments to pass to compute_func
            
        Returns:
            Body mask (numpy array) or None if computation failed
        """
        # Check if we need to recompute
        needs_compute = (
            self._cached_mask is None or  # No cached mask
            self._cache_counter >= self.cache_frames or  # Cache expired
            frame_idx < self._cache_frame_idx  # Video restarted/seeked
        )
        
        if needs_compute:
            # Compute new mask
            start_time = time.time()
            try:
                new_mask = compute_func(*args, **kwargs)
                computation_time = time.time() - start_time
                self._computation_times.append(computation_time)
                
                if new_mask is not None:
                    self._cached_mask = new_mask
                    self._cache_frame_idx = frame_idx
                    self._cache_counter = 0
                    self._total_computations += 1
                    return new_mask
                else:
                    # Computation returned None - keep using old cache if available
                    self._cache_counter += 1
                    self._total_computations += 1
                    return self._cached_mask
            except Exception as e:
                print(f"Warning: Mask R-CNN computation failed at frame {frame_idx}: {e}")
                self._cache_counter += 1
                self._total_computations += 1
                return self._cached_mask
        else:
            # Use cached mask
            self._cache_counter += 1
            self._total_cache_hits += 1
            return self._cached_mask
    
    def invalidate(self):
        """Invalidate the cache, forcing recomputation on next call."""
        self._cached_mask = None
        self._cache_counter = self.cache_frames  # Force recompute
    
    def get_stats(self) -> dict:
        """Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._total_computations + self._total_cache_hits
        hit_rate = self._total_cache_hits / total_requests if total_requests > 0 else 0.0
        
        avg_computation_time = (
            np.mean(self._computation_times) if self._computation_times else 0.0
        )
        
        # Calculate effective speedup
        # If we compute every frame: total_requests * avg_time
        # With caching: total_computations * avg_time
        if self._total_computations > 0 and avg_computation_time > 0:
            time_without_cache = total_requests * avg_computation_time
            time_with_cache = self._total_computations * avg_computation_time
            speedup = time_without_cache / time_with_cache if time_with_cache > 0 else 1.0
        else:
            speedup = 1.0
        
        return {
            'total_requests': total_requests,
            'cache_hits': self._total_cache_hits,
            'computations': self._total_computations,
            'hit_rate': hit_rate,
            'avg_computation_time_ms': avg_computation_time * 1000,
            'theoretical_speedup': speedup,
            'time_saved_seconds': (
                self._total_cache_hits * avg_computation_time
            ),
        }
    
    def __str__(self) -> str:
        """Return string representation of cache stats."""
        stats = self.get_stats()
        return (
            f"MaskRCNN Cache Stats:\n"
            f"  Cache frames: {self.cache_frames}\n"
            f"  Total requests: {stats['total_requests']}\n"
            f"  Cache hits: {stats['cache_hits']}\n"
            f"  Computations: {stats['computations']}\n"
            f"  Hit rate: {stats['hit_rate']:.1%}\n"
            f"  Avg computation time: {stats['avg_computation_time_ms']:.1f}ms\n"
            f"  Theoretical speedup: {stats['theoretical_speedup']:.2f}x\n"
            f"  Time saved: {stats['time_saved_seconds']:.2f}s"
        )


def compute_body_mask(maskrcnn, frame, confidence_threshold: float = 0.7):
    """Compute body mask using Mask R-CNN.
    
    Args:
        maskrcnn: Mask R-CNN model
        frame: Input frame (BGR image)
        confidence_threshold: Minimum confidence for person detection
        
    Returns:
        Body mask (numpy array) or None if no person detected
    """
    import torch
    from torchvision.transforms import functional as F
    
    with torch.no_grad():
        pred = maskrcnn([F.to_tensor(frame)])[0]
    
    # Find first person detection above threshold
    for mask, label, score in zip(pred["masks"], pred["labels"], pred["scores"]):
        if label == 1 and score > confidence_threshold:
            return (mask[0] > 0.5).cpu().numpy()
    
    return None


if __name__ == "__main__":
    # Demo usage
    print("MaskRCNN Cache Demo")
    print("=" * 50)
    
    cache = MaskRCNNCache(cache_frames=5)
    
    # Simulate processing frames
    def mock_compute(*args, **kwargs):
        """Mock computation that takes time."""
        import time
        time.sleep(0.05)  # Simulate 50ms computation
        return np.ones((480, 640), dtype=bool)
    
    print("\nSimulating 100 frames with 5-frame cache...")
    for i in range(100):
        mask = cache.get_or_compute(i, mock_compute)
    
    print("\nCache Statistics:")
    print(cache)
    print("\nExpected hit rate: ~80% (4 out of 5 frames use cache)")
