import unittest

from htmlnode import HTMLNode


class TestTextNode(unittest.TestCase):
    def test_repr(self):
        child = HTMLNode("p", "Paragraph", None, None)
        parent = HTMLNode("a", "Value", [child], {"href": "http://example.com"})
        self.assertEqual(
            repr(parent),
            "HTMLNode('a', 'Value', [HTMLNode('p', 'Paragraph', [], {})], {'href': 'http://example.com'})",
        )


if __name__ == "__main__":
    _ = unittest.main()
