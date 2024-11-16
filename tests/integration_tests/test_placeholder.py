import os

def assert_github_secrets():
    data_service_account = os.getenv("DATA_SERVICE_ACCOUNT")
    text_generator = os.getenv("TEXT_GENERATOR")
    
    assert data_service_account is not None, "DATA_SERVICE_ACCOUNT secret is missing!"
    assert text_generator is not None, "TEXT_GENERATOR secret is missing!"
