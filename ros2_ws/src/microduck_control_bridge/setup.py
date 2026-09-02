"""Install the MicroDuck ROS-to-Isaac playground bridge."""

from glob import glob
import os

from setuptools import find_packages, setup


PACKAGE_NAME = "microduck_control_bridge"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{PACKAGE_NAME}"]),
        (f"share/{PACKAGE_NAME}", ["package.xml", "README.md", "LICENSE"]),
        (os.path.join("share", PACKAGE_NAME, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="dajianli",
    maintainer_email="8427748+dajianli@users.noreply.github.com",
    description="ROS 2 command and telemetry bridge for the MicroDuck Isaac playground.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "microduck_bridge = microduck_control_bridge.bridge_node:main",
            "microduck_teleop = microduck_control_bridge.keyboard_teleop:main",
        ],
    },
)
