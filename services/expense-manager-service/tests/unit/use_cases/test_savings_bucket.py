"""Unit tests for the Savings Bucket use case service."""

import pytest
import uuid
from datetime import datetime, UTC

from app.use_cases.account import AccountService
from app.use_cases.savings_bucket import SavingsBucketService
from app.use_cases.errors.savings_bucket import (
    SavingsBucketDuplicateNameError,
    SavingsBucketInsufficientFundsError,
    SavingsBucketNotFoundError,
    SavingsBucketProtectedError,
)


@pytest.fixture(scope="module")
def account_service(account_repo) -> AccountService:
    """Provide an instance of AccountService."""
    return AccountService(account_repository=account_repo)


@pytest.fixture(scope="module")
def savings_bucket_service(savings_bucket_repo) -> SavingsBucketService:
    """Provide an instance of SavingsBucketService."""
    return SavingsBucketService(savings_bucket_repository=savings_bucket_repo)


async def create_test_account(account_service: AccountService, name: str = None) -> str:
    """Helper to create a new unique test account and return its ID."""
    unique_name = name or f"Savings-Test-Account-{uuid.uuid4().hex[:8]}"
    acc = await account_service.account_repository.get_or_create_account(account_name=unique_name)
    return acc.id


class TestSavingsBucketAutoSeeding:
    async def test__auto_seeding__success(self, account_service, savings_bucket_service):
        """Test retrieving buckets for a brand new account triggers auto-seeding of defaults."""
        account_id = await create_test_account(account_service)
        
        # Initially no buckets in DB, retrieving should auto-seed
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        
        assert len(buckets) == 4
        names = [b.name for b in buckets]
        assert "Savings" in names
        assert "Minimum Balance" in names
        assert "Medical Insurance" in names
        assert "LIC" in names
        
        # Verify initial balances are 0.0
        for b in buckets:
            assert b.allocated_amount == 0.0
            assert b.target_amount is None


class TestSavingsBucketCRUD:
    async def test__create_bucket__success(self, account_service, savings_bucket_service):
        """Test creating a custom bucket successfully."""
        account_id = await create_test_account(account_service)
        await savings_bucket_service.get_buckets_for_account(account_id)  # Seed defaults
        
        new_bucket = await savings_bucket_service.create_bucket(
            account_id=account_id,
            name="Emergency Fund",
            target_amount=50000.0
        )
        
        assert new_bucket.name == "Emergency Fund"
        assert new_bucket.target_amount == 50000.0
        assert new_bucket.allocated_amount == 0.0
        
        # Verify it lists
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        assert any(b.id == new_bucket.id for b in buckets)

    async def test__create_bucket__duplicate_name(self, account_service, savings_bucket_service):
        """Test creating a bucket with an existing name raises error."""
        account_id = await create_test_account(account_service)
        await savings_bucket_service.get_buckets_for_account(account_id)
        
        # Try to create duplicate of 'LIC'
        with pytest.raises(SavingsBucketDuplicateNameError):
            await savings_bucket_service.create_bucket(account_id=account_id, name="LIC")

    async def test__edit_bucket__success(self, account_service, savings_bucket_service):
        """Test editing a bucket's name and target."""
        account_id = await create_test_account(account_service)
        await savings_bucket_service.get_buckets_for_account(account_id)
        
        custom_bucket = await savings_bucket_service.create_bucket(account_id=account_id, name="Car Fund")
        
        # Edit
        updated = await savings_bucket_service.edit_bucket(
            bucket_id=custom_bucket.id,
            name="Tesla Fund",
            target_amount=80000.0
        )
        
        assert updated.name == "Tesla Fund"
        assert updated.target_amount == 80000.0

    async def test__edit_bucket__rename_savings_fails(self, account_service, savings_bucket_service):
        """Test that renaming the root Savings bucket is blocked."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        
        with pytest.raises(SavingsBucketProtectedError):
            await savings_bucket_service.edit_bucket(bucket_id=savings.id, name="General Pool")

    async def test__delete_bucket__protection(self, account_service, savings_bucket_service):
        """Test that deleting the root Savings bucket is protected/blocked."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        
        with pytest.raises(SavingsBucketProtectedError):
            await savings_bucket_service.delete_bucket(bucket_id=savings.id)


