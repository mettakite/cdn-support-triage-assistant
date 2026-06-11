import unittest

from triage import classify_ticket, load_ticket, triage_ticket


class TestTriageAssistant(unittest.TestCase):
    def test_classifies_stale_content(self):
        ticket = "Users are seeing stale cached content after a deploy."
        self.assertEqual(classify_ticket(ticket), "stale_content")

    def test_classifies_redirect_loop(self):
        ticket = "The page is stuck in a redirect loop after HTTP to HTTPS changes."
        self.assertEqual(classify_ticket(ticket), "redirect_loop")

    def test_classifies_server_error(self):
        ticket = "Users are seeing 503 Service Unavailable errors from the origin."
        self.assertEqual(classify_ticket(ticket), "server_error")

    def test_classifies_header_behavior(self):
        ticket = "The response changes depending on request headers from the mobile app."
        self.assertEqual(classify_ticket(ticket), "header_behavior")

    def test_unknown_ticket(self):
        ticket = "Something is wrong but we do not have any details yet."
        self.assertEqual(classify_ticket(ticket), "unknown")

    def test_triage_output_contains_customer_response(self):
        ticket = "Users are seeing stale cached content."
        result = triage_ticket(ticket)
        self.assertIn("Customer-safe response draft", result)
        self.assertIn("Evidence to collect", result)

    def test_load_ticket_reads_example_file(self):
        ticket = load_ticket("examples/stale_content.txt")
        self.assertIn("old version", ticket)


if __name__ == "__main__":
    unittest.main()
