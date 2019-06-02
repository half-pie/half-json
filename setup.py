# coding=utf-8
# author@alingse
# 2019.05.29

import io

from setuptools import setup


with io.open('README.md', encoding='utf-8') as f:
    readme = f.read()


setup(
    name='halfjson',
    version='0.1.2',
    url='https://github.com/half-pie/half-json',
    description='A command tool/package fix invalid json: broken-json / truncated-json.',
    long_description=readme,
    author='alingse',
    author_email='alingse@foxmail.com',
    packages=['half_json'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jsonfixer = half_json.main:fixjson',
        ],
    }
)
