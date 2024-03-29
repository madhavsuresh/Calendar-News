#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




"""A Python blobstore API used by app developers.

Contains methods uses to interface with Blobstore API.  Defines db.Key-like
class representing a blob-key.  Contains API part that forward to apiproxy.
"""








import datetime
import time

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_types
from google.appengine.api import api_base_pb
from google.appengine.api.blobstore import blobstore_service_pb
from google.appengine.runtime import apiproxy_errors


__all__ = ['BLOB_INFO_KIND',
           'BLOB_KEY_HEADER',
           'BLOB_MIGRATION_KIND',
           'BLOB_RANGE_HEADER',
           'MAX_BLOB_FETCH_SIZE',
           'UPLOAD_INFO_CREATION_HEADER',
           'BlobFetchSizeTooLargeError',
           'BlobKey',
           'BlobNotFoundError',
           'DataIndexOutOfRangeError',
           'PermissionDeniedError',
           'Error',
           'InternalError',
           'create_upload_url',
           'delete',
           'fetch_data',
          ]


BlobKey = datastore_types.BlobKey



BLOB_INFO_KIND = '__BlobInfo__'

BLOB_KEY_HEADER = 'X-AppEngine-BlobKey'

BLOB_MIGRATION_KIND = '__BlobMigration__'

BLOB_RANGE_HEADER = 'X-AppEngine-BlobRange'

MAX_BLOB_FETCH_SIZE = (1 << 20) - (1 << 15)



UPLOAD_INFO_CREATION_HEADER = 'X-AppEngine-Upload-Creation'
_BASE_CREATION_HEADER_FORMAT = '%Y-%m-%d %H:%M:%S'

class Error(Exception):
  """Base blobstore error type."""


class InternalError(Error):
  """Raised when an internal error occurs within API."""


class BlobNotFoundError(Error):
  """Raised when attempting to access blob data for non-existant blob."""


class DataIndexOutOfRangeError(Error):
  """Raised when attempting to access indexes out of range in wrong order."""


class BlobFetchSizeTooLargeError(Error):
  """Raised when attempting to fetch too large a block from a blob."""


class _CreationFormatError(Error):
  """Raised when attempting to parse bad creation date format."""


class PermissionDeniedError(Error):
  """Raised when permissions are lacking for a requested operation."""



def _ToBlobstoreError(error):
  """Translate an application error to a datastore Error, if possible.

  Args:
    error: An ApplicationError to translate.
  """
  error_map = {
      blobstore_service_pb.BlobstoreServiceError.INTERNAL_ERROR:
      InternalError,
      blobstore_service_pb.BlobstoreServiceError.BLOB_NOT_FOUND:
      BlobNotFoundError,
      blobstore_service_pb.BlobstoreServiceError.DATA_INDEX_OUT_OF_RANGE:
      DataIndexOutOfRangeError,
      blobstore_service_pb.BlobstoreServiceError.BLOB_FETCH_SIZE_TOO_LARGE:
      BlobFetchSizeTooLargeError,
      blobstore_service_pb.BlobstoreServiceError.PERMISSION_DENIED:
      PermissionDeniedError,
      }
  desired_exc = error_map.get(error.application_error)
  return desired_exc(error.error_detail) if desired_exc else error


def _format_creation(stamp):
  """Format an upload creation timestamp with milliseconds.

  This method is necessary to format a timestamp with microseconds on Python
  versions before 2.6.

  Cannot simply convert datetime objects to str because the microseconds are
  stripped from the format when set to 0.  The upload creation date format will
  always have microseconds padded out to 6 places.

  Args:
    stamp: datetime.datetime object to format.

  Returns:
    Formatted datetime as Python 2.6 format '%Y-%m-%d %H:%M:%S.%f'.
  """
  return '%s.%06d' % (stamp.strftime(_BASE_CREATION_HEADER_FORMAT),
                      stamp.microsecond)


def _parse_creation(creation_string, field_name):
  """Parses upload creation string from header format.

  Parse creation date of the format:

    YYYY-mm-dd HH:MM:SS.ffffff

    Y: Year
    m: Month (01-12)
    d: Day (01-31)
    H: Hour (00-24)
    M: Minute (00-59)
    S: Second (00-59)
    f: Microsecond

  Args:
    creation_string: String creation date format.

  Returns:
    datetime object parsed from creation_string.

  Raises:
    _CreationFormatError when the creation string is formatted incorrectly.
  """


  split_creation_string = creation_string.split('.', 1)
  if len(split_creation_string) != 2:
    raise _CreationFormatError(
        'Could not parse creation %s in field %s.' % (creation_string,
                                                      field_name))
  timestamp_string, microsecond = split_creation_string

  try:
    timestamp = time.strptime(timestamp_string,
                              _BASE_CREATION_HEADER_FORMAT)
    microsecond = int(microsecond)
  except ValueError:
    raise _CreationFormatError('Could not parse creation %s in field %s.'
                               % (creation_string, field_name))

  return datetime.datetime(*timestamp[:6] + tuple([microsecond]))


