from ee.clickhouse.client import sync_execute
from ee.clickhouse.sql.person import (
    KAFKA_PERSONS_DISTINCT_ID_TABLE_SQL,
    PERSONS_DISTINCT_ID_TABLE,
    PERSONS_DISTINCT_ID_TABLE_MV_SQL,
    PERSONS_DISTINCT_ID_TABLE_SQL,
)
from posthog.settings import CLICKHOUSE_CLUSTER, CLICKHOUSE_DATABASE
from posthog.special_migrations.definition import SpecialMigrationDefinition, SpecialMigrationOperation
from posthog.version_requirement import ServiceVersionRequirement

ONE_DAY = 60 * 60 * 24

TEMPORARY_TABLE_NAME = "person_distinct_id_special_migration"


class Migration(SpecialMigrationDefinition):

    posthog_min_version = "1.29.0"
    posthog_max_version = "1.30.0"

    service_version_requirements = [
        ServiceVersionRequirement(service="clickhouse", supported_version=">=21.6.0,<21.7.0"),
    ]

    # ideas:
    # 1. support functions as operations instead of just sql?
    #   1.1. receive the output of the previous op?
    operations = [
        SpecialMigrationOperation(
            sql=PERSONS_DISTINCT_ID_TABLE_SQL.replace(PERSONS_DISTINCT_ID_TABLE, TEMPORARY_TABLE_NAME, 1),
            database="clickhouse",
        ),
        SpecialMigrationOperation(
            sql=f"DROP TABLE person_distinct_id_mv ON CLUSTER {CLICKHOUSE_CLUSTER}", database="clickhouse",
        ),
        SpecialMigrationOperation(
            sql=f"DROP TABLE kafka_person_distinct_id ON CLUSTER {CLICKHOUSE_CLUSTER}", database="clickhouse",
        ),
        SpecialMigrationOperation(
            sql=f"""
                INSERT INTO {TEMPORARY_TABLE_NAME} (distinct_id, person_id, team_id, _sign, _timestamp, _offset)
                SELECT
                    distinct_id,
                    person_id,
                    team_id,
                    if(is_deleted==0, 1, -1) as _sign,
                    _timestamp,
                    _offset
                FROM {PERSONS_DISTINCT_ID_TABLE}
            """,
            database="clickhouse",
            timeout_seconds=ONE_DAY,
        ),
        SpecialMigrationOperation(
            sql=f"""
                RENAME TABLE
                    {CLICKHOUSE_DATABASE}.{PERSONS_DISTINCT_ID_TABLE} to {CLICKHOUSE_DATABASE}.person_distinct_id_backup,
                    {CLICKHOUSE_DATABASE}.{TEMPORARY_TABLE_NAME} to {CLICKHOUSE_DATABASE}.{PERSONS_DISTINCT_ID_TABLE}
                ON CLUSTER {CLICKHOUSE_CLUSTER}
            """,
            database="clickhouse",
        ),
        SpecialMigrationOperation(sql=KAFKA_PERSONS_DISTINCT_ID_TABLE_SQL, database="clickhouse",),
        SpecialMigrationOperation(sql=PERSONS_DISTINCT_ID_TABLE_MV_SQL, database="clickhouse",),
    ]

    def precheck():
        result = sync_execute("SELECT total_space, free_space FROM system.disks")
        total_space = result[0][0]
        free_space = result[0][1]
        if free_space > total_space / 2:
            return (True, None)
        else:
            return (False, "Upgrade your ClickHouse storage.")

    def progress():
        result = sync_execute(f"SELECT COUNT(1) FROM {TEMPORARY_TABLE_NAME}")
        result2 = sync_execute(f"SELECT COUNT(1) FROM {PERSONS_DISTINCT_ID_TABLE}")
        total_events_to_move = result2[0][0]
        total_events_moved = result[0][0]

        progress = 100 * total_events_moved / total_events_to_move
        return progress

    def rollback(migration_instance):
        if migration_instance.current_operation_index < 2:
            return True
        return False