"""Retry decorator for E2E tests to handle LLM non-determinism.

This module provides a retry mechanism specifically designed for E2E tests
that interact with LLMs. Since LLM responses are non-deterministic, a test
might occasionally fail due to response variation rather than actual bugs.

The retry decorator will:
1. Run the test up to 3 times
2. Pass if ANY attempt succeeds
3. Only fail if ALL 3 attempts fail
4. Track which attempt succeeded for debugging
"""

import functools
from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable)


def retry_on_llm_variability(max_attempts: int = 3) -> Callable[[F], F]:
    """Retry a test up to max_attempts times to handle LLM non-determinism.

    This decorator is specifically for E2E tests that call LLMs. Since LLM
    responses can vary, a test might fail occasionally due to response
    variation rather than actual system failures.

    Args:
        max_attempts: Maximum number of attempts (default: 3)

    Returns:
        Decorated test function that retries on failure

    Example:
        @pytest.mark.e2e
        @retry_on_llm_variability(max_attempts=3)
        def test_combo_detection(self, interactor):
            response = interactor.find_combo_pieces("Isochron Scepter")
            assert "combo" in response.lower()

    Note:
        - Only retries on AssertionError (test failures)
        - Other exceptions (system errors) fail immediately
        - Prints which attempt succeeded for debugging

    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    # Test passed!
                    if attempt > 1:
                        print(f"\n✓ Test passed on attempt {attempt}/{max_attempts}")
                    return result
                except AssertionError as e:
                    # Test failed - might be LLM variability
                    last_exception = e
                    if attempt < max_attempts:
                        print(f"\n⚠ Test failed on attempt {attempt}/{max_attempts}, retrying...")
                        print(f"   Reason: {str(e)[:100]}...")
                    continue
                except Exception:
                    # System error (not LLM variability) - fail immediately
                    print(f"\n✗ System error on attempt {attempt}/{max_attempts} (not retrying)")
                    raise

            # All attempts failed
            print(f"\n✗ Test failed on all {max_attempts} attempts")
            raise last_exception

        return wrapper

    return decorator


def retry_on_assertion(max_attempts: int = 3, verbose: bool = True) -> Callable[[F], F]:
    """Simplified retry decorator that retries on any AssertionError.

    This is a more general version that can be used for any test that might
    have flaky assertions.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        verbose: Whether to print retry information (default: True)

    Returns:
        Decorated test function that retries on assertion failures

    Example:
        @pytest.mark.e2e
        @retry_on_assertion(max_attempts=3, verbose=True)
        def test_something(self):
            assert potentially_flaky_check()

    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if verbose and attempt > 1:
                        print(f"\n✓ Passed on attempt {attempt}/{max_attempts}")
                    return result
                except AssertionError as e:
                    last_exception = e
                    if verbose and attempt < max_attempts:
                        print(f"\n⚠ Failed attempt {attempt}/{max_attempts}, retrying...")
                    continue
                except Exception:
                    # Non-assertion errors fail immediately
                    raise

            # All attempts failed
            if verbose:
                print(f"\n✗ Failed all {max_attempts} attempts")
            raise last_exception

        return wrapper

    return decorator
