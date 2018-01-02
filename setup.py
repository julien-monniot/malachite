from setuptools import setup, find_packages

setup(
    name='malachite',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'napalm',
        'python-igraph',
        'plotly'
    ],
    entry_points='''
        [console_scripts]
        malachite-cli=malachite.scripts.cli_script:cli
    ''',
)
