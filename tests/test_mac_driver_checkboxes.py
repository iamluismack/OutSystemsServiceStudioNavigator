"""The elements tree keeps a row whose label sits one indentation level off."""

from types import SimpleNamespace

from os_module_navigator.automation import mac_ocr
from os_module_navigator.automation.mac_driver import MacServiceStudioDriver, _DepsView

GREY = (168, 156, 148)
BLACK = (0, 0, 0)


def _pixel_with_boxes(centres):
    def pixel(x, y):
        for cx, cy in centres:
            if abs(x - cx) <= 6 and abs(y - cy) <= 6:
                return BLACK
        return GREY

    return pixel


def _view(rows, checkbox_centres):
    layout = mac_ocr.DependencyLayout(None, None, [], rows, {})
    shot = SimpleNamespace(pixel=_pixel_with_boxes(checkbox_centres))
    return _DepsView(window=None, shot=shot, scale=1.0, layout=layout)


def test_leaf_row_one_level_too_far_left_is_kept():
    # Seen on Mac: a server action inside the URLs folder was placed at the folder's
    # level, where there is no checkbox, and silently dropped.
    rows = [
        mac_ocr.DependencyRow("Utilities_LIB", (354.0, 149.0), 142.0),
        mac_ocr.DependencyRow("URLs", (374.0, 189.0), 182.0),
        mac_ocr.DependencyRow("GetURL_X", (374.0, 209.0), 202.0),
    ]
    view = _view(rows, [(354, 149), (374, 189), (394, 209)])
    found = MacServiceStudioDriver()._checkboxes(view)
    assert [(r.label, r.state) for r in found] == [
        ("Utilities_LIB", 0),
        ("URLs", 0),
        ("GetURL_X", 0),
    ]
    assert found[2].element[0] == 394


def test_row_without_any_checkbox_is_still_skipped():
    rows = [
        mac_ocr.DependencyRow("Root", (354.0, 149.0), 142.0),
        mac_ocr.DependencyRow("UI Flows", (374.0, 169.0), 162.0),
    ]
    view = _view(rows, [(354, 149)])
    assert [r.label for r in MacServiceStudioDriver()._checkboxes(view)] == ["Root"]


def test_module_root_without_a_readable_checkbox_stays_first():
    # Seen on Mac: a module referenced in part showed no readable root checkbox, so the
    # first element row was taken for the module and the selection was refused.
    rows = [
        mac_ocr.DependencyRow("Counters_BL", (354.0, 149.0), 142.0),
        mac_ocr.DependencyRow("Counter_UpdateWrapper", (374.0, 169.0), 162.0),
        mac_ocr.DependencyRow("Counter_TakeNext", (374.0, 189.0), 182.0),
    ]
    view = _view(rows, [(374, 169), (374, 189)])
    driver = MacServiceStudioDriver()
    found = driver._resolve_root_state(driver._checkboxes(view))
    assert [r.label for r in found] == [
        "Counters_BL",
        "Counter_UpdateWrapper",
        "Counter_TakeNext",
    ]
    assert found[0].state == 0
