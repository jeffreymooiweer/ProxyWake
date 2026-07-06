"""Tests for credential encryption."""

from services.credential_service import get_credential, save_credentials


def test_credential_round_trip(client, sample_device):
    save_credentials(sample_device['id'], {'ipmi_password': 'bmc-secret'})
    assert get_credential(sample_device['id'], 'ipmi_password') == 'bmc-secret'
