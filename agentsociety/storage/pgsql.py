import asyncio
from typing import Any

import psycopg
import psycopg.sql
import ray
from psycopg.rows import dict_row

from ..utils.decorators import lock_decorator
from ..logger import get_logger

__all__ = ["PgWriter"]

TABLE_PREFIX = "as_"

PGSQL_DICT: dict[str, list[Any]] = {
    # Experiment
    "experiment": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        tenant_id TEXT,
        id UUID,
        name TEXT,
        num_day INT4,
        status INT4, 
        cur_day INT4,
        cur_t FLOAT,
        config TEXT,
        error TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (tenant_id, id)
    )
""",
    ],
    # Agent Profile
    "agent_profile": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT PRIMARY KEY,
        name TEXT,
        profile JSONB
    )
""",
    ],
    # Global Prompt
    "global_prompt": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        day INT4,
        t FLOAT,
        prompt TEXT,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
    # Agent Dialog
    "agent_dialog": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT,
        day INT4,
        t FLOAT,
        type INT4,
        speaker TEXT,
        content TEXT,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_id_idx ON {table_name} (id)",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
    # Agent Status
    "agent_status": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT,
        day INT4,
        t FLOAT,
        lng DOUBLE PRECISION,
        lat DOUBLE PRECISION,
        parent_id INT4,
        friend_ids INT[],
        action TEXT,
        status JSONB,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_id_idx ON {table_name} (id)",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
    # Agent Survey
    "agent_survey": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT,
        day INT4,
        t FLOAT,
        survey_id UUID,
        result JSONB,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_id_idx ON {table_name} (id)",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
}
TO_UPDATE_EXP_INFO_KEYS_AND_TYPES: list[tuple[str, Any]] = [
    ("tenant_id", str),
    ("id", None),
    ("name", str),
    ("num_day", int),
    ("status", int),
    ("cur_day", int),
    ("cur_t", float),
    ("config", str),
    ("error", str),
    ("created_at", None),
    ("updated_at", None),
]


def _create_pg_tables(exp_id: str, dsn: str):
    for table_type, exec_strs in PGSQL_DICT.items():
        if not table_type == "experiment":
            table_name = f"{TABLE_PREFIX}{exp_id.replace('-', '_')}_{table_type}"
        else:
            table_name = f"{TABLE_PREFIX}{table_type}"
        # # debug str
        # for _str in [f"DROP TABLE IF EXISTS {table_name}"] + [
        #     _exec_str.format(table_name=table_name) for _exec_str in exec_strs
        # ]:
        #     print(_str)
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                if not table_type == "experiment":
                    # delete table
                    cur.execute(f"DROP TABLE IF EXISTS {table_name}")  # type:ignore
                    get_logger().debug(
                        f"table:{table_name} sql: DROP TABLE IF EXISTS {table_name}"
                    )
                    conn.commit()
                # create table
                for _exec_str in exec_strs:
                    exec_str = _exec_str.format(table_name=table_name)
                    cur.execute(exec_str)
                    get_logger().debug(f"table:{table_name} sql: {exec_str}")
                conn.commit()