class TestSavingsBucketTransactions:
    async def test__deposit_and_ledger(self, account_service, savings_bucket_service):
        """Test depositing money into Savings and checking the ledger/balance."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        
        # Deposit ₹10,000 to Savings
        tx = await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=None,
            destination_bucket_id=savings.id,
            amount=10000.0,
            transaction_type="deposit",
            description="Initial deposit to base pool"
        )
        
        assert tx.amount == 10000.0
        assert tx.transaction_type == "deposit"
        assert tx.description == "Initial deposit to base pool"
        
        # Verify bucket balance
        buckets_after = await savings_bucket_service.get_buckets_for_account(account_id)
        savings_after = next(b for b in buckets_after if b.name == "Savings")
        assert savings_after.allocated_amount == 10000.0
        
        # Verify transaction logs
        txs = await savings_bucket_service.get_transactions_for_account(account_id)
        assert len(txs) == 1
        assert txs[0].id == tx.id

    async def test__allocation_and_release(self, account_service, savings_bucket_service):
        """Test allocating funds from Savings to LIC, and releasing back to Savings."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        lic = next(b for b in buckets if b.name == "LIC")
        
        # Deposit ₹10,000 first
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=None,
            destination_bucket_id=savings.id,
            amount=10000.0,
            transaction_type="deposit",
            description="Seed"
        )
        
        # Allocate ₹4,000 from Savings to LIC
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=savings.id,
            destination_bucket_id=lic.id,
            amount=4000.0,
            transaction_type="allocate",
            description="LIC monthly reserve"
        )
        
        # Check balances
        buckets_after = await savings_bucket_service.get_buckets_for_account(account_id)
        s = next(b for b in buckets_after if b.name == "Savings")
        l = next(b for b in buckets_after if b.name == "LIC")
        assert s.allocated_amount == 6000.0
        assert l.allocated_amount == 4000.0
        
        # Release ₹1,500 from LIC back to Savings
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=lic.id,
            destination_bucket_id=savings.id,
            amount=1500.0,
            transaction_type="release",
            description="Excess LIC release"
        )
        
        # Check balances again
        buckets_final = await savings_bucket_service.get_buckets_for_account(account_id)
        s_final = next(b for b in buckets_final if b.name == "Savings")
        l_final = next(b for b in buckets_final if b.name == "LIC")
        assert s_final.allocated_amount == 7500.0
        assert l_final.allocated_amount == 2500.0

    async def test__allocation__insufficient_funds(self, account_service, savings_bucket_service):
        """Test allocating more than bucket balance raises insufficient funds error."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        lic = next(b for b in buckets if b.name == "LIC")
        
        # Try to allocate ₹500 when balance is ₹0
        with pytest.raises(SavingsBucketInsufficientFundsError):
            await savings_bucket_service.add_transaction(
                account_id=account_id,
                source_bucket_id=savings.id,
                destination_bucket_id=lic.id,
                amount=500.0,
                transaction_type="allocate",
                description="Failed allocation"
            )


class TestSavingsBucketSafeDeletionRefund:
    async def test__delete_bucket__safe_refund(self, account_service, savings_bucket_service):
        """Test deleting a custom bucket refunds its remaining balance back to Savings."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        
        # Deposit ₹10,000 to Savings
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=None,
            destination_bucket_id=savings.id,
            amount=10000.0,
            transaction_type="deposit",
            description="Seed pool"
        )
        
        # Create a new custom bucket "Vacation"
        vacation = await savings_bucket_service.create_bucket(account_id=account_id, name="Vacation")
        
        # Allocate ₹3,000 to "Vacation"
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=savings.id,
            destination_bucket_id=vacation.id,
            amount=3000.0,
            transaction_type="allocate",
            description="Vacation goal funding"
        )
        
        # Verify balances before delete
        buckets_before = await savings_bucket_service.get_buckets_for_account(account_id)
        s_before = next(b for b in buckets_before if b.name == "Savings")
        v_before = next(b for b in buckets_before if b.name == "Vacation")
        assert s_before.allocated_amount == 7000.0
        assert v_before.allocated_amount == 3000.0
        
        # Delete custom bucket "Vacation"
        await savings_bucket_service.delete_bucket(bucket_id=vacation.id)
        
        # Verify "Vacation" is deleted and balance is refunded to "Savings" (7000 + 3000 = 10000)
        buckets_after = await savings_bucket_service.get_buckets_for_account(account_id)
        assert not any(b.name == "Vacation" for b in buckets_after)
        
        s_after = next(b for b in buckets_after if b.name == "Savings")
        assert s_after.allocated_amount == 10000.0
        
        # Verify a "release" transaction log exists for the refund
        txs = await savings_bucket_service.get_transactions_for_account(account_id)
        refund_tx = next(t for t in txs if t.transaction_type == "release" and "Refunded remaining balance upon deletion" in t.description)
        assert refund_tx.amount == 3000.0
        assert refund_tx.destination_bucket_id == savings.id


