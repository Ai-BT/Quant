"""
Upbit API 예외 처리
"""


class UpbitError(Exception):
    """Upbit API 기본 예외"""
    pass


class UpbitAuthError(UpbitError):
    """인증 오류"""
    pass


class UpbitRateLimitError(UpbitError):
    """Rate Limit 오류"""
    pass


class UpbitAPIError(UpbitError):
    """API 오류"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code



