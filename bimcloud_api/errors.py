# MIT License
#
# Copyright (c) 2020 GRAPHISOFT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

MANGER_ERRORS = {
    1: 'GenericError',
    2: 'AuthenticationRequiredError',
    3: 'AccessDeniedError',
    4: 'EntityCyclicDependencyError',
    5: 'EntityExistsError',
    6: 'EntityNotFoundError',
    7: 'EntityValidationError',
    8: 'OptimisticLockError',
    9: 'RevisionObsoletedError',
    10: 'LdapConnectionError',
    11: 'LdapInvalidCredentialsError',
    12: 'FileConnectionBaseDnError',
    13: 'ModelServerSideError',
    14: 'ReferenceError',
    15: 'ProhibitDeleteError',
    16: 'LicenseManagerError',
    17: 'ResultLimitExceededError',
    18: 'ModelServerNotCompatibleError',
    19: 'NotEnoughFreeSpaceError',
    20: 'ChangeHostError',
    21: 'GSIDConnectionError',
    22: 'GSIDInvalidCredentialsError',
    23: 'TagAlreadyAssignedError',
    24: 'KeyExistsError',
    25: 'NotAllowedError',
    26: 'NotYetAvailableError',
    27: 'InsufficientLicenseError'
}

BLOB_SERVER_ERRORS = {
    1: 'GenericError',
    2: 'AuthenticationRequired',
    3: 'AuthenticationFailed',
    4: 'AccessControlTicketExpired',
    5: 'AccessDenied',
    11: 'SessionNotFound',
    12: 'BatchUploadCommitFailed',
    13: 'InvalidBlobContentPart',
    14: 'UploadSessionNotFound',
    15: 'IncompleteUpload',
    16: 'BlobAttachmentNotFound',
    17: 'BlobNamespaceNotFound',
    18: 'BlobRevisionNotFound',
    19: 'BlobChunkNotFound',
    20: 'BlobAlreadyExists',
    21: 'BlobNotFound',
    22: 'BlobAccessDenied',
    23: 'BlobPermissionDenied'
}


def get_manager_error_id(code):
    name = MANGER_ERRORS.get(code)
    if name is None:
        'UnknownBIMcloudManagerError'
    return name


def get_blob_server_error_id(code):
    name = BLOB_SERVER_ERRORS.get(code)
    if name is None:
        'UnknownBIMcloudBlobServerError'
    return name


def raise_bimcloud_manager_error(error_content):
    raise BIMcloudManagerError(error_content['error-code'], error_content['error-message'])


def raise_bimcloud_blob_server_error(error_content):
    data = error_content['data']
    raise BIMcloudBlobServerError(data['error-code'], data['error-message'])


class BIMcloudError(Exception):
    def __init__(self, code, message):
        id = get_manager_error_id(code)
        self.code = code
        self.name = id
        self.message = message


class BIMcloudManagerError(BIMcloudError):
    pass


class BIMcloudBlobServerError(BIMcloudError):
    pass


class HttpError(Exception):
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.text = response.text
        if self.status_code == 200:
            self.reason = 'Invalid Model Server route.'
            self.message = f'HttpErrror: status={self.status_code}, reason={self.text or self.reason}.'
            return
        self.reason = response.reason
        self.message = f'HttpErrror: status={self.status_code}. {self.text or self.reason}.'
