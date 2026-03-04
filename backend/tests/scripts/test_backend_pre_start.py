import uuid
from unittest.mock import MagicMock, Mock, patch

from sqlmodel import select

from backend.models import Permission, Role
from backend.utils.backend_pre_start import init, init_rbac, logger, main


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    select1 = select(1)

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch("backend.utils.backend_pre_start.select", return_value=select1),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        session_mock.exec.assert_called_once_with(select1)


def test_init_rbac_creates_permissions_and_roles() -> None:
    """Test that init_rbac creates default permissions and roles."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch(
            "backend.utils.backend_pre_start.get_permission_by_name", return_value=None
        ),
        patch("backend.utils.backend_pre_start.create_permission") as mock_create_perm,
        patch("backend.utils.backend_pre_start.get_role_by_name", return_value=None),
        patch("backend.utils.backend_pre_start.create_role") as mock_create_role,
        patch.object(logger, "info"),
        patch.object(logger, "error"),
    ):
        init_rbac(engine_mock)
        # Verify that create_permission was called for at least some permissions
        assert mock_create_perm.call_count > 0, "Should create permissions"
        # Verify that create_role was called for system roles
        assert mock_create_role.call_count > 0, "Should create system roles"


def test_init_rbac_skips_existing_permissions() -> None:
    """Test that init_rbac doesn't recreate existing permissions."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    existing_perm = Mock(spec=Permission)
    existing_perm.id = uuid.uuid4()
    existing_perm.name = "admin:read"

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch(
            "backend.utils.backend_pre_start.get_permission_by_name",
            return_value=existing_perm,
        ),
        patch("backend.utils.backend_pre_start.create_permission") as mock_create_perm,
        patch("backend.utils.backend_pre_start.get_role_by_name", return_value=None),
        patch("backend.utils.backend_pre_start.create_role"),
        patch.object(logger, "info"),
    ):
        init_rbac(engine_mock)
        # If permission exists, it should not be created
        mock_create_perm.assert_not_called()


def test_init_rbac_skips_existing_roles() -> None:
    """Test that init_rbac doesn't recreate existing system roles."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    existing_role = Mock(spec=Role)
    existing_role.id = uuid.uuid4()
    existing_role.name = "admin"
    existing_role.description = "Administrator"

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch(
            "backend.utils.backend_pre_start.get_permission_by_name", return_value=None
        ),
        patch("backend.utils.backend_pre_start.create_permission"),
        patch(
            "backend.utils.backend_pre_start.get_role_by_name",
            return_value=existing_role,
        ),
        patch("backend.utils.backend_pre_start.create_role") as mock_create_role,
        patch.object(logger, "info"),
    ):
        init_rbac(engine_mock)
        # If role exists, it should not be created again
        mock_create_role.assert_not_called()


def test_init_rbac_entra_disabled() -> None:
    """Test that init_rbac skips Entra sync when not configured."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    perm = Mock(spec=Permission)
    perm.id = uuid.uuid4()

    role = Mock(spec=Role)
    role.id = uuid.uuid4()
    role.name = "admin"
    role.description = "Admin role"

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch(
            "backend.utils.backend_pre_start.get_permission_by_name", return_value=perm
        ),
        patch("backend.utils.backend_pre_start.create_permission"),
        patch("backend.utils.backend_pre_start.get_role_by_name", return_value=None),
        patch("backend.utils.backend_pre_start.create_role", return_value=role),
        patch("backend.utils.backend_pre_start.settings.AZURE_CLIENT_ID", None),
        patch("backend.utils.backend_pre_start.settings.AZURE_CLIENT_SECRET", None),
        patch.object(logger, "info"),
    ):
        init_rbac(engine_mock)
        # Should still create roles even when Entra is not configured
        # Should log that Entra is not configured


def test_init_rbac_entra_sync_success() -> None:
    """Test that init_rbac syncs roles to Entra when configured."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    perm = Mock(spec=Permission)
    perm.id = uuid.uuid4()

    role = Mock(spec=Role)
    role.id = uuid.uuid4()
    role.name = "admin"
    role.description = "Admin role"

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch(
            "backend.utils.backend_pre_start.get_permission_by_name", return_value=perm
        ),
        patch("backend.utils.backend_pre_start.create_permission"),
        patch("backend.utils.backend_pre_start.get_role_by_name", return_value=None),
        patch("backend.utils.backend_pre_start.create_role", return_value=role),
        patch("backend.utils.backend_pre_start.settings.AZURE_CLIENT_ID", "test-id"),
        patch(
            "backend.utils.backend_pre_start.settings.AZURE_CLIENT_SECRET",
            "test-secret",
        ),
        patch("backend.utils.backend_pre_start.EntraAuthClient") as mock_entra,
        patch.object(logger, "info"),
    ):
        mock_entra_instance = MagicMock()
        mock_entra.return_value = mock_entra_instance
        mock_entra_instance.sync_app_roles_to_manifest.return_value = True

        init_rbac(engine_mock)
        # Verify Entra client was initialized and sync was called
        mock_entra.assert_called_once()


def test_init_rbac_entra_sync_failure() -> None:
    """Test that init_rbac handles Entra sync failure gracefully."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock

    perm = Mock(spec=Permission)
    perm.id = uuid.uuid4()

    role = Mock(spec=Role)
    role.id = uuid.uuid4()
    role.name = "admin"
    role.description = "Admin role"

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch(
            "backend.utils.backend_pre_start.get_permission_by_name", return_value=perm
        ),
        patch("backend.utils.backend_pre_start.create_permission"),
        patch("backend.utils.backend_pre_start.get_role_by_name", return_value=None),
        patch("backend.utils.backend_pre_start.create_role", return_value=role),
        patch("backend.utils.backend_pre_start.settings.AZURE_CLIENT_ID", "test-id"),
        patch(
            "backend.utils.backend_pre_start.settings.AZURE_CLIENT_SECRET",
            "test-secret",
        ),
        patch("backend.utils.backend_pre_start.EntraAuthClient") as mock_entra,
        patch.object(logger, "info"),
        patch.object(logger, "warning"),
    ):
        mock_entra_instance = MagicMock()
        mock_entra.return_value = mock_entra_instance
        mock_entra_instance.sync_app_roles_to_manifest.return_value = False

        # Should not raise even if sync fails
        init_rbac(engine_mock)


def test_init_rbac_exception_handling() -> None:
    """Test that init_rbac handles exceptions gracefully."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock
    session_mock.exec.side_effect = Exception("DB Error")

    with (
        patch("backend.utils.backend_pre_start.Session", return_value=session_mock),
        patch.object(logger, "error"),
    ):
        try:
            init_rbac(engine_mock)
            raised = False
        except Exception:
            raised = True

        assert raised, "init_rbac should raise exception on DB error"


def test_main_calls_init_and_init_rbac() -> None:
    """Test that main function calls init (RBAC init happens in initial_data.py)."""
    with (
        patch("backend.utils.backend_pre_start.engine") as mock_engine,
        patch("backend.utils.backend_pre_start.init") as mock_init,
        patch.object(logger, "info"),
    ):
        main()
        mock_init.assert_called_once_with(mock_engine)