class TestSavingsBucketCRUDExtended:
    async def test__edit_bucket__not_found(self, savings_bucket_service):
        """Test editing a non-existent bucket raises SavingsBucketNotFoundError."""
        random_id = uuid.uuid4().hex
        with pytest.raises(SavingsBucketNotFoundError):
            await savings_bucket_service.edit_bucket(bucket_id=random_id, name="Nonexistent")

    async def test__edit_bucket__duplicate_name(self, account_service, savings_bucket_service):
        """Test editing a bucket's name to an existing bucket's name raises duplicate error."""
        account_id = await create_test_account(account_service)
        await savings_bucket_service.get_buckets_for_account(account_id)  # Seed defaults
        
        # Create two custom buckets
        b1 = await savings_bucket_service.create_bucket(account_id=account_id, name="Emergency")
        b2 = await savings_bucket_service.create_bucket(account_id=account_id, name="Vacation")
        
        # Rename b1 to 'Vacation'
        with pytest.raises(SavingsBucketDuplicateNameError):
            await savings_bucket_service.edit_bucket(bucket_id=b1.id, name="Vacation")

    async def test__delete_bucket__not_found(self, savings_bucket_service):
        """Test deleting a non-existent bucket raises SavingsBucketNotFoundError."""
        random_id = uuid.uuid4().hex
        with pytest.raises(SavingsBucketNotFoundError):
            await savings_bucket_service.delete_bucket(bucket_id=random_id)


class TestSavingsBucketTransactionsExtended:
    async def test__add_transaction__zero_amount(self, account_service, savings_bucket_service):
        """Test that zero or negative transaction amounts raise ValueError."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        
        with pytest.raises(ValueError, match="Transaction amount must be greater than zero."):
            await savings_bucket_service.add_transaction(
                account_id=account_id,
                source_bucket_id=None,
                destination_bucket_id=savings.id,
                amount=0.0,
                transaction_type="deposit",
                description="Zero deposit"
            )

        with pytest.raises(ValueError, match="Transaction amount must be greater than zero."):
            await savings_bucket_service.add_transaction(
                account_id=account_id,
                source_bucket_id=None,
                destination_bucket_id=savings.id,
                amount=-100.0,
                transaction_type="deposit",
                description="Negative deposit"
            )

    async def test__add_transaction__source_not_found(self, account_service, savings_bucket_service):
        """Test that transaction with non-existent source bucket raises SavingsBucketNotFoundError."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        random_id = uuid.uuid4().hex
        
        with pytest.raises(SavingsBucketNotFoundError):
            await savings_bucket_service.add_transaction(
                account_id=account_id,
                source_bucket_id=random_id,
                destination_bucket_id=savings.id,
                amount=100.0,
                transaction_type="allocate",
                description="Invalid source"
            )

    async def test__add_transaction__destination_not_found(self, account_service, savings_bucket_service):
        """Test that transaction with non-existent destination bucket raises SavingsBucketNotFoundError."""
        account_id = await create_test_account(account_service)
        await savings_bucket_service.get_buckets_for_account(account_id)
        random_id = uuid.uuid4().hex
        
        with pytest.raises(SavingsBucketNotFoundError):
            await savings_bucket_service.add_transaction(
                account_id=account_id,
                source_bucket_id=None,
                destination_bucket_id=random_id,
                amount=100.0,
                transaction_type="deposit",
                description="Invalid destination"
            )

    async def test__add_transaction__source_account_mismatch(self, account_service, savings_bucket_service):
        """Test allocating from a bucket belonging to another account raises ValueError."""
        account_a_id = await create_test_account(account_service)
        account_b_id = await create_test_account(account_service)
        
        buckets_a = await savings_bucket_service.get_buckets_for_account(account_a_id)
        buckets_b = await savings_bucket_service.get_buckets_for_account(account_b_id)
        
        savings_a = next(b for b in buckets_a if b.name == "Savings")
        savings_b = next(b for b in buckets_b if b.name == "Savings")
        
        # Seed some money in savings_a
        await savings_bucket_service.add_transaction(
            account_id=account_a_id,
            source_bucket_id=None,
            destination_bucket_id=savings_a.id,
            amount=500.0,
            transaction_type="deposit",
            description="Seed A"
        )
        
        # Try to allocate from savings_a to savings_b inside account_b context
        with pytest.raises(ValueError, match="Source bucket does not belong to the selected account."):
            await savings_bucket_service.add_transaction(
                account_id=account_b_id,
                source_bucket_id=savings_a.id,
                destination_bucket_id=savings_b.id,
                amount=100.0,
                transaction_type="allocate",
                description="Cross account leak"
            )

    async def test__add_transaction__destination_account_mismatch(self, account_service, savings_bucket_service):
        """Test allocating to a bucket belonging to another account raises ValueError."""
        account_a_id = await create_test_account(account_service)
        account_b_id = await create_test_account(account_service)
        
        buckets_a = await savings_bucket_service.get_buckets_for_account(account_a_id)
        buckets_b = await savings_bucket_service.get_buckets_for_account(account_b_id)
        
        savings_a = next(b for b in buckets_a if b.name == "Savings")
        savings_b = next(b for b in buckets_b if b.name == "Savings")
        
        # Seed some money in savings_a
        await savings_bucket_service.add_transaction(
            account_id=account_a_id,
            source_bucket_id=None,
            destination_bucket_id=savings_a.id,
            amount=500.0,
            transaction_type="deposit",
            description="Seed A"
        )
        
        # Try to allocate from savings_a to savings_b inside account_a context
        with pytest.raises(ValueError, match="Destination bucket does not belong to the selected account."):
            await savings_bucket_service.add_transaction(
                account_id=account_a_id,
                source_bucket_id=savings_a.id,
                destination_bucket_id=savings_b.id,
                amount=100.0,
                transaction_type="allocate",
                description="Cross account leak"
            )


