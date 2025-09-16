import unittest

from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_repr(self):
        node = LeafNode(
            "a", "This is a leaf node", {"href": "http://example.com"}
        )
        self.assertEqual(
            repr(node),
            "LeafNode('a', 'This is a leaf node', {'href': 'http://example.com'})",
        )


if __name__ == "__main__":
    _ = unittest.main()
