from setuptools import find_packages, setup

#setup file that builds a distribution file and  can be installed in another environment
setup(
    name='tjenaFlask',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)