@ray.remote
class PgWriter:
    def __init__(self, tenant_id: str, exp_id: str, dsn: str, init: bool):
        """
        Initialize the PgWriter.

        - **Args**:
            - `tenant_id` (str): The ID of the tenant.
            - `exp_id` (str): The ID of the experiment.
            - `dsn` (str): The DSN of the PostgreSQL database.
            - `init` (bool): Whether to initialize the PostgreSQL tables.
        """
        self.tenant_id = tenant_id
        self.exp_id = exp_id
        self._dsn = dsn
        self._lock = asyncio.Lock()
        if init:
            _create_pg_tables(exp_id, dsn)

    @lock_decorator
    async def write_dialog(self, rows: list[tuple]):
        _tuple_types = [int, int, float, int, str, str, str, None]
        table_name = f"{TABLE_PREFIX}{self.exp_id.replace('-', '_')}_agent_dialog"
        async with await psycopg.AsyncConnection.connect(self._dsn) as aconn:
            copy_sql = psycopg.sql.SQL(
                "COPY {} (id, day, t, type, speaker, content, created_at) FROM STDIN"
            ).format(psycopg.sql.Identifier(table_name))
            _rows: list[Any] = []
            async with aconn.cursor() as cur:
                async with cur.copy(copy_sql) as copy:
                    for row in rows:
                        _row = [
                            _type(r) if _type is not None and r is not None else r
                            for (_type, r) in zip(_tuple_types, row)
                        ]
                        await copy.write_row(_row)
                        _rows.append(_row)
            get_logger().debug(f"table:{table_name} sql: {copy_sql} values: {_rows}")

    @lock_decorator
    async def write_status(self, rows: list[tuple]):
        _tuple_types = [int, int, float, float, float, int, list, str, str, None]
        table_name = f"{TABLE_PREFIX}{self.exp_id.replace('-', '_')}_agent_status"
        async with await psycopg.AsyncConnection.connect(self._dsn) as aconn:
            copy_sql = psycopg.sql.SQL(
                "COPY {} (id, day, t, lng, lat, parent_id, friend_ids, action, status, created_at) FROM STDIN"
            ).format(psycopg.sql.Identifier(table_name))
            _rows: list[Any] = []
            async with aconn.cursor() as cur:
                async with cur.copy(copy_sql) as copy:
                    for row in rows:
                        _row = [
                            _type(r) if _type is not None and r is not None else r
                            for (_type, r) in zip(_tuple_types, row)
                        ]
                        await copy.write_row(_row)
                        _rows.append(_row)
            get_logger().debug(f"table:{table_name} sql: {copy_sql} values: {_rows}")

    @lock_decorator
    async def write_profile(self, rows: list[tuple]):
        _tuple_types = [int, str, str]
        table_name = f"{TABLE_PREFIX}{self.exp_id.replace('-', '_')}_agent_profile"
        async with await psycopg.AsyncConnection.connect(self._dsn) as aconn:
            copy_sql = psycopg.sql.SQL("COPY {} (id, name, profile) FROM STDIN").format(
                psycopg.sql.Identifier(table_name)
            )
            _rows: list[Any] = []
            async with aconn.cursor() as cur:
                async with cur.copy(copy_sql) as copy:
                    for row in rows:
                        _row = [
                            _type(r) if _type is not None and r is not None else r
                            for (_type, r) in zip(_tuple_types, row)
                        ]
                        await copy.write_row(_row)
                        _rows.append(_row)
            get_logger().debug(f"table:{table_name} sql: {copy_sql} values: {_rows}")

    @lock_decorator
    async def write_survey(self, rows: list[tuple]):
        _tuple_types = [str, int, int, float, str, str, None]
        table_name = f"{TABLE_PREFIX}{self.exp_id.replace('-', '_')}_agent_survey"
        async with await psycopg.AsyncConnection.connect(self._dsn) as aconn:
            copy_sql = psycopg.sql.SQL(
                "COPY {} (id, day, t, survey_id, result, created_at) FROM STDIN"
            ).format(psycopg.sql.Identifier(table_name))
            _rows: list[Any] = []
            async with aconn.cursor() as cur:
                async with cur.copy(copy_sql) as copy:
                    for row in rows:
                        _row = [
                            _type(r) if _type is not None and r is not None else r
                            for (_type, r) in zip(_tuple_types, row)
                        ]
                        await copy.write_row(_row)
                        _rows.append(_row)
            get_logger().debug(f"table:{table_name} sql: {copy_sql} values: {_rows}")

    @lock_decorator
    async def save_global_prompt(self, prompt_info: dict[str, Any]):
        table_name = f"{TABLE_PREFIX}{self.exp_id.replace('-', '_')}_global_prompt"
        async with await psycopg.AsyncConnection.connect(self._dsn) as aconn:
            async with aconn.cursor() as cur:
                copy_sql = psycopg.sql.SQL(
                    "COPY {} (day, t, prompt, created_at) FROM STDIN"
                ).format(psycopg.sql.Identifier(table_name))
                row = (
                    prompt_info["day"],
                    prompt_info["t"],
                    prompt_info["prompt"],
                    prompt_info["created_at"],
                )
                async with cur.copy(copy_sql) as copy:
                    await copy.write_row(row)
                get_logger().debug(f"table:{table_name} sql: {copy_sql} values: {row}")

    @lock_decorator
    async def update_exp_info(self, exp_info: dict[str, Any]):
        # timestamp不做类型转换
        table_name = f"{TABLE_PREFIX}experiment"
        async with await psycopg.AsyncConnection.connect(self._dsn) as aconn:
            async with aconn.cursor(row_factory=dict_row) as cur:
                exec_str = "SELECT * FROM {table_name} WHERE id=%s".format(
                    table_name=table_name
                ), (self.exp_id,)
                await cur.execute(
                    "SELECT * FROM {table_name} WHERE id=%s".format(
                        table_name=table_name
                    ),
                    (self.exp_id,),
                )  # type:ignore
                get_logger().debug(f"table:{table_name} sql: {exec_str}")
                record_exists = await cur.fetchall()
                if record_exists:
                    # UPDATE
                    columns = ", ".join(
                        f"{key} = %s" for key, _ in TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
                    )
                    update_sql = psycopg.sql.SQL(
                        f"UPDATE {{}} SET {columns} WHERE id='{self.exp_id}'"  # type:ignore
                    ).format(psycopg.sql.Identifier(table_name))
                    params = [
                        (
                            _type(exp_info[key])
                            if _type is not None and exp_info[key] is not None
                            else exp_info[key]
                        )
                        for key, _type in TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
                    ]
                    get_logger().debug(
                        f"table:{table_name} sql: {update_sql} values: {params}"
                    )
                    await cur.execute(update_sql, params)
                else:
                    # INSERT
                    keys = ", ".join(
                        key for key, _ in TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
                    )
                    placeholders = ", ".join(
                        ["%s"] * len(TO_UPDATE_EXP_INFO_KEYS_AND_TYPES)
                    )
                    insert_sql = psycopg.sql.SQL(
                        f"INSERT INTO {{}} ({keys}) VALUES ({placeholders})"  # type:ignore
                    ).format(psycopg.sql.Identifier(table_name))
                    params = [
                        (
                            _type(exp_info[key])
                            if _type is not None and exp_info[key] is not None
                            else exp_info[key]
                        )
                        for key, _type in TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
                    ]
                    get_logger().debug(
                        f"table:{table_name} sql: {insert_sql} values: {params}"
                    )
                    await cur.execute(insert_sql, params)
                await aconn.commit()
