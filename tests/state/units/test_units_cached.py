import miniflask  # noqa: E402


assert_out = """
modules.main
modules.defineunits_cached
time data {time1}
--------------
time 1440.00 [minute]
time 1440.00 [minute] (re-access)
time 1440.00 [minute] (re-access)
time 24.00 [hour]
time 24.00 [hour] (re-access)
time 86400.00 [second]
time 1.00 [day]
time computation list m,h,d
time data 86400s, ['m', 'h', 'd']computation_list, 1440.0m, 24.0h, 1.0d

time2 data {time2}
--------------
time2 8640.00 [minute]
time2 144.00 [hour]
time2 518400.00 [second]
time2 6.00 [day]
time2 computation list m,h,d
time2 data 518400s, ['m', 'h', 'd']computation_list, 8640.0m, 144.0h, 6.0d

-------------
changing time
-------------

time base 175800.0s, ['m', 'h', 'd', 'm']computation_list
--------------
time 2930.00 [minute]
time 2930.00 [minute] (re-access)
time 2930.00 [minute] (re-access)
time 2930.00 [minute] (re-access)
time 48.83 [hour]
time 48.83 [hour] (re-access)
time 48.83 [hour] (re-access)
time 175800.00 [second]
time 2.03 [day]
time computation list m,h,d,m,m,h,d
time data 175800.0s, ['m', 'h', 'd', 'm', 'm', 'h', 'd']computation_list, 2930.0m, 48.833333333333336h, 2.0347222222222223d

time2 base 1039800.0s, ['m', 'h', 'd', 'm']computation_list
--------------
time2 17330.00 [mminute]
time2 288.83 [hour]
time2 1039800.00 [second]
time2 12.03 [day]
time2 computation list m,h,d,m,m,h,d
time2 data 1039800.0s, ['m', 'h', 'd', 'm', 'm', 'h', 'd']computation_list, 17330.0m, 288.8333333333333h, 12.034722222222221d
""".lstrip()


def test_unit_argparse_1d(capsys):
    mf = miniflask.init("modules")
    mf.load(["main", "defineunits_cached"])
    time1, time2 = "1d", "6d"
    mf.parse_args([
        "--time", time1,
        "--time2", time2
    ])
    mf.event.main()
    assert assert_out.format(time1=time1, time2=time2) == capsys.readouterr().out


def test_unit_argparse_24h(capsys):
    mf = miniflask.init("modules")
    mf.load(["main", "defineunits_cached"])
    time1, time2 = "24h", "144h"
    mf.parse_args([
        "--time", time1,
        "--time2", time2
    ])
    mf.event.main()
    assert assert_out.format(time1=time1, time2=time2) == capsys.readouterr().out


def test_unit_argparse_1440m(capsys):
    mf = miniflask.init("modules")
    mf.load(["main", "defineunits_cached"])
    time1, time2 = "24h", "144h"
    mf.parse_args([
        "--time", time1,
        "--time2", time2
    ])
    mf.event.main()
    assert assert_out.format(time1=time1, time2=time2) == capsys.readouterr().out
