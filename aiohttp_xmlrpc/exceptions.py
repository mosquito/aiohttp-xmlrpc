from functools import singledispatch


__all__ = (
    'XMLRPCError', 'ApplicationError', 'InvalidCharacterError', 'ParseError', 'ServerError',
    'SystemError', 'TransportError', 'UnsupportedEncodingError', 'xml_exception'
)


class XMLRPCError(Exception):
    code = -32500


class ParseError(XMLRPCError):
    code = -32700


class UnsupportedEncodingError(ParseError):
    code = -32701


class InvalidCharacterError(ParseError):
    code = -32702


class ServerError(XMLRPCError):
    code = -32603


class InvalidData(ServerError):
    code = -32600


class MethodNotFound(ServerError):
    code = -32601


class InvalidArguments(ServerError):
    code = -32602


class ApplicationError(XMLRPCError):
    code = -32500


class SystemError(XMLRPCError):
    code = -32400


class TransportError(XMLRPCError):
    code = -32300


@singledispatch
def xml_exception(exc: Exception):
    return -32500, repr(exc)


@xml_exception.register(XMLRPCError)
def _(exc: XMLRPCError):
    return exc.code, repr(exc)

