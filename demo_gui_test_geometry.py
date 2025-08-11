import sys

# Add the parent directory to the path to find the 'gui' module
sys.path.insert(0, '.')

from gui.rect import Point, Rect

# --- Simple Test Runner ---
_test_count = 0
_fail_count = 0

def assert_equal(actual, expected, message):
    """A simple assertion helper for our test runner."""
    global _test_count, _fail_count
    _test_count += 1
    if actual == expected:
        # ANSI escape code for green text
        print(f"\033[92mPASS\033[0m: {message}")
    else:
        # ANSI escape code for red text
        print(f"\033[91mFAIL\033[0m: {message}")
        print(f"      Expected: {expected}, Actual: {actual}")
        _fail_count += 1

# --- Test Functions ---

def test_point_logic():
    print("\n--- Testing Point Class ---")
    p1 = Point(10, 20)
    p2 = Point(10, 20)
    p3 = Point(30, 40)
    
    assert_equal(p1.x, 10, "Point initializes x correctly")
    assert_equal(p1.y, 20, "Point initializes y correctly")
    assert_equal(p1, p2, "Points with same coordinates are equal")
    assert_equal(p1 != p3, True, "Points with different coordinates are not equal")
    
    p_copy = p1.copy()
    assert_equal(p1, p_copy, "Copied point is equal to the original")
    p_copy.x = 99
    assert_equal(p1.x, 10, "Modifying a copy does not affect the original")

def test_rect_logic():
    print("\n--- Testing Rect Class ---")
    r = Rect(10, 20, 109, 79) # Creates a 100x60 rectangle

    # Test properties
    assert_equal(r.width, 100, "Rect width property is correct")
    assert_equal(r.height, 60, "Rect height property is correct")
    assert_equal(r.center, Point(60, 50), "Rect center property is correct")

    # Test contains()
    assert_equal(r.contains(10, 20), True, "Contains top-left corner")
    assert_equal(r.contains(109, 79), True, "Contains bottom-right corner")
    assert_equal(r.contains(50, 50), True, "Contains a point inside")
    assert_equal(r.contains(9, 20), False, "Does not contain point to the left")
    assert_equal(r.contains(110, 79), False, "Does not contain point to the right")
    assert_equal(r.contains(10, 19), False, "Does not contain point above")
    assert_equal(r.contains(10, 80), False, "Does not contain point below")
    assert_equal(r.contains(Point(50, 50)), True, "Contains a Point object")

    # Test overlaps()
    r_overlap = Rect(100, 70, 200, 170)
    r_no_overlap = Rect(200, 200, 300, 300)
    assert_equal(r.overlaps(r_overlap), True, "Detects overlapping rectangle")
    assert_equal(r.overlaps(r_no_overlap), False, "Detects non-overlapping rectangle")

    # Test manipulation
    r_copy = r.copy()
    r_copy.move_to(0, 0)
    assert_equal(r_copy.left, 0, "move_to() sets left correctly")
    assert_equal(r_copy.top, 0, "move_to() sets top correctly")
    assert_equal(r_copy.width, 100, "move_to() preserves width")
    assert_equal(r_copy.height, 60, "move_to() preserves height")

    r_copy.shift(5, -5)
    assert_equal(r_copy.top_left, Point(5, -5), "shift() moves the rectangle correctly")


print("Starting geometry tests...")
test_point_logic()
test_rect_logic()
print("\n-------------------------")
if _fail_count == 0:
    print(f"\033[92mAll {_test_count} tests passed!\033[0m")
else:
    print(f"\033[91m{_fail_count} out of {_test_count} tests failed.\033[0m")
    # Exit with a non-zero code to indicate failure for scripts
    sys.exit(1)