def create_upload_url(success_path,
                      _make_sync_call=None,
                      max_bytes_per_blob=None,
                      max_bytes_total=None):
  """Create upload URL for POST form.

  Args:
    success_path: Path within application to call when POST is successful
      and upload is complete.
    _make_sync_call: Used for dependency injection in tests.
    max_bytes_per_blob: The maximum size in bytes that any one blob in the
      upload can be or None for no maximum size.
    max_bytes_total: The maximum size in bytes that the aggregate sizes of all
      of the blobs in the upload can be or None for no maximum size.

  Raises:
    TypeError: If max_bytes_per_blob or max_bytes_total are not integral types.
    ValueError: If max_bytes_per_blob or max_bytes_total are not
      positive values.
  """
  request = blobstore_service_pb.CreateUploadURLRequest()
  response = blobstore_service_pb.CreateUploadURLResponse()
  request.set_success_path(success_path)

  if _make_sync_call is not None:
    if not callable(_make_sync_call):
      raise TypeError('_make_sync_call must be callable')
  else:
    _make_sync_call = apiproxy_stub_map.MakeSyncCall

  if max_bytes_per_blob is not None:
    if not isinstance(max_bytes_per_blob, (int, long)):
      raise TypeError('max_bytes_per_blob must be integer.')
    if max_bytes_per_blob < 1:
      raise ValueError('max_bytes_per_blob must be positive.')
    request.set_max_upload_size_per_blob_bytes(max_bytes_per_blob)

  if max_bytes_total is not None:
    if not isinstance(max_bytes_total, (int, long)):
      raise TypeError('max_bytes_total must be integer.')
    if max_bytes_total < 1:
      raise ValueError('max_bytes_total must be positive.')
    request.set_max_upload_size_bytes(max_bytes_total)

  if (request.has_max_upload_size_bytes() and
      request.has_max_upload_size_per_blob_bytes()):
    if (request.max_upload_size_bytes() <
        request.max_upload_size_per_blob_bytes()):
      raise ValueError('max_bytes_total can not be less'
                       ' than max_upload_size_per_blob_bytes')

  try:
    _make_sync_call('blobstore', 'CreateUploadURL', request, response)
  except apiproxy_errors.ApplicationError, e:
    raise _ToBlobstoreError(e)

  return response.url()


def delete(blob_keys, _make_sync_call=apiproxy_stub_map.MakeSyncCall):
  """Delete a blob from Blobstore.

  Args:
    blob_keys: Single instance or list of blob keys.  A blob-key can be either
      a string or an instance of BlobKey.
    _make_sync_call: Used for dependency injection in tests.
  """
  if isinstance(blob_keys, (basestring, BlobKey)):
    blob_keys = [blob_keys]
  request = blobstore_service_pb.DeleteBlobRequest()
  for blob_key in blob_keys:
    request.add_blob_key(str(blob_key))
  response = api_base_pb.VoidProto()
  try:
    _make_sync_call('blobstore', 'DeleteBlob', request, response)
  except apiproxy_errors.ApplicationError, e:
    raise _ToBlobstoreError(e)


def fetch_data(blob_key, start_index, end_index,
               _make_sync_call=apiproxy_stub_map.MakeSyncCall):
  """Fetch data for blob.

  See docstring for ext.blobstore.fetch_data for more details.

  Args:
    blob: BlobKey, str or unicode representation of BlobKey of
      blob to fetch data from.
    start_index: Start index of blob data to fetch.  May not be negative.
    end_index: End index (exclusive) of blob data to fetch.  Must be
      >= start_index.

  Returns:
    str containing partial data of blob.  See docstring for
    ext.blobstore.fetch_data for more details.

  Raises:
    See docstring for ext.blobstore.fetch_data for more details.
  """
  if not isinstance(start_index, (int, long)):
    raise TypeError('start_index must be integer.')

  if not isinstance(end_index, (int, long)):
    raise TypeError('end_index must be integer.')

  if isinstance(blob_key, BlobKey):
    blob_key = str(blob_key).decode('utf-8')
  elif isinstance(blob_key, str):
    blob_key = blob_key.decode('utf-8')
  elif not isinstance(blob_key, unicode):
    raise TypeError('Blob-key must be str, unicode or BlobKey: %s' % blob_key)


  if start_index < 0:
    raise DataIndexOutOfRangeError(
        'May not fetch blob at negative index.')


  if end_index < start_index:
    raise DataIndexOutOfRangeError(
        'Start index %d > end index %d' % (start_index, end_index))


  fetch_size = end_index - start_index + 1

  if fetch_size > MAX_BLOB_FETCH_SIZE:
    raise BlobFetchSizeTooLargeError(
        'Blob fetch size is too large: %d' % fetch_size)

  request = blobstore_service_pb.FetchDataRequest()
  response = blobstore_service_pb.FetchDataResponse()

  request.set_blob_key(blob_key)
  request.set_start_index(start_index)
  request.set_end_index(end_index)

  try:
    _make_sync_call('blobstore', 'FetchData', request, response)
  except apiproxy_errors.ApplicationError, e:
    raise _ToBlobstoreError(e)

  return response.data()
