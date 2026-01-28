"""
Error handling utilities for robust pipeline operation.

Provides graceful degradation, retry logic, and failure tracking.
"""
import functools
import logging
from typing import Callable, Any, Optional, TypeVar, Tuple
from collections import deque


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


T = TypeVar('T')


class FailureTracker:
    """Track consecutive failures to detect persistent problems.
    
    Useful for deciding when to stop processing or skip a component.
    """
    
    def __init__(self, max_consecutive_failures: int = 10):
        """Initialize failure tracker.
        
        Args:
            max_consecutive_failures: Stop after this many consecutive failures
        """
        self.max_consecutive_failures = max_consecutive_failures
        self.consecutive_failures = 0
        self.total_failures = 0
        self.total_attempts = 0
    
    def record_success(self):
        """Record a successful operation."""
        self.consecutive_failures = 0
        self.total_attempts += 1
    
    def record_failure(self):
        """Record a failed operation."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.total_attempts += 1
    
    def should_stop(self) -> bool:
        """Check if we should stop due to too many failures."""
        return self.consecutive_failures >= self.max_consecutive_failures
    
    def get_failure_rate(self) -> float:
        """Get overall failure rate (0.0 to 1.0)."""
        if self.total_attempts == 0:
            return 0.0
        return self.total_failures / self.total_attempts
    
    def __str__(self) -> str:
        """Return string representation of failure stats."""
        rate = self.get_failure_rate()
        return (
            f"FailureTracker: {self.total_failures}/{self.total_attempts} failures "
            f"({rate:.1%}), {self.consecutive_failures} consecutive"
        )


def with_fallback(
    fallback_value: T,
    log_errors: bool = True,
    component_name: str = "unknown"
) -> Callable:
    """Decorator to provide fallback value on exception.
    
    Args:
        fallback_value: Value to return if function raises exception
        log_errors: Whether to log exceptions
        component_name: Name of component for logging
        
    Returns:
        Decorated function that returns fallback on error
        
    Usage:
        @with_fallback(fallback_value=None, component_name="pose_detection")
        def detect_pose(frame):
            return model(frame)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.warning(
                        f"{component_name} failed: {type(e).__name__}: {e}. "
                        f"Using fallback value."
                    )
                return fallback_value
        return wrapper
    return decorator


def with_retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    log_errors: bool = True,
    component_name: str = "unknown"
) -> Callable:
    """Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        log_errors: Whether to log retry attempts
        component_name: Name of component for logging
        
    Returns:
        Decorated function that retries on failure
        
    Usage:
        @with_retry(max_attempts=3, component_name="hand_detection")
        def detect_hands(frame):
            return hand_detector(frame)
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if log_errors and attempt < max_attempts - 1:
                        logger.warning(
                            f"{component_name} attempt {attempt+1}/{max_attempts} failed: "
                            f"{type(e).__name__}: {e}. Retrying..."
                        )
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            
            # All attempts failed
            if log_errors:
                logger.error(
                    f"{component_name} failed after {max_attempts} attempts. "
                    f"Last error: {type(last_exception).__name__}: {last_exception}"
                )
            raise last_exception
        return wrapper
    return decorator


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default on division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Value to return if denominator is zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def validate_detection_result(
    result: Any,
    min_confidence: float = 0.0,
    required_fields: Optional[list] = None
) -> Tuple[bool, str]:
    """Validate a detection result.
    
    Args:
        result: Detection result to validate
        min_confidence: Minimum confidence threshold
        required_fields: List of required field names (if result is dict)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if result is None:
        return False, "Result is None"
    
    # Check confidence if available
    if hasattr(result, 'conf'):
        if result.conf < min_confidence:
            return False, f"Confidence {result.conf} < {min_confidence}"
    
    # Check required fields if result is dict
    if required_fields and isinstance(result, dict):
        missing = [f for f in required_fields if f not in result]
        if missing:
            return False, f"Missing fields: {', '.join(missing)}"
    
    return True, ""


class GracefulDegradation:
    """Manager for graceful degradation when components fail.
    
    Tracks which components are working and automatically skips failing ones.
    """
    
    def __init__(self, failure_threshold: int = 5):
        """Initialize graceful degradation manager.
        
        Args:
            failure_threshold: Disable component after this many consecutive failures
        """
        self.failure_threshold = failure_threshold
        self.component_failures = {}
        self.disabled_components = set()
    
    def is_enabled(self, component: str) -> bool:
        """Check if a component is enabled.
        
        Args:
            component: Component name
            
        Returns:
            True if component should be used
        """
        return component not in self.disabled_components
    
    def record_success(self, component: str):
        """Record successful operation for a component.
        
        Args:
            component: Component name
        """
        if component in self.component_failures:
            self.component_failures[component] = 0
        
        # Re-enable if it was disabled
        if component in self.disabled_components:
            logger.info(f"Re-enabling component: {component}")
            self.disabled_components.remove(component)
    
    def record_failure(self, component: str):
        """Record failed operation for a component.
        
        Args:
            component: Component name
        """
        if component not in self.component_failures:
            self.component_failures[component] = 0
        
        self.component_failures[component] += 1
        
        # Disable if threshold exceeded
        if self.component_failures[component] >= self.failure_threshold:
            if component not in self.disabled_components:
                logger.warning(
                    f"Disabling component '{component}' after {self.failure_threshold} "
                    f"consecutive failures"
                )
                self.disabled_components.add(component)
    
    def get_status(self) -> dict:
        """Get status of all components.
        
        Returns:
            Dictionary mapping component to status info
        """
        status = {}
        for component, failures in self.component_failures.items():
            status[component] = {
                'failures': failures,
                'enabled': component not in self.disabled_components,
            }
        return status
    
    def __str__(self) -> str:
        """Return string representation of degradation status."""
        enabled = len([c for c in self.component_failures if c not in self.disabled_components])
        disabled = len(self.disabled_components)
        return f"GracefulDegradation: {enabled} enabled, {disabled} disabled"


if __name__ == "__main__":
    # Demo usage
    print("Error Handling Utilities Demo")
    print("=" * 50)
    
    # Test FailureTracker
    print("\n1. FailureTracker Demo:")
    tracker = FailureTracker(max_consecutive_failures=3)
    
    tracker.record_success()
    tracker.record_failure()
    tracker.record_failure()
    print(f"After 1 success, 2 failures: {tracker}")
    print(f"Should stop? {tracker.should_stop()}")
    
    tracker.record_failure()
    print(f"After 3 consecutive failures: {tracker}")
    print(f"Should stop? {tracker.should_stop()}")
    
    # Test with_fallback
    print("\n2. with_fallback Demo:")
    
    @with_fallback(fallback_value=None, component_name="test_function")
    def failing_function():
        raise ValueError("Test error")
    
    result = failing_function()
    print(f"Result from failing function: {result}")
    
    # Test GracefulDegradation
    print("\n3. GracefulDegradation Demo:")
    degradation = GracefulDegradation(failure_threshold=2)
    
    print(f"Initial: hand_detection enabled? {degradation.is_enabled('hand_detection')}")
    
    degradation.record_failure('hand_detection')
    degradation.record_failure('hand_detection')
    
    print(f"After 2 failures: hand_detection enabled? {degradation.is_enabled('hand_detection')}")
    print(f"Status: {degradation}")
