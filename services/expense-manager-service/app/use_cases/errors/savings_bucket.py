"""Errors related to savings bucket operations in use cases."""

from app.use_cases.errors.base import ExpenseManagerUseCaseError


class SavingsBucketNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when a savings bucket is not found."""

    def __init__(self, bucket_id: str):
        """Initialize the error with the bucket ID."""
        super().__init__(f"Savings bucket with ID '{bucket_id}' not found.")
        self.bucket_id = bucket_id


class SavingsBucketDuplicateNameError(ExpenseManagerUseCaseError):
    """Error raised when a bucket name already exists in an account."""

    def __init__(self, name: str):
        """Initialize the error with the bucket name."""
        super().__init__(f"A savings bucket with the name '{name}' already exists for this account.")
        self.name = name


class SavingsBucketProtectedError(ExpenseManagerUseCaseError):
    """Error raised when trying to delete a protected bucket like the root Savings bucket."""

    def __init__(self, name: str):
        """Initialize the error with the bucket name."""
        super().__init__(f"The bucket '{name}' is protected and cannot be deleted.")
        self.name = name


class SavingsBucketInsufficientFundsError(ExpenseManagerUseCaseError):
    """Error raised when a bucket doesn't have enough balance for a transaction."""

    def __init__(self, name: str, current_balance: float, requested_amount: float):
        """Initialize the error."""
        super().__init__(
            f"Insufficient funds in bucket '{name}'. "
            f"Current balance is {current_balance}, but requested {requested_amount}."
        )
        self.name = name
        self.current_balance = current_balance
        self.requested_amount = requested_amount
