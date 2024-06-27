from setuptools import setup

setup(
    name='sapienpd',
    version='0.0.0',
    packages=['sapienpd'],
    package_dir={'':'src'},
    install_requires=[
        'numpy',
        'meshio',
        'scipy',
    ],
)
