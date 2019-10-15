from enum import Enum


class QueryType(Enum):
    SELECT = "SELECT"
    CONSTRUCT = "CONSTRUCT"
    ASK = "ASK"
    DESCRIBE = "DESCRIBE"
    INSERT = "INSERT"
    DELETE = "DELETE"
    CREATE = "CREATE"
    CLEAR = "CLEAR"
    DROP = "DROP"
    LOAD = "LOAD"
    COPY = "COPY"
    MOVE = "MOVE"
    ADD = "ADD"

    @classmethod
    def aslist(cls):
        return list(map(lambda c: c.value, cls))
