from core import labels
from tests.helpers import accidents, hourly_table


def test_hour_1_counts_at_hour_0():
    counts = labels.count_near_accidents(accidents([{"Day": 3, "Hour": 1, "SkidAngle": 40}]))
    assert counts.loc[(3, 0)] == 1


def test_hour_24_counts_at_hour_23():
    counts = labels.count_near_accidents(accidents([{"Day": 3, "Hour": 24, "CloseCarCm": 10}]))
    assert counts.loc[(3, 23)] == 1


def test_each_near_accident_kind_counts():
    frame = accidents([
        {"Day": 1, "Hour": 5, "SkidAngle": 40},
        {"Day": 1, "Hour": 5, "CloseCarCm": 10},
        {"Day": 1, "Hour": 5, "CloseGuardrailCm": 10},
    ])
    assert labels.count_near_accidents(frame).loc[(1, 4)] == 3


def test_real_accidents_are_not_near_accidents():
    frame = accidents([{"Day": 1, "Hour": 5, "Damage": 3000, "Injured": 1}])
    assert labels.count_near_accidents(frame).sum() == 0


def test_empty_row_is_reported_not_counted():
    frame = accidents([{"Day": 1, "Hour": 5}, {"Day": 1, "Hour": 5, "SkidAngle": 35}])
    report = labels.label_report(frame)
    assert report == {"rows": 2, "near_accidents": 1, "accidents": 0, "empty_rows": 1}
    assert labels.count_near_accidents(frame).sum() == 1


def test_only_skidding_mode():
    frame = accidents([{"Day": 1, "Hour": 5, "SkidAngle": 40}, {"Day": 1, "Hour": 5, "CloseCarCm": 10}])
    assert labels.count_near_accidents(frame, kinds=("SkidAngle",)).sum() == 1


def test_hours_without_events_are_zero():
    counts = labels.count_near_accidents(accidents([{"Day": 1, "Hour": 5, "SkidAngle": 40}]))
    assert len(counts) == 744
    assert counts.loc[(2, 2)] == 0


def test_attach_labels_adds_column():
    table = hourly_table().drop(columns="near_accidents")
    result = labels.attach_labels(table, accidents([{"Day": 1, "Hour": 1, "SkidAngle": 40}]))
    assert result["near_accidents"].sum() == 1
    assert result.query("day == 1 and hour == 0")["near_accidents"].iloc[0] == 1
