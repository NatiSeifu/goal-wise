import pytest
from app.services.planning_import_parser import (
    MAX_PLANNING_IMPORT_BYTES,
    MAX_PLANNING_IMPORT_ROWS,
    PlanningCsvParseError,
    parse_planning_csv,
)

HEADER = "record_type,name,target_amount"


def test_parses_quoted_commas_utf8_and_blank_lines() -> None:
    parsed = parse_planning_csv(
        (f'{HEADER}\ngoal,"Moving, fund",3000.00\n\nincome,"Sala\u00e4ry",2500.00\n').encode()
    )

    assert parsed.headers == ("record_type", "name", "target_amount")
    assert [(row.row_number, row.values) for row in parsed.rows] == [
        (2, ("goal", "Moving, fund", "3000.00")),
        (4, ("income", "Salaäry", "2500.00")),
    ]


def test_accepts_text_input_and_preserves_raw_values() -> None:
    parsed = parse_planning_csv(f"{HEADER}\n goal , Name , 3000 \n")

    assert parsed.rows[0].values == (" goal ", " Name ", " 3000 ")


def test_rejects_malformed_csv_with_row_context() -> None:
    with pytest.raises(PlanningCsvParseError) as exc_info:
        parse_planning_csv(f'{HEADER}\n goal,"unterminated,3000\n')

    assert exc_info.value.code == "malformed_csv"
    assert exc_info.value.row_number == 2


def test_rejects_invalid_utf8() -> None:
    with pytest.raises(PlanningCsvParseError) as exc_info:
        parse_planning_csv(b"record_type\n\xff")

    assert exc_info.value.code == "invalid_utf8"
    assert exc_info.value.row_number is None


def test_rejects_wrong_column_count_before_returning_partial_rows() -> None:
    with pytest.raises(PlanningCsvParseError) as exc_info:
        parse_planning_csv(f"{HEADER}\n goal,Goal,3000\n cash,Only two\n")

    assert exc_info.value.code == "wrong_column_count"
    assert exc_info.value.row_number == 3


def test_rejects_duplicate_headers() -> None:
    with pytest.raises(PlanningCsvParseError) as exc_info:
        parse_planning_csv("record_type,name,name\ngoal,Goal,Goal\n")

    assert exc_info.value.code == "duplicate_header"
    assert exc_info.value.row_number == 1


def test_rejects_empty_file_and_header_only_file() -> None:
    for data, code in [("", "empty_file"), (HEADER + "\n", "missing_data")]:
        with pytest.raises(PlanningCsvParseError) as exc_info:
            parse_planning_csv(data)

        assert exc_info.value.code == code


def test_rejects_files_over_the_byte_limit() -> None:
    oversized = ("x" * (MAX_PLANNING_IMPORT_BYTES + 1)).encode("utf-8")

    with pytest.raises(PlanningCsvParseError, match="cannot exceed") as exc_info:
        parse_planning_csv(oversized)

    assert exc_info.value.code == "file_size_limit_exceeded"


def test_rejects_files_over_the_data_row_limit() -> None:
    data = (
        HEADER
        + "\n"
        + "\n".join(f"goal,Name {index},3000.00" for index in range(MAX_PLANNING_IMPORT_ROWS + 1))
    )

    with pytest.raises(PlanningCsvParseError) as exc_info:
        parse_planning_csv(data)

    assert exc_info.value.code == "row_limit_exceeded"
    assert exc_info.value.row_number == MAX_PLANNING_IMPORT_ROWS + 2
