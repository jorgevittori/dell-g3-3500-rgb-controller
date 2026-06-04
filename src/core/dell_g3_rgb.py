import argparse
import ctypes
from ctypes import wintypes


VID = 0x187C
PID = 0x0550

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010

hid = ctypes.WinDLL("hid.dll")
setupapi = ctypes.WinDLL("setupapi.dll")
kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("InterfaceClassGuid", GUID),
        ("Flags", wintypes.DWORD),
        ("Reserved", ctypes.c_void_p),
    ]


class HIDD_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Size", wintypes.ULONG),
        ("VendorID", wintypes.USHORT),
        ("ProductID", wintypes.USHORT),
        ("VersionNumber", wintypes.USHORT),
    ]


class HIDP_CAPS(ctypes.Structure):
    _fields_ = [
        ("Usage", wintypes.USHORT),
        ("UsagePage", wintypes.USHORT),
        ("InputReportByteLength", wintypes.USHORT),
        ("OutputReportByteLength", wintypes.USHORT),
        ("FeatureReportByteLength", wintypes.USHORT),
        ("Reserved", wintypes.USHORT * 17),
        ("NumberLinkCollectionNodes", wintypes.USHORT),
        ("NumberInputButtonCaps", wintypes.USHORT),
        ("NumberInputValueCaps", wintypes.USHORT),
        ("NumberInputDataIndices", wintypes.USHORT),
        ("NumberOutputButtonCaps", wintypes.USHORT),
        ("NumberOutputValueCaps", wintypes.USHORT),
        ("NumberOutputDataIndices", wintypes.USHORT),
        ("NumberFeatureButtonCaps", wintypes.USHORT),
        ("NumberFeatureValueCaps", wintypes.USHORT),
        ("NumberFeatureDataIndices", wintypes.USHORT),
    ]


hid.HidD_GetHidGuid.argtypes = [ctypes.POINTER(GUID)]
hid.HidD_GetAttributes.argtypes = [wintypes.HANDLE, ctypes.POINTER(HIDD_ATTRIBUTES)]
hid.HidD_GetAttributes.restype = wintypes.BOOLEAN
hid.HidD_GetPreparsedData.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
hid.HidD_GetPreparsedData.restype = wintypes.BOOLEAN
hid.HidD_FreePreparsedData.argtypes = [ctypes.c_void_p]
hid.HidD_SetOutputReport.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.ULONG]
hid.HidD_SetOutputReport.restype = wintypes.BOOLEAN
hid.HidD_GetInputReport.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.ULONG]
hid.HidD_GetInputReport.restype = wintypes.BOOLEAN

hidp = ctypes.WinDLL("hid.dll")
hidp.HidP_GetCaps.argtypes = [ctypes.c_void_p, ctypes.POINTER(HIDP_CAPS)]
hidp.HidP_GetCaps.restype = ctypes.c_long

setupapi.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID), wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD]
setupapi.SetupDiGetClassDevsW.restype = wintypes.HANDLE
setupapi.SetupDiEnumDeviceInterfaces.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.POINTER(GUID),
    wintypes.DWORD,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
]
setupapi.SetupDiEnumDeviceInterfaces.restype = wintypes.BOOL
setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.c_void_p,
]
setupapi.SetupDiGetDeviceInterfaceDetailW.restype = wintypes.BOOL
setupapi.SetupDiDestroyDeviceInfoList.argtypes = [wintypes.HANDLE]

kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
]
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def enumerate_hid_paths():
    guid = GUID()
    hid.HidD_GetHidGuid(ctypes.byref(guid))
    info = setupapi.SetupDiGetClassDevsW(ctypes.byref(guid), None, None, DIGCF_PRESENT | DIGCF_DEVICEINTERFACE)
    if info == INVALID_HANDLE_VALUE:
        raise RuntimeError("SetupDiGetClassDevsW failed")

    paths = []
    try:
        index = 0
        while True:
            data = SP_DEVICE_INTERFACE_DATA()
            data.cbSize = ctypes.sizeof(data)
            if not setupapi.SetupDiEnumDeviceInterfaces(info, None, ctypes.byref(guid), index, ctypes.byref(data)):
                break

            needed = wintypes.DWORD()
            setupapi.SetupDiGetDeviceInterfaceDetailW(info, ctypes.byref(data), None, 0, ctypes.byref(needed), None)
            buf = ctypes.create_string_buffer(needed.value)
            ctypes.cast(buf, ctypes.POINTER(wintypes.DWORD))[0] = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
            if setupapi.SetupDiGetDeviceInterfaceDetailW(info, ctypes.byref(data), buf, needed.value, None, None):
                paths.append(ctypes.wstring_at(ctypes.addressof(buf) + 4))
            index += 1
    finally:
        setupapi.SetupDiDestroyDeviceInfoList(info)
    return paths


