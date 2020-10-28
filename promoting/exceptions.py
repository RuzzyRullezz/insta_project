class IgLimitReachedException(RuntimeError):
    pass


class ConditionWaitException(RuntimeError):
    pass


class SpamUnblockWait(ConditionWaitException):
    pass


class ChangeFriendshipWait(ConditionWaitException):
    pass


class UserRestrictedWait(ConditionWaitException):
    pass
