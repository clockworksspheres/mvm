import platform


def tell_hw_platform():
    hw = platform.machine()

    amd64_hw_types = ["x86_64", "amd64", "AMD64"]
    arm64_hw_types = ["aarch64", "arm64"]

    if hw in amd64_hw_types:
        hw_type = "amd64"
    elif hw in arm64_hw_types:
        hw_type = "arm64"
    else:
        print("unknown hw type: {hw}")
        hw_type = ""

    return hw_type


