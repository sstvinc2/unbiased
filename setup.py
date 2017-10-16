from setuptools import setup

setup(
    name="unbiased",
    version="5",
    packages=['unbiased', 'unbiased.sources'],
    package_data={
        'unbiased': [
            'html_template/*.html',
            'html_template/*.css',
            'html_template/*.ico',
            'html_template/*.png',
        ],
    },
    install_requires=[
        'jinja2',
        'Pillow',
        'requests',
        'lxml',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'unbiased = unbiased.main:main',
        ],
    },
)
