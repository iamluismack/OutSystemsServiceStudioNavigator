"""Parsing of the macOS "Open from Environment" screenshot text (no GUI needed).

Boxes are real Vision output from Service Studio 11.55 for Mac (x, y, w, h, text).
"""

import pytest

from os_module_navigator.automation import mac_ocr
from os_module_navigator.automation.mac_ocr import (
    TextBox,
    ocr_equivalent,
    parse_results,
    selected_row_index,
)

FULL_LIST = [
    (657, 21, 261, 25, "Open from Environment"),
    (34, 87, 663, 27, "Modules available at 'example.outsystemsenterprise.com'"),
    (53, 137, 602, 30, "Search for Module Name, Application Name or Author"),
    (1142, 233, 32, 27, "By"),
    (46, 235, 85, 23, "Module"),
    (398, 235, 162, 26, "* Application"),
    (821, 235, 103, 28, "Changed"),
    (821, 299, 229, 26, "26/09/2023 at 14:21"),
    (1139, 299, 156, 25, "Administrator"),
    (43, 302, 194, 27, "AIMS_BaseTypes"),
    (435, 302, 275, 23, "Al Mentor Studio Shared"),
    (43, 366, 158, 27, "AmazonS3_IS"),
    (435, 368, 348, 25, "Amazon Simple Storage Serv..."),
    (821, 368, 167, 25, "April 9 at 17:07"),
    (1142, 368, 137, 26, "Jane Smith"),
    (819, 496, 69, 25, "18:35"),
    (432, 497, 101, 25, "Inventory"),
    (43, 498, 101, 23, "Inventory"),
    (1142, 498, 199, 23, "John Doe"),
    (48, 827, 224, 16, "Shinninn Carvirac CC"),
    (439, 827, 323, 19, "Chinninn Intanratinn C"),
    (824, 827, 231, 16, "Nnuamhar 1 at 17•05"),
    (1142, 827, 137, 21, "Jnhn Nna"),
    (1411, 925, 96, 28, "Cancel"),
    (1256, 926, 73, 32, "Open"),
    (988, 928, 185, 25, "View Versions"),
]


def boxes(raw):
    return [TextBox(*r) for r in raw]


def test_rows_are_rebuilt_by_column():
    rows = parse_results(boxes(FULL_LIST))
    assert rows is not None
    cells = [r.row.cells for r in rows if r.row.on_screen]
    assert cells[0] == {
        "Module": "AIMS_BaseTypes",
        "Application": "Al Mentor Studio Shared",
        "Changed": "26/09/2023 at 14:21",
        "By": "Administrator",
    }
    assert cells[2]["Module"] == "Inventory"
    assert cells[2]["Application"] == "Inventory"
    assert cells[2]["Changed"] == "18:35"
    assert len(cells) == 3


def test_clipped_bottom_row_is_flagged_and_blanked():
    rows = parse_results(boxes(FULL_LIST))
    last = rows[-1].row
    assert last.on_screen is False
    assert last.cells == {}


def test_header_and_footer_are_not_rows():
    rows = parse_results(boxes(FULL_LIST))
    texts = " ".join(" ".join(r.row.cells.values()) for r in rows)
    assert "Cancel" not in texts
    assert "Module" not in texts


def test_no_table_returns_none():
    assert parse_results(boxes(FULL_LIST[:3])) is None


def test_no_matches_hides_the_table_but_keeps_the_footer():
    no_matches = [*FULL_LIST[:2], (53, 137, 275, 27, "Zzq_Nothing"), *FULL_LIST[-3:]]
    assert parse_results(boxes(no_matches)) == []


def test_empty_results():
    header_only = [b for b in FULL_LIST if b[1] < 280 or b[4] in ("Open", "Cancel")]
    assert parse_results(boxes(header_only)) == []


def test_ocr_equivalent_folds_confusable_characters():
    assert ocr_equivalent("Al_Mentor", "AI_Mentor")
    assert ocr_equivalent("M0dule1", "Modulel")
    assert not ocr_equivalent("Inventory", "Inventory_CW")


