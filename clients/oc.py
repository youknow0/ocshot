from __future__ import print_function
import owncloud
import os
import string
import random

class OcError(Exception):
    pass

class OcClient(object):
    def __init__(self, occonf):
        if not occonf.has_option("owncloud", "url"):
            raise ValueError("No owncloud URL given!")
        
        if not occonf.has_option("owncloud", "username"):
            raise ValueError("No owncloud username given!")

        if not occonf.has_option("owncloud", "password"):
            raise ValueError("No owncloud password given!")

        if not occonf.has_option("owncloud", "path"):
            self._path = "/"
        else:
            # add a trailing / if not given
            path = occonf.get("owncloud", "path")

            if not path.endswith("/"):
                path = path + "/"

            self._path = path

        self._url = occonf.get("owncloud", "url")
        self._user = occonf.get("owncloud", "username")
        self._password = occonf.get("owncloud", "password")
        self._oc = None

    def _get_oc(self):
        if self._oc == None:
            oc = owncloud.Client(self._url)
            oc.login(self._user, self._password)
            self._oc = oc

        return self._oc

    def _remote_dir_exists(self, path):
        oc = self._get_oc()

        try:
            fileinfo = oc.file_info(path)

        except owncloud.ResponseError as e:
            # the owncloud library throws a HTTPError 404 if the file 
            # does not exists. we must handle this case here.
            if e.status_code == 404:
                return False
            else:
                raise e
        
        return fileinfo.is_dir()

    def _generate_filename(self, orig_name):
        length = 30

        # try to preserve the extension, if any
        ext = os.path.splitext(orig_name)[1]

        randstr = ''.join(random.choice(string.ascii_lowercase + string.digits)
                for _ in range(length))

        return randstr + ext

    def _open_file_to_upload(self, filepath):
        filehandle = open(filepath, 'rb')

        return filehandle
    
    def _check_remote_destdir_existant(self):
        if not self._remote_dir_exists(self._path):
            if not oc.mkdir(self._path):
                raise OcError("Could not create the given remote " + 
                              "directory '%s'" % (self._path,))

    def _get_remote_path(self, filepath):
        orig_filename = os.path.basename(filepath)

        remote_name = self._generate_filename(orig_filename)
        return self._path + remote_name

    def share(self, filepath):
        filehandle = self._open_file_to_upload(filepath)

        return self._share(filehandle, filepath)

    def _share(self, filehandle, filepath):
        oc = self._get_oc()
        self._check_remote_destdir_existant()

        remote_path = self._get_remote_path(filepath)

        if not oc.put_file_contents(remote_path, filehandle):
            raise OcError("Uploading failed")

        link_info = oc.share_file_with_link(remote_path)

        if not link_info:
            raise OcError("Sharing failed")

        return link_info.link
