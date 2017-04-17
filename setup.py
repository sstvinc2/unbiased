from setuptools import setup

setup(
    name="unbiased",
    version="0",
    packages=['unbiased'],
    package_data={
        'unbiased': [
            'html_template/*.html',
            'html_template/*.css',
        ],
    },
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'unbiased = unbiased.main:main',
        ],
    },
)
