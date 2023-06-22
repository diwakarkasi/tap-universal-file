"""File tap class."""

from __future__ import annotations

import os

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_file import streams


class TapFile(Tap):
    """File tap class."""

    name = "tap-file"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "stream_name",
            th.StringType,
            required=False,
            default="file",
            description="The name of the stream that is output by the tap.",
        ),
        th.Property(
            "protocol",
            th.StringType,
            required=True,
            allowed_values=["file", "s3"],
            description="The protocol to use to retrieve data. One of `file` or `s3`.",
        ),
        th.Property(
            "filepath",
            th.StringType,
            required=True,
            description=(
                "The path to obtain files from. Example: `/foo/bar`. Or, for "
                "`protocol==s3`, use `s3-bucket-name` instead."
            ),
        ),
        th.Property(
            "file_regex",
            th.RegexType,
            description=(
                "A regex pattern to only include certain files. Example: `.*\\.csv`."
            ),
        ),
        th.Property(
            "file_type",
            th.RegexType,
            default="delimited",
            description=(
                "Can be any of `delimited`, `jsonl`, or `avro`. Indicates the type of "
                "file to sync, where `delimited` is for CSV/TSV files and similar. "
                "Note that *all* files will be read as that type, regardless of file "
                "extension. To only read from files with a matching file extension, "
                "appropriately configure `file_regex`."
            ),
        ),
        th.Property(
            "compression",
            th.StringType,
            allowed_values=["none", "zip", "bz2", "gzip", "lzma", "xz", "detect"],
            default="detect",
            description=(
                "The encoding to use to decompress data. One of `zip`, `bz2`, `gzip`, "
                "`lzma`, `xz`, `none`, or `detect`. If set to `none` or any encoding, "
                "that setting will be applied to *all* files, regardless of file "
                "extension. If set to `detect`, encodings will be applied based on "
                "file extension."
            ),
        ),
        th.Property(
            "delimiter",
            th.StringType,
            default="detect",
            description=(
                "The character used to separate records in a delimited file. Can be "
                "any character or the special value `detect`. If a character is "
                "provided, all delimited files will use that value. `detect` will use "
                "`,` for `.csv` files, `\\t` for `.tsv` files, and fail if other file "
                "types are present."
            ),
        ),
        th.Property(
            "quote_character",
            th.StringType,
            default='"',
            description=(
                "The character used to indicate when a record in a CSV contains a "
                "delimiter character."
            ),
        ),
        th.Property(
            "jsonl_sampling_strategy",
            th.StringType,
            allowed_values=["first", "all"],
            default="first",
            description=(
                "The strategy determining how to read the keys in a JSONL file. Must "
                "be one of `first` or `all`. Currently, only `first` is supported, "
                "which will assume that the first record in a file is representative "
                "of all keys."
            ),
        ),
        th.Property(
            "jsonl_type_coercion_strategy",
            th.StringType,
            allowed_values=["any", "string", "blob"],
            default="any",
            description=(
                "The strategy determining how to construct the schema for JSONL files "
                "when the types represented are ambiguous. Must be one of `any`, "
                "`string`, or `blob`. `any` will provide a generic schema for all "
                "keys, allowing them to be any valid JSON type. `string` will require "
                "all keys to be strings and will convert other values accordingly. "
                "`blob` will deliver each JSONL row as a JSON object with no internal "
                "schema. Currently, only `any` and `string` are supported."
            ),
        ),
        th.Property(
            "s3_anonymous_connection",
            th.BooleanType,
            default=False,
            description=(
                "Whether to use an anonymous S3 connection, without any credentials. "
                "Ignored if `protocol!=s3`."
            ),
        ),
        th.Property(
            "AWS_ACCESS_KEY_ID",
            th.StringType,
            default=os.getenv("AWS_ACCESS_KEY_ID"),
            description=(
                "The access key to use when authenticating to S3. Ignored if "
                "`protocol!=s3` or `s3_anonymous_connection=True`. Defaults to the "
                "value of the environment variable of the same name."
            ),
        ),
        th.Property(
            "AWS_SECRET_ACCESS_KEY",
            th.StringType,
            default=os.getenv("AWS_SECRET_ACCESS_KEY"),
            description=(
                "The access key secret to use when authenticating to S3. Ignored if "
                "`protocol!=s3` or `s3_anonymous_connection=True`. Defaults to the "
                "value of the environment variable of the same name."
            ),
        ),
        th.Property(
            "caching_strategy",
            th.StringType,
            default="once",
            allowed_values=["none", "once", "persistent"],
            description=(
                "*DEVELOPERS ONLY* The caching method to use when `protocol!=file`. "
                "One of `none`, `once`, or `persistent`. `none` does not use caching "
                "at all. `once` (the default) will cache all files for the duration of "
                "the tap's invocation, then discard them upon completion. `peristent` "
                "will allow caches to persist between invocations of the tap, storing "
                "them in your OS's temp directory. It is recommended that you do not "
                "modify this setting."
            ),
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.FileStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        name = self.config["stream_name"]
        file_type = self.config["file_type"]
        if file_type == "delimited":
            return [streams.DelimitedStream(self, name=name)]
        if file_type == "jsonl":
            return [streams.JSONLStream(self, name=name)]
        if file_type == "avro":
            msg = "avro has not yet been implemented."
            raise NotImplementedError(msg)
        if file_type in {"csv", "tsv"}:
            msg = f"{file_type} is not a valid 'file_type'. Did you mean 'delimited'?"
            raise ValueError(msg)
        msg = f"{file_type} is not a valid 'file_type'."
        raise ValueError(msg)


if __name__ == "__main__":
    TapFile.cli()
