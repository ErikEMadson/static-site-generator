import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_url_default(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertIs(node.url, None)

    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(
            repr(node), 'TextNode("This is a text node", TextType.BOLD, None)'
        )

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node3 = TextNode(
            "This is a test node", TextType.PLAIN, "https://example.com"
        )
        self.assertNotEqual(node, node3)

    def test_different_type_repr(self):
        node3 = TextNode(
            "This is a test node", TextType.PLAIN, "https://example.com"
        )
        self.assertEqual(
            repr(node3),
            'TextNode("This is a test node", TextType.PLAIN, "https://example.com")',
        )


if __name__ == "__main__":
    _ = unittest.main()
