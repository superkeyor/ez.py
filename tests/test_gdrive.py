import ast
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1]
drive = types.ModuleType("ez_drive_helpers")
drive.os = os
drive.json = json
source = ast.parse((ROOT / "ez/ez.py").read_text())
helpers = [node for node in source.body if isinstance(node, ast.FunctionDef)
           and node.name.startswith("_gdrive_")]
exec(compile(ast.Module(body=helpers, type_ignores=[]), "ez/ez.py", "exec"), vars(drive))


def fake_modules(attributes):
    modules = {}
    for name, values in attributes.items():
        parts = name.split(".")
        for index in range(1, len(parts) + 1):
            module_name = ".".join(parts[:index])
            if module_name not in modules:
                modules[module_name] = types.ModuleType(module_name)
                modules[module_name].__path__ = []
            if index > 1:
                setattr(modules[".".join(parts[:index - 1])], parts[index - 1],
                        modules[module_name])
        for key, value in values.items():
            setattr(modules[name], key, value)
    return modules


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="ez-drive-auth-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.token = self.root / "gdrive_token.json"
        self.config = {"installed": {
            "client_id": "test-client", "client_secret": "test-placeholder",
            "auth_uri": "https://accounts.example/authorize",
            "token_uri": "https://accounts.example/token",
        }}
        self.credentials = Mock(valid=True, expired=False, refresh_token="test-refresh")
        self.credentials.has_scopes.return_value = True
        self.credentials.to_json.return_value = '{"token": "test-placeholder"}'
        self.factory = Mock()
        self.factory.from_authorized_user_info.return_value = self.credentials
        self.flow = Mock()
        self.flow.from_client_config.return_value.run_local_server.return_value = self.credentials
        self.build = Mock()
        self.request = Mock()
        self.modules = fake_modules({
            "google.auth.transport.requests": {"Request": self.request},
            "google.oauth2.credentials": {"Credentials": self.factory},
            "google_auth_oauthlib.flow": {"InstalledAppFlow": self.flow},
            "googleapiclient.discovery": {"build": self.build},
        })
        self.patcher = patch.dict(sys.modules, self.modules)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.cwd = Path.cwd()

    def tearDown(self):
        self.assertEqual(Path.cwd(), self.cwd)

    def authenticate(self):
        return drive._gdrive_authenticate(self.config, self.root)

    def test_initial_authorization_and_private_cache(self):
        self.assertIs(self.authenticate(), self.build.return_value)
        self.flow.from_client_config.assert_called_once_with(
            self.config, ["https://www.googleapis.com/auth/drive"],
        )
        self.flow.from_client_config.return_value.run_local_server.assert_called_once_with(
            port=0, access_type="offline", prompt="consent",
        )
        self.assertEqual(self.token.read_text(), self.credentials.to_json())
        for path in (self.token, self.root / "gdrive_secrets.json"):
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.root / "settings.yaml").exists())
        self.build.assert_called_once_with(
            "drive", "v3", credentials=self.credentials, cache_discovery=False,
        )

    def test_valid_cache_never_opens_browser_or_refreshes(self):
        self.token.write_text('{"refresh_token": "test-placeholder"}')
        self.authenticate()
        self.flow.from_client_config.assert_not_called()
        self.credentials.refresh.assert_not_called()
        self.assertEqual(self.token.read_text(), '{"refresh_token": "test-placeholder"}')

    def test_gauth_reuses_saved_secrets_and_token_without_configured_key(self):
        (self.root / "gdrive_secrets.json").write_text(json.dumps(self.config))
        self.token.write_text('{"refresh_token": "test-placeholder"}')
        namespace = {**vars(drive), "__file__": str(self.root / "ez.py")}
        function = next(node for node in source.body
                        if isinstance(node, ast.FunctionDef) and node.name == "gauth")
        exec(compile(ast.Module(body=[function], type_ignores=[]), "ez/ez.py", "exec"),
             namespace)
        self.assertIs(namespace["gauth"](), self.build.return_value)
        self.factory.from_authorized_user_info.assert_called_once_with(
            {"refresh_token": "test-placeholder"},
        )
        self.flow.from_client_config.assert_not_called()
        self.credentials.refresh.assert_not_called()

    def test_expired_credentials_refresh_and_persist(self):
        self.token.write_text("{}")
        self.credentials.valid = False
        self.credentials.expired = True
        self.authenticate()
        self.credentials.refresh.assert_called_once_with(self.request.return_value)
        self.flow.from_client_config.assert_not_called()
        self.assertEqual(self.token.read_text(), self.credentials.to_json())

    def test_refresh_failure_does_not_fall_back_or_replace_token(self):
        self.token.write_text("{}")
        self.credentials.valid = False
        self.credentials.expired = True
        self.credentials.refresh.side_effect = RuntimeError("refresh failed")
        with self.assertRaisesRegex(RuntimeError, "refresh failed"):
            self.authenticate()
        self.flow.from_client_config.assert_not_called()
        self.assertEqual(self.token.read_text(), "{}")

    def test_legacy_token_reauthorizes_once(self):
        self.token.write_text('{"_module": "oauth2client.client", "_class": "OAuth2Credentials"}')
        with self.assertWarnsRegex(UserWarning, "one-time"):
            self.authenticate()
        self.factory.from_authorized_user_info.assert_not_called()
        self.assertEqual(self.token.read_text(), self.credentials.to_json())

    def test_failed_legacy_authorization_preserves_original_token(self):
        original = '{"_class": "OAuth2Credentials"}'
        self.token.write_text(original)
        self.flow.from_client_config.return_value.run_local_server.side_effect = RuntimeError("cancelled")
        with self.assertWarns(UserWarning), self.assertRaisesRegex(RuntimeError, "cancelled"):
            self.authenticate()
        self.assertEqual(self.token.read_text(), original)

    def test_invalid_token_never_silently_reauthorizes(self):
        for content in ("invalid json", "[]", '{"_module": null}'):
            with self.subTest(content=content):
                self.token.write_text(content)
                with self.assertRaises(ValueError):
                    self.authenticate()
                self.assertEqual(self.token.read_text(), content)
        self.flow.from_client_config.assert_not_called()

    def test_invalid_modern_credentials_do_not_leak_values(self):
        self.token.write_text("{}")
        self.factory.from_authorized_user_info.side_effect = ValueError("do-not-print")
        with self.assertRaises(ValueError) as result:
            self.authenticate()
        self.assertNotIn("do-not-print", str(result.exception))
        self.flow.from_client_config.assert_not_called()

    def test_unrefreshable_or_insufficient_credentials_fail(self):
        self.token.write_text("{}")
        self.credentials.has_scopes.return_value = False
        with self.assertRaisesRegex(ValueError, "lack Drive access"):
            self.authenticate()
        self.credentials.has_scopes.return_value = True
        self.credentials.valid = False
        self.credentials.expired = True
        self.credentials.refresh_token = None
        with self.assertRaisesRegex(ValueError, "cannot be refreshed"):
            self.authenticate()
        self.flow.from_client_config.assert_not_called()

    def test_invalid_client_configuration_fails_before_writing(self):
        for value in (None, {}, {"installed": {}}, {"installed": "invalid"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                drive._gdrive_authenticate(value, self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_write_failure_propagates_and_cleans_temporary_file(self):
        with patch.object(drive.os, "replace", side_effect=PermissionError("write denied")):
            with self.assertRaises(PermissionError):
                self.authenticate()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_failed_token_replace_preserves_existing_token(self):
        original = '{"_class": "OAuth2Credentials"}'
        self.token.write_text(original)
        original_replace = drive.os.replace

        def replace(source, target):
            if target == self.token:
                raise PermissionError("token write denied")
            original_replace(source, target)

        with patch.object(drive.os, "replace", side_effect=replace):
            with self.assertWarns(UserWarning), self.assertRaises(PermissionError):
                self.authenticate()
        self.assertEqual(self.token.read_text(), original)
        self.assertFalse(any(path.name.startswith(".gdrive") for path in self.root.iterdir()))


class DriveFunctionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="ez-drive-functions-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        source = ast.parse((ROOT / "ez/ez.py").read_text())
        names = {"gauth", "gdownload", "gupload", "gdelete", "gcopy", "gmove", "gls", "gfileid"}
        functions = [node for node in source.body
                     if isinstance(node, ast.FunctionDef) and node.name in names]
        self.namespace = {
            "__file__": str(self.root / "ez.py"), "__package__": "ez",
            "joinpath": os.path.join, "pwd": os.getcwd,
            "splitpath": lambda value: (
                os.path.dirname(value), *os.path.splitext(os.path.basename(value)),
            ),
            **{node.name: getattr(drive, node.name) for node in helpers},
        }
        exec(compile(ast.Module(body=functions, type_ignores=[]), "drive_functions", "exec"),
             self.namespace)
        self.original_auth = self.namespace["gauth"]
        self.service = MagicMock()
        self.namespace["gauth"] = Mock(return_value=self.service)
        self.download = Mock()
        self.upload = Mock()
        self.modules = fake_modules({
            "googleapiclient.http": {
                "MediaIoBaseDownload": self.download, "MediaFileUpload": self.upload,
            },
        })
        self.patcher = patch.dict(sys.modules, self.modules)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def call(self, name, *args, **kwargs):
        return self.namespace[name](*args, **kwargs)

    def test_auth_uses_package_location_without_cwd_changes(self):
        self.namespace["GDRIVE_KEY"] = {"test": "placeholder"}
        with patch.dict(self.namespace, {"_gdrive_authenticate": Mock()}) as namespace:
            authenticate = namespace["_gdrive_authenticate"]
            self.assertIs(self.original_auth(), authenticate.return_value)
        authenticate.assert_called_once_with(self.namespace["GDRIVE_KEY"], self.root)

    def test_auth_loads_saved_client_configuration(self):
        config = {"installed": {"client_id": "test-client"}}
        secrets = self.root / "gdrive_secrets.json"
        secrets.write_text(json.dumps(config))
        cwd = Path.cwd()
        with patch.dict(self.namespace, {"_gdrive_authenticate": Mock()}) as namespace:
            authenticate = namespace["_gdrive_authenticate"]
            self.assertIs(self.original_auth(), authenticate.return_value)
        authenticate.assert_called_once_with(config, self.root)
        self.assertEqual(Path.cwd(), cwd)

    def test_configured_key_takes_precedence_over_saved_configuration(self):
        self.namespace["GDRIVE_KEY"] = {"test": "placeholder"}
        (self.root / "gdrive_secrets.json").write_text("invalid")
        with patch.dict(self.namespace, {"_gdrive_authenticate": Mock()}) as namespace:
            self.original_auth()
            namespace["_gdrive_authenticate"].assert_called_once_with(
                self.namespace["GDRIVE_KEY"], self.root,
            )

    def test_invalid_saved_client_configuration_is_explicit_and_private(self):
        for content in (b"do-not-print", b"\xff"):
            with self.subTest(content=content):
                (self.root / "gdrive_secrets.json").write_bytes(content)
                with self.assertRaisesRegex(ValueError, "Invalid gdrive_secrets.json") as result:
                    self.original_auth()
                self.assertNotIn("do-not-print", str(result.exception))

    def test_missing_auth_configuration_is_explicit(self):
        with self.assertRaisesRegex(ValueError, "GDRIVE_KEY"):
            self.original_auth()

    def test_binary_docx_download_overwrites_and_streams_without_remote_mutation(self):
        self.service.files.return_value.get.return_value.execute.return_value = {
            "id": "doc", "name": "book.docx",
            "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        def downloader(stream, request):
            stream.write(b"downloaded docx")
            return Mock(next_chunk=Mock(side_effect=[(None, False), (None, True)]))

        self.download.side_effect = downloader
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.docx"
            path.write_bytes(b"old contents")
            self.assertEqual(self.call("gdownload", "doc", str(path)), str(path))
            self.assertEqual(path.read_bytes(), b"downloaded docx")
        self.service.files.return_value.get_media.assert_called_once_with(fileId="doc")
        self.service.files.return_value.export_media.assert_not_called()
        for operation in ("create", "update", "delete", "copy"):
            getattr(self.service.files.return_value, operation).assert_not_called()

    def test_native_document_uses_export_mime(self):
        self.service.files.return_value.get.return_value.execute.return_value = {
            "name": "report", "mimeType": "application/vnd.google-apps.document",
        }
        self.download.return_value.next_chunk.return_value = (None, True)
        with tempfile.TemporaryDirectory() as directory:
            self.call("gdownload", "doc", str(Path(directory) / "export.docx"))
        self.service.files.return_value.export_media.assert_called_once_with(
            fileId="doc",
            mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.service.files.return_value.get_media.assert_not_called()

    def test_unsupported_export_fails_before_opening_destination(self):
        self.service.files.return_value.get.return_value.execute.return_value = {
            "name": "native", "mimeType": "application/vnd.google-apps.document",
        }
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "bad.unknown"
            with self.assertRaisesRegex(ValueError, "Unsupported"):
                self.call("gdownload", "doc", str(target))
            self.assertFalse(target.exists())

    def test_implicit_filename_and_unknown_binary_extension(self):
        self.service.files.return_value.get.return_value.execute.return_value = {
            "name": "remote.bin", "mimeType": "application/octet-stream",
        }
        self.download.return_value.next_chunk.return_value = (None, True)
        with tempfile.TemporaryDirectory() as directory:
            self.namespace["pwd"] = lambda: directory
            self.assertEqual(self.call("gdownload", "doc"), str(Path(directory) / "remote.bin"))
            self.assertTrue((Path(directory) / "remote.bin").exists())

    def test_download_api_and_filesystem_errors_propagate(self):
        self.service.files.return_value.get.return_value.execute.side_effect = RuntimeError("API error")
        with self.assertRaisesRegex(RuntimeError, "API error"):
            self.call("gdownload", "doc", "unused")
        self.service.files.return_value.get.return_value.execute.side_effect = None
        self.service.files.return_value.get.return_value.execute.return_value = {
            "name": "remote", "mimeType": "application/octet-stream",
        }
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                self.call("gdownload", "doc", "unused")

    def test_list_paginates_and_preserves_tuple_order(self):
        listing = self.service.files.return_value.list
        listing.return_value.execute.side_effect = [
            {"files": [{"id": "1", "name": "first"}], "nextPageToken": "next"},
            {"files": [{"id": "2", "name": "second"}]},
        ]
        self.assertEqual(self.call("gls"), [("first", "1"), ("second", "2")])
        self.assertEqual(listing.call_args_list[0].kwargs["q"], "'root' in parents and trashed=false")
        self.assertEqual(listing.call_args_list[1].kwargs["pageToken"], "next")

    def test_list_escapes_folder_and_propagates_api_failure(self):
        self.service.files.return_value.list.return_value.execute.return_value = {"files": []}
        self.assertEqual(self.call("gls", "folder'\\id"), [])
        self.assertEqual(
            self.service.files.return_value.list.call_args.kwargs["q"],
            "'folder\\'\\\\id' in parents and trashed=false",
        )
        self.service.files.return_value.list.return_value.execute.side_effect = RuntimeError("list failed")
        with self.assertRaisesRegex(RuntimeError, "list failed"):
            self.call("gls")

    def test_upload_new_file_preserves_result_and_escapes_query(self):
        self.service.files.return_value.list.return_value.execute.return_value = {"files": []}
        self.service.files.return_value.create.return_value.execute.return_value = {"id": "new"}
        filename = "/tmp/title's\\file.docx"
        self.assertEqual(self.call("gupload", filename, "folder"), ("title's\\file.docx", "new"))
        query = self.service.files.return_value.list.call_args.kwargs["q"]
        self.assertEqual(query, "name='title\\'s\\\\file.docx' and trashed=false")
        self.service.files.return_value.create.assert_called_once_with(
            body={"name": "title's\\file.docx", "parents": ["folder"]},
            media_body=self.upload.return_value, fields="id",
        )
        self.upload.assert_called_once_with(filename, resumable=True)

    def test_upload_updates_first_match_and_moves_parent(self):
        self.service.files.return_value.list.return_value.execute.return_value = {
            "files": [{"id": "first"}, {"id": "second"}],
        }
        self.service.files.return_value.get.return_value.execute.return_value = {"parents": ["old"]}
        self.service.files.return_value.update.return_value.execute.return_value = {"id": "first"}
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.call("gupload", "/tmp/book.docx", "new"), ("book.docx", "first"))
        self.assertIn("Updated file book.docx", output.getvalue())
        parameters = self.service.files.return_value.update.call_args.kwargs
        self.assertEqual(parameters["fileId"], "first")
        self.assertEqual(parameters["body"], {"name": "book.docx"})
        self.assertEqual(parameters["addParents"], "new")
        self.assertEqual(parameters["removeParents"], "old")

    def test_upload_defaults_to_root_and_propagates_failure(self):
        self.service.files.return_value.list.return_value.execute.return_value = {"files": []}
        self.service.files.return_value.create.return_value.execute.side_effect = RuntimeError("upload failed")
        with self.assertRaisesRegex(RuntimeError, "upload failed"):
            self.call("gupload", "/tmp/book.docx")
        self.assertEqual(
            self.service.files.return_value.create.call_args.kwargs["body"],
            {"name": "book.docx", "parents": ["root"]},
        )

    def test_upload_in_same_parent_does_not_add_or_remove_parents(self):
        self.service.files.return_value.list.return_value.execute.return_value = {
            "files": [{"id": "existing"}],
        }
        self.service.files.return_value.get.return_value.execute.return_value = {"parents": ["folder"]}
        self.service.files.return_value.update.return_value.execute.return_value = {"id": "existing"}
        with redirect_stdout(io.StringIO()):
            self.call("gupload", "/tmp/book.docx", "folder")
        parameters = self.service.files.return_value.update.call_args.kwargs
        self.assertNotIn("addParents", parameters)
        self.assertNotIn("removeParents", parameters)

    def test_move_to_same_parent_does_not_update(self):
        self.service.files.return_value.get.return_value.execute.return_value = {"parents": ["folder"]}
        self.assertIsNone(self.call("gmove", "file", "folder"))
        self.service.files.return_value.update.assert_not_called()

    def test_move_removes_old_parents_and_resolves_root(self):
        self.service.files.return_value.get.return_value.execute.side_effect = [
            {"id": "root-id"}, {"parents": ["old", "extra"]},
        ]
        self.call("gmove", "file", "root")
        self.service.files.return_value.update.assert_called_once_with(
            fileId="file", addParents="root-id", removeParents="old,extra",
        )

    def test_existing_destination_not_added_twice(self):
        self.service.files.return_value.get.return_value.execute.return_value = {
            "parents": ["target", "old"],
        }
        self.assertEqual(drive._gdrive_parent_changes(self.service, "file", "target"), {"removeParents": "old"})

    def test_copy_preserves_name_return_and_optional_folder(self):
        self.assertEqual(self.call("gcopy", "file", "new"), "new")
        self.service.files.return_value.copy.assert_called_with(fileId="file", body={"name": "new"})
        self.call("gcopy", "file", "new", "folder")
        self.service.files.return_value.copy.assert_called_with(
            fileId="file", body={"name": "new", "parents": ["folder"]},
        )

    def test_delete_id_precedence_and_permanent_operation(self):
        self.assertIsNone(self.call("gdelete", "file", "ignored"))
        self.service.files.return_value.delete.assert_called_once_with(fileId="file")
        self.service.files.return_value.list.assert_not_called()

    def test_delete_by_name_duplicate_warning_and_first_match(self):
        self.namespace["gls"] = Mock(return_value=[("same", "first"), ("same", "second")])
        output = io.StringIO()
        with redirect_stdout(output):
            self.call("gdelete", file_name="same", folderid="folder")
        self.assertIn("deleting the first", output.getvalue())
        self.service.files.return_value.delete.assert_called_once_with(fileId="first")

    def test_missing_delete_and_fileid_errors(self):
        self.namespace["gls"] = Mock(return_value=[])
        with self.assertRaises(ValueError):
            self.call("gdelete")
        with self.assertRaises(FileNotFoundError):
            self.call("gdelete", file_name="missing")
        with self.assertRaises(FileNotFoundError):
            self.call("gfileid", "missing")
        self.namespace["gls"].return_value = [("match", "first"), ("match", "second")]
        self.assertEqual(self.call("gfileid", "match"), "first")


if __name__ == "__main__":
    unittest.main()
