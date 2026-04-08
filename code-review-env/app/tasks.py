# All 3 task definitions + graders
from app.models import Observation

TASKS = {
    "easy_bug_detection": {
        "id": "easy_bug_detection",
        "max_steps": 5,
        "pr_title": "Fix: Update list iteration in user processor",
        "pr_description": (
            "This PR updates the user processing function to iterate "
            "through all users and apply a discount. Simple change."
        ),
        "file_names": ["user_processor.py"],
        "code_diff": """\
--- a/user_processor.py
+++ b/user_processor.py
@@ -1,18 +1,18 @@
 def apply_discount(users, discount_rate):
     \"\"\"Apply discount to all users in the list.\"\"\"
     results = []
-    for i in range(len(users) - 1):   # iterate through users
+    for i in range(len(users)):
         user = users[i]
         original_price = user['price']
-        discounted = original_price * discount_rate
+        discounted = original_price * (1 - discount_rate)
         results.append({
             'user_id': user['id'],
-            'discount_applied': True,
+            'discount_applied': True,
             'final_price': discounted
         })
     return results

 def process_batch(user_list):
     unused_variable = []   # this was left in by accident
     return apply_discount(user_list, 0.1)
""",
        # What a perfect grader looks for
        "expected_issues": {
            "bugs": [
                "off-by-one error",
                "range(len(users) - 1)",
                "last user skipped",
                "missing last element",
                "incorrect discount formula",
                "discount formula wrong",
                "multiplying by rate instead of subtracting",
            ],
            "style": [
                "unused_variable",
                "unused variable",
                "dead code",
            ],
            "verdict": "request_changes",
            "required_flags": ["bug"],
            "optional_flags": ["style"],
        },
    },

    "medium_security_review": {
        "id": "medium_security_review",
        "max_steps": 5,
        "pr_title": "Feature: Add user search endpoint with database lookup",
        "pr_description": (
            "Adds a new /search endpoint that lets users search by name. "
            "Also fixes the pagination logic that was returning wrong page counts."
        ),
        "file_names": ["api/search.py", "utils/pagination.py"],
        "code_diff": """\
--- a/api/search.py
+++ b/api/search.py
@@ -0,0 +1,24 @@
+import sqlite3
+
+def search_users(db_path, username_query):
+    \"\"\"Search users by name from the database.\"\"\"
+    conn = sqlite3.connect(db_path)
+    cursor = conn.cursor()
+    # Build query dynamically from user input
+    query = f"SELECT * FROM users WHERE name = '{username_query}'"
+    cursor.execute(query)
+    results = cursor.fetchall()
+    conn.close()
+    return results
+
+def get_user_by_id(db_path, user_id):
+    \"\"\"Fetch a user by their ID.\"\"\"
+    conn = sqlite3.connect(db_path)
+    cursor = conn.cursor()
+    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
+    result = cursor.fetchone()
+    conn.close()
+    return result

--- a/utils/pagination.py
+++ b/utils/pagination.py
@@ -3,7 +3,7 @@
 def get_page_count(total_items, page_size):
     \"\"\"Calculate total number of pages.\"\"\"
-    return total_items // page_size
+    return (total_items + page_size - 1) // page_size

""",
        "expected_issues": {
            "security": [
                "sql injection",
                "sql injection vulnerability",
                "f-string query",
                "string interpolation",
                "unsanitized input",
                "parameterized query",
                "user input directly in query",
            ],
            "bugs": [
                "integer division",
                "floor division",
                "pagination wrong",
                "missing last page",
                "page count incorrect",
                "truncates",
            ],
            "verdict": "request_changes",
            "required_flags": ["security", "bug"],
            "optional_flags": ["logic"],
        },
    },

    "hard_concurrency_review": {
        "id": "hard_concurrency_review",
        "max_steps": 5,
        "pr_title": "Perf: Parallel order processing with shared state cache",
        "pr_description": (
            "Refactors the order processor to run in parallel threads for speed. "
            "Adds a shared cache to avoid re-fetching order data. "
            "Also adds retry logic for failed orders."
        ),
        "file_names": ["orders/processor.py", "orders/cache.py", "orders/retry.py"],
        "code_diff": """\
--- a/orders/processor.py
+++ b/orders/processor.py
@@ -0,0 +1,40 @@
+import threading
+from orders.cache import order_cache
+
+# Shared mutable state - no locking
+processed_orders = []
+failed_count = 0
+
+def process_order(order):
+    global failed_count
+    try:
+        # Check cache first
+        cached = order_cache.get(order['id'])
+        if cached:
+            processed_orders.append(cached)   # race condition: list not thread-safe
+            return
+
+        result = expensive_computation(order)
+        order_cache.set(order['id'], result)
+        processed_orders.append(result)        # race condition here too
+    except:                                    # bare except catches everything
+        failed_count += 1                      # race condition on integer
+        pass                                   # silently swallows all errors
+
+def run_parallel(orders):
+    threads = []
+    for order in orders:
+        t = threading.Thread(target=process_order, args=(order,))
+        threads.append(t)
+        t.start()
+    # Missing: join threads before returning
+    return processed_orders
+
--- a/orders/cache.py
+++ b/orders/cache.py
@@ -0,0 +1,12 @@
+class OrderCache:
+    def __init__(self):
+        self.data = {}          # dict not thread-safe for concurrent writes
+
+    def get(self, key):
+        return self.data.get(key)
+
+    def set(self, key, value):
+        self.data[key] = value  # concurrent writes can corrupt dict
+
+order_cache = OrderCache()
+
--- a/orders/retry.py
+++ b/orders/retry.py
@@ -0,0 +1,14 @@
+def retry_failed(orders, max_retries=3):
+    # Variable name 'l' is misleading - actually a list of failed orders
+    l = [o for o in orders if o.get('status') == 'failed']
+    attempt = 0
+    while attempt < max_retries:
+        for order in l:
+            try:
+                process_order(order)
+            except Exception as e:
+                pass              # still swallows exceptions in retry
+        attempt += 1
+    # Returns None implicitly - caller gets no feedback
+
""",
        "expected_issues": {
            "bugs": [
                "race condition",
                "thread safety",
                "threads not joined",
                "missing join",
                "thread join",
                "list not thread-safe",
            ],
            "security": [
                "bare except",
                "silently swallows",
                "exception swallowed",
                "errors hidden",
            ],
            "style": [
                "misleading variable",
                "variable name l",
                "single letter variable",
                "unclear variable name",
            ],
            "logic": [
                "returns none",
                "no return value",
                "caller gets no feedback",
                "dict not thread-safe",
                "concurrent writes",
            ],
            "verdict": "reject",
            "required_flags": ["bug", "logic"],
            "optional_flags": ["security", "style", "performance"],
        },
    },
}


def get_task_observation(task_id: str, step_number: int = 0) -> Observation:
    task = TASKS[task_id]
    return Observation(
        pr_title=task["pr_title"],
        pr_description=task["pr_description"],
        code_diff=task["code_diff"],
        file_names=task["file_names"],
        task_id=task_id,
        step_number=step_number,
        max_steps=task["max_steps"],
    )