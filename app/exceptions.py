class PermissionDenied(Exception):
    """权限不足异常"""
    def __init__(self, message="权限不足"):
        self.message = message
        super().__init__(self.message)