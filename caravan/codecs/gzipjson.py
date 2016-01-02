import json
import zlib
import base64
import logging

log = logging.getLogger(__name__)

# http://docs.aws.amazon.com/amazonswf/latest/developerguide/swf-dg-limits.html
MAX_SWF_MESSAGE_SIZE = 32000


def dumps(data):
    """Encode data in JSON. Compress in zlib/base64 if too large for SWF.

    Boto3 expect any payload to be unicode and thus will crash on unicode errors
    if we don't base64 encode all zlib compressed payloads.
    """
    encoded_data = json.dumps(data)

    if len(encoded_data) > MAX_SWF_MESSAGE_SIZE:
        encoded_data = encoded_data.encode('utf-8')
        encoded_data = base64.b64encode(zlib.compress(encoded_data))

    return encoded_data


def loads(data):
    """Decode data in JSON, possibly zlib/base64 compressed."""
    try:
        decompressed_data = zlib.decompress(base64.b64decode(data))
        data = decompressed_data.decode('utf-8')
    except:
        pass

    return json.loads(data)
