class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def traverse_tree(node):
    if node is None:
        return

    # Process the current node
    print(node.val)

    # Recursively traverse the left subtree
    traverse_tree(node.left)

    # Recursively traverse the right subtree
    traverse_tree(node.right)
