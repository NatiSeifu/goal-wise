"""Pure parser for canonical planning CSV files."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Any, cast

MAX_PLANNING_IMPORT_BYTES = 1 * 1024 * 1024
MAX_PLANNING_IMPORT_ROWS = 500


@dataclass(frozen=True, slots=True)
class PlanningCsvRow:
    """One nonblank CSV record and its physical source row number."""

    row_number: int
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ParsedPlanningCsv:
    """Raw CSV records before domain-specific validation."""

    headers: tuple[str, ...]
    rows: tuple[PlanningCsvRow, ...]


class PlanningCsvParseError(ValueError):
    """Raised when CSV input cannot be converted into raw records."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        row_number: int | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.row_number = row_number
        super().__init__(message)


def parse_planning_csv(data: bytes | str) -> ParsedPlanningCsv:
    """Parse bounded UTF-8 CSV input into immutable raw records."""

    text = _decode_input(data)
    if not text.strip():
        raise PlanningCsvParseError(
            code="empty_file",
            message="The CSV file must contain a header and at least one data row.",
        )

    reader: Any = csv.reader(io.StringIO(text, newline=""), strict=True)
    try:
        headers = _read_headers(reader)
        rows: list[PlanningCsvRow] = []
        for values in reader:
            row_number = reader.line_num
            if not values:
                continue
            if len(rows) >= MAX_PLANNING_IMPORT_ROWS:
                raise PlanningCsvParseError(
                    code="row_limit_exceeded",
                    message=(
                        "The CSV file cannot contain more than "
                        f"{MAX_PLANNING_IMPORT_ROWS} data rows."
                    ),
                    row_number=row_number,
                )
            if len(values) != len(headers):
                raise PlanningCsvParseError(
                    code="wrong_column_count",
                    message=f"Row must contain exactly {len(headers)} columns.",
                    row_number=row_number,
                )
            rows.append(PlanningCsvRow(row_number=row_number, values=tuple(values)))
    except csv.Error as exc:
        raise PlanningCsvParseError(
            code="malformed_csv",
            message="The CSV file contains malformed quoting or delimiters.",
            row_number=reader.line_num or None,
        ) from exc

    if not rows:
        raise PlanningCsvParseError(
            code="missing_data",
            message="The CSV file must contain at least one data row.",
        )

    return ParsedPlanningCsv(headers=tuple(headers), rows=tuple(rows))


def _decode_input(data: bytes | str) -> str:
    if isinstance(data, bytes):
        if len(data) > MAX_PLANNING_IMPORT_BYTES:
            raise PlanningCsvParseError(
                code="file_size_limit_exceeded",
                message=f"The CSV file cannot exceed {MAX_PLANNING_IMPORT_BYTES} bytes.",
            )
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PlanningCsvParseError(
                code="invalid_utf8",
                message="The CSV file must be valid UTF-8.",
            ) from exc

    encoded = data.encode("utf-8")
    if len(encoded) > MAX_PLANNING_IMPORT_BYTES:
        raise PlanningCsvParseError(
            code="file_size_limit_exceeded",
            message=f"The CSV file cannot exceed {MAX_PLANNING_IMPORT_BYTES} bytes.",
        )
    return data


def _read_headers(reader: Any) -> list[str]:
    try:
        headers = cast(list[str], next(reader))
    except StopIteration as exc:
        raise PlanningCsvParseError(
            code="missing_header",
            message="The CSV file must contain a header row.",
        ) from exc
    except csv.Error as exc:
        raise PlanningCsvParseError(
            code="malformed_csv",
            message="The CSV header contains malformed quoting or delimiters.",
            row_number=reader.line_num or None,
        ) from exc

    if not headers or any(not header.strip() for header in headers):
        raise PlanningCsvParseError(
            code="invalid_header",
            message="Every header column must have a nonblank name.",
            row_number=reader.line_num or None,
        )
    if len(set(headers)) != len(headers):
        raise PlanningCsvParseError(
            code="duplicate_header",
            message="The CSV header cannot contain duplicate column names.",
            row_number=reader.line_num or None,
        )
    return headers