def test_selected_row_requires_exactly_one_highlight():
    rows = parse_results(boxes(FULL_LIST))
    target = rows[1]
    assert selected_row_index(rows, lambda top, bottom: 0.9 if top == target.top else 0.0) == 1
    assert selected_row_index(rows, lambda top, bottom: 0.0) is None
    assert selected_row_index(rows, lambda top, bottom: 0.9) is None


def test_repair_confusables_keeps_ocr_case():
    from os_module_navigator.automation.mac_ocr import repair_confusables

    assert repair_confusables("Inventory", "inventory") == "Inventory"
    assert repair_confusables("AlMS_BaseTypes", "AIMS_BaseTypes") == "AIMS_BaseTypes"
    assert repair_confusables("AlMS_BaseTypes", "aims_basetypes") == "AiMS_BaseTypes"


# --- Manage Dependencies (boxes recorded from Service Studio 11.55 for Mac, 2x) -----

DEPS_BOXES = [
    mac_ocr.TextBox(677.8, 21.0, 250.1, 26.0, "Manage Dependencies"),
    mac_ocr.TextBox(35.1, 95.8, 582.0, 30.4, "Select public elements to use in this module."),
    mac_ocr.TextBox(56.1, 184.6, 247.7, 28.4, "Q OutSystemsCharts"),
    mac_ocr.TextBox(479.1, 186.9, 30.4, 21.0, "All"),
    mac_ocr.TextBox(556.1, 186.4, 72.8, 22.1, "In use"),
    mac_ocr.TextBox(694.2, 184.6, 301.5, 28.4, "Q Search public elements"),
    mac_ocr.TextBox(1154.6, 182.3, 32.7, 25.7, "All"),
    mac_ocr.TextBox(1229.4, 184.6, 74.8, 23.4, "In use"),
    mac_ocr.TextBox(1332.2, 184.6, 222.0, 28.4, "Modified or missing"),
    mac_ocr.TextBox(44.4, 271.0, 212.7, 28.0, "OutSystemsCharts"),
    mac_ocr.TextBox(768.9, 287.4, 210.3, 25.7, "OutSystemsCharts"),
    mac_ocr.TextBox(44.4, 308.4, 261.8, 25.7, "OutSystemsChartsWeb"),
    mac_ocr.TextBox(771.3, 327.0, 135.6, 23.5, "- UI Flows"),
    mac_ocr.TextBox(44.4, 341.0, 451.1, 28.2, 'Search for "OutSystemsCharts" in Forge'),
    mac_ocr.TextBox(694.2, 371.5, 21.0, 16.4, "V"),
    mac_ocr.TextBox(766.6, 366.8, 198.7, 26.2, "• Client Actions"),
    mac_ocr.TextBox(808.7, 406.6, 278.1, 25.7, "AdvancedFormat_Init_v1"),
    mac_ocr.TextBox(888.0, 805.4, 154.5, 29.5, "StackingType"),
    mac_ocr.TextBox(95.8, 937.0, 231.4, 28.0, "'OutSystemsCharts'"),
    mac_ocr.TextBox(100.5, 967.0, 1371.9, 31.0, "This component features the most commonly used"),
    mac_ocr.TextBox(1065.7, 1126.0, 79.7, 33.2, "Apply"),
    mac_ocr.TextBox(1227.0, 1126.0, 137.9, 28.3, "Refresh all"),
    mac_ocr.TextBox(1446.7, 1126.1, 93.6, 28.4, "Cancel"),
]


def test_dependency_dialog_modules_skip_forge_link_and_info_panel():
    layout = mac_ocr.parse_dependency_dialog(DEPS_BOXES, 2.0)
    assert layout is not None
    assert layout.modules == [("OutSystemsCharts", False), ("OutSystemsChartsWeb", False)]
    assert set(layout.buttons) == {"Apply", "Refresh all", "Cancel", "All"}
    assert layout.buttons["All"].x == 1154.6  # the elements panel's filter, not the modules'