class TestSavingsBucketTransactionHistory:
    async def test__get_transactions_count__empty(self, account_service, savings_bucket_service):
        """Test that count of transactions for an account is initially 0."""
        account_id = await create_test_account(account_service)
        count = await savings_bucket_service.get_transactions_count_for_account(account_id)
        assert count == 0

    async def test__get_transactions_count__success(self, account_service, savings_bucket_service):
        """Test retrieving correct total count after transactions are added."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        lic = next(b for b in buckets if b.name == "LIC")
        
        # Execute 3 transactions
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=None,
            destination_bucket_id=savings.id,
            amount=1000.0,
            transaction_type="deposit",
            description="T1"
        )
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=savings.id,
            destination_bucket_id=lic.id,
            amount=400.0,
            transaction_type="allocate",
            description="T2"
        )
        await savings_bucket_service.add_transaction(
            account_id=account_id,
            source_bucket_id=lic.id,
            destination_bucket_id=savings.id,
            amount=100.0,
            transaction_type="release",
            description="T3"
        )
        
        count = await savings_bucket_service.get_transactions_count_for_account(account_id)
        assert count == 3

    async def test__get_transactions__pagination(self, account_service, savings_bucket_service):
        """Test limit and offset pagination on transaction history."""
        account_id = await create_test_account(account_service)
        buckets = await savings_bucket_service.get_buckets_for_account(account_id)
        savings = next(b for b in buckets if b.name == "Savings")
        
        # Add 5 transactions sequentially
        txs = []
        for i in range(5):
            tx = await savings_bucket_service.add_transaction(
                account_id=account_id,
                source_bucket_id=None,
                destination_bucket_id=savings.id,
                amount=100.0 * (i + 1),
                transaction_type="deposit",
                description=f"Tx {i}"
            )
            txs.append(tx)
            
        # Get page 1 (limit 2, offset=0). Should contain Tx 4 and Tx 3 (newest first).
        page_1 = await savings_bucket_service.get_transactions_for_account(account_id, limit=2, offset=0)
        assert len(page_1) == 2
        assert page_1[0].id == txs[4].id
        assert page_1[1].id == txs[3].id
        
        # Get page 2 (limit 2, offset=2). Should contain Tx 2 and Tx 1.
        page_2 = await savings_bucket_service.get_transactions_for_account(account_id, limit=2, offset=2)
        assert len(page_2) == 2
        assert page_2[0].id == txs[2].id
        assert page_2[1].id == txs[1].id
        
        # Get page 3 (limit 2, offset=4). Should contain Tx 0.
        page_3 = await savings_bucket_service.get_transactions_for_account(account_id, limit=2, offset=4)
        assert len(page_3) == 1
        assert page_3[0].id == txs[0].id


class TestSavingsBucketImmutability:
    async def test__transactions__are_immutable(self, savings_bucket_service):
        """Test that the repository interface and service enforce transaction immutability."""
        # Verify that there are no methods to delete or edit transactions
        for obj in [savings_bucket_service, savings_bucket_service.savings_bucket_repository]:
            for attr in dir(obj):
                assert "delete_transaction" not in attr.lower()
                assert "edit_transaction" not in attr.lower()
                assert "update_transaction" not in attr.lower()

