"""Install the MicroDuck ROS 2 simulation examples."""

from glob import glob
import os

from setuptools import find_packages, setup


PACKAGE_NAME = "microduck_examples"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{PACKAGE_NAME}"]),
        (f"share/{PACKAGE_NAME}", ["package.xml", "README.md"]),
        (os.path.join("share", PACKAGE_NAME, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="dajianli",
    maintainer_email="8427748+dajianli@users.noreply.github.com",
    description="Runnable ROS 2 simulation examples for MicroDuck.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "rviz_motion_demo = microduck_examples.rviz_motion_demo:main",
            "isaac_showcase = microduck_examples.isaac_showcase:main",
        ],
    },
)
