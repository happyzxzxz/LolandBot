# Shamelessly stolen from lavalink.py
import struct
from io import BytesIO
from typing import Optional


class DataWriter:
    def __init__(self):
        self._buf = BytesIO()

    def _write(self, data):
        self._buf.write(data)

    def write_byte(self, byte):
        """
        Writes a single byte to the stream.

        Parameters
        ----------
        byte: Any
            This can be anything ``BytesIO.write()`` accepts.
        """
        self._buf.write(byte)

    def write_boolean(self, boolean: bool):
        """
        Writes a bool to the stream.

        Parameters
        ----------
        boolean: :class:`bool`
            The bool to write.
        """
        enc = struct.pack('B', 1 if boolean else 0)
        self.write_byte(enc)

    def write_unsigned_short(self, short: int):
        """
        Writes an unsigned short to the stream.

        Parameters
        ----------
        short: :class:`int`
            The unsigned short to write.
        """
        enc = struct.pack('>H', short)
        self._write(enc)

    def write_int(self, integer: int):
        """
        Writes an int to the stream.

        Parameters
        ----------
        integer: :class:`int`
            The integer to write.
        """
        enc = struct.pack('>i', integer)
        self._write(enc)

    def write_long(self, long_value: int):
        """
        Writes a long to the stream.

        Parameters
        ----------
        long_value: :class:`int`
            The long to write.
        """
        enc = struct.pack('>Q', long_value)
        self._write(enc)

    def write_nullable_utf(self, utf_string: Optional[str]):
        """
        Writes an optional string to the stream.

        Parameters
        ----------
        utf_string: Optional[:class:`str`]
            The optional string to write.
        """
        self.write_boolean(bool(utf_string))

        if utf_string:
            self.write_utf(utf_string)

    def write_utf(self, utf_string: str):
        """
        Writes a utf string to the stream.

        Parameters
        ----------
        utf_string: :class:`str`
            The string to write.
        """
        utf = utf_string.encode('utf8')
        byte_len = len(utf)

        if byte_len > 65535:
            raise OverflowError('UTF string may not exceed 65535 bytes!')

        self.write_unsigned_short(byte_len)
        self._write(utf)

    def finish(self) -> bytes:
        """
        Finalizes the stream by writing the necessary flags, byte length etc.

        Returns
        ----------
        :class:`bytes`
            The finalized stream.
        """
        with BytesIO() as track_buf:
            byte_len = self._buf.getbuffer().nbytes
            flags = byte_len | (1 << 30)
            enc_flags = struct.pack('>i', flags)
            track_buf.write(enc_flags)

            self._buf.seek(0)
            track_buf.write(self._buf.read())
            self._buf.close()

            track_buf.seek(0)
            return track_buf.read()
