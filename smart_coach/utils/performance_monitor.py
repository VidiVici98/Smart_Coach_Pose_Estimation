"""
Performance monitoring utility for tracking pipeline bottlenecks.

Provides lightweight timing and profiling to identify slow components.
"""
import time
from typing import Dict, List, Optional
from contextlib import contextmanager
import statistics


class PerformanceMonitor:
    """Track performance metrics for pipeline components.
    
    Usage:
        monitor = PerformanceMonitor()
        
        with monitor.measure('pose_detection'):
            result = pose_model(frame)
        
        # Later, get stats
        stats = monitor.get_stats()
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self._timings: Dict[str, List[float]] = {}
        self._current_measurements: Dict[str, float] = {}
    
    @contextmanager
    def measure(self, component: str):
        """Context manager to measure execution time of a component.
        
        Args:
            component: Name of the component being measured
            
        Usage:
            with monitor.measure('yolov8_pose'):
                result = model(frame)
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if component not in self._timings:
                self._timings[component] = []
            self._timings[component].append(elapsed)
            self._current_measurements[component] = elapsed
    
    def record(self, component: str, elapsed_time: float):
        """Manually record a timing.
        
        Args:
            component: Name of the component
            elapsed_time: Time taken in seconds
        """
        if component not in self._timings:
            self._timings[component] = []
        self._timings[component].append(elapsed_time)
        self._current_measurements[component] = elapsed_time
    
    def get_stats(self, component: Optional[str] = None) -> Dict:
        """Get performance statistics.
        
        Args:
            component: Specific component to get stats for, or None for all
            
        Returns:
            Dictionary with performance statistics
        """
        if component:
            return self._compute_component_stats(component)
        else:
            return {
                comp: self._compute_component_stats(comp)
                for comp in self._timings.keys()
            }
    
    def _compute_component_stats(self, component: str) -> Dict:
        """Compute statistics for a single component."""
        timings = self._timings.get(component, [])
        
        if not timings:
            return {
                'count': 0,
                'total_ms': 0.0,
                'mean_ms': 0.0,
                'median_ms': 0.0,
                'min_ms': 0.0,
                'max_ms': 0.0,
                'std_ms': 0.0,
            }
        
        timings_ms = [t * 1000 for t in timings]
        
        return {
            'count': len(timings),
            'total_ms': sum(timings_ms),
            'mean_ms': statistics.mean(timings_ms),
            'median_ms': statistics.median(timings_ms),
            'min_ms': min(timings_ms),
            'max_ms': max(timings_ms),
            'std_ms': statistics.stdev(timings_ms) if len(timings) > 1 else 0.0,
        }
    
    def get_bottlenecks(self, top_n: int = 5) -> List[tuple]:
        """Identify top N bottlenecks by total time.
        
        Args:
            top_n: Number of top bottlenecks to return
            
        Returns:
            List of (component, total_time_ms) tuples, sorted by time
        """
        component_times = []
        for component, timings in self._timings.items():
            total_ms = sum(t * 1000 for t in timings)
            component_times.append((component, total_ms))
        
        # Sort by total time descending
        component_times.sort(key=lambda x: x[1], reverse=True)
        return component_times[:top_n]
    
    def get_per_frame_breakdown(self) -> Dict[str, float]:
        """Get average time per frame for each component.
        
        Returns:
            Dictionary mapping component to average time per frame in ms
        """
        breakdown = {}
        for component, timings in self._timings.items():
            if timings:
                breakdown[component] = statistics.mean(timings) * 1000
        return breakdown
    
    def print_summary(self, frame_count: Optional[int] = None):
        """Print a formatted summary of performance metrics.
        
        Args:
            frame_count: Total frames processed (for FPS calculation)
        """
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)
        
        # Get all stats
        all_stats = self.get_stats()
        
        if not all_stats:
            print("No performance data collected.")
            return
        
        # Print per-component stats
        print("\nPer-Component Timing (in milliseconds):")
        print("-" * 70)
        print(f"{'Component':<30} {'Mean':<10} {'Median':<10} {'Total':<12}")
        print("-" * 70)
        
        total_time_ms = 0.0
        for component, stats in sorted(all_stats.items(), key=lambda x: x[1]['total_ms'], reverse=True):
            if stats['count'] > 0:
                print(f"{component:<30} {stats['mean_ms']:>8.1f} ms {stats['median_ms']:>8.1f} ms {stats['total_ms']:>10.1f} ms")
                total_time_ms += stats['total_ms']
        
        print("-" * 70)
        print(f"{'TOTAL':<30} {'':>10} {'':>10} {total_time_ms:>10.1f} ms")
        
        # Print bottlenecks
        print("\nTop Bottlenecks:")
        print("-" * 70)
        bottlenecks = self.get_bottlenecks(top_n=5)
        for i, (component, time_ms) in enumerate(bottlenecks, 1):
            pct = (time_ms / total_time_ms * 100) if total_time_ms > 0 else 0
            print(f"{i}. {component:<30} {time_ms:>10.1f} ms ({pct:>5.1f}%)")
        
        # Overall stats
        if frame_count:
            total_time_s = total_time_ms / 1000
            fps = frame_count / total_time_s if total_time_s > 0 else 0
            time_per_frame = total_time_s / frame_count if frame_count > 0 else 0
            
            print("\nOverall Performance:")
            print("-" * 70)
            print(f"Total frames: {frame_count}")
            print(f"Total time: {total_time_s:.2f} seconds")
            print(f"Average FPS: {fps:.2f}")
            print(f"Time per frame: {time_per_frame*1000:.1f} ms")
        
        print("=" * 70)
    
    def reset(self):
        """Reset all collected timings."""
        self._timings.clear()
        self._current_measurements.clear()
    
    def __str__(self) -> str:
        """Return string representation of current stats."""
        stats = self.get_stats()
        if not stats:
            return "PerformanceMonitor (no data)"
        
        total_time = sum(s['total_ms'] for s in stats.values())
        components = len(stats)
        
        return f"PerformanceMonitor ({components} components, {total_time:.1f}ms total)"


def create_default_monitor() -> PerformanceMonitor:
    """Create a performance monitor with standard component names.
    
    Returns:
        PerformanceMonitor instance
    """
    return PerformanceMonitor()


if __name__ == "__main__":
    # Demo usage
    import random
    
    print("Performance Monitor Demo")
    print("=" * 50)
    
    monitor = PerformanceMonitor()
    
    # Simulate processing 10 frames
    for frame_idx in range(10):
        # Simulate different components
        with monitor.measure('yolov8_pose'):
            time.sleep(random.uniform(0.03, 0.05))  # 30-50ms
        
        with monitor.measure('yolov8_face'):
            time.sleep(random.uniform(0.01, 0.02))  # 10-20ms
        
        with monitor.measure('mediapipe_hands'):
            time.sleep(random.uniform(0.015, 0.025))  # 15-25ms
        
        with monitor.measure('maskrcnn'):
            time.sleep(random.uniform(0.1, 0.15))  # 100-150ms (bottleneck)
        
        with monitor.measure('csv_write'):
            time.sleep(random.uniform(0.001, 0.002))  # 1-2ms
    
    # Print summary
    monitor.print_summary(frame_count=10)
