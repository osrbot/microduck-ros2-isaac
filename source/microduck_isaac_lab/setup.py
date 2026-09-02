"""Install the MicroDuck external Isaac Lab task package."""

from setuptools import find_packages, setup


setup(
    name="microduck_isaac_lab",
    version="0.1.0",
    description="Isaac Lab learning environments for MicroDuck",
    author="OSRBOT contributors",
    license="Apache-2.0",
    python_requires=">=3.12",
    packages=find_packages(),
    zip_safe=False,
)