def open_device(path):
    handle = kernel32.CreateFileW(
        path,
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if handle == INVALID_HANDLE_VALUE:
        raise OSError(ctypes.get_last_error(), f"CreateFileW failed for {path}")
    return handle


def get_caps(handle):
    attrs = HIDD_ATTRIBUTES()
    attrs.Size = ctypes.sizeof(attrs)
    if not hid.HidD_GetAttributes(handle, ctypes.byref(attrs)):
        raise RuntimeError("HidD_GetAttributes failed")

    preparsed = ctypes.c_void_p()
    if not hid.HidD_GetPreparsedData(handle, ctypes.byref(preparsed)):
        raise RuntimeError("HidD_GetPreparsedData failed")
    try:
        caps = HIDP_CAPS()
        if hidp.HidP_GetCaps(preparsed, ctypes.byref(caps)) != 0x110000:
            raise RuntimeError("HidP_GetCaps failed")
        return attrs, caps
    finally:
        hid.HidD_FreePreparsedData(preparsed)


def find_controller():
    for path in enumerate_hid_paths():
        try:
            handle = open_device(path)
            try:
                attrs, caps = get_caps(handle)
                if attrs.VendorID == VID and attrs.ProductID == PID:
                    return path, caps.OutputReportByteLength or 34
            finally:
                kernel32.CloseHandle(handle)
        except (OSError, RuntimeError):
            pass
    raise RuntimeError("RGB controller VID_187C/PID_0550 not found. Run scripts\\TURN_ON.bat.")


def send_elc(handle, length, fragment):
    payload = bytearray.fromhex("03" + fragment)
    payload += bytes(max(0, 33 - len(payload)))
    raw = bytes([0]) + bytes(payload) if length == 34 else bytes(payload[:length])
    buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
    if not hid.HidD_SetOutputReport(handle, ctypes.byref(buf), len(raw)):
        raise RuntimeError(f"HidD_SetOutputReport failed for {fragment}")

    reply = (ctypes.c_ubyte * len(raw))()
    reply[0] = 0
    hid.HidD_GetInputReport(handle, ctypes.byref(reply), len(raw))
    return bytes(reply)


def apply_action(handle, length, animation, zones, color):
    r, g, b = color
    zone_hex = "".join(f"{z:02x}" for z in zones)
    zone_count = len(zones)
    rgb = f"{r:02x}{g:02x}{b:02x}"

    send_elc(handle, length, f"220004{animation:04x}")
    send_elc(handle, length, f"220001{animation:04x}")
    send_elc(handle, length, f"2301{zone_count:04x}{zone_hex}")
    send_elc(handle, length, f"2400ffff0001{rgb}")
    send_elc(handle, length, f"220002{animation:04x}")
    send_elc(handle, length, f"220006{animation:04x}")


def apply_multi_action(handle, length, animation, zone_colors):
    send_elc(handle, length, f"220004{animation:04x}")
    send_elc(handle, length, f"220001{animation:04x}")

    for zones, color in zone_colors:
        r, g, b = color
        zone_hex = "".join(f"{z:02x}" for z in zones)
        rgb = f"{r:02x}{g:02x}{b:02x}"
        send_elc(handle, length, f"2301{len(zones):04x}{zone_hex}")
        send_elc(handle, length, f"2400ffff0001{rgb}")

    send_elc(handle, length, f"220002{animation:04x}")
    send_elc(handle, length, f"220006{animation:04x}")


def set_static(handle, length, r, g, b, brightness):
    scale = max(0, min(100, brightness)) / 100
    full = tuple(int(c * scale) for c in (r, g, b))
    half = tuple(int(c * scale / 2) for c in (r, g, b))
    zones = [0, 1, 2, 3]

    apply_action(handle, length, 0x5B, zones, (0, 0, 0))
    apply_action(handle, length, 0x5C, zones, full)
    apply_action(handle, length, 0x5D, zones, full)
    apply_action(handle, length, 0x5E, zones, (0, 0, 0))
    apply_action(handle, length, 0x5F, zones, half)
    send_elc(handle, length, f"2600{len(zones):04x}{''.join(f'{z:02x}' for z in zones)}")


def scale_color(color, brightness, divisor=1):
    scale = max(0, min(100, brightness)) / 100 / divisor
    return tuple(int(c * scale) for c in color)


def set_zones_static(handle, length, zone_settings):
    all_zones = [0, 1, 2, 3]
    zone_colors = [
        ([zone], scale_color(color, brightness))
        for zone, color, brightness in zone_settings
    ]
    half_zone_colors = [
        ([zone], scale_color(color, brightness, divisor=2))
        for zone, color, brightness in zone_settings
    ]

    apply_action(handle, length, 0x5B, all_zones, (0, 0, 0))
    apply_multi_action(handle, length, 0x5C, zone_colors)
    apply_multi_action(handle, length, 0x5D, zone_colors)
    apply_action(handle, length, 0x5E, all_zones, (0, 0, 0))
    apply_multi_action(handle, length, 0x5F, half_zone_colors)
    send_elc(handle, length, f"2600{len(all_zones):04x}{''.join(f'{z:02x}' for z in all_zones)}")


def parse_color(value):
    if value.startswith("#"):
        value = value[1:]
    if len(value) == 6:
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    parts = [int(x.strip(), 0) for x in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Use #RRGGBB or R,G,B")
    return tuple(max(0, min(255, p)) for p in parts)


def main():
    parser = argparse.ArgumentParser(description="Dell G3 3500 4-zone RGB keyboard controller")
    parser.add_argument("command", choices=["on", "off", "color", "zones", "status"])
    parser.add_argument("value", nargs="?", default="#ffffff")
    parser.add_argument("--brightness", type=int, default=100)
    parser.add_argument("--zone1", default="#ffffff")
    parser.add_argument("--zone2", default="#ffffff")
    parser.add_argument("--zone3", default="#ffffff")
    parser.add_argument("--zone4", default="#ffffff")
    parser.add_argument("--zone1-brightness", type=int, default=100)
    parser.add_argument("--zone2-brightness", type=int, default=100)
    parser.add_argument("--zone3-brightness", type=int, default=100)
    parser.add_argument("--zone4-brightness", type=int, default=100)
    args = parser.parse_args()

    path, length = find_controller()
    if args.command == "status":
        print(f"OK {path} report_length={length}")
        return

    handle = open_device(path)
    try:
        if args.command == "off":
            set_static(handle, length, 0, 0, 0, 0)
        elif args.command == "on":
            set_static(handle, length, 255, 255, 255, args.brightness)
        elif args.command == "color":
            r, g, b = parse_color(args.value)
            set_static(handle, length, r, g, b, args.brightness)
        else:
            set_zones_static(handle, length, [
                (0, parse_color(args.zone1), args.zone1_brightness),
                (1, parse_color(args.zone2), args.zone2_brightness),
                (2, parse_color(args.zone3), args.zone3_brightness),
                (3, parse_color(args.zone4), args.zone4_brightness),
            ])
    finally:
        kernel32.CloseHandle(handle)


if __name__ == "__main__":
    main()