def test_dependency_tree_rows_map_to_the_checkbox_column():
    layout = mac_ocr.parse_dependency_dialog(DEPS_BOXES, 2.0)
    rows = {r.label: round(r.box[0]) for r in layout.elements}
    # Root at level 0, folders at level 1 (with or without an icon read as text),
    # an entity at level 3; the action row lands on its chevron (no checkbox there).
    assert rows == {
        "OutSystemsCharts": 706,
        "UI Flows": 746,
        "Client Actions": 746,
        "AdvancedFormat_Init_v1": 746,
        "StackingType": 826,
    }


def test_no_dependency_dialog_without_filters():
    assert mac_ocr.parse_dependency_dialog(DEPS_BOXES[:3], 2.0) is None


ACCENT, WHITE, BLACK, BG = (71, 65, 201), (255, 255, 255), (0, 0, 0), (24, 26, 31)


def _box(mark):
    def pixel(x, y):
        if not (90 <= x <= 110 and 90 <= y <= 110):
            return BG
        if mark == "none":
            return BLACK
        if mark == "dash" and y == 100 and 94 <= x <= 106:
            return WHITE
        if mark == "tick" and abs((x - 100) + (y - 100)) <= 1 and 94 <= x <= 106:
            return WHITE
        return ACCENT

    return pixel


@pytest.mark.parametrize(("mark", "state"), [("none", 0), ("tick", 1), ("dash", 2)])
def test_checkbox_state_from_pixels(mark, state):
    assert mac_ocr.checkbox_state(_box(mark), 100, 100, 2.0) == state


def test_checkbox_state_none_where_no_box_is_drawn():
    assert mac_ocr.checkbox_state(lambda x, y: BG, 100, 100, 2.0) is None
    # Accent without a white mark (e.g. a highlighted row's background) is not a box.
    assert mac_ocr.checkbox_state(lambda x, y: ACCENT, 100, 100, 2.0) is None


def test_module_merged_with_application_is_split():
    merged = [
        *FULL_LIST[:7],
        (43, 302, 540, 27, "Shipping_BL Shipping Business Logic"),
        (821, 299, 229, 26, "01:20"),
        (1139, 299, 156, 25, "Administrator"),
        *FULL_LIST[-3:],
    ]
    rows = parse_results(boxes(merged))
    assert rows[0].row.cells["Module"] == "Shipping_BL"
    assert rows[0].row.cells["Application"] == "Shipping Business Logic"


def test_module_merged_without_application_header_is_split():
    no_app_header = [b for b in FULL_LIST if b[4] != "* Application"]
    merged = [
        *no_app_header[:6],
        (43, 302, 540, 27, "Shipping_BL Shipping Business Logic"),
        (821, 299, 229, 26, "01:20"),
        (1139, 299, 156, 25, "Administrator"),
        *no_app_header[-3:],
    ]
    rows = parse_results(boxes(merged))
    assert rows[0].row.cells["Module"] == "Shipping_BL"
    assert rows[0].row.cells["Application"] == "Shipping Business Logic"


def test_selection_fill_detects_plain_accent_only():
    red = lambda x, y: (209, 65, 72)  # noqa: E731
    assert mac_ocr.is_selection_fill(red, 10, 10, 2.0)
    tick = lambda x, y: (255, 255, 255) if y == 10 else (209, 65, 72)  # noqa: E731
    assert not mac_ocr.is_selection_fill(tick, 10, 10, 2.0)
    dark = lambda x, y: (30, 30, 30)  # noqa: E731
    assert not mac_ocr.is_selection_fill(dark, 10, 10, 2.0)


def test_module_suffix_read_as_space_is_rejoined():
    cells = {"Module": "ORDERS CW Acrne - ORDFRS Cora Widnets", "Application": ""}
    mac_ocr._split_merged_module(cells)
    assert cells["Module"] == "ORDERS_CW"
    assert cells["Application"] == "Acrne - ORDFRS Cora Widnets"
    plain = {"Module": "ORDERS Acme - ORDERS", "Application": ""}
    mac_ocr._split_merged_module(plain)
    assert plain["Module"] == "ORDERS" and plain["Application"] == "Acme - ORDERS"
