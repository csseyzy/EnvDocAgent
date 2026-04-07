# sonic-utilities Deployment Document

## Platform

- **Base Image:** sonicdev-microsoft.azurecr.io:443/sonic-slave-bookworm:master
- **Python Version:** 3.11 (Debian Bookworm system Python)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-protobuf \
    build-essential=12.9 \
    libnl-3-200 \
    libnl-genl-3-200 \
    libnl-route-3-200 \
    libnl-nf-3-200
```

## Build Steps

The following `.deb` and `.whl` packages must be obtained from the SONiC build infrastructure (Azure DevOps pipeline):
```bash
dpkg -i libyang_1.0.73_amd64.deb libyang-cpp_1.0.73_amd64.deb python3-yang_1.0.73_amd64.deb
dpkg -i libswsscommon_1.0.0_amd64.deb python3-swsscommon_1.0.0_amd64.deb
pip3 install swsssdk-2.0.1-py3-none-any.whl
pip3 install sonic_py_common-1.0-py3-none-any.whl
pip3 install sonic_yang_mgmt-1.0-py3-none-any.whl
pip3 install sonic_yang_models-1.0-py3-none-any.whl
pip3 install sonic_config_engine-1.0-py3-none-any.whl
pip3 install sonic_platform_common-1.0-py3-none-any.whl
pip3 install ".[testing]"
pip3 uninstall --yes sonic-utilities
```

## Test Steps

```bash
pytest
```

## Unexpected Issues

- **This project is NOT deployable outside the SONiC build infrastructure.** The required `.whl` and `.deb` packages are only available from Azure DevOps pipeline artifacts (`sonic-buildimage` pipeline). There is no public PyPI or apt repository for these dependencies.
- Recommend marking as **untestable in a generic Docker environment**.
