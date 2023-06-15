"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_tap_test_class

from tap_file.tap import TapFile

SAMPLE_CONFIG = {
    "protocol": "s3",
    "filepath": "tap-file-taptesting",
    # S3 access key and secret are retrieved from environment variables.
}

# Run standard built-in tap tests from the SDK:
TestTapFile = get_tap_test_class(
    tap_class=TapFile,
    config=SAMPLE_CONFIG,
